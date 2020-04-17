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
import os
import numpy as np
import nemo
import nemo.collections.nlp as nemo_nlp
from nemo import logging
from nemo.collections.nlp.nm.trainables import TokenClassifier
from nemo.collections.nlp.utils.data_utils import get_vocab

MAX_SEQ_LENGTH=128
PRETRAINED_MODEL_NAME='bert-base-uncased'
CHECKPOINT_DIR = 'trained_ner_model_checkpoints'
LABELS_DICT = 'ner_label_ids.csv'
BERT_CONFIG = None
TOKENIZER='nemobert'
TOKENIZER_MODEL = None
NONE_LABEL='O'
ADD_BRACKETS = True
#QUERIES_PLACEHOLDER = ['we bought four shirts from the nvidia gear store in santa clara', 'Nvidia is a company', 'The Adventures of Tom Sawyer by Mark Twain is an 1876 novel about a young boy growing up along the Mississippi River',]


nf = nemo.core.NeuralModuleFactory(backend=nemo.core.Backend.PyTorch, log_dir=None)

in_file = open('cleaned_ner_note_test.txt')
out_file = open('ner_output_test.txt', 'w+')
QUERIES_PLACEHOLDER = in_file.readlines()

labels_dict = get_vocab(LABELS_DICT)

""" Load the pretrained BERT parameters
See the list of pretrained models, call:
nemo_nlp.huggingface.BERT.list_pretrained_models()
"""
pretrained_bert_model = nemo_nlp.nm.trainables.get_huggingface_model(
    bert_config=BERT_CONFIG, pretrained_model_name=PRETRAINED_MODEL_NAME
)

tokenizer = nemo.collections.nlp.data.tokenizers.get_tokenizer(
    tokenizer_name=TOKENIZER,
    pretrained_model_name=PRETRAINED_MODEL_NAME,
    tokenizer_model=TOKENIZER_MODEL,
)
hidden_size = pretrained_bert_model.hidden_size


data_layer = nemo_nlp.nm.data_layers.BertTokenClassificationInferDataLayer(
    queries=QUERIES_PLACEHOLDER, tokenizer=tokenizer, max_seq_length=MAX_SEQ_LENGTH, batch_size=1
)

classifier = TokenClassifier(hidden_size=hidden_size, num_classes=len(labels_dict))

input_ids, input_type_ids, input_mask, _, subtokens_mask = data_layer()

hidden_states = pretrained_bert_model(input_ids=input_ids, token_type_ids=input_type_ids, attention_mask=input_mask)
logits = classifier(hidden_states=hidden_states)

###########################################################################

# Instantiate an optimizer to perform `infer` action
evaluated_tensors = nf.infer(tensors=[logits, subtokens_mask], checkpoint_dir=CHECKPOINT_DIR)


def concatenate(lists):
    return np.concatenate([t.cpu() for t in lists])


def add_brackets(text, add=ADD_BRACKETS):
    return '[' + text + ']' if add else text


logits, subtokens_mask = [concatenate(tensors) for tensors in evaluated_tensors]

preds = np.argmax(logits, axis=2)

for i, query in enumerate(QUERIES_PLACEHOLDER):
    logging.info(f'Query: {query}')

    pred = preds[i][subtokens_mask[i] > 0.5]
    words = query.strip().split()
    if len(pred) != len(words):
        raise ValueError('Pred and words must be of the same length')

    output = ''
    for j, w in enumerate(words):
        output += w
        label = labels_dict[pred[j]]
        if label != NONE_LABEL:
            label = add_brackets(label)
            output += label
        output += ' '
    print(output.strip(), file = out_file)
    logging.info(f'Combined: {output.strip()}')
