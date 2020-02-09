#!/usr/bin/env python
# coding: utf-8

"""
loads word2vec model and creates binary features from search terms found that are related to infection
--need to add capability for returning similar terms for multiple key words- e.g., model.most_similar ('infection, infected')
input: index (record_id), unstructured medical note (note_text)
output: idndex (record_id),one hot-encoding representation of all_found_key_terms_infection
last update: 2.4.20
author: Andrew Malinow, PhD
"""

"""
imports
"""
import pandas as pd
import json
import gensim
import sklearn
from sklearn.preprocessing import MultiLabelBinarizer
import pymongo
import gridfs
import datetime
import pickle

"""
retrieve data and store in dataframe
this needs to be updated to retrieve all data
"""
def get_first_dataframe():
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['emr_steps']
    collection = db['first_dataframe']
    fs = gridfs.GridFS(db)
    most_recent_entry = collection.find_one(sort=[('_id', pymongo.DESCENDING)])
    df_json = fs.get(most_recent_entry['gridfs_id'])
    df_json_decoded =  df_json.decode()
    df = pandas.read_json(df_json_decoded)
    return df

"""
global variables
should also write infected_key_words to a table/file for future use since we 
are currently only using the term and not the associated cosine similarity score for anything
"""
def get_word2vec_model():
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['emr_steps']
    collection = db['word2vec']
    fs = gridfs.GridFS(db)
    most_recent_entry = collection.find_one(sort=[('_id', pymongo.DESCENDING)])
    word2vec_pickle = fs.get(most_recent_entry['gridfs_id'])
    return word2vec_pickle

"""
use word2vec to find similar terms
simalar terms are returned as a list of tuples: term, value [cosine of term and related_term]
append just the term to a new list
"""
def find_infection_similar_terms(model):
    base_words=['infection', 'infected', 'sepsis','septic']
    infected_key_words=[]

    for word in base_words:
        infected_key_words.append(model.most_similar(word, topn=15))

    flattened=[item for sublist in infected_key_words for item in sublist]  

    key_words=[]
    for label, value in infected_key_words:
        key_words.append(label)

    return flattened, key_words

"""
iterate through data and look for key words in notes field
append found words to new column, all_found_key_terms_infection
"""
def add_found_words_column(df, key_words):
    all_found_key_terms_infection=[]
    for i, row in df.iterrows():
        found_r=[]
        note=row['text']
        for word in key_words:
            if str(word) in str(note):
                found_r.append(word)
            else:
                found_r.append('none')
    
        all_found_key_terms_infection.append(found_r)
    df['all_found_key_terms_infection']=all_found_key_terms_infection
    return df

"""
one-hot-encode the all_found_key_terms_infection column
drop the column 'none'
"""
def one_hot_encode_found_key_terms(df):
    mlb = MultiLabelBinarizer()
    terms=(df['all_found_key_terms_infection'])
    df = (pd.DataFrame(mlb.fit_transform(terms), columns=mlb.classes_,index=df.index))
    del df['none']
    return df

"""
write one-hot encoded variables and index to file/table
write term and cosine similarity value tuples to file/table
"""
#df1=pd.DataFrame()
#df.to_json('tpot_prep-infection_key_words_one_hot_encoded.json')
#df1['infected_key_words']=infected_key_words
#df1.to_json('infected_similarity_terms_cosine_values.json')
def write_to_db(updated_df, flattened_list):
    client = pymongo.MongoClient('mongodb://localhost:27017')
    db = client['emr_steps']
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

def infected_one_hot():
    first_dataframe = get_first_dataframe()
    word2vec_pickle = get_word2vec_model()
    word2vec_model = pickle.loads(word2vec_pickle)
    flattened, key_words = find_readmit_similar_terms(word2vec_model)
    df_found_words = add_found_words_column(first_dataframe, key_words)
    df_one_hot = one_hot_encode_found_key_terms(df_found_words)
    write_to_db(df_one_hot, flattened)

