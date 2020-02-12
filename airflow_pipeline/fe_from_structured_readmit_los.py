import pymongo
import gridfs
import pandas as pd
import numpy as np
import datetime
from workflow_read_and_write import standard_read_from_db, standard_write_to_db

def get_first_dataframe():
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['emr_steps']
    collection = db['first_dataframe']
    fs = gridfs.GridFS(db)
    most_recent_entry = collection.find_one(sort=[('_id', pymongo.DESCENDING)])
    df_json = fs.get(most_recent_entry['gridfs_id']).read()
    df_json_decoded =  df_json.decode()
    df = pandas.read_json(df_json_decoded)
    return df

def write_to_db(df):
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['emr_steps']
    fs = gridfs.GridFS(db)
    collection = db['structured_data_features']
    df_json_encoded = df.to_json().encode()
    gridfs_id = fs.put(df_json_encoded)
    timestamp = datetime.datetime.timestamp().now()
    mongodb_output = {'timestamp': timestamp, 'gridfs_id':gridfs_id}
    collection.insert_one(mongodb_output)

def add_los_and_binary_deathtime_columns(df):
    los_list=[]
    dt_binary_list = []
    for row in df.iterrows():
        admit = pd.to_datetime(row['admittime'])
        discharge = pd.to_datetime(row['dischtime'])
        los = str(admit-discharge)
        los_list.append(los)
    df['los'] = los_list
    df['death_time_present'] = df['deathtime'].notnull()
    return df

def add_readmission_column(df):
    readmit_list = []
    readmit_threshold = pd.to_timedelta('30 days 00:00:00')
    zero_timedelta = pd.to_timedelta('0 days 00:00:00')
    for row in df.iterrows():
        current_admittime = pd.to_datetime(row['admittime'])
        
        patient_id = row['patient_id']
        same_patient_df = df.loc[df['patient_id'] == patient_id]

        readmit = False
        for subrow in same_patient_df.iterrows():
            #don't compare the row to itself
            if subrow['admission_id'] != row['admission_id']:
                other_dischtime = pd.to_datetime(subrow['dischtime'])
                time_between_visits = current_admit_time - sub_dischtime
                #first conditional statement filters out future subrow visits from the current row
                if time_between_visits > zero_timedelta and time_between_visits <= readmit_threshold:
                    readmit = True
        readmit_list.append(readmit)
    df['readmission'] = readmit_list
    return df

def create_structured_data_features():
    df_json_encoded = standard_read_from_db('first_dataframe')
    df_json = df_json_encoded.decode()
    df = pd.read_json(df_json)

    df = add_los_and_binary_deathtime_columns(df)
    df = add_readmission_column(df)
    
    df_json = df.to_json()
    df_json_encoded = df_json.encode()
    standard_write_to_db('structured_data_features', df_json_encoded)

