import pandas as pd
from workflow_read_and_write import standard_read_from_db, standard_write_to_db, one_hot_read_from_db, one_hot_write_to_db, standard_write_to_db

def combine():
    infection_one_hot_df_json_encoded, _ = one_hot_read_from_db('infection_one_hot')
    readmission_one_hot_df_json_encoded, _ = one_hot_read_from_db('readmission_one_hot')
    structured_features_df_json_encoded = standard_read_from_db('structured_data_features')
    vitals_ngrams_df_json_encoded = standard_read_from_db('vitals_ngrams')
    #ner_processed_df_json_encoded = standard_read_from_db('post_ner_inference')

    infection_one_hot_df = pd.read_json(infection_one_hot_df_json_encoded.decode())
    readmission_one_hot_df = pd.read_json(readmission_one_hot_df_json_encoded.decode())
    structured_features_df = pd.read_json(structured_features_df_json_encoded.decode())
    vitals_ngrams_df = pd.read_json(vitals_ngrams_df_json_encoded.decode())
    #ner_processed_df = pd.read_json(ner_processed_df_json_encoded.decode())

    combined_df = infection_one_hot_df
    combined_columns = combined_df.columns

    for column in readmission_one_hot_df.columns:
        if column not in combined_columns:
            combined_df[column] = readmission_one_hot_df[column]

    combined_columns = combined_df.columns

    for column in structured_features_df.columns:
        if column not in combined_columns:
            combined_df[column] = structured_features_df[column]

    combined_columns = combined_df.columns

    for column in vitals_ngrams_df.columns:
        if column not in combined_columns:
            combined_df[column] = vitals_ngrams_df[column]

    combined_columns = combined_df.columns

    #for column in ner_processed_df.columns:
    #    if column not in combined_columns:
    #        combined_df[column] = ner_processed_df[column]

    columns_to_remove = [
            'admission_id',
            'admittime',
            'deathtime',
            'dischtime',
            'patient_id',
            'notes',
            #'note_entities_labeled',
            'index',
            'tokens_in_record',
            'vitals',
            'non-vitals',
            'vitals_ngrams',
            ]

    combined_df.drop(columns_to_remove,axis=1,inplace=True)

    combined_df_json_encoded = combined_df.to_json().encode()

    standard_write_to_db('combined_dataframe', combined_df_json_encoded)
