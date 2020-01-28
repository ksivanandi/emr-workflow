#!/usr/bin/env python

"""
Using LDA on MIMIC clinical notes data to create features for tpot
Updates that need to be made prior to deploying to kubernetes
- update infile to point to correct source file/table
- update outfile location and potentially type
- leverage Spark NLP (john snow labs)
- add logic to export themes (topics from LDA) as search terms to be used to create features in downstream tasks
- figure out what to do with gensim model that is created for LDA
- potentially split out prep for LDA code (removal of stop words, tokenization)
"""

"""
imports
"""
import pickle
import nltk
from nltk import sent_tokenize, word_tokenize
import pandas as pd
import gensim
import re
import pyLDAvis
import pyLDAvis.gensim
import matplotlib.pyplot as plt

"""
Global Variables
"""
input_file='EMR_Tokens.json'
def load_tokens():
    with open(input_file, 'r') as json_file:
        data = json.load(json_file)
        return data['token_list']

"""
Prep for LDA: 
"""
def prep_lda(tokens):
    dictionary = gensim.corpora.Dictionary(tokens)
    #create corpus 
    corpus = [dictionary.doc2bow(text) for text in tokens]
    #save corpus and dictionary
    pickle.dump(corpus, open('mimic-corpus.pkl', 'wb'))
    dictionary.save('mimic.gensim')
    return corpus, dictionary

"""
Use topic modeling to extract themes (data should be segmented for readmissions and sepsis- length of stay can run LDA on entire data set)
train and save an LDA model
use num_topics parameter to determine the number of topics for the model,
and num_words parameter for how much to show
"""
def create_lda_model(corpus, dictionary):
    lda = gensim.models.LdaMulticore(corpus=corpus,num_topics=5,id2word=dictionary,passes=100,workers=7)
    lda.save("default_mimic.model")
    return lda

"""
Explore topics, write topics to output/table/file to be used as 
search terms-- maybe cull list based on clinical entity (or not); proper name (or not), etc.
decide when to create a new feature is TBD
"""
def write_topics(lda):
    topics=lda.print_topics(num_words=5)
    df = pd.DataFrame()
    df['topics'].append(topics)
    df.to_json('lda_topics.json')

def run_topic_modeling():
    tokens = load_tokens()
    corpus, dictionary = prep_lda()
    lda = create_lda_model(corpus, dictionary)
    write_topics(lda)
    visualize_cluster(lda, corpus, dictionary)

"""
visualize clusters-- including this- we should consider printing out a PDF report
"""
def visualize_clusters(lda,corpus,dictionary):
    # Visualize the topics
    id2word=dictionary
    pyLDAvis.enable_notebook()
    vis = pyLDAvis.gensim.prepare(lda, corpus, id2word)
    vis

