import pandas as pd
from gensim.Model import Word2Vec

#placeholder for df_tokens_no_stops_json until it is figured out how to transfer from step 2.3.2
df_tokens_no_stops_json = {}

df = pd.DataFrame().read_json(df_tokens_no_stops_json)
tokens_list = df['tokens_no_stop_words'].tolist()
word_embeddings_model = Word2Vec(tokens_list, min_count = 1)
