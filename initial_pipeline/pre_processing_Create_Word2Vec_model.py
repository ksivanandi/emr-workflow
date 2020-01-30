#!/usr/bin/env python
# coding: utf-8

# In[513]:


"""
Creates Word2Vec Model
input: raw unstructured EMR data (['text'] column in our schema)
output:Word2Vec model (.bin)
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
from gensim.models import Word2Vec
import nltk
import re


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


# In[131]:


"""
Prep data
"""

#text=re.sub(r'([^\s\w]|_)+', '', str(notes_text))
text=re.sub('\n','',str(text))
sentences=word_tokenize(str(text))
sentences=[token for token in sentences if len(token)>3]
sentences=[token for token in sentences if token not in en_stop]


# In[132]:


"""
validate data
(there should be more sentences than number of records)
"""
print (len(sentences))


# In[133]:


"""
create Word2Vec Model and save for future use
need to update location for saved model
"""

model = Word2Vec([sentences], size=100, window=10, min_count=2, workers=3)
model.wv.save_word2vec_format('Word2VecModel.bin', binary=True)


# In[ ]:


"""
build phrases
"""
from gensim.models.phrases import Phrases, Phraser
def build_phrases(sentences):
    phrases = Phrases(sentences,
                      min_count=5,
                      threshold=7,
                      progress_per=1000)
    return Phraser(phrases)

phrases_model=build_phrases(sentences)
phrases_model.save('phrases_model.txt')
phrases_model= Phraser.load('phrases_model.txt')


# In[ ]:




