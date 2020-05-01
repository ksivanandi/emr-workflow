import pandas as pd

from ner.ner_callable import label_notes
from workflow_read_and_write import standard_read_from_db, standard_write_to_db

def create_label_notes():
    df_json_encoded = standard_read_from_db('ner_cleaned_notes')
    df_json = df_json_encoded.decode()
    df = pd.read_json(df_json)
    
    '''
    labeled_notes = []
    for i, row in df.iterrows():
        note = row['ner_cleaned_notes']
        labeled_note = label_note(note)
        labeled_notes.append(labeled_note)
    '''
    
    notes_length = len(df)
    num_notes_labeled = 0
    labeled_notes = []
    num_notes = len(df)
    for i, row in df.iterrows():
        note = row['ner_cleaned_notes']
        note_lines = note.split('\n')
        labeled_note = label_notes(note_lines)
        labeled_notes.append(labeled_note)
        num_notes_labeled += 1
        print(str(num_notes_labeled/num_notes*100)+'% notes labeled')



    df['labeled_notes'] = labeled_notes
    df_json_encoded = df.to_json().encode()
    standard_write_to_db('labeled_notes', df_json_encoded)

