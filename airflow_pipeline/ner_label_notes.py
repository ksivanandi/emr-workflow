import pandas as pd

from ner.ner_callable import label_note
from workflow_read_and_write import standard_read_from_db, standard_write_to_db

def label_notes():
    df_json_encoded = standard_read_from_db('ner_cleaned_notes')
    df_json = df_json_encoded.decode()
    df = pd.read_json(df_json)

    labeled_notes = []
    for i, row in df.iterrows():
        note = row['ner_cleaned_notes']
        labeled_note = label_note(note)
        labeled_notes.append(labeled_note)

    df['labeled_notes'] = labeled_notes
    df_json_encoded = df.to_json().encode()
    standard_write_to_db('labeled_notes', df_json_encoded)

