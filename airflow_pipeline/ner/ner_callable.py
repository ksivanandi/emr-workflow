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
CHECKPOINT_DIR = '/home/mworthington/emr-workflow/airflow_pipeline/ner/trained_ner_model_checkpoints'
LABELS_DICT = '/home/mworthington/emr-workflow/airflow_pipeline/ner/ner_label_ids.csv'
BERT_CONFIG = None
TOKENIZER='nemobert'
TOKENIZER_MODEL = None
NONE_LABEL='O'
ADD_BRACKETS = True

nf = nemo.core.NeuralModuleFactory(backend=nemo.core.Backend.PyTorch, log_dir='home/mworthington/emr-workflow/airflow_pipeline/ner/logs')

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

def concatenate(lists):
    return np.concatenate([t.cpu() for t in lists])


def add_brackets(text, add=ADD_BRACKETS):
    return '[' + text + ']' if add else text

def label_notes(all_notes_lines):
#    nf = nemo.core.NeuralModuleFactory(backend=nemo.core.Backend.PyTorch, log_dir=None)
    #note_line_queries = notes.split('\n')
    #note_line_queries = ['pt arrived obtunded not answering questions responding to voice and sternal rub speaking in garbled voice pupils unequal left 3mm and right 2mm brisk bilaterally trauma sicu MD aware currently recieving keppra IV finished dilantin gtt due for level at 08a EEG today LSCTA on 3LNC sats 100 % SBP 90 s to 100 s HR NSR no ectopy 60 s NS @ 75cc continuous +BS no stools rec d lactulose at OSH to recieve PR q4h abd soft non-tender non-distended foley in place draining adequate amt clear yellow urine skin intact left 20G x2 WNL wife Name  NI']

#    labels_dict = get_vocab(LABELS_DICT)

    """ Load the pretrained BERT parameters
    See the list of pretrained models, call:
    nemo_nlp.huggingface.BERT.list_pretrained_models()
    """
#    pretrained_bert_model = nemo_nlp.nm.trainables.get_huggingface_model(
#        bert_config=BERT_CONFIG, pretrained_model_name=PRETRAINED_MODEL_NAME
#    )

#    tokenizer = nemo.collections.nlp.data.tokenizers.get_tokenizer(
#        tokenizer_name=TOKENIZER,
#        pretrained_model_name=PRETRAINED_MODEL_NAME,
#        tokenizer_model=TOKENIZER_MODEL,
#    )
#    hidden_size = pretrained_bert_model.hidden_size

    data_layer = nemo_nlp.nm.data_layers.BertTokenClassificationInferDataLayer(
        queries=all_notes_lines, tokenizer=tokenizer, max_seq_length=MAX_SEQ_LENGTH, batch_size=2000
    )

    classifier = TokenClassifier(hidden_size=hidden_size, num_classes=len(labels_dict))

    input_ids, input_type_ids, input_mask, _, subtokens_mask = data_layer()

    hidden_states = pretrained_bert_model(input_ids=input_ids, token_type_ids=input_type_ids, attention_mask=input_mask)
    logits = classifier(hidden_states=hidden_states)

    ###########################################################################

    # Instantiate an optimizer to perform `infer` action
    evaluated_tensors = nf.infer(tensors=[logits, subtokens_mask], checkpoint_dir=CHECKPOINT_DIR)

    logits, subtokens_mask = [concatenate(tensors) for tensors in evaluated_tensors]

    preds = np.argmax(logits, axis=2) 
    all_notes_labeled_lines = []

    for i, query in enumerate(all_notes_lines):
        logging.info(f'Query: {query}')

        pred = preds[i][subtokens_mask[i] > 0.5]
        words = query.strip().split()

        #replaced with logic below instead of raising an error:
        '''
        if len(pred) != len(words):
            logging.info('Preds length: ' + str(len(preds[i])))
            logging.info('subtokens_mask length: ' + str(len(subtokens_mask[i])))
            logging.info('Pred length: ' + str(len(pred)))
            logging.info('words length: ' + str(len(words)))
            logging.info('Preds: ' + str(preds.tolist()))
            logging.info('subtokens_mask: ' + str(subtokens_mask[i]))
            logging.info('Pred:' + str(pred.tolist()))
            logging.info('words:' + str(words))

            labeled_note = '__Prediction/Word Mismatch__ pred length: ' + str(len(pred)) + ', words length: ' + str(len(words))
            break
            #raise ValueError('Pred and words must be of the same length')
        
        output = ''
        for j, w in enumerate(words):
            output += w
            label = labels_dict[pred[j]]
            if label != NONE_LABEL:
                label = add_brackets(label)
                output += label
            output += ' '
        labeled_note += '\n' + output.strip()
        logging.info(f'Combined: {output.strip()}')

        '''

        if len(pred) == len(words):
            output = ''
            for j, w in enumerate(words):
                output += w
                label = labels_dict[pred[j]]
                if label != NONE_LABEL:
                    label = add_brackets(label)
                    output += label
                output += ' '
            all_notes_labeled_lines.append(output.strip())
            logging.info(f'Combined: {output.strip()}')
        else:
            all_notes_labeled_lines.append(query)
            pred_length = str(len(pred))
            word_length = str(len(words))
            logging.info(f'__Prediction/Word Length Mismatch__ pred length: {pred_length}, words length: {word_length}')
            logging.info(f'{query}')
        
    return all_notes_labeled_lines

