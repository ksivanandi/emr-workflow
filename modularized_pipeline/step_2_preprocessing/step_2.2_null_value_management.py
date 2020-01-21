import pandas as pd

#placeholder until it is figure out how to transfer dataframe from step 2.1 
df_json={}

df = pd.DataFrame()
df.read_json(df_json)
df.dropna()

df_no_null_json = df.to_json()
