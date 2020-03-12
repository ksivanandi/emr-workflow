import re
import pandas as pd
import pymongo
import gridfs
import datetime
from workflow_read_and_write import standard_read_from_db, standard_write_to_db


def placeholder_function():
   string = ''

def combine_and_clean(df):
    notes = df['notes']
    all_notes = ''
    for note in notes:
        all_notes += ' ' + note

    all_notes = all_notes.replace('\\n', '')
    all_notes = all_notes.replace("|", ' ')
    all_notes = re.sub(r'\( (.*) \)', r'(\1)', all_notes)
    all_notes = re.sub(' +', ' ', all_notes.strip())
    all_notes = re.sub(r' ([,.:])', r'\1', all_notes)
    all_notes = all_notes.strip()
    return all_notes

def clean_readmission_notes():
    df_json_encoded = standard_read_from_db('structured_data_features')
    df_json = df_json_encoded.decode()
    df = pd.read_json(df_json)

    #filter dataframe by readmission==True
    is_readmission = df['readmission'] == True
    df_readmissions = df[is_readmission]

    readmission_notes = combine_and_clean(df)

    readmission_notes_encoded = readmission_notes.encode()
    standard_write_to_db('readmission_notes_cleansed', readmission_notes_encoded)
