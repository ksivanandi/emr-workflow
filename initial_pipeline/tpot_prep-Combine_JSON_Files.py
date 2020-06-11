#!/usr/bin/env python
# coding: utf-8

# In[ ]:


"""
combines output from pre-processing, feature-engineering steps, and the target, into a single output that is used
as the input for TPOT.

NEED TO FIGURE OUT THE INDEXING STRATEGY FOR COMBINING JSON!!!!

input: multiple json files with the same index
output: .csv input file for tpot

last updated: 2.4.20
author: Andrew Malinow, PhD
"""


# In[1]:


"""
imports
"""
import json
import pandas as pd
import glob


# In[2]:


"""
read all json files and add to list
nb: the following code reads all json located in the directory that this script is in
"""
result = []
read_files = glob.glob("*.json")


# In[10]:


combined_json=[]
for l in read_files:
    a= pd.read_json(l)
    combined_json.append(a)
    


# In[15]:


result = pd.concat(combined_json, axis=1, sort=False)
result.to_csv('TPOT_Input_File.csv')


# In[ ]:




