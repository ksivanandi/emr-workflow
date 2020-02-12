#!/usr/bin/env python
# coding: utf-8

"""
Creates Word2Vec Model
input: raw unstructured EMR data (['text'] column in our schema)
output:Word2Vec model (.bin)
Last update: 1.29.20
Author:  Andrew Malinow, PhD
"""

"""
Imports
"""
import gensim
from gensim.models import Word2Vec
import pymongo
import gridfs
import datetime
import ast
import pickle
from workflow_read_and_write import standard_read_from_db, standard_write_to_db

"""
Get Data
"""
def read_from_db():
    client = pymongo.MyClient('mongodb://localhost:27017/')
    db = client['emr_steps']
    collection = db['word2vec_notes_tokenized']
    fs = gridfs.GridFS(db)
    most_recent_entry = collection.find_one(sort=[('_id', pymongo.DESCENDING)])
    tokens_list_string = fs.get(most_recent_entry['gridfs_id']).read().decode()
    return tokens_list_string

def write_to_db(bin_model):
    client = pymongo.MyClient('mongodb://localhost:27017/')
    db = client['emr_steps']
    collection = db['word2vec']
    fs = gridfs.GridFS(db)
    gridfs_id = fs.put(bin_model)
    timestamp = datetime.datetime.now().timestamp()
    mongodb_output = {'timestamp': timestamp, 'gridfs_id': gridfs_id}
    collection.insert_one(mongodb_output)

def create_word2vec_model():
    tokens_string = standard_read_from_db('word2vec_notes_tokenized').decode()
    tokens = ast.literal_eval(tokens_string)
    model = Word2Vec([tokens], size=100, window=10, min_count=2, workers=3)
    model_pickled = pickle.dumps(model)
    standard_write_to_db('word2vec', model_pickled)

