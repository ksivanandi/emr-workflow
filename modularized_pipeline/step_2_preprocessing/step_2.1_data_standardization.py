from pyforest import *
import cudf
import spacy
from spacy.lang.en import English
import time
from nltk import sent_tokenize, word_tokenize
import pandas as pd

#placeholder until it is figured out how to migrate json_notes from step 1 in a given workflow
json_notes=[{'row_id':1,'text':'Note 1'},{'row_id':2,'text':'Note 2'},{'row_id':3,'text':'Note 3'}]

df = pd.DataFrame()
index = []
record=[]
text=[]

for i in range(len(json_notes)):
    index.append(str(i))
    record.append(str(json_notes[i]['row_id']))
    text.append(json_notes[i]['text'].replace('\n', ''))

df['index']=index
df['record_id']=record
df['text']=text

json_df = df.to_json()
