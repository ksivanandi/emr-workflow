#!/usr/bin/env python
# coding: utf-8

# In[ ]:


"""
Text Classifier Pre-Processing Script creates necessary directory structure for RandomForest Classifier
input: unique identifier, unstructured clinical note field
output: individual files written to labeled directories-e.g., 'readmissions', 'not-readmissions'
last modified: 4/3/20
author: Andrew Malinow, PhD
"""


# In[ ]:


"""
imports
"""
import pandas as pd
from workflow_read_and_write import get_dataframe_from_apis


# In[ ]:


"""
data
Morgan to fix :-)
"""
df=get_dataframe_from_apis


# In[ ]:


"""
create dataframe with just readmissions
"""
def create_readmissions_df (df):
    is_readmission=df['readmission']==True
    df_readmissions=df[is_readmission]
    return df_readmissions

"""
create dataframe with non-readmissions
"""
def create_non_readmissions_df (df):
    not_readmission=df['readmission']==False
    df_readmissions=df[is_readmission]
    df_not_readmission=df[not_readmission]
    return df_not_readmission

"""
write non-readmissions records as individual files to separate directory
"""
def write_non_readmissions_to_file (df, non_readmissions_classifier_sub_dir_loc):
    directory=non_readmissions_classifier_sub_dir_loc
    os.chdir(directory)
    counter=1
    for index,record in df_not_readmission.iterrows():
        record=pd.Series(record).values
        f=open('not_readmission' + str(counter)+ '.txt','w')
        f.write(str(record))
        f.close()
        counter+=1
    return

"""
write readmissions records as individual files to separate direcory
"""
def write_readmissions_to_file (df, readmissions_classifier_sub_dir_loc):
    directory=readmissions_classifier_sub_dir_loc
    os.chdir(directory)
    counter=1
    for index,record in df_not_readmission.iterrows():
        record=pd.Series(record).values
        f=open('not_readmission' + str(counter)+ '.txt','w')
        f.write(str(record))
        f.close()
        counter+=1
    return

