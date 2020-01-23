#!/usr/bin/env python
# coding: utf-8

# In[513]:


"""
This script creates the Word Embeddings for the customer's corpus of EMR data
input: raw EMR data
output: word2vec model [saved to persistant volume]
Last update: 1/22/20
Author:  Andrew Malinow, PhD
"""


# In[1]:


"""
Imports
"""
from nltk import word_tokenize
import gensim
from gensim.models import Word2Vec
import nltk
import re


# In[2]:


"""
nltk dependencies
"""
nltk.download('stopwords')
nltk.download('punkt')


# In[31]:


"""
Global Variables
"""
mimic_file="/rapids/notebooks/hostfs/MIMIC-data/mimic-iii-clinical-database-1.4/mimic-unstructured.txt"
text=open(mimic_file).readlines()


# In[39]:


"""
Prep data, create model
need to investigate different parameter settings and different Models (FastText, other)
"""

text=re.sub(r'([^\s\w]|_)+', '', str(text))
text=re.sub('\n','',str(text))
sentences=word_tokenize(str(text))
sentences=[token for token in sentences if len(token)>2]
sentences=[token for token in sentences if token not in en_stop]
model = Word2Vec([sentences], size=100, window=10, min_count=1, workers=7, max_vocab_size=None)

