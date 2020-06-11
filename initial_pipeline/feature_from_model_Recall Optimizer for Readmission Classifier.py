#!/usr/bin/env python
# coding: utf-8

# In[ ]:


"""
Recall Optimizer for Readmission Classifier
optimizes threshold probability to identify readmissions in a test data set
input: admission_id (unique identifier) & cleaned, tokenized records-> [probability scores, X_test, Y_test]
output: new binary feature "Readmission_screening"= binary value assigned to new records during deployed phase--this is not implemented in the code below
author:Andrew Malinow, PhD
last modified: 4.8.20
"""


# In[95]:


"""
imports
"""
import sklearn
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import numpy as np
import re
import nltk
from sklearn.datasets import load_files
import pickle
from nltk.corpus import stopwords
from nltk import sent_tokenize
import os
from sklearn.model_selection import train_test_split
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, recall_score
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import GridSearchCV
from nltk.stem import WordNetLemmatizer


# In[ ]:


"""
nltk dependencies
"""
#nltk.download('punkt')
#nltk.download('stopwords')
#nltk.download('wordnet')


# In[2]:


"""
Data
"""

#load data into categories using sklearn, and create X,y(target) data sets
#load_files needs to point to parent directory, where each subdir is a category label containing individual records

admission = load_files('C:\\Users\\amalinow\\Documents\\GitHub\\emr-workflow\\initial_pipeline\\Text_Classifier\\',decode_error="ignore")

X, y = admission.data, admission.target


# In[4]:


"""
preprocessing
this can be updated to point to the appropriate column(s) in our MongoDB
[we need the unique record identifier- e.g.,admission_id, the tokens for the record('X'), and the 'readmssion' column ('y')]
"""

from nltk.stem import WordNetLemmatizer

documents=[]
stemmer = WordNetLemmatizer()

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


# In[383]:


"""
vectorize data and split
[use stratify=True to ensure train-test split preserves the original distribution of label values]
"""
train_test_split.stratify=True
tfidfconverter = TfidfVectorizer(max_features=5000,strip_accents='unicode',decode_error='ignore', stop_words=stopwords.words('english'))
X = tfidfconverter.fit_transform(documents).toarray()
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0,stratify=y)


# In[ ]:


"""
define classifier model and fit data
[adjust class_weight based on distribution of labels in source data]
"""
classifier = RandomForestClassifier(n_estimators=1000, random_state=0, class_weight={0:.80, 1:.20})
classifier.fit(X_train, y_train)


# In[386]:


"""
functions
"""
def generate_class_prob(X_test):
    """
    this function generates probabilities for a readmission
    """
    y_scores=classifier.predict_proba(X_test)[:,1]
    return y_scores
            
def recall_score(confusion_matrix_passed):
    """
    recall=(true positive/(true positive)+(false negative))
    """
    cm=confusion_matrix_passed
    tn, fp, fn, tp = cm.ravel()
    recall=(tp/(tp + fn))
    return recall

def adjusted_classes(y_scores, t):
    """
    This function adjusts class predictions based on the prediction threshold (t).
    Will only work for binary classification problems.
    """
    
    return [1 if y >= t else 0 for y in y_scores]


def recall_optimizer(y_score_probs,y_test):
    """
    calculate readmission label probability at various thresholds until recall =>80%
    """
    #generate readmission probability
    y_scores_prob=y_scores
    y_test=y_test
    #set start point for threshold
    initial=.55
    for n in [x * 0.01 for x in range(100, 0,-1)]:
        threshold=abs(initial-n)
        #assign readmission label beased on threshold
        y_scores_adj=[1 if y >= threshold else 0 for y in y_scores_prob]
        #generate confusion_matrix
        cm=confusion_matrix(y_test,y_scores_adj)
        #calculate recall score
        recall=recall_score(cm)
        #set target recall score
        if recall >=.80:
            print(recall)
            break  
    return threshold


# In[387]:


"""
main function
"""
#generate probabilities
y_score_probs=generate_class_prob(X_test)
#optimize threshold for recall
t=recall_optimizer(y_score_probs,y_test)
#assign readmission label based on optimized threshold
y_scores_adj=adjusted_classes(y_score_probs, t)


# In[388]:


"""
evaluate results from main function
"""
print(t)
print(pd.DataFrame(confusion_matrix(y_test, y_scores_adj),
                       columns=['pred_neg', 'pred_pos'], 
                       index=['neg', 'pos']))


# In[ ]:




