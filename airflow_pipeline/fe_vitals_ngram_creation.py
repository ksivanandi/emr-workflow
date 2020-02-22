#!/usr/bin/env python
# coding: utf-8

"""
create vitals_related text field and vitals_related_ngrams from unstructured clinical note field
input: record_text
output: [index], record_text, vitals_related, vitals_related_ngrams

last modified: 1-23-20
author: andrew malinow
"""

"""
Imports
"""
import pandas as pd
import nltk
from nltk import sent_tokenize, word_tokenize
import re
from workflow_read_and_write import standard_read_from_db, standard_write_to_db

"""
global variables
"""
en_stop = set(nltk.corpus.stopwords.words('english'))

"""
generate n-grams function
"""
def generate_ngrams(s, n):
    # Convert to lowercases
    s = s.lower()
    # Replace all none alphanumeric characters with spaces
    s = re.sub(r'[^a-zA-Z0-9\s]', ' ', s)
    # Break sentence in the token, remove empty tokens
    tokens = [token for token in s.split(" ") if token != ""]
    tokens = [token for token in s.split(" ") if len(token)>=3]
    # Use the zip function to help us generate n-grams
    # Concatentate the tokens into ngrams and return
    ngrams = zip(*[tokens[i:] for i in range(n)])
    return ["_".join(ngram) for ngram in ngrams]

"""
feature engineering: pull out vitals
"""
def get_vitals_and_generate_ngrams(df):
    all_vitals=[]
    non_vital=[]
    all_ngrams = []
    for record in df['tokens_in_record']:
        
        #block for getting vitals
        missing=[]
        vitals=[]
        for line in record:
            if re.findall(r'temperature', str(line)):
                junk, temp, keep=str(line).partition('temperature')
                vital=temp+keep
                vitals.append(vital)
                missing.append('na')
            if re.findall(r'blood pressure', str(line)):
                junk, bp, keep=str(line).partition('blood pressure')
                vital=bp+keep
                vitals.append(vital)
                missing.append('na')
            if re.findall(r'breathing',str(line)):
                junk, breath, keep=str(line).partition('breathing')
                vital=breath+keep
                vitals.append(vital)
                missing.append('na')
            if re.findall(r'respitory',str(line)):
                junk, breath, keep=str(line).partition('respitory')
                vital=breath+keep
                vitals.append(vital)
                missing.append('na')
        all_vitals.append(vitals)
        non_vital.append(missing)
        
        #block for generating ngrams
        clinical_ngrams = generate_ngrams(str(vitals),5)
        all_ngrams.append(clinical_ngrams)

    df['non-vitals']=non_vital
    df['vitals']=all_vitals
    df['vitals_ngrams'] = all_ngrams
    return df

"""
generate n-grams for df['vitals'] to further refine vitals and prep for topic modeling
"""
#slows down code to go through the dataframe twice so combined this function into the function above

#def generate_ngrams(df):
#    ngrams=[]
#    for row in data.iterrows():
#        vitals=row['vitals']
#        clinical_ngrams=generate_ngrams(str(vitals),5)
#        ngrams.append(clinical_ngrams)
#    df['clinical_ngrams']=ngrams
#    return df

def create_vitals_ngrams():
    df_json_encoded = standard_read_from_db('ngram_prep_tokenize')
    df_json = df_json_encoded.decode()
    df = pd.read_json(df_json)

    df = get_vitals_and_generate_ngrams(df)

    df_json = df.to_json()
    df_json_encoded = df_json.encode()
    standard_write_to_db('vitals_ngrams' ,df_json_encoded)

