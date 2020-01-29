#!/usr/bin/env python
"""
input: [index],'drugs_clean'
output: [index], one_hot_endoded_medications(multiple)
last modified: 11-20-19
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
#takes as input the output from the diagnosis_one_hot_encoding script
infile = 'tpot_prep-diagnosis_names_one_hot_encoded.json'

outputfile = 'tpot_prep-medication_names_one_hot_encoded.json'
mlb = MultiLabelBinarizer()

def load_dataframe():
    with open(infile) as json_file:
        df = pd.read_json(infile)
        return df

def write_dataframe(df):
    with open(outputfile,'w') as f:
        json = df.to_json()
        f.write(json)

def medications_one_hot_encoding():
    df = load_dataframe()

    #create boolean mask matched non NaNs values
    mask = df['drug_cleaned'].notnull()
    #filter by boolean indexing
    arr = mlb.fit_transform(df.loc[mask, 'drug_cleaned'].dropna().str.strip('[]').str.split(','))
    #create DataFrame and add missing (NaN)s index values
    df = (pd.DataFrame(arr, index=df.index[mask], columns=mlb.classes_).reindex(df.index, fill_value=0))

    write_dataframe(df)

