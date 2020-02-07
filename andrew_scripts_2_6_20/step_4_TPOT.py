#!/usr/bin/env python
# coding: utf-8

# In[4]:


"""
Runs TPOT
input: TPOT input file (contains one-hot encoded and numeric variables, and a target)
output: model file (python script)
last updated: 2.5.20
author: Andrew Malinow, PhD
"""


# In[1]:


"""
installs
"""
get_ipython().system('pip install tpot')


# In[10]:


"""
imports
"""
from tpot import TPOTClassifier
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd
import cudf
from cudf import DataFrame


# In[11]:


"""
global variables
nb. need to update input file location prior to deployment
"""

input_file='/rapids/notebooks/hostfs/Pipeline/TPOT_Input_File.csv'
data=pd.read_csv(input_file,sep='|')


# In[12]:


"""
define target variable from variable in source data (Length of Stay) then drop
from dataframe in preparation for model fitting
"""
df=pd.DataFrame(data)
target=df['target']
df.drop('target',inplace=True, axis=1)


# In[13]:


##tpot
X_train, X_test, y_train, y_test = train_test_split(df.astype(np.float64),
    target, train_size=0.75, test_size=0.25)


# In[ ]:


tpot = TPOTClassifier(generations=100, population_size=20, verbosity=3)
tpot.fit(X_train, y_train)
print(tpot.score(X_test, y_test))
tpot.export('tpot_los_pipeline.py')

