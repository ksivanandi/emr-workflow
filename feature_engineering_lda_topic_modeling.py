import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd
from nltk import sent_tokenize
import re

table = pq.read_table('/home/emrm1/emr-workflow/admissions.parquet')
df = table.to_pandas()

notes_list = df['notes'].tolist()

all_notes_text = ''
for note in notes_list:
    all_notes_text += ' ' + note.replace('\n','')

new_sentences = sent_tokenize(all_notes_text)

def generate_ngrams(s, n):
    # Convert to lowercases
    s = s.lower()

    #Replace all non alphanumeric characters with spaces
    s = re.sub(r'[^a-zA-Z0-9\s]', ' ', s)

    # Break sentence into tokens, remove empty tokens
    tokens = [token for token in s.split(" ") if token != ""]
    tokens = [token for token in s.split(" ") if len(token)>=3]
    # Use the zip function to help us generate n-grams
    # Concatentate the tokens into ngrams and return
    ngrams = zip(*[tokens[i:] for i in range(n)])
    return ["_".join(ngram) for ngram in ngrams]

all_ngrams=[]
for sentence in new_sentences:
    sentence_ngrams=generate_ngrams(sentence, 5)
    all_ngrams+=sentence_ngrams

ngrams_concat_tokens = [[ngram] for ngram in all_ngrams]

dictionary = gensim.corpora.Dictionary(ngrams_concat_tokens)

#create corpus 
#the statement below doesn't work, changed input to ngram_concat_tokens
#corpus = [dictionary.doc2bow(text) for text in all_ngrams]
corpus = dictionary.doc2bow(ngrams_concat_tokens)
#save corpus and dictionary
pickle.dump(corpus, open('Default_n_grams-corpus.pkl', 'wb'))
dictionary.save('Default_Dictionary')

model = Word2Vec(ngram_concat_tokens, size=100, window=10, min_count=1, workers=3)
model.wv.save_word2vec_format('Word2VecModelSentences.bin', binary=True)

lda=gensim.models.LdaMulticore(corpus=corpus,num_topics=5,id2word=dictionary,passes=10,workers=3)
lda.save("mimic-lda-full_notes.model")
