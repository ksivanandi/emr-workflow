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
from workflow_read_and_write import standard_read_from_db, standard_write_to_db

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

def add_tokens_column():
    df_json_encoded = standard_read_from_db('first_dataframe')
    df_json = df_json_encoded.decode()
    df = pd.read_json(df_json)

    df = tokenize_by_sentence()

    df_json = df.to_json()
    df_json_encoded = df_json.encode()
    standard_write_to_db('ngram_prep_tokenize', df_json_encoded)

