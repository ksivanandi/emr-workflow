import pandas as pd
from worfklow_read_and_write import standard_read_from_db, standard_write_to_db

def extract_entities(note):
    lines = note.split('\n')
    medications = []
    features = []

    for line in lines:
        words = line.split()
        word_index = 0
        while word_index < len(words):
            if '[' in words[word_index]:
                ent_end = word_index+1
                if 'B-MEDICATION' in words[word_index]:
                    while 'I-MEDICATION' in words[ent_end]:
                        ent_end += 1
                    medication = ''
                    for sub_ent in words[word_index:ent_end]:
                        medication += ' ' + sub_ent.split('[')[0]
                    medications += medication.strip()
                elif 'B-FEATURE' in words[word_index]:
                    while 'I-FEATURE' in words[ent_end]:
                        ent_end += 1
                    feature = ''
                    for sub_ent in words[word_index:ent_end]:
                        feature += ' ' + sub_ent.split('[')[0]
                    features += feature.strip()
            else:
                word_index +=1

    return medications, features


def get_columns_from_notes(df):

    all_medication_entities = []
    all_general_feature_entities = []

    for i, row in df.iterrows():
        note = row['labeled_notes']
        medications, features = extract_entities(note)
        all_medication_entities.append(medications)
        all_general_feature_entities.append(features)

    df['medication_entities'] = all_medication_entities
    df['feature_entities'] = all_general_feature_entities

    return df
        

def create_entity_columns():
    df_json_encoded = standard_read_from_db('labeled_notes')
    df = pd.read_json(df_json_encoded.decode())

    new_df = get_columns_from_notes(df)

    new_df_json_encoded = new_df.to_json().encode()
    standard_write_to_db('make_entity_columns', new_df_json_encoded)
