#!/usr/bin/env python

"""
create admission_related,discharge_relateed and deceased_flag fields from unstructured note field
input: record_text
output: record_text, admission_related, discharge_related, deceased_flag

last modified: 1-22-20
author: andrew malinow
"""

"""
Imports
"""
import pandas as pd
import nltk
from nltk import sent_tokenize, word_tokenize
import re
import pymongo
import gridfs

def read_from_db():
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['emr_steps']
    collection = db['first_dataframe']
    fs = gridfs.GridFS(db)
    most_recent_entry = collection.find_one(sort=[('_id', pymongo.DESCENDING)])
    json_df = fs.get(most_recent_entry['gridfs_id']).read()
    df = pd.read_json(json_df.decode())
    return df

"""
pre-processing Pandas: tokenize text
"""
def tokenize_by_sentence(df):
    tokens_in_record = []
    for row in df.iterrows():
        notes = record['notes']
        tokens=sent_tokenize(notes)
        tokens_in_record.append(tokens)
    df['tokens_in_record'] = tokens_in_record
    return df

def write_to_db(df):
    # set up connections to the database
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['emr_steps']
    fs = gridfs.GridFS(db)
    collection = db['ngram_prep_tokenize']

    # save the dataframe as a json string to the database gridfs store for large objects
    json_df = df.to_json()
    json_df_encoded = json_df.encode()
    gridfs_id = fs.put(json_df_encoded)
    timestamp = datetime.datetime.now().timestamp()

    # save reference to the gridfs store and a timestamp to the main table for this step
    mongodb_output = {'timestamp': timestamp, 'gridfs_id': gridfs_id}
    collection.insert_one(mongodb_output)

def add_tokens_column():
    df = read_from_db()
    df = tokenize_by_sentence()
    write_to_db(df)
