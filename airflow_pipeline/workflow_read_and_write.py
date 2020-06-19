import pymongo
import gridfs
import datetime
import pandas as pd

def get_db():
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['emr_steps']
    return db

def standard_read_from_db(collection_name):
    db = get_db()
    fs = gridfs.GridFS(db)
    collection = db[collection_name]
    most_recent_entry = collection.find_one(sort=[('_id', pymongo.DESCENDING)])
    prev_step_output = fs.get(most_recent_entry['gridfs_id']).read()
    return prev_step_output

def standard_write_to_db(collection_name, step_output):
    db = get_db()
    fs = gridfs.GridFS(db)
    collection = db[collection_name]
    timestamp = datetime.datetime.now().timestamp()
    gridfs_id = fs.put(step_output)
    mongodb_output = {'timestamp':timestamp, 'gridfs_id':gridfs_id}
    collection.insert_one(mongodb_output)

def lda_read_from_db():
    db = get_db()
    collection = db['lda_model']
    most_recent_entry = collection.find_one(sort=[('_id', pymongo.DESCENDING)])

    dictionary_pickle = fs.get(most_recent_entry['dictionary_gridfs_id']).read()
    corpus_pickle = fs.get(most_recent_entry['corpus_gridfs_id']).read()
    lda_model_pickle = fs.get(most_recent_entry['lda_model_gridfs_id']).read()

    dictionary = pickle.loads(dictionary_pickle)
    corpus = pickle.loads(corpus_pickle)
    lda_model = pickle.loads(lda_model_pickle)

    return dictionary, corpus, lda_model

def lda_write_to_db(dictionary, corpus, lda_model):
    db = get_db()
    collection = db['lda_model']
    fs = gridfs.GridFS(db)

    #serialize objects
    dictionary_pickle = pickle.dumps(dictionary)
    corpus_pickle = pickle.dumps(corpus)
    lda_model_pickle = pickle.dumps(lda_model)

    dictionary_gridfs_id = fs.put(dictionary_pickle)
    corpus_gridfs_id = fs.put(corpus_pickle)
    lda_model_gridfs_id = fs.put(lda_model_pickle)
    timestamp = datetime.datetime.now().timestamp()

    mongodb_output = {
            'timestamp': timestamp,
            'dictionary_gridfs_id': dictionary_gridfs_id,
            'corpus_gridfs_id': corpus_gridfs_id,
            'lda_model_gridfs_id': lda_model_gridfs_id
            }

    collection.insert_one(mongodb_output)

def train_ner_write_to_db(tokenizer_pickle, bert_model_pickle, label_ids_pickle):
        db = get_db()
        fs = gridfs.GridFS(db)
        collection = db['trained_ner']
        timestamp = datetime.datetime.now().timestamp()
        tokenizer_gridfs_id = fs.put(tokenizer_pickle)
        bert_model_gridfs_id = fs.put(bert_model_pickle)
        label_ids_gridfs_id = fs.put(label_ids_pickle)
        mongodb_output = {
                'timestamp':timestamp,
                'tokenizer_gridfs_id':tokenizer_gridfs_id,
                'bert_model_gridfs_id':bert_model_gridfs_id,
                'label_ids_gridfs_id': label_ids_gridfs_id
                }

        collection.insert_one(mongodb_output)

def train_ner_read_from_db():
    db = get_db()
    fs = gridfs.GridFS(db)
    collection = db['trained_ner']

    most_recent_entry = collection.find_one(sort=[('_id', pymongo.DESCENDING)])
    tokenizer_pickle = fs.get(most_recent_entry['tokenizer_gridfs_id'])
    bert_model_pickle = fs.get(most_recent_entry['bert_model_gridfs_id'])
    label_ids_pickle = fs.get(most_recent_entry['label_ids_gridfs_id'])
    return tokenizer_pickle, bert_model_pickle, label_ids_pickle

def one_hot_write_to_db(updated_df_json_encoded, term_cos_simil_df_json_encoded, collection_name):
    db = get_db()
    fs = gridfs.GridFS(db)
    collection = db[collection_name]

    updated_df_gridfs_id = fs.put(updated_df_json_encoded)
    term_cos_simil_df_gridfs_id = fs.put(term_cos_simil_df_json_encoded)
    timestamp = datetime.datetime.now().timestamp()

    mongodb_output = {
            'timestamp': timestamp,
            'updated_df_gridfs_id': updated_df_gridfs_id,
            'term_cos_simil_df_gridfs_id': term_cos_simil_df_gridfs_id
            }

    collection.insert_one(mongodb_output)

def one_hot_read_from_db(collection_name):
    db = get_db()
    fs = gridfs.GridFS(db)
    collection = db[collection_name]

    most_recent_entry = collection.find_one(sort=[('_id', pymongo.DESCENDING)])
    updated_df_json_encoded = fs.get(most_recent_entry['updated_df_gridfs_id']).read()
    term_cos_simil_df_json_encoded = fs.get(most_recent_entry['term_cos_simil_df_gridfs_id']).read()

    return updated_df_json_encoded, term_cos_simil_df_json_encoded

def tpot_write_to_db(tpot_pipeline_code_encoded, score_encoded, collection_name):
    db = get_db()
    fs = gridfs.GridFS(db)
    collection = db[collection_name]

    tpot_pipeline_gridfs_id = fs.put(tpot_pipeline_code_encoded)
    score_gridfs_id = fs.put(score_encoded)
    timestamp = datetime.datetime.now().timestamp()

    mongodb_output = {
        'timestamp': timestamp,
        'tpot_pipeline_gridfs_id': tpot_pipeline_gridfs_id,
        'score_gridfs_id': score_gridfs_id
        }

    collection.insert_one(mongodb_output)

def tpot_read_from_db(collection_name):
    db = get_db()
    fs = gridfs.GridFS(db)
    collection = db[collection_name]

    most_recent_entry = collection.find_one(sort=[('_id', pymongo.DESCENDING)])
    tpot_pipeline_code_encoded = fs.get(most_recent_entry['tpot_pipeline_gridfs_id']).read()
    score_encoded = fs.get(most_recent_entry['score_gridfs_id']).read()

    return tpot_pipeline_code_encoded, score_encoded

def readmission_classifier_write_to_db(df_json_encoded, classifier_pickle):
    db = get_db()
    fs = gridfs.GridFS(db)
    collection = db['readmission_classifier_train_predict']
    
    df_gridfs_id = fs.put(df_json_encoded)
    classifier_gridfs_id = fs.put(classifier_pickle)
    timestamp = datetime.datetime.now().timestamp()

    mongodb_output = {
        'timestamp': timestamp,
        'df_gridfs_id': df_gridfs_id,
        'classifier_gridfs_id': classifier_gridfs_id
        }

    collection.insert_one(mongodb_output)     

def readmission_classifier_read_from_db():
    db = get_db()
    fs = gridfs.GridFS(db)
    collection = db['readmission_classifier_train_predict']

    most_recent_entry = collection.find_one(sort=[('_id', pymongo.DESCENDING)])
    df_json_encoded = fs.get(most_recent_entry['df_gridfs_id']).read()
    classifier_pickle = fs.get(most_recent_entry['classifier_gridfs_id'])

    return df_json_encoded, classifier_pickle

def xgb_write_to_db(collection_name, df_json_encoded, xgb_pickle):
    db = get_db()
    fs = gridfs.GridFS(db)
    collection = db[collection_name]

    df_gridfs_id = fs.put(df_json_encoded)
    xgb_gridfs_id = fs.put(xgb_pickle)
    timestamp = datetime.datetime.now().timestamp()

    mongodb_output = {
        'timestamp': timestamp,
        'df_gridfs_id': df_gridfs_id,
        'xgb_gridfs_id': xgb_gridfs_id
        }

    collection.insert_one(mongodb_output)

def xgb_read_from_db(collection_name):
    db = get_db()
    fs = gridfs.GridFS(db)
    collection = db[collection_name]

    most_recent_entry = collection.find_one(sort=[('_id', pymongo.DESCENDING)])
    df_json_encoded = fs.get(most_recent_entry['df_gridfs_id']).read()
    xgb_pickle = fs.get(most_recent_entry['xgb_gridfs_id'])

    return df_json_encoded, xgb_pickle

