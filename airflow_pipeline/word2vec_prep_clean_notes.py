#!/usr/bin/env python
# coding: utf-8

import re
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pymongo
import gridfs
import datetime
from workflow_read_and_write import standard_read_from_db, standard_write_to_db

def combine_and_cleanse(df):
    notes = df['notes']
    all_notes = ''
    for note in notes:
        #note = note.replace('\\n', '')
        #note = note.replace("|", ' ')
        #note = re.sub(r'\( (.*) \)', r'(\1)', note)
        #note = re.sub(' +', ' ', note.strip())
        #note = re.sub(r' ([,.:])', r'\1', note)
        all_notes += ' ' + note

    all_notes = all_notes.replace('\\n', '')
    all_notes = all_notes.replace("|", ' ')
    all_notes = re.sub(r'\( (.*) \)', r'(\1)', all_notes)
    all_notes = re.sub(' +', ' ', all_notes.strip())
    all_notes = re.sub(r' ([,.:])', r'\1', all_notes)
    all_notes = all_notes.strip()
    return all_notes

def clean_all_notes():
    df_json_encoded = standard_read_from_db('first_dataframe')
    df_json = df_json_encoded.decode()
    df = pd.read_json(df_json)

    all_notes = combine_and_cleanse(df)

    all_notes_encoded = all_notes.encode()
    standard_write_to_db('all_notes_cleansed' ,all_notes_encoded)
