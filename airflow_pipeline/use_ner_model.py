# =============================================================================
# Copyright 2020 NVIDIA. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================

#This is a modified version of this script:
# https://github.com/NVIDIA/NeMo/blob/master/examples/nlp/token_classification/token_classification_infer.py

import argparse
import os

import numpy as np
import pandas as pd
import pickle

import nemo
import nemo.collections.nlp as nemo_nlp
from nemo.collections.nlp.data import NemoBertTokenizer
from nemo.collections.nlp.nm.trainables import TokenClassifier
from nemo.collections.nlp.utils.common_nlp_utils import get_vocab

from workflow_read_and_write import train_ner_read_from_db, standard_read_from_db, standard_write_to_db

max_seq_length = int(128)
fc_droput = float(0)
none_label = 'O'
#This specifies that we would like to use the TensorCores in the GPU
amp_opt_level = 'O1'
work_dir = './output/checkpoints'

# queries is a list of strings to be used as input for inference
def infer_from_ner_model(tokenizer, bert_model, label_ids, queries):
    nf = nemo.core.NeuralModuleFactory(
            backend = nemo.core.Backend.PyTorch, 
            optimization_level = amp_opt_level, 
            log_dir = None)
    hidden_size = bert_model.hidden_size
    data_layer = nemo_nlp.nm.data_layers.BertTokenClassificationInferDataLayer(
                queries=queries, tokenizer=tokenizer, max_seq_length=max_seq_length, batch_size=1
                )
    classifier = TokenClassifier(hidden_size=hidden_size, num_classes=len(label_ids), dropout=fc_dropout)
    input_ids, input_type_ids, input_mask, _, subtokens_mask = data_layer()
    #changed pretrained_bert_model to the passed-in bert_model
    hidden_states = bert_model(input_ids=input_ids, token_type_ids=input_type_ids, attention_mask=input_mask)
    logits = classifier(hidden_states=hidden_states)
    evaluated_tensors = nf.infer(tensors=[logits, subtokens_mask], checkpoint_dir=work_dir)
    logits, subtokens_mask = [concatenate(tensors) for tensors in evaluated_tensors]
    preds = np.argmax(logits, axis=2)
    
    query_outputs = []
    for i, query in enumerate(queries):
        pred = preds[i][subtokens_mask[i] > 0.5]
        words = query.strip().split()
        if len(pred) != len(words):
            raise ValueError('Pred and words must be of the same length')
        output = ''
        for j, w in enumerate(words):
            output += w
            label = labels_ds[pred[j]]
            if label != none_label:
                label = '[' + label + ']'
                output += label
            output += ' '
        query_outputs += output
    return query_outputs


def concatenate(lists):
    return np.concatenate([t.cpu() for t in lists])

def run_ner_on_notes():
    first_dataframe_json_encoded = standard_read_from_db('first_dataframe')
    df_json = first_dataframe_json_encoded.decode()
    df = pd.read_json(df_json)
    notes_list = df['notes'].tolist()

    tokenizer_pickle, bert_model_pickle, label_ids_pickle = train_ner_read_from_db()
    tokenizer = pickle.loads(tokenizer_pickle)
    bert_model = pickle.loads(bert_model_pickle)
    lable_ids = pickle.loads(label_ids_pickle)

    notes_labeled = infer_from_ner_model(tokenizer, bert_model, label_ids, notes_list)
    df['note_entities_labeled'] = notes_labeled

    df_json = df.to_json()
    df_json_encoded = df_json.encode()
    standard_write_to_db('post_ner_inference',df_json_encoded)
