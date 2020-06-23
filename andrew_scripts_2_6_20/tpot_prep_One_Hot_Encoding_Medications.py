#!/usr/bin/env python
# coding: utf-8

# In[6]:


"""
input: [index],'drugs_clean'
output: [index], one_hot_endoded_medications(multiple)
last modified: 11-20-19
author: andrew malinow
"""


# In[1]:


"""
install dependencies
"""
#!pip install nltk


# In[26]:


"""
Imports
"""
import pandas as pd
import sklearn
from sklearn.preprocessing import MultiLabelBinarizer


# In[38]:


"""
global variables
"""
infile='jason_mimc-554_new.csv'
data=pd.read_csv(infile, nrows=100)
mlb = MultiLabelBinarizer()


# In[39]:


#create boolean mask matched non NaNs values
mask = data['drug_cleaned'].notnull()
#filter by boolean indexing
arr = mlb.fit_transform(data.loc[mask, 'drug_cleaned'].dropna().str.strip('[]').str.split(','))
#create DataFrame and add missing (NaN)s index values
data = (pd.DataFrame(arr, index=data.index[mask], columns=mlb.classes_)
               .reindex(data.index, fill_value=0))
data.to_json('tpot_prep-medication_names_one_hot_encoded.json')


# In[ ]:




