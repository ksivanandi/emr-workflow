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

def infection_keywords_read_from_db():
    db = get_db()
    collection = db['infection_one_hot']
    fs = gridfs.GridFS(db)

    most_recent_entry = collection.find_one(sort=[('_id', pymongo.DESCENDING)])
    updated_df_json = fs.get(most_recent_entry['updated_df_gridfs_id']).read().decode()
    term_cos_simil_df_json = fs.get(most_recent_entry['term_cos_simil_df_gridfs_id']).read().decode()

    updated_df = pd.read_json(update_df_json)
    term_cos_simil_df = pd.read_json(term_cos_simil_df_json)

    return updated_df, term_cos_simil_df

def infection_keywords_write_to_db(updated_df, flattened_list):
    db = get_db()
    collection = db['infection_one_hot']
    fs = gridfs.GridFS(db)

    df_term_and_cos_simil = pd.DataFrame()
    df_term_and_cos_simil['infected_key_words'] = flattened_list

    updated_df_json = updated_df.to_json()
    term_cos_simil_df_json = term_cos_simil_df.to_json()

    timestamp = datetime.datetime.now().timestamp()
    updated_df_gridfs_id = fs.put(updated_df_json.encode())
    term_cos_simil_df_gridfs_id = fs.put(term_cos_simil_df_json.encode())

    mongodb_output = {
        'timestamp': timestamp,
        'updated_df_gridfs_id': updated_df_gridfs_id,
        'term_cos_simil_df_gridfs_id': term_cos_simil_df_gridfs_id
        }

    collection.insert_one(mongodb_output)

def readmission_keywords_read_from_db():
    db = get_db()
    collection = db['readmission_one_hot']
    fs = gridfs.GridFS(db)

    most_recent_entry = collection.find_one(sort=[('_id', pymongo.DESCENDING)])
    updated_df_json = fs.get(most_recent_entry['updated_df_gridfs_id']).read().decode()
    term_cos_simil_df_json = fs.get(most_recent_entry['term_cos_simil_df_gridfs_id']).read().decode()

    updated_df = pd.read_json(update_df_json)
    term_cos_simil_df = pd.read_json(term_cos_simil_df_json)

    return updated_df, term_cos_simil_df

def readmission_keywords_write_to_db(updated_df, flattened_list):
    db = get_db()
    collection = db['readmission_one_hot']
    fs = gridfs.GridFS(db)

    df_term_and_cos_simil = pd.DataFrame()
    df_term_and_cos_simil['readmission_key_words'] = flattened_list

    updated_df_json = updated_df.to_json()
    term_cos_simil_df_json = term_cos_simil_df.to_json()

    timestamp = datetime.datetime.now().timestamp()
    updated_df_gridfs_id = fs.put(updated_df_json.encode())
    term_cos_simil_df_gridfs_id = fs.put(term_cos_simil_df_json.encode())

    mongodb_output = {
            'timestamp': timestamp,
            'updated_df_gridfs_id': updated_df_gridfs_id,
            'term_cos_simil_df_gridfs_id': term_cos_simil_df_gridfs_id
            }

    collection.insert_one(mongodb_output)


