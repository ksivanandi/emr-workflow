#!/usr/bin/env python
# coding: utf-8

# In[6]:


"""
create admission_related,discharge_relateed and deceased_flag fields from unstructured note field
input: record_text
output: record_text, admission_related, discharge_related, deceased_flag

last modified: 1-22-20
author: andrew malinow
"""


# In[19]:


"""
install dependencies
"""
#pip install nltk


# In[3]:


"""
Imports
"""
import pandas as pd
import nltk
from nltk import sent_tokenize, word_tokenize
import re


# In[4]:


"""
global variables
"""
infile='jason_mimc-554_new.csv'
data=pd.read_csv(infile, nrows=100)
record_text=data['record_text'].to_json()
df=pd.DataFrame()


# In[6]:


"""
pre-processing Pandas: tokenize text
"""
tokens_in_record=[]
for record in data['record_text']:
    tokens=sent_tokenize(str(record))
    tokens_in_record.append(tokens)
df['tokens_in_record']=tokens_in_record


# In[43]:


"""
feature engineering: pull out admission and discharge details
"""
admission_related=[]
discharge_related=[]
deceased_flag=[]

for record in data['record_text']:
    sentences=sent_tokenize(str(record))
    admit=[]
    discharge=[]
    deceased=[]
    for line in sentences:
        if re.findall(r'admitted',str(line)):
            admit.append(line)
            break       
        elif re.findall(r'discharge',str(line)):
            discharge.append(line)
            break
        elif re.findall(r'patient died',str(line)):
            deceased.append(1)
            break   
        else:
            continue
    admission_related.append(admit)
    discharge_related.append(discharge)
    deceased_flag.append(deceased)
df['admission_related']=admission_related
df['discharge_related']=discharge_related
df['deceased_flag']=deceased_flag
df.to_json('fe_clinical_note_sequenced.json')


# In[ ]:




