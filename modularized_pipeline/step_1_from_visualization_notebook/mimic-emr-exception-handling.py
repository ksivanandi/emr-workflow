"""
Imports
"""
import pickle
from nltk.stem.wordnet import WordNetLemmatizer
import nltk
from nltk.corpus import wordnet as wn
import gensim 
import glob2
import os
import random
import spacy
from spacy import displacy
from spacy.lang.en import English
from gensim.models import FastText
    
import numpy as np
import pandas as pd
    
from nltk import word_tokenize, sent_tokenize
import time
import re
	
from Jason_model import Model
    
from jason_unit_component import UnitComponent
from jason_volume_unit_component import VolumeUnitComponent
from pkg_resources import resource_filename
import os
import re
import shutil
    
import time
import json
    
    
start = time.time()
last_end = start
    
    
activated = spacy.prefer_gpu()
#activated = spacy.require_gpu()
#print(activated)
    
nlp = spacy.load("en_core_web_sm")
nlp.max_length = 30000000
    
unitcomponent=UnitComponent(nlp)
    
nlp.replace_pipe("ner", unitcomponent)
    
#path="/rapids/notebooks/hostfs/i2b2_data/"
    
for i in range(552, 555):  
    if (i==5000):
        end=time.time()
        print(end-last_end)
        last_end = end
        break
            
    if (i==12 or i==36 or i==141 or i==200 or i== 360 or i== 366 or i== 384 or i==468):
        continue
        
    file_name = "/home/amalinow/andrew-rapids//MIMIC-data/mimic-iii-clinical-database-1.4/ready_mimic-unstructured" + str(i) + ".txt"
        
    with open (file_name) as f:
        lines = f.read()
            
            
    #read in cleaned list, one record at a time
    #with open('test_i2b2.txt', 'r') as f:
    #    records = json.loads(f.read())
    #    f.close
        
    print(i, "OK")
    #print("aadoc type", type(lines))
    #print("aadoc len is, ", len(lines))
    try:
        doc=nlp(lines)
    except ValueError as e:
        print (e)
        continue
        
    #save to disk
    #doc_file_name="""/hostfs/Jason's Sandbox/i2b2_doc_files/doc_record_"""
    #vocab_file_name="/hostfs/Jason's Sandbox/i2b2_doc_files/vocab_record_"
    doc_file_name="doc_record_"
    vocab_file_name="vocab_record_"
        
    this_doc_file_name= doc_file_name + str(i)
    this_vocab_file_name= vocab_file_name + str(i)
    
    doc.to_disk(this_doc_file_name)
    nlp.vocab.to_disk(this_vocab_file_name)
    
    #dst_doc_file_name="/hostfs/Jason's Sandbox/new_i2b2_doc_files/doc_record_"
    #dst_vocab_file_name="/hostfs/Jason's Sandbox/new_i2b2_doc_files/vocab_record_"
        
    #dst_doc_file_name="./new_i2b2_doc_files/doc_record_"
    #dst_vocab_file_name="./new_i2b2_doc_files/vocab_record_"
        
    dst_doc_file_name="./new_mimic_doc_files/doc_record_y"
    dst_vocab_file_name="./new_mimic_doc_files/vocab_record_y"
        
    this_dst_doc_file_name=dst_doc_file_name + str(i)
    this_dst_vocab_file_name=dst_vocab_file_name + str(i)
    
    #print(this_doc_file_name)
    #print(this_vocab_file_name)
    
    #print(this_dst_doc_file_name)
    #print(this_dst_vocab_file_name)
    
    shutil.move(this_doc_file_name, this_dst_doc_file_name)
    shutil.move(this_vocab_file_name, this_dst_vocab_file_name)
    end=time.time()
    print(end-last_end)
    last_end = end
    
#files = os.listdir("/hostfs/Jason's Sandbox/i2b2_doc_files/")
    
print (end-start)
    
#!nvidia-smi
