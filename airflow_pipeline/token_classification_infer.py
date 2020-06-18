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

import argparse
import os

import numpy as np
import time

import nemo
import nemo.collections.nlp as nemo_nlp
from nemo import logging
from nemo.collections.nlp.nm.trainables import TokenClassifier
from nemo.collections.nlp.utils.data_utils import get_vocab
from nemo.core import NeuralGraph, OperationMode

MAX_SEQ_LENGTH = 128
#choices for PRETRAINED_MODEL_NAME: choices=nemo_nlp.nm.trainables.get_pretrained_lm_models_list()
PRETRAINED_MODEL_NAME = 'bert-base-uncased'
BERT_CONFIG = None
TOKENIZER_MODEL = None
VOCAB_FILE = None
#choices for TOKENIZER: ["nemobert", "sentencepiece"]
TOKENIZER = 'nemobert'
NONE_LABEL = 'O'
ADD_BRACKETS = True
#CHECKPOINT_DIR = 'ner/trained_ner_model_checkpoints'
CHECKPOINT_DIR = '/home/ubuntu/emr-workflow/airflow_pipeline/ner/trained_ner_model_checkpoints'
LABELS_DICT = 'ner/ner_label_ids.csv'

def concatenate(lists):
    return np.concatenate([t.cpu() for t in lists])

def add_brackets(text, add=ADD_BRACKETS):
    return '[' + text + ']' if add else text

#out_file = open('all_notes_label_lines.txt', 'a')
out_file = open('./all_notes_label_lines.txt', 'w+')

if not os.path.exists(CHECKPOINT_DIR):
    raise ValueError(f'Checkpoint directory not found at {CHECKPOINT_DIR}')
if not os.path.exists(LABELS_DICT):
    raise ValueError(f'Dictionary with ids to labels not found at {LABELS_DICT}')

nf = nemo.core.NeuralModuleFactory(backend=nemo.core.Backend.PyTorch, log_dir='nemo_logs')

labels_dict = get_vocab(LABELS_DICT)

""" Load the pretrained BERT parameters
See the list of pretrained models, call:
nemo_nlp.huggingface.BERT.list_pretrained_models()
"""
pretrained_bert_model = nemo_nlp.nm.trainables.get_pretrained_lm_model(
    config=BERT_CONFIG, pretrained_model_name=PRETRAINED_MODEL_NAME, vocab=VOCAB_FILE
)

tokenizer = nemo.collections.nlp.data.tokenizers.get_tokenizer(
    tokenizer_name=TOKENIZER,
    pretrained_model_name=PRETRAINED_MODEL_NAME,
    tokenizer_model=TOKENIZER_MODEL,
)
hidden_size = pretrained_bert_model.hidden_size

classifier = TokenClassifier(hidden_size=hidden_size, num_classes=len(labels_dict))

#functionalized for our pipeline
def inference(queries):
    begin = time.time()
    datalayer_begin = time.time()
    data_layer = nemo_nlp.nm.data_layers.BertTokenClassificationInferDataLayer(
        queries=queries, tokenizer=tokenizer, max_seq_length=MAX_SEQ_LENGTH, batch_size=2048
    )
    datalayer_end = time.time()
    datalayer_time =datalayer_end - datalayer_begin

    with NeuralGraph(operation_mode=OperationMode.evaluation) as g1:
        input_ids, input_type_ids, input_mask, _, subtokens_mask = data_layer()
        hidden_states = pretrained_bert_model(input_ids=input_ids, token_type_ids=input_type_ids, attention_mask=input_mask)
        logits = classifier(hidden_states=hidden_states)

    ###########################################################################

    # Instantiate an optimizer to perform `infer` action
    infer_begin = time.time()
    evaluated_tensors = nf.infer(tensors=[logits, subtokens_mask], checkpoint_dir=CHECKPOINT_DIR)
    infer_end = time.time()
    infer_time = infer_end - infer_begin

    logits, subtokens_mask = [concatenate(tensors) for tensors in evaluated_tensors]

    preds = np.argmax(logits, axis=2)

    for i, query in enumerate(queries):
        logging.info(f'Query: {query}')

        pred = preds[i][subtokens_mask[i] > 0.5]
        words = query.strip().split()
        if len(pred) == len(words):
            #raise ValueError('Pred and words must be of the same length')
            output = ''
            for j, w in enumerate(words):
                output += w
                label = labels_dict[pred[j]]
                if label != NONE_LABEL:
                    label = add_brackets(label)
                    output += label
                output += ' '
        else:
            output = query
        logging.info(f'Combined: {output.strip()}')
        print(output.strip(),file=out_file)

    del data_layer
    del g1
    del evaluated_tensors

    end=time.time()
    total_time = end-begin
    logging.info(f'Load datalayer time: {datalayer_time}')
    logging.info(f'Inference time: {infer_time}')
    logging.info(f'Total time: {total_time}')
