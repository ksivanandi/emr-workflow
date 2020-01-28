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
from pre_processing_Create_Tokens import get_data

"""
global variables
"""
outputfile='fe_clinical_note_sequenced.json'

"""
pre-processing Pandas: tokenize text
"""
def tokenize_by_sentence():
    tokens_in_record = []
    data = get_data()

    for record in data:
        text = record['text']
        tokens=sent_tokenize(text)
        tokens_in_record.append(tokens)

    return tokens_in_record

"""
feature engineering: pull out admission and discharge details
"""
def create_feature_lists(tokenized_records):
    
    admission_related=[]
    discharge_related=[]
    deceased_flag=[]
    
    for record in tokenized_records:
        admit=[]
        discharge=[]
        deceased=[]

        for sentence in record:
            if re.findall(r'admitted',sentence):
                admit.append(sentence)
            if re.findall(r'discharge',str(sentence)):
                discharge.append(sentence)
            if re.findall(r'patient died',str(sentence)):
                deceased.append(1)

    admission_related.append(admit)
    discharge_related.append(discharge)
    deceased_flag.append(deceased)

    return admission_related, discharge_related, deceased_flag

def write_dataframe(df):
    with open(outputfile,'w') as f:
        json = df.to_json()
        f.write(json)

def add_admit_discharge_columns():
    #tokenize and separate into features
    tokens_in_record = tokenize_by_sentence()
    admission_related, discharge_related, deceased_flag = create_feature_lists(tokens_in_record)

    #format into dataframe
    df = pd.DataFrame()
    df['tokens_in_record'] = tokens_in_record
    df['admission_related'] = admission_related
    df['discharge_related'] = discharge_related
    df['deceased_flag'] = deceased_flag

    #save dataframe as json on disk
    write_dataframe(df)
