#!/usr/bin/env python
# coding: utf-8

# In[513]:


"""
Creates Word2Vec Model and features related to key term: 'readmission'
input: raw unstructured EMR data
output:Word2Vec model OR FastText Model
Last update: 1.29.20
Author:  Andrew Malinow, PhD
"""


# In[46]:


"""
Imports
"""
import requests
from nltk import word_tokenize
import gensim
import pandas as pd
from gensim.models import Word2Vec
import time
import nltk
import os
import re
from gensim.models import FastText


# In[32]:


"""
nltk dependencies
"""
nltk.download('words')
nltk.download('stopwords')
nltk.download('punkt')


# In[33]:


"""
Global Variables
"""
#this is the key variable that needs to be altered to address a specific clicnical/business challenge
key_words=['septic','infection','infected','pneumonia','catheter line infection']
#the words set from nltk should be replaced eventually with a better vocab- currently it filters our important words such as 'copays'
related_terms_dict={}
en_stop = set(nltk.corpus.stopwords.words('english'))


# In[124]:


"""
Get Data
"""
resp = requests.get('http://10.32.22.16:56733/noteevents/100000')
#if resp.status_code != 200:
#        raise ApiError('GET /noteevents/<size> {}'.format(resp.status_code))
json_notes=resp.json()['json_notes']
notes_text = [note['text'] for note in json_notes]


# In[ ]:


"""
Prep data
"""

text=re.sub(r'([^\s\w]|_)+', '', str(notes_text))
text=re.sub('\n','',str(text))
sentences=word_tokenize(str(text))
sentences=[token for token in sentences if len(token)>3]
sentences=[token for token in sentences if token not in en_stop]


# In[122]:


"""
validate data
(there should be more sentences than number of records)
"""
print (len(sentences))


# In[117]:


"""
create Word2Vec Model and save for future use
need to update location for saved model
"""

model = Word2Vec([sentences], size=100, window=10, min_count=2, workers=3)
model.wv.save_word2vec_format('Word2VecModel.bin', binary=True)

