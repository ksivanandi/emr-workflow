import requests
import pandas as pd
from pandas.io.json import json_normalize
import pyarrow as pa
import pyarrow.parquet as pq
import math
import pymongo
import gridfs

def get_all_notes():
    json_count = requests.get('http://10.32.22.16:56733/noteeventscount').json()
    count = json_count['note_count']
    page_count = math.ceil(count/100000)
    all_notes = []

    for i in range(page_count):
        resp = requests.get('http://10.32.22.16:56733/noteevents/page/'+str(i+1))
        notes = resp.json()['json_notes']
        all_notes += notes
    return all_notes

def get_admissions():
    resp = requests.get('http://10.32.22.16:56733/admissions')
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

def write_to_db(df):
    # set up connections to the database
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = myclient['emr_steps']
    fs = gridfs.GridFS(db)
    collection = db['first_dataframe']

    # save the dataframe as a json string to the database gridfs store for large objects
    json_df = df.to_json()
    json_df_encoded = json_df.encode()
    gridfs_id = fs.put(json_df_encoded)
    timestamp = datetime.datetime.now().timestamp()

    # save reference to the gridfs store and a timestamp to the main table for this step
    mongodb_output = {'timestamp': timestamp, 'json_df_gridfs_id': gridfs_id}
    collection.insert_one(mongodb_output)

def get_dataframe_from_apis():
    notes = get_all_notes()
    admissions = get_admissions()
    admissions_with_notes = combine_notes_and_admissions(admissions, notes)
    df = json_normalize(admissions_with_notes)
    write_to_db(df)

