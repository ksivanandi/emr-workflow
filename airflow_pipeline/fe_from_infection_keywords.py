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
from workflow_read_and_write import one_hot_write_to_db, standard_read_from_db

collection_name = 'infection_one_hot'

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
    for label, value in flattened:
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
        note=row['notes']
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
def infected_one_hot():
    first_dataframe_json_encoded = standard_read_from_db('first_dataframe')
    first_dataframe_json = first_dataframe_json_encoded.decode()
    first_dataframe = pd.read_json(first_dataframe_json)

    word2vec_pickle = standard_read_from_db('word2vec')
    word2vec_model = pickle.loads(word2vec_pickle)

    flattened, key_words = find_infection_similar_terms(word2vec_model)
    df_found_words = add_found_words_column(first_dataframe, key_words)
    df_one_hot = one_hot_encode_found_key_terms(df_found_words)

    df_term_cos_simil = pd.DataFrame()
    df_term_cos_simil['infected_key_words'] = flattened

    df_one_hot_json_encoded = df_one_hot.to_json().encode()
    df_term_cos_simil_json_encoded = df_term_cos_simil.to_json().encode()
    one_hot_write_to_db(df_one_hot_json_encoded, df_term_cos_simil_json_encoded, collection_name)

