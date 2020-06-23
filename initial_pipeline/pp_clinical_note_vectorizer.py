#!/usr/bin/env python
# coding: utf-8

# In[ ]:


"""
Vectorizes clinical notes and writes output (as pickle file) to Mongo
input: full clinical note field
output: vectorized clinical_notes (for entire corpus) as pickle file
author: Andrew Malinow, PhD
last updated:04.02.20
"""


# In[1]:


"""
Imports
"""
import sklearn
import pandas as pd
import numpy as np
import re
import nltk
import pickle
from nltk.corpus import stopwords
from nltk import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem import WordNetLemmatizer


# In[ ]:


"""
nltk dependencies
"""
#nltk.download('punkt')
#nltk.download('stopwords')
#nltk.download('wordnet')





"""
load data
"""
#update to use python callable to retrieve all clinical notes from first table [readmissions only]
data=pd.read_csv('admissions_los_readmit_added.csv', sep='|')
X=data['notes']



"""
Text Preprocessing
"""

def text_preprocessing (data)
    stemmer = WordNetLemmatizer()
    documents=[]


    for sen in range(0, len(X)):
        # Remove all the special characters
        document = re.sub(r'\W', ' ', str(X[sen]))
    
        # remove all single characters
        document = re.sub(r'\s+[a-zA-Z]\s+', ' ', document)
    
        # Remove single characters from the start
        document = re.sub(r'\^[a-zA-Z]\s+', ' ', document) 
    
        # Substituting multiple spaces with single space
        document = re.sub(r'\s+', ' ', document, flags=re.I)
    
        # Removing prefixed 'b'
        document = re.sub(r'^b\s+', '', document)
        
        # Removing prefixed '_'
        document = re.sub(r'_', '', document)
    
        # Converting to Lowercase
        document = document.lower()
    
        # Lemmatization
        document = document.split()

        document = [stemmer.lemmatize(word) for word in document]
        document = ' '.join(document)
    
        documents.append(document)
    return documents

# In[8]:


"""
convert text documents into TFIDF feature values and write output to Mongo
"""
def vectorize_clinical_note(data):
    tfidfconverter = TfidfVectorizer(strip_accents='unicode',decode_error='ignore', stop_words=stopwords.words('english'))
    vectorized_notes = tfidfconverter.fit_transform(documents).toarray()
    vectorized_notes_pickle = pickle.dumps(vectorized_notes)
    vectorized_notes_pickle_encoded = vectorized_notes_pickle.encode()
    standard_write_to_db('vectorized_ notes', vectorized_notes_pickle_encoded)
    return
