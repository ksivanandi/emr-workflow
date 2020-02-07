#!/usr/bin/env python
# coding: utf-8

# In[ ]:


"""
Tokenize raw EMR data to support downstream feature engineering tasks
input: raw EMR notes
output: tokenized notes (json)
Last updated: 1.24.20
Author: Andrew Malinow
"""


# In[36]:


# -*- coding: utf-8 -*-
"""
imports
"""
import json
import nltk
from nltk.corpus import wordnet as wn
from nltk import word_tokenize


# In[46]:


"""
global variables
"""
infile=r'C:\Users\amalinow\Documents\mimic-unstructured.txt'
outputfile='EMR_Tokens.json'
en_stop = set(nltk.corpus.stopwords.words('english'))
with open(infile) as f:
    data = f.readlines()
data = [x.strip() for x in data] 


# In[47]:


"""
Data Prep Functions
prepare text for topic modeling
"""
def prepare_text_for_lda(text):
    tokens = word_tokenize(text)
    tokens = [token for token in tokens if len(token) > 3]
    tokens = [token for token in tokens if token not in en_stop]
    return tokens


# In[ ]:


"""
tokenize data
"""
text_data = []
tokens=prepare_text_for_lda(str(data))
text_data.append(tokens)


# In[ ]:


"""
write tokens to json
"""
with open (outputfile, 'wb') as f:
    json.dumps(text_data, f)

