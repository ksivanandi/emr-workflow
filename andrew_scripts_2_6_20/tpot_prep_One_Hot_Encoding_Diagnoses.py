#!/usr/bin/env python
# coding: utf-8

# In[40]:


"""
input: [index],'diagnosis'
output: [index], one_hot_endoded_diagnoses(multiple)
last modified: 1-23-20
author: andrew malinow
"""


# In[1]:


"""
install dependencies
"""
#pip install sklearn
#pip install pandas


# In[5]:


"""
Imports
"""
import pandas as pd
import sklearn
from sklearn.preprocessing import MultiLabelBinarizer


# In[6]:


"""
global variables
"""
infile='jason_mimc-554_new.csv'
data=pd.read_csv(infile, nrows=100)
mlb = MultiLabelBinarizer()


# In[7]:


#create boolean mask matched non NaNs values
mask = data['diagnosis'].notnull()
#filter by boolean indexing
arr = mlb.fit_transform(data.loc[mask, 'diagnosis'].dropna().str.strip('[]').str.split(','))
#create DataFrame and add missing (NaN)s index values
data = (pd.DataFrame(arr, index=data.index[mask], columns=mlb.classes_)
               .reindex(data.index, fill_value=0))
data.to_json('tpot_prep-diagnosis_names_one_hot_encoded.json')


# In[ ]:




