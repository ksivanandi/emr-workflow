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
from workflow_read_and_write import standard_read_from_db, standard_write_to_db

"""
nltk dependencies
"""
nltk.download('stopwords')
nltk.download('punkt')

"""
global variables
"""
en_stop = set(nltk.corpus.stopwords.words('english'))

"""
Prep data, create model
need to investigate different parameter settings and different Models (FastText, other)
"""
def tokenize(text):
    tokens=word_tokenize(text)
    tokens=[token for token in tokens if len(token)>2]
    tokens=[token for token in tokens if token not in en_stop]
    return tokens

def tokenize_all_notes():
    notes_encoded = standard_read_from_db('all_notes_cleansed')
    notes = notes_encoded.decode()
    
    tokens = tokenize(notes)

    tokens_string_encoded = str(tokens).encode()
    standard_write_to_db('word2vec_notes_tokenized', tokens_string_encoded)

