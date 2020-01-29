#!/usr/bin/env python

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
import pyarrow as pa
import pyarrow.parquet as pq

"""
global variables
"""
infile = 'fe_clinical_note_sequenced.parquet'
outputfile = 'fe_vitals_related_added.parquet'

def load_dataframe():
    table = pa.read_table(infile)
    df = table.to_pandas()
    return df

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
    return [" ".join(ngram) for ngram in ngrams]

"""
feature engineering: pull out vitals
"""
def make_vitals_columns(data):
    all_vitals=[]
    non_vital=[]
    for record in data['tokens_in_record']:
        missing=[]
        vitals=[]
        for line in record:
            if re.findall(r'temperature', line): 
                junk, temp, keep=line.partition('temperature')
                vital=temp+keep
                vitals.append(vital)
                missing.append('na')
            if re.findall(r'blood pressure', line):
                junk, bp, keep=line.partition('blood pressure')
                vital=bp+keep
                vitals.append(vital)
                missing.append('na')
            if re.findall(r'breathing',line):
                junk, breath, keep=line.partition('breathing')
                vital=breath+keep
                vitals.append(vital)
                missing.append('na')
           if re.findall(r'respitory',line):
                junk, breath, keep=line.partition('respitory')
                vital=breath+keep
                vitals.append(vital)
                missing.append('na')

        all_vitals.append(vitals)
        non_vital.append(missing)
    return all_vitals, non_vital

"""
generate n-grams for df['vitals'] to further refine vitals and prep for topic modeling
"""
def make_ngrams_column(data):
    ngrams=[]
    for i, row in data.iterrows():
        vitals=row['vitals']
        clinical_ngrams=generate_ngrams(str(vitals),5)
        ngrams.append(clinical_ngrams)
    return ngrams

"""
turn ngrams into single 'words' by replacing " " with "_"
"""
def make_ngrams_concat_column(data)
    clinical_ngrams_concat=[]
    for i, row in data.iterrows():
        ngram_list=[]
        ngrams=row['clinical_ngrams']
        for n in ngrams:
            n=str(n)
            a=str(n).replace(" ","_")
            ngram_list.append(a)
        clinical_ngrams_concat.append(ngram_list)
    return clinical_ngrams_concat

def write_dataframe(df):
    table = pa.Table.from_pandas(df)
    pq.write_table(table, output_file)

def add_vitals_ngrams_columns():
    #create the columns for the vitals and for the ngrams
    all_vitals, non_vital = make_vitals_columns(df)
    ngrams = make_ngrams_column(df)
    clinical_ngrams_concat = make_ngrams_concat_column(df)

    #add the columns to the dataframe from the previous step
    df = load_dataframe()
    df['non-vitals'] = non_vital
    df['vitals'] = all_vitals
    df['clinical_ngrams'] = ngrams
    df['clinical_ngrams_concat'] = clinical_ngrams_concat

    #save dataframe as json on disk
    write_dataframe(df)
