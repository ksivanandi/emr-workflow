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
import json
from Jason_model import Model
from jason_unit_component import UnitComponent
from jason_volume_unit_component import VolumeUnitComponent
from pkg_resources import resource_filename
import shutil

#make the nlp object from spacy and replace it with a custom component for this use case
nlp = spacy.load("en_core_web_sm")
nlp.max_length = 30000000
unitcomponent=UnitComponent(nlp)
nlp.replace_pipe("ner", unitcomponent)

#get the unstructured data notes from the EMR DB API
resp = requests.get('http://10.32.22.16:56733/noteevents/55500')
if resp.status_code != 200:
    raise ApiError('GET /noteevents/<size> {}'.format(resp.status_code))
notes=resp.json()['notes']

#process through the notes with spacy and save the docs and vocabs in a json named "records"
doc_records = []
vocab_records_bytes = []
records = []
for note in notes:
    doc = nlp(note)
    vocab = nlp.vocab.to_bytes()
    record = {'doc_bytes':doc.to_bytes(),'vocab_bytes':vocab}
    records.append(record)
    doc_records.append(doc)
    vocab_records_bytes.append(vocab)
