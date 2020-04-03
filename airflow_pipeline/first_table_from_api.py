import requests
import pandas as pd
from pandas.io.json import json_normalize
import math
import pymongo
import gridfs
from workflow_read_and_write import standard_write_to_db

def get_all_notes():
    json_count = requests.get('http://10.32.22.6:56733/noteeventscount').json()
    count = json_count['note_count']
    page_count = math.ceil(count/100000)
    all_notes = []

    for i in range(page_count):
        resp = requests.get('http://10.32.22.6:56733/noteevents/page/'+str(i+1))
        notes = resp.json()['json_notes']
        all_notes += notes
    return all_notes

def get_admissions():
    resp = requests.get('http://10.32.22.6:56733/admissions')
    admissions = resp.json()['json_admissions']
    return admissions

def get_icd_codes():
    resp = requests.get('http://10.32.22.6:56733/icdcodes')
    icd_codes = resp.json()['json_codes']
    return icd_codes

def combine_notes_and_admissions_and_codes(admissions, all_notes, icd_codes):
    for admission in admissions:
        notes_per_admission = [note for note in all_notes if note['admission_id'] == admission['admission_id']]
        codes_per_admission = [code.icd_code for code in icd_codes if code['admission_id'] == admission['admission_id']]
        notes_concat = ''
        for note in notes_per_admission:
            notes_concat += ' ' + note['text']
        admission['notes'] = notes_concat
        admission['icd_codes'] = codes_per_admission
    return admissions

# create a smaller dataset than the whole mimic database, faster for testing
def testing_admissions_with_notes():
    # change this to change the size of the dataset for testing
    num_records = 102

    resp = requests.get('http://10.32.22.6:56733/admissions/' + str(num_records))
    admissions = resp.json()['json_admissions']
    for admission in admissions:
        resp = requests.get('http://10.32.22.6:56733/noteevents/admitid/'+str(admission['admission_id']))
        notes_per_admission = resp.json()['json_notes']
        notes_concat = ''
        for note in notes_per_admission:
            notes_concat += ' ' + note['note']
        admission['notes'] = notes_concat
    return admissions


def get_dataframe_from_apis():
    notes = get_all_notes()
    admissions = get_admissions()
    icd_codes = get_icd_codes()

    admissions_with_notes_and_codes = combine_notes_and_admissions_and_codes(admissions, notes, icd_codes)
    #admissions_with_notes = testing_admissions_with_notes()

    df = pd.json_normalize(admissions_with_notes)
    # create an index column where the rows have values from 0 to len(df.iterrows())-1
    df.reset_index(inplace=True)

    df_json_encoded = df.to_json().encode()
    standard_write_to_db('first_dataframe', df_json_encoded)

