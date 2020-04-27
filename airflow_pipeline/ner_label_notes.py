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

    all_notes_lines=[]
    num_of_lines_per_note = []
    
    notes_length = len(df)
    note_lines_added = 0
    for i, row in df.iterrows():
        note = row['ner_cleaned_notes']
        note_lines = note.split('\n')
        num_of_lines = len(note_lines)
        num_of_lines_per_note.append(num_of_lines)
        all_notes_lines += note_lines

        note_lines_added +=1
        print(str(note_lines_added/notes_length*100)+'% of notes added to all note lines')
    
    
    labeled_lines = label_notes(all_notes_lines) 

    begin = 0
    end = 0
    labeled_notes = []
    for num_lines in num_of_lines_per_note:
        end += num_lines
        note_lines = labeled_lines[begin:end]
        begin += num_lines

        note = ''
        for line in note_lines:
            note += '\n' + line
        labeled_notes.append(note)

    df['labeled_notes'] = labeled_notes
    df_json_encoded = df.to_json().encode()
    standard_write_to_db('labeled_notes', df_json_encoded)

