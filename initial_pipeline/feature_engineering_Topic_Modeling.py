#!/usr/bin/env python
# coding: utf-8

# In[1]:


"""
Using LDA on MIMIC clinical notes data to create features for tpot
Updates that need to be made prior to deploying to kubernetes
- update infile to point to correct source file/table
- update outfile location and potentially type
- leverage Spark NLP (john snow labs)
- add logic to export themes (topics from LDA) as search terms to be used to create features in downstream tasks
- figure out what to do with gensim model that is created for LDA
- potentially split out prep for LDA code (removal of stop words, tokenization)
"""


# In[3]:


"""
imports
"""
import pickle
import nltk
from nltk import sent_tokenize, word_tokenize
import pandas as pd
import gensim
import re


# In[4]:


"""
NLTK/Spacy downloads
"""
nltk.download('punkt')
nltk.download('stopwords')


# In[5]:


"""
Global Variables
"""
en_stop = set(nltk.corpus.stopwords.words('english'))
infile='/rapids/notebooks/hostfs/Pipeline/jason_mimc-554_new.csv'
data=pd.read_csv(infile)
record_text=data['record_text'].to_json()


# In[6]:


"""
Prep for LDA: 
"""
text=re.sub(r'([^\s\w]|_)+', '', str(record_text))
sentences=(word_tokenize(str(text)))
sentences=[token for token in sentences if len(token)>3]
sentences=[token for token in sentences if token not in en_stop]


# In[ ]:


sentences=[d.split() for d in sentences]
dictionary = gensim.corpora.Dictionary(sentences)
#create corpus 
corpus = [dictionary.doc2bow(text) for text in sentences]
#save corpus and dictionary
pickle.dump(corpus, open('mimic-corpus.pkl', 'wb'))
dictionary.save('mimic.gensim')


# In[ ]:


"""
Use topic modeling to extract themes (data should be segmented for readmissions and sepsis- length of stay can run LDA on entire data set)
train and save an LDA model
use num_topics parameter to determine the number of topics for the model,
and num_words parameter for how much to show
"""
lda=gensim.models.LdaMulticore(corpus=corpus,num_topics=5,id2word=dictionary,passes=100,workers=7)
lda.save("default_mimic.model")
topics=lda.print_topics(num_words=10)


# In[ ]:


"""
Explore topics, write topics to output/table/file to be used as 
search terms-- maybe cull list based on clinical entity (or not); proper name (or not), etc.
decide when to create a new feature is TBD
"""
df=pd.DataFrame()
topics=lda.print_topics(num_words=5)
df['topics'].append(topics)
for topic in topics:
    print (topic)
df.to_json('lda_topics.json')


# In[ ]:


"""
use !pip install to install 
the following packages: pyLDAvis
"""
get_ipython().system('pip install pyLDAvis')


# In[ ]:


"""
visualize clusters-- including this- we should consider printing out a PDF report
"""
import pyLDAvis
import pyLDAvis.gensim  # don't skip this
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')
# Visualize the topics
id2word=dictionary
pyLDAvis.enable_notebook()
vis = pyLDAvis.gensim.prepare(lda, corpus, id2word)
vis

