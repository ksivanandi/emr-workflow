import pandas as pd
from workflow_read_and_write import standard_read_from_db, standard_write_to_db

def extract_entities(note):
    lines = note.split('\n')
    medications = []
    features = []
    covid_terms = []
    neg_medications = []
    neg_features = []
    neg_covid_terms = []

    for line in lines:
        words = line.split()
        word_index = 0
        while word_index < len(words):
            if '[' in words[word_index]:
                ent_end = word_index+1
                #take into account negation of an entity
                possible_negation = ''
                if words[word_index-1] == 'no' or words[word_index-1] == 'not':
                    possible_negation = words[word_index-1] + '_'
                if 'B-MEDICATION' in words[word_index]:
                    while ent_end < len(words) and 'I-MEDICATION' in words[ent_end]:
                        ent_end += 1
                    medication = possible_negation
                    for i,sub_ent in enumerate(words[word_index:ent_end]):
                        if i == 0:
                            medication += sub_ent.split('[')[0]
                        else:
                            medication += '_' + sub_ent.split('[')[0]
                    if possible_negation != '':
                        neg_medications.append(medication)
                    else:
                        medications.append(medication)
                elif 'B-DIAGNOSIS' in words[word_index]:
                    while ent_end < len(words) and 'I-DIAGNOSIS' in words[ent_end]:
                        ent_end += 1
                    feature = possible_negation
                    for i,sub_ent in enumerate(words[word_index:ent_end]):
                        if i == 0:
                            feature += sub_ent.split('[')[0]
                        else:
                            feature += '_' + sub_ent.split('[')[0]
                    if possible_negation != '':
                        neg_features.append(feature)
                    else:
                        features.append(feature)
                elif 'B-COVID' in words[word_index]:
                    while ent_end < len(words) and 'I-COVID' in words[ent_end]:
                        ent_end += 1
                    covid_term = possible_negation
                    for i, sub_ent in enumerate(words[word_index:ent_end]):
                        if i == 0:
                            covid_term += sub_ent.split('[')[0]
                        else:
                            covid_term += '_' + sub_ent.split('[')[0]
                    if possible_negation != '':
                        neg_covid_terms.append(covid_term)
                    else:
                        covid_terms.append(covid_term)
                word_index += (ent_end-word_index)
            else:
                word_index += 1

    return medications, neg_medications, features, neg_features, covid_terms, neg_covid_terms


def get_columns_from_notes(df):

    all_medication_entities = []
    all_general_feature_entities = []
    all_covid_term_entities = []

    all_neg_medication_entities = []
    all_neg_general_feature_entities = []
    all_neg_covid_term_entities = []

    for i, row in df.iterrows():
        note = row['labeled_notes']
        medications, neg_medications, features, neg_features, covid_terms, neg_covid_terms = extract_entities(note)
        #remove duplicates from the list:
        medications = list(dict.fromkeys(medications))
        neg_medications = list(dict.fromkeys(neg_medications))
        features = list(dict.fromkeys(features))
        neg_features = list(dict.fromkeys(neg_features))
        covid_terms = list(dict.fromkeys(covid_terms))
        neg_covid_terms = list(dict.fromkeys(neg_covid_terms))
        #
        all_medication_entities.append(medications)
        all_general_feature_entities.append(features)
        all_covid_term_entities.append(covid_terms)
        all_neg_medication_entities.append(neg_medications)
        all_neg_general_feature_entities.append(neg_features)
        all_neg_covid_term_entities.append(neg_covid_terms)

    df['medication_entities'] = all_medication_entities
    df['feature_entities'] = all_general_feature_entities
    df['covid19_entities'] = all_covid_term_entities
    df['neg_medication_entities'] = all_neg_medication_entities
    df['neg_feature_entities'] = all_neg_general_feature_entities
    df['neg_covid_term_entities'] = all_neg_covid_term_entities

    return df
        

def create_entity_columns():
    df_json_encoded = standard_read_from_db('ner_labeled_notes')
    df = pd.read_json(df_json_encoded.decode())

    new_df = get_columns_from_notes(df)

    new_df_json_encoded = new_df.to_json().encode()
    standard_write_to_db('entity_columns', new_df_json_encoded)
