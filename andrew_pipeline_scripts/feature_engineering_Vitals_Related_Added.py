#!/usr/bin/env python
# coding: utf-8

# In[6]:


"""
create vitals_related text field and vitals_related_ngrams from unstructured clinical note field
input: record_text
output: [index], record_text, vitals_related, vitals_related_ngrams

last modified: 1-23-20
author: andrew malinow
"""


# In[19]:


"""
install dependencies
"""
#!pip install nltk


# In[24]:


"""
Imports
"""
import pandas as pd
import nltk
from nltk import sent_tokenize, word_tokenize
import re


# In[28]:


"""
global variables
"""
infile='pp_clinical_note_sequenced.json'
data=pd.read_json(infile)
en_stop = set(nltk.corpus.stopwords.words('english'))
df=pd.DataFrame()


# In[33]:


"""
generate n-grams function
"""
def generate_ngrams(s, n):
    # Convert to lowercases
    s = s.lower()
    
    # Replace all none alphanumeric characters with spaces
    s = re.sub(r'[^a-zA-Z0-9\s]', ' ', s)
    
    # Break sentence in the token, remove empty tokens
    tokens = [token for token in s.split(" ") if token != ""]
    tokens = [token for token in s.split(" ") if len(token)>=3]
    # Use the zip function to help us generate n-grams
    # Concatentate the tokens into ngrams and return
    ngrams = zip(*[tokens[i:] for i in range(n)])
    return [" ".join(ngram) for ngram in ngrams]


# In[34]:


"""
feature engineering: pull out vitals
"""
all_vitals=[]
non_vital=[]
for record in data['tokens_in_record']:
    
    missing=[]
    vitals=[]
    
    sentences=sent_tokenize(str(record))
    
    for line in sentences:
       
        if re.findall(r'temperature', str(line)): 
            junk, temp, keep=str(line).partition('temperature')
            vital=temp+keep
            vitals.append(vital)
            missing.append('na')
        if re.findall(r'blood pressure', str(line)):
            junk, bp, keep=str(line).partition('blood pressure')
            vital=bp+keep
            vitals.append(vital)
            missing.append('na')
        if re.findall(r'breathing',str(line)):
            junk, breath, keep=str(line).partition('breathing')
            vital=breath+keep
            vitals.append(vital)
            missing.append('na')
        if re.findall(r'respitory',str(line)):
            junk, breath, keep=str(line).partition('respitory')
            vital=breath+keep
            vitals.append(vital)
            missing.append('na')
        
        else:
            
            continue
   
    all_vitals.append(vitals)
    non_vital.append(missing)
    continue
   
data['non-vitals']=non_vital
data['vitals']=all_vitals


# In[37]:


"""
generate n-grams for df['vitals'] to further refine vitals and prep for topic modeling
"""
ngrams=[]
for i, row in data.iterrows():
    vitals=row['vitals']
    clinical_ngrams=generate_ngrams(str(vitals),5)
    ngrams.append(clinical_ngrams)

data['clinical_ngrams']=ngrams


# In[38]:


"""
turn ngrams into single 'words' by replacing " " with "_"
"""
clinical_ngrams_concat=[]
for i, row in df.iterrows():
    ngram_list=[]
    ngrams=row['clinical_ngrams']
    for n in ngrams:
        n=str(n)
        a=str(n).replace(" ","_")
        ngram_list.append(a)
        continue
    clinical_ngrams_concat.append(ngram_list)
    continue
data['clinical_ngrams_concat']=clinical_ngrams_concat
data['clinical_ngrams_concat']
data.to_json("fe_vitals_related_added.json")


# In[ ]:




