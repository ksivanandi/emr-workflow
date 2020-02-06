import requests
import pandas as pd
from pandas.io.json import json_normalize
import pyarrow as pa
import pyarrow.parquet as pq
import math
import pymongo

json_count = requests.get('http://10.32.22.16:56733/noteeventscount').json()
count = json_count['note_count']
page_count = math.ceil(count/100000)
all_notes = []

for i in range(page_count):
    resp = requests.get('http://10.32.22.16:56733/noteevents/page/'+str(i+1))
    notes = resp.json()['json_notes']
    all_notes += notes

resp = requests.get('http://10.32.22.16:56733/admissions')
admissions = resp.json()['json_admissions']

for admission in admissions:
    notes_per_admission = [note for note in all_notes if note['admission_id'] == admission['admission_id']]
    notes_concat = ''
    for note in notes_per_admission:
        notes_concat += ' ' + note['text']
    admission['notes'] = notes_concat

df = json_normalize(admissions)
table = pa.Table.from_pandas(df)
pq.write_table(table, 'admissions.parquet')

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient['emr_steps']
mycollection = mydb['first_dataframe']
timestamp = datetime.datetime.now().timestamp()
json_df = df.to_json()
mongodb_output = {'timestamp': timestamp, 'json_df': json_df}
mycollection.insert_one(mongodb_output)
