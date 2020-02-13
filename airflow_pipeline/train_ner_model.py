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

import pymongo
import gridfs
import datetime
import pickle
import nemo
import math
import os

import nemo
from nemo.utils.lr_policies import WarmupAnnealing

import nemo.collections.nlp as nemo_nlp
from nemo.collections.nlp.data import NemoBertTokenizer, SentencePieceTokenizer
from nemo.collections.nlp.callbacks.token_classification_callback import eval_iter_callback, eval_epochs_done_callback
from nemo.collections.nlp.nm.losses import TokenClassificationLoss
from nemo.collections.nlp.nm.trainables import TokenClassifier
from workflow_read_and_write import train_ner_write_to_db

def read_from_db():
    client = pymongo.MyClient('mongodb://localhost:27017/')
    db = client['emr_steps']
    collection = db['word2vec']
    fs = gridfs.GridFS(db)
    most_recent_entry = collection.find_one(sort=[('_id', pymongo.DESCENDING)])
    word2vec_model_pickle = fs.get(most_recent_entry['gridfs_id']).read()
    return word2vec_model_pickle

def write_to_db(ner_output):
    client = pymongo.MyClient('mongodb://localhost:27017/')
    db = client['emr_steps']
    collection = db['entity_recognition']
    fs = gridfs.GridFS(db)
    ner_output_encoded = ner_output.encode()
    gridfs_id = fs.put(ner_output_encoded)
    timestamp = datetime.datetime.now().timestamp()
    mongodb_output = {'timestamp': timestamp, 'gridfs_id': gridfs_id}
    collection.insert_one(mongodb_output)

def train_clinical_bert_for_ner():
    nf = nemo.core.NeuralModuleFactory(backend=nemo.core.Backend.PyTorch,
                                        local_rank=None,
                                        optimization_level="O1",
                                        log_dir="output_ner",
                                        create_tb_writer=True)

    tokenizer = NemoBertTokenizer(pretrained_model="clinicalBERT_model")
    bert_model = nemo_nlp.huggingface.BERT(pretrained_model="clinicalBERT_model")

    train_data_layer = nemo_nlp.BertTokenClassificationDataLayer(
        tokenizer=tokenizer,
        text_file=os.path.join('./ner_data', 'train_text.txt'),
        label_file=os.path.join('./ner_data', 'train_labels.txt'),
        max_seq_length=MAX_SEQ_LENGTH,
        batch_size=BATCH_SIZE)

    label_ids = train_data_layer.dataset.label_ids
    num_classes = len(label_ids)

    hidden_size = bert_model.hidden_size
    ner_classifier = TokenClassifier(hidden_size=hidden_size,
                                             num_classes=num_classes,
                                             dropout=CLASSIFICATION_DROPOUT)

    ner_loss = TokenClassificationLoss(num_classes=len(label_ids))

    input_ids, input_type_ids, input_mask, loss_mask, _, labels = train_data_layer()

    hidden_states = bert_model(input_ids=input_ids,
                               token_type_ids=input_type_ids,
                               attention_mask=input_mask)

    logits = ner_classifier(hidden_states=hidden_states)
    loss = ner_loss(logits=logits, labels=labels, loss_mask=loss_mask)

    # Describe evaluation DAG
    eval_data_layer = nemo_nlp.nm.data_layers.BertTokenClassificationDataLayer(
            tokenizer=tokenizer,
            text_file=os.path.join('./ner_data', 'test_text.txt'),
            label_file=os.path.join('./ner_data', 'test_labels.txt'),
            max_seq_length=MAX_SEQ_LENGTH,
            batch_size=BATCH_SIZE,
            label_ids=label_ids)

    eval_input_ids, eval_input_type_ids, eval_input_mask, _, eval_subtokens_mask, eval_labels = eval_data_layer()

    hidden_states = bert_model(
        input_ids=eval_input_ids,
        token_type_ids=eval_input_type_ids,
        attention_mask=eval_input_mask)

    eval_logits = ner_classifier(hidden_states=hidden_states)

    callback_train = nemo.core.SimpleLossLoggerCallback(
        tensors=[loss],
        print_func=lambda x: print("Loss: {:.3f}".format(x[0].item())))

    train_data_size = len(train_data_layer)

    # If you're training on multiple GPUs, this should be
    # train_data_size / (batch_size * batches_per_step * num_gpus)
    steps_per_epoch = int(train_data_size / (BATCHES_PER_STEP * BATCH_SIZE))

    # Callback to evaluate the model
    callback_eval = nemo.core.EvaluatorCallback(
        eval_tensors=[eval_logits, eval_labels, eval_subtokens_mask],
        user_iter_callback=lambda x, y: eval_iter_callback(x, y),
        user_epochs_done_callback=lambda x: eval_epochs_done_callback(x, label_ids),
        eval_step=steps_per_epoch)

    # Callback to store checkpoints
    # Checkpoints will be stored in checkpoints folder inside WORK_DIR
    ckpt_callback = nemo.core.CheckpointCallback(
        folder=neural_factory.checkpoint_dir,
        epoch_freq=1)

    lr_policy = WarmupAnnealing(NUM_EPOCHS * steps_per_epoch,
                                warmup_ratio=LR_WARMUP_PROPORTION)
    neural_factory.train(
        tensors_to_optimize=[loss],
        callbacks=[callback_train, callback_eval, ckpt_callback],
        lr_policy=lr_policy,
        batches_per_step=BATCHES_PER_STEP,
        optimizer=OPTIMIZER,
        optimization_params={
            "num_epochs": NUM_EPOCHS,
            "lr": LEARNING_RATE
        })

    return tokenizer, bert_model, label_ids

def create_entity_recognition():
    tokenizer, bert_model, label_ids = train_clinical_bert_for_ner()
    tokenizer_pickle = pickle.dumps(tokenizer)
    bert_model_pickle = pickle.dumps(bert_model)
    label_ids_pickle = pickle.dumps(label_ids)
    train_ner_write_to_db(tokenizer_pickle, bert_model_pickle, label_ids_pickle)
