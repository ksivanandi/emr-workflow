import pymongo
import gridfs
import datetime
import pickle


def read_from_db():
    client = pymongo.MyClient('mongodb://localhost:27017/')
    db = client['emr_steps']
    collection = db['word2vec']
    fs = gridfs.GridFS(db)
    most_recent_entry = collection.find_one(sort=[('_id', pymongo.DESCENDING)])
    word2vec_model_pickle = fs.get(most_recent_entry['gridfs_id'])
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

def make_ner(word2vec_model):
    #to be filled in
    return ner_output

def create_entity_recognition():
    word2vec_model_pickle = read_from_db()
    word2vec_model = pickle.loads(word2vec_model_pickle)
    ner_output = make_ner(word2vec_model)
    write_to_db(ner_output)
    
