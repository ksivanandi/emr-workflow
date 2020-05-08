#!/usr/bin/env python
# coding: utf-8

# In[1]:


"""
Creating word2vec model with just notes from patients who have been readmitted
input: admission_id, notes
output: readmission word2vec model file
last modified:3.2.20
author: Andrew Malinow, PhD
"""


# In[8]:


get_ipython().system('pip install nltk')


# In[55]:


"""
imports
"""
import pickle
import pandas as pd
from nltk import word_tokenize
import nltk
import math
import requests
from gensim.models import Word2Vec
#from workflow_read_and_write import standard_write_to_db
import numpy as np
import pyarrow.parquet as pq


# In[10]:


"""
nltk dependencies
"""
nltk.download('stopwords')
nltk.download('punkt')


# In[11]:


"""
Global Variables
"""
en_stop = set(nltk.corpus.stopwords.words('english'))


# In[13]:


"""
Read data
"""
table=pq.read_table('admissions.parquet')
df=table.to_pandas()


# In[14]:


"""
clean and prep for word2vec
"""
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


# In[15]:


"""
tokenize notes
"""
def tokenize(text):
    tokens=word_tokenize(text)
    tokens=[token for token in tokens if len(token)>2]
    tokens=[token for token in tokens if token not in en_stop]
    return tokens


# In[16]:


"""
create readmission field to use for filtering using Morgan's function
"""

def add_readmission_column(df):
    readmit_list = []
    readmit_threshold = pd.to_timedelta('30 days 00:00:00')
    zero_timedelta = pd.to_timedelta('0 days 00:00:00')
    for row in df.iterrows():
        current_admittime = pd.to_datetime(row[1]['admittime'])
        
        patient_id = row[1]['patient_id']
        same_patient_df = df.loc[df['patient_id'] == patient_id]

        readmit = False
        for subrow in same_patient_df.iterrows():
            #don't compare the row to itself
            if subrow[1]['admission_id'] != row[1]['admission_id']:
                sub_dischtime = pd.to_datetime(subrow[1]['dischtime'])
                time_between_visits = current_admittime - sub_dischtime
                #first conditional statement filters out future subrow visits from the current row
                if time_between_visits > zero_timedelta and time_between_visits <= readmit_threshold:
                    readmit = True
        readmit_list.append(readmit)
    df['readmission'] = readmit_list
    return df


# In[17]:


"""
retrieve data
"""
#notes=get_all_notes()
#admissions=get_admissions()
#all_admissions=combine_notes_and_admissions(admissions, notes)


# In[18]:


"""
clean data
"""
#df = pd.DataFrame(all_admissions)DataFrame
#clean_df=combine_and_clean(df)


# In[58]:


"""
add readmission column
"""
df=add_readmission_column(df)


# In[59]:


"""
filter dataframe by readmission==True and write to mongo
"""
is_readmission=df['readmission']==True
df_readmissions=df[is_readmission]
#standard_write_to_db(df_readmissions, 'readmissions')


# In[60]:


"""
tokenize data
"""
tokens=tokenize(str(df_readmissions['notes']))


# In[62]:


"""
create word2vec model and wirte model to mongo
"""

readmission_model = Word2Vec([tokens], size=100, window=10, min_count=1, workers=3)
model_pickled = pickle.dumps(readmission_model)
#standard_write_to_db('word2vec_readmission', model_pickled)


# In[ ]:




