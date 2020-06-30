import pandas as pd
from workflow_read_and_write import standard_read_from_db, standard_write_to_db

def make_likert_column(df):
    likert_vals = []

    for i, row in df.iterrows():
        if row['keras_pred'] < 0.2:
            likert_vals.append('Very Unlikely Readmission')
        elif 0.2 <= row['keras_pred'] and row['keras_pred'] < 0.4:
            likert_vals.append('Unlikely Readmission')
        elif 0.4 <= row['keras_pred'] and row['keras_pred'] < 0.6:
            likert_vals.append('Neither Likely or Unlikely Readmission')
        elif 0.6 <= row['keras_pred'] and row['keras_pred'] < 0.8:
            likert_vals.append('Likely Readmission')
        else:
            likert_vals.append('Very Likely Readmission')

    return likert_vals

def convert_to_likert():
    df_json_encoded = standard_read_from_db('readmission_tensorflow_predictions')
    df = pd.read_json(df_json_encoded.decode())

    likert_values = make_likert_column(df)
    df['readmission_likert'] = likert_values

    df_json_encoded = df.to_json().encode()
    standard_write_to_db('readmission_likert', df_json_encoded)
