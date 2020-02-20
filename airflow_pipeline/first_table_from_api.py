import requests
import pandas as pd
from pandas.io.json import json_normalize
import pyarrow as pa
import pyarrow.parquet as pq
import math
import pymongo
import gridfs
from workflow_read_and_write import standard_write_to_db

def get_all_notes():
    json_count = requests.get('http://10.32.22.8:56733/noteeventscount').json()
    count = json_count['note_count']
    page_count = math.ceil(count/100000)
    all_notes = []

    for i in range(page_count):
        resp = requests.get('http://10.32.22.8:56733/noteevents/page/'+str(i+1))
        notes = resp.json()['json_notes']
        all_notes += notes
    return all_notes

def get_admissions():
    resp = requests.get('http://10.32.22.8:56733/admissions')
    admissions = resp.json()['json_admissions']
    return admissions

def combine_notes_and_admissions(admissions, all_notes):
    for admission in admissions:
        notes_per_admission = [note for note in all_notes if note['admission_id'] == admission['admission_id']]
        notes_concat = ''
        for note in notes_per_admission:
            notes_concat += ' ' + note['text']
        admission['notes'] = notes_concat
    return admissions

def get_dataframe_from_apis():
    notes = get_all_notes()
    admissions = get_admissions()
    admissions_with_notes = combine_notes_and_admissions(admissions, notes)

    df = pd.json_normalize(admissions_with_notes)
    # create an index column where the rows have values from 0 to len(df.iterrows())-1
    df.reset_index(inplace=True)

    df_json_encoded = df.to_json().encode()
    standard_write_to_db(df_json_encoded, 'first_dataframe')

