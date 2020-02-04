#!/usr/bin/env python
# coding: utf-8

# In[ ]:


"""
creates 'target' variable from lenght of stay (pre-calculated)
input: index, los[length of stay] fields
output: index, target[los] as json
last updated: 2.4.20
author: Andrew Malinow, PhD
"""


# In[41]:


"""
imports
"""
import requests
import json
import pandas as pd


# In[ ]:


"""
retrieve data
"""
json_count=requests.get('http://10.32.22.16:56733/noteeventscount').json()
count = json_count['note_count']
page_count = math.ceil(count/100000)
all_admissions = []
for i in range(page_count):
    resp = requests.get('http://10.32.22.16:56733/admissions/los/page/'+str(i+1))
    admissions = resp.json()['json_admissions']
    all_admissions += admissions


# In[ ]:


"""
create dataframe from response, create 'target' variable
"""

df=pd.DataFrame(all_admissions)
target=[]
for i, row in df.iterrows():
    los=row['los']
    days=los['days']
    target.append(days)
df['target']=target


# In[ ]:


"""
drop unnecessary columns (not needed for tpot)
write output to json
"""
del df['los']
del df['admittime']
del df['dischtime']

df.to_json('tpot_prep_target__los_added.json')

