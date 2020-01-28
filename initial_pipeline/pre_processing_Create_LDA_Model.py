#!/usr/bin/env python
# coding: utf-8

# In[513]:


"""
Reads tokenized EMR data and creates LDA Model
input: tokenized EMR data (tokens.json)
output: LDA model artifacts [saved to persistant volume]: corpora, dictionary, model, list of topics to potentially create features
Last update: 1/22/20
Author:  Andrew Malinow, PhD
"""


# In[7]:


"""
Imports
"""
import pickle
import requests
import json
import gensim
from gensim.models import Word2Vec


# In[4]:


"""
Global Variables
"""
resp = requests.get('http://10.32.22.16:56733/noteevents/55500')
if resp.status_code != 200:
        raise ApiError('GET /noteevents/<size> {}'.format(resp.status_code))
json_notes=resp.json()['json_notes']
notes_text = [note['text'] for note in json_notes]


# In[8]:


"""
create corpus, dictionary
"""
sentences=[d.split() for d in notes_text]
dictionary = gensim.corpora.Dictionary(sentences)

#create corpus 
corpus = [dictionary.doc2bow(text) for text in sentences]
#save corpus and dictionary
pickle.dump(corpus, open('default_corpus.pkl', 'wb'))
dictionary.save('mimic.gensim')


# In[9]:


"""
Use topic modeling to extract themes
train and save an LDA model
use num_topics parameter to determine the number of topics for the model,
and num_words parameter for how much to show
"""
lda=gensim.models.LdaMulticore(corpus=corpus,num_topics=5,id2word=dictionary,passes=100,workers=7)
lda.save("defaultLDA.model")
topics=lda.print_topics(num_words=10)


# In[ ]:




