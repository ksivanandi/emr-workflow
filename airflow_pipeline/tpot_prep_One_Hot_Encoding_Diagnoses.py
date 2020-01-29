#!/usr/bin/env python
"""
input: [index],'diagnosis'
output: [index], one_hot_endoded_diagnoses(multiple)
last modified: 1-23-20
author: andrew malinow
"""

"""
Imports
"""
import pandas as pd
import sklearn
from sklearn.preprocessing import MultiLabelBinarizer

"""
global variables
"""
#need to coordinate with Jason on how this is created and how to refactor using the API instead of a document.
#it is a dataframe with the entities
infile = 'jason_mimc-554_new.csv'

outputfile = 'tpot_prep-diagnosis_names_one_hot_encoded.json'
mlb = MultiLabelBinarizer()

def load_dataframe():
    with open(infile) as json_file:
        df = pd.read_csv(infile)
        return df

def write_dataframe(df):
    with open(outputfile,'w') as f:
        json = df.to_json()
        f.write(json)

def diagnoses_one_hot_encoding():
    df = load_dataframe()

    #create boolean mask matched non NaNs values
    mask = df['diagnosis'].notnull()
    #filter by boolean indexing
    arr = mlb.fit_transform(df.loc[mask,'diagnosis'].dropna().str.strip('[]').str.split(','))
    #create DataFrame and add missing (NaN)s index values
    df = (pd.DataFrame(arr, index=df.index[mask], columns=mlb.classes_).reindex(data.index, fill_value=0))

    write_dataframe(df)
