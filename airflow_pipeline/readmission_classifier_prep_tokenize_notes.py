import pandas as pd
import re
from nltk.stem import WordNetLemmatizer
from workflow_read_and_write import standard_read_from_db, standard_write_to_db


def clean_notes(df):
    stemmer = WordNetLemmatizer()

    cleaned_notes = []
    for i, row in df.iterrows():
        note = row['notes']
        note = re.sub(r'\W', ' ', note)
        note = re.sub(r'\s+[a-zA-Z]\s+', ' ', note)
        note = re.sub(r'\^[a-zA-Z]\s+', ' ', note)
        note = re.sub(r'\s+', ' ', note, flags=re.I)
        note = re.sub(r'^b\s+', '', note)
        note = re.sub(r'_', '', note)

        note = note.lower()
        words = note.split()
        lemmatized_words = [stemmer.lemmatize(word) for word in words]
        
        cleaned_note = ''
        for word in lemmatized_words:
            cleaned_note += ' ' + word
        cleaned_note = cleaned_note.strip()

        cleaned_notes.append(cleaned_note)
    return cleaned_notes


def readmission_classifier_clean_notes():
    df_json_encoded = standard_read_from_db('structured_data_features')
    df = pd.read_json(df_json_encoded.decode())
    
    cleaned_notes = clean_notes(df)
    df['readmission_classifier_tokens']

    df_json_encoded = df.to_json().encode()
    standard_write_to_db('readmission_classifer_tokenized',df_json_encoded)


