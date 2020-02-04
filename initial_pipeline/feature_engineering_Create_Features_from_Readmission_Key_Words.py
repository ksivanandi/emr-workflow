#!/usr/bin/env python
# coding: utf-8

# In[ ]:


"""
loads word2vec model and creates binary features from search terms found that are related to readmission
input: index (record_id), unstructured medical note (note_text)
output: index (record_id),one hot-encoding representation of all_found_key_terms_readmission
last update: 2.4.20
author: Andrew Malinow, PhD
"""


# In[234]:


"""
imports
"""
import requests
import re
import pandas as pd
import json
import gensim
import sklearn
from sklearn.preprocessing import MultiLabelBinarizer


# In[235]:


"""
retrieve data and store in dataframe
this needs to be updated to retrieve all data
"""
resp = requests.get('http://10.32.22.16:56733/noteevents/50000')
if resp.status_code != 200:
        raise ApiError('GET /noteevents/<size> {}'.format(resp.status_code))
data=resp.json()['json_notes']
df=pd.DataFrame(data)


# In[236]:


"""
global variables
should also write infected_key_words to a table/file for future use since we 
are currently only using the term and not the associated cosine similarity score for anything
"""
#loads word2vec model created in previous pre_processing step
model_file="Word2VecModel.bin"
model=gensim.models.KeyedVectors.load_word2vec_format(model_file, binary=True, encoding='latin1')
mlb = MultiLabelBinarizer()


# In[237]:


"""
use word2vec to find similar terms
simalar terms are returned as a list of tuples: term, value [cosine of term and related_term]
append just the term to a new list
"""
base_words=['readmission','readmitted','readmit', 'prior']
readmit_base_words=[]
for word in base_words:
    readmit_base_words.append(model.most_similar(word, topn=15))

flattened=[item for sublist in readmit_base_words for item in sublist]    

key_words=[]
for label, value in flattened:
    key_words.append(label)


# In[239]:


"""
iterate through data and look for key words in notes field
append found words to new column, all_found_key_terms_infection
"""
all_found_key_terms_readmission=[]
for i, row in df.iterrows():
    found_r=[]
    note=row['text']
    for word in key_words:
        if str(word) in str(note):
            found_r.append(word)
            continue
        else:
            found_r.append('none')
            continue
    
    all_found_key_terms_readmission.append(found_r)
    continue
#print(all_found_key_terms_infection)
df['all_found_key_terms_readmission']=all_found_key_terms_readmission


# In[240]:


"""
one-hot-encode the all_found_key_terms_infection column
drop the column 'none'
"""
terms=(df['all_found_key_terms_readmission'])
df = (pd.DataFrame(mlb.fit_transform(terms), columns=mlb.classes_,index=df.index))
del df['none']


# In[241]:


"""
write one-hot encoded variables and index to file/table
write term and cosine similarity value tuples to file/table
"""
df1=pd.DataFrame()
df.to_json('tpot_prep-readmission_key_words_one_hot_encoded.json')
df1['readmission_key_words']=flattened
df1.to_json('readmission_similarity_terms_cosine_values.json')

