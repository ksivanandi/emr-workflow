#!/usr/bin/env python
# coding: utf-8

# In[ ]:


"""
utility script to clean, filter and combined diagnostic terms for i2b2 and icd-10 codes
input-diagnostic source data
output-single csv file
last updated: 3/16/20
author: Andrew Malinow, PhD
"""


# In[ ]:


"""
install dependencies
"""
#!pip install TextBlob
#!pip install fuzzywuzzy
#!pip install python-Levenshtein


# In[181]:


"""
imports
"""
import pandas as pd
import nltk
from nltk import word_tokenize, sent_tokenize
from fuzzywuzzy import fuzz 
from fuzzywuzzy import process 
import time
from textblob import TextBlob
import numpy as np


# In[ ]:


"""
nltk dependencies
"""
nltk.download('brown')


# In[3]:


"""
read data
"""
dx=open("dx.txt").readlines()
i2b2=open("cleaned_i2b2.txt").readlines()


# In[ ]:


"""
open icd-10 codes
"""
icd_10_terms=getTermsICD10(dx)


# In[514]:


"""
open i2b2 terms
"""
initial_i2b2_terms=initialTerms(i2b2)


# In[195]:


"""
open i2b2 and icd-10 cleaned terms
"""
df=pd.read_csv("i2b2_terms.csv")
df_icd=pd.read_csv("cleaned_icd10.csv")


# In[196]:


"""
dedupe and remove blank lines
"""
df.drop_duplicates(subset='terms', keep="first",inplace=True)
df['terms'].replace("", np.nan, inplace=True)
df.dropna(subset=['terms'], inplace=True)

df_icd.drop_duplicates(subset='terms', keep="first",inplace=True)
df_icd['terms'].replace("", np.nan, inplace=True)
df_icd.dropna(subset=['terms'], inplace=True)


# In[197]:


combined=pd.concat([df,df_icd],axis=0)
combined.drop_duplicates(subset='terms', keep="first",inplace=True)
combined['terms'].replace("", np.nan, inplace=True)
combined.dropna(subset=['terms'], inplace=True)


# In[199]:


combined.to_csv('combined_dx_terms.csv')


# In[ ]:


"""
dedupe terms
"""
df=pd.DataFrame()
df['terms']=combined_terms
    #filter out blank lines
    df['terms'].replace("", np.nan, inplace=True)
    df.dropna(subset=['terms'], inplace=True)
    #drop duplicates
    df.drop_duplicates(subset='terms', keep="first",inplace=True)


# In[491]:


"""
combines 2 lists of terms, writes out the combined file and also returns the combined list as a dataframe
"""

def combineTerms(list1, list2):
    df=pd.DataFrame()
    a=list1
    b=list2
    terms=[]
    terms.append(a)
    terms.append(b)
    df['terms']=terms
    df.to_csv('combined_terms.txt')
    return df


# In[16]:


"""
parse diagnosis terms from i2b2
"""

def initialTerms(opened_data_file):
    terms=[]
    for line in i2b2:
        line=str(line)
        if "DIAGNOSIS:" in line:
            dx_list=line.partition(":")
            dx=dx_list[2]
            terms.append(dx)
        else:
            continue
    
    return terms


# In[15]:


"""
create list of diagnoses from icd-10 codes
"""
def getTermsICD10(raw_term_list):
    df=pd.DataFrame()
    term=[]
    for row in dx:
        #row=str(row).rstrip()
        if 'or' in str(row):
            ab=str(line).partition('or')
            a=ab[0]
            b=ab[2]
            term.append(a)
            term.append(b)
            continue
        if 'with' in str(row):
            cd=str(line).partition('with')
            c=cd[0]
            d=cd[2]
            term.append(c)
            term.append(d)
            continue  
        if 'without' in str(row):
            ef=str(line).partition('without')
            e=ef[0]
            f=ef[2]
            term.append(e)
            term.append(f)
            continue
        if 'and' in str(row):
            gh=str(line).partition('and')
            g=gh[0]
            h=gh[2]
            term.append(g)
            term.append(h)
            continue
        else:
            term.append(row)
            continue
        continue
    df['terms']=term
    df.to_csv("icd-terms.csv")
    return term


# In[17]:


def cleanTerms():
    df=pd.DataFrame()
    terms=initialTerms(i2b2)
    cleaned_terms=[]
    for term in terms:
        if len(term)<3:
            del term
        else:
            term=term.strip('\n')
            term=term.lower()
            term=re.sub(r'([^\s\w]|_)+', '', term)
            cleaned_terms.append(term)
    df['terms']=cleaned_terms
    df.to_csv("i2b2_terms.csv")
    return cleaned_terms


# In[187]:


"""
pre-processing to remove clinically irrelevant words from ICD-10 dx terms
"""
icd10=pd.read_csv('icd-terms.csv')
icd10['terms'].replace('', np.nan, inplace=True)
icd10.dropna(subset=['terms'], inplace=True)
icd10.drop_duplicates(subset='terms', keep="first", inplace=True)
stopwords=['boat','aircraft','car','watercraft','fishing boat','sailboat','trunk','craft','fishing','submersion']
icd10_lines=icd10['terms'].tolist()


# In[188]:


"""
use i2b2 terms to remove clinically irrelevant words from ICD-10 dx terms
"""

i2b2=pd.read_csv('i2b2_terms.csv')
i2b2['terms']=i2b2['terms']
df=pd.DataFrame()
matches=[]
###first pass
for line in icd10_lines:
    line=str(line).strip()
    for d in i2b2['terms']:
        d=str(d).strip()
        ratio=fuzz.ratio(line, d)
        if ratio>30:
            #print(line)
            matches.append(line)
            break
        else:
            continue
        continue
    continue
df['terms']=matches


# In[190]:


###second pass-remove lines with stopwords

stopwords=['boat','aircraft','car','watercraft','fishing boat','sailboat','trunk','craft','fishing','ship', 'passenger', 'water-skis','overboard']
good_lines=[]
for line in matches:
    tokens=word_tokenize(str(line))
    good_lines.append([item for item in tokens if item not in stopwords])
    continue
df['terms']=good_lines


# In[192]:


###third pass-final formatting
df1=pd.DataFrame()
final_terms=[]
for line in good_lines:
    line=' '.join(word for word in line)
    if "," in line:
        line_list=line.partition(",")
        dx=line_list[0]
        final_terms.append(dx)
        dx=[]
        continue
    if "of" in line:
        line_list=line.partition("of")
        dx=line_list[0]
        final_terms.append(dx)
        dx=[]
        continue
    else:
        final_terms.append(line)
        continue
    continue
df1['terms']=final_terms


# In[194]:


df1.drop_duplicates(subset='terms', keep="first",inplace=True)
df1.to_csv("cleaned_icd10.csv")

