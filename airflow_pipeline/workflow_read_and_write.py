import pymongo
import gridfs
import datetime

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
    labe_ids_pickle = fs.get(most_recent_entry['label_ids_gridfs_id'])
    return tokenizer_pickle, bert_model_pickle, label_ids_pickle
