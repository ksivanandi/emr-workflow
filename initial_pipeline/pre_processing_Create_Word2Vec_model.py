#!/usr/bin/env python
# coding: utf-8

# In[513]:


"""
Reads tokenized EMR data and creates Word2Vec Model
input: tokenized EMR data (tokens.json)
output: word2vec model artifacts [saved to persistant volume]: corpora, dictionary, embeddings (.model file)
Last update: 1/22/20
Author:  Andrew Malinow, PhD
"""


# In[1]:


"""
Imports
"""
import requests
import json
import gensim
from gensim.models import Word2Vec


# In[2]:


"""
Global Variables
"""
resp = requests.get('http://10.32.22.16:56733/noteevents/55500')
if resp.status_code != 200:
        raise ApiError('GET /noteevents/<size> {}'.format(resp.status_code))
json_notes=resp.json()['json_notes']
notes_text = [note['text'] for note in json_notes]


# In[3]:


"""
pre-processing for Word2Vec
"""
documents=[]
for line in notes_text:
    documents.append(gensim.utils.simple_preprocess (line))


# In[4]:


"""
create word2vec model
need to tune parameters
"""
model = Word2Vec(documents, min_count=2,workers=10)
model.train(documents,total_examples=len(documents),epochs=10)
word_vectors=model.wv
vocabulary=model.wv.vocab  


# In[7]:


"""
save model, and word vectors
"""
model.save('word2vec.model')
model.wv.save_word2vec_format('word2vecKeyVectors.model',binary=True)


# In[6]:


sepsis_sim_words=model.wv.most_similar("infection")
readmit_sim_words=model.wv.most_similar("readmitted")


# In[18]:


"""
write out similar terms ["sepsis" and "readmission"] to separate files
these terms will be turned into features- e.g., sepsis_term_1 (0/1/); sepsis_term_2 (0/1)
"""
with open('sepsis_related.json','w') as f:
    json.dump(dict(sepsis_sim_words), f)

with open('readmit_related.json','w') as a:
    json.dump(dict(readmit_sim_words),a)


# In[ ]:




