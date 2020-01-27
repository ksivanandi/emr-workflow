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


# In[2]:


"""
Imports
"""
import json
import gensim
from gensim.models import Word2Vec


# In[4]:


"""
Global Variables
"""
with open('tokens.json') as f:
    data = json.load(f)


# In[ ]:


"""
create word2vec model
need to tune parameters
"""
model = Word2Vec(data, min_count=2,workers=4)
word_vectors=model.wv
vocabulary=model.wv.vocab  
sepsis_sim_words=model.wv.most_similar("sepsis")
readmit_sim_words=model.wv.most_similar("readmission")


# In[ ]:


"""
save model, and word vectors
"""
model.save('word2vec.model')
model.save_word2vec_format('word2vecKeyVectors.model',binary=True)


# In[ ]:


"""
write out similar terms ["sepsis" and "readmission"] to separate files
these terms will be turned into features- e.g., sepsis_term_1 (0/1/); sepsis_term_2 (0/1)
"""
with open ('sepsis_related_terms.json','wb') as f:
    json.dumps(sepsis_sim_words,f)

with open ('readmission_related_terms.json','wb') as f:
    json.dumps(readmit_sim_words,f)

