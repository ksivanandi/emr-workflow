#!/usr/bin/env python
# coding: utf-8

"""
Tokenize unstructured EMR records to support downstream model creation (for feature engineering)
input: raw EMR note data
output: tokenized text (tokens.json)
Last updated: 1.26.20
Author: Andrew Malinow
"""

"""
imports
"""
import json
from nltk import word_tokenize
import nltk
import pymongo
import gridfs
import datetime

"""
nltk dependencies
"""
nltk.download('stopwords')
nltk.download('punkt')

"""
global variables
"""
en_stop = set(nltk.corpus.stopwords.words('english'))

def read_from_db():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["emr_steps"]
    collection = db['all_notes_cleansed']
    fs = gridfs.GridFS(db)
    most_recent_entry = collection.find_one(sort=[('_id', pymongo.DESCENDING)])
    notes = fs.get(most_recent_entry['gridfs_id']).decode()
    return notes
    

"""
Prep data, create model
need to investigate different parameter settings and different Models (FastText, other)
"""
def tokenize(text):
    tokens=word_tokenize(text)
    tokens=[token for token in tokens if len(token)>2]
    tokens=[token for token in tokens if token not in en_stop]
    return tokens

def write_to_db(tokens):
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['emr_steps']
    collection = db['notes_tokenized']
    fs = gridfs.GridFS(db)

    tokens_string_encoded = str(tokens).encode()
    gridfs_id = fs.put(tokens_string_encoded)
    timestamp = datetime.datetime.now().timestamp()
    mongodb_output = {'timestamp':timestamp, 'gridfs_id': gridfs_id}
    collection.insert_one(mongodb_output)

def tokenize_all_notes():
    notes = read_from_db()
    tokens = tokenize(notes)
    write_to_db(tokens)
