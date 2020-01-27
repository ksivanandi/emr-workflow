#!/usr/bin/env python
# coding: utf-8

# In[ ]:


"""
Tokenize unstructured EMR records to support downstream model creation (for feature engineering)
input: raw EMR note data
output: tokenized text (tokens.json)
Last updated: 1.26.20
Author: Andrew Malinow
"""


# In[35]:


"""
imports
"""
import re
import requests
import json
from nltk import word_tokenize
import nltk


# In[32]:


"""
nltk dependencies
"""
nltk.download('stopwords')
nltk.download('punkt')


# In[21]:


"""
global variables
"""
en_stop = set(nltk.corpus.stopwords.words('english'))
data = requests.get('http://10.32.22.16:56733/noteevents/55500')
if data.status_code != 200:
        raise ApiError('GET /noteevents/<size> {}'.format(data.status_code))
json_notes=data.json()['json_notes']
notes_text = [note['text'] for note in json_notes]


# In[36]:


"""
Prep data, create model
need to investigate different parameter settings and different Models (FastText, other)
"""
text=re.sub(r'([^\s\w]|_)+', '', str(notes_text))
text=re.sub('\n','',str(text))
sentences=word_tokenize(str(text))
sentences=[token for token in sentences if len(token)>2]
sentences=[token for token in sentences if token not in en_stop]


# In[38]:


"""
write tokens to file/db table
"""
with open('tokens.json', 'w') as f:
    json.dump(sentences, f)


# In[ ]:




