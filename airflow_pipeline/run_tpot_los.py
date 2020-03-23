#!/usr/bin/env python
# coding: utf-8

"""
Runs TPOT
input: TPOT input file (contains one-hot encoded and numeric variables, and a target)
output: model file (python script)
last updated: 2.5.20
author: Andrew Malinow, PhD
"""

"""
imports
"""
from tpot import TPOTClassifier
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd
import pickle
from workflow_read_and_write import standard_read_from_db, tpot_write_to_db

"""
define target variable from variable in source data (Length of Stay) then drop
from dataframe in preparation for model fitting
"""
def create_tpot_pipeline(df, target_column):
    target=df[target_column]
    df.drop(target_column,inplace=True, axis=1)

    type_conversion_dict = {}
    for column in df.columns:
        type_conversion_dict[column] = 'float64'
    float_df = df.astype(type_conversion_dict)

    ##tpot
    print('BB1')
    X_train, X_test, y_train, y_test = train_test_split(float_df,
        target, train_size=0.75, test_size=0.25)

    print('BB2')
    tpot = TPOTClassifier(generations=100, population_size=20, verbosity=3, config_dict="TPOT sparse")
    print('BB3')
    XX_train = X_train.values
    tpot.fit(XX_train, y_train)
    print('BB4')
    XX_test = X_test.values
    score = tpot.score(XX_test, y_test)

    print('BB5')
    tpot_pipeline_code = tpot.export()
    print('BB6')
    return tpot_pipeline_code, score


def run_tpot():
    print('AA1')
    combined_df_json_encoded = standard_read_from_db('combined_dataframe')
    print('AA2')
    combined_df_json = combined_df_json_encoded.decode()
    print('AA3')
    combined_df = pd.read_json(combined_df_json)

    print('AA4')
    tpot_pipeline_code, score = create_tpot_pipeline(combined_df, 'los')

    print('AA5')
    tpot_pipeline_code_encoded = tpot_pipeline_code.encode()
    print('AA6')
    score_encoded = str(score).encode()
    print('AA7')
    tpot_write_to_db(tpot_pipeline_code_encoded, score_encoded, 'tpot_los')
