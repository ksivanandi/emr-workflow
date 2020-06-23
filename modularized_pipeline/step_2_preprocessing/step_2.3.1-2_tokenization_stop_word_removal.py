import nltk
from nltk import word_tokenize
import pandas as pd

#placeholder until it is figured out how to transfer df_no_null_json from step 2.2
df_no_null_json = {}
df = pd.DataFrame().read_json(df_no_null_json)


en_stop = set(nltk.corpus.stopwords.words('english'))
tokens_in_record = []
for record in df['text']:
    tokens = word_tokenize(str(record))
    tokens_in_record.append(tokens)
df['tokens_in_record'] = tokens_in_record

tokens_no_stop_words = []
for record in df['tokens_in_record']:
    tokens = [token for token in tokenized_sentence if token.lower() not in en_stop]
    tokens_no_stop_words.append(tokens)
df['tokens_no_stop_words'] = tokens_no_stop_words

df_tokens_no_stops_json = df.to_json()
