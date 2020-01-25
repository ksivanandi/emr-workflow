#!/usr/bin/env python
"""
This script creates the Word Embeddings for the customer's corpus of EMR data
input: json file
output: word2vec model [saved to persistant volume]
Last update: 1/22/20
Author:  Andrew Malinow, PhD
"""

"""
Imports
"""
from nltk import word_tokenize
import gensim
from gensim.models import Word2Vec
import nltk
import re
import json

"""
Get data from the previous step where the data was tokenized
"""
def load_tokens():
    with open('EMR_Tokens.json') as json_file:
        data = json.load(json_file)
        return data['token_list']

"""
Prep data, create model
need to investigate different parameter settings and different Models (FastText, other)
"""
def create_and_save_word2vec():
    data=load_tokens()
    if(data != None):
        model = Word2Vec([data], size=100, window=10, min_count=1, workers=7, max_vocab_size=None)
        model.save('word2vec.model')
