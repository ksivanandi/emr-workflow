import pandas as pd
import math

from ner.ner_callable import label_notes
from workflow_read_and_write import standard_read_from_db, standard_write_to_db

def inference(df):
    all_lines = []
    num_lines_per_note = []
    for i, row in df.iterrows():
        note = row['ner_cleaned_notes']
        note_lines = note.split('\n')
        num_lines = len(note_lines)
        num_lines_per_note.append(num_lines)
        all_lines += note_lines

    labeled_lines = label_notes(all_lines)
    
    begin = 0
    end = 0
    labeled_notes = []
    for num_lines in num_lines_per_note:
        end += num_lines
        note_lines = labeled_lines[begin:end]
        begin += num_lines

        note = ''
        for line in note_lines:
            note += '\n' + line
        labeled_notes.append(note)
    return labeled_notes

def create_label_notes():
    df_json_encoded = standard_read_from_db('ner_cleaned_notes')
    df_json = df_json_encoded.decode()
    df = pd.read_json(df_json)

    num_records = len(df)
    inf_increment=1000
    inference_runs=math.ceil(num_records/inf_increment)
    labeled_notes = []
    for i in range(inference_runs):
        if i != inference_runs-1:
            shortened_df = df.iloc[i*inf_increment:(i+1)*inf_increment]
        else:
            shortened_df = df.iloc[i*inf_increment:num_records]

        sub_labeled_notes = inference(shortened_df)
        labeled_notes += sub_labeled_notes

    df['labeled_notes'] = labeled_notes
    df_json_encoded = df.to_json().encode()
    standard_write_to_db('labeled_notes', df_json_encoded)

