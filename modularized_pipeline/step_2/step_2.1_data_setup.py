from pyforest import *
import cudf
import spacy
from spacy.lang.en import English
import time
from nltk import sent_tokenize, word_tokenize

"""
global variables
"""
parser=English()
en_stop = set(nltk.corpus.stopwords.words('english'))

#placeholder until it is figured out how to migrate json_dataframe from step_1.2
json_dataframe = {}
data=pd.read_json()
