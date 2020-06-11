import pandas as pd
from workflow_read_and_write import standard_read_from_db, standard_write_to_db

def get_line_length_array(df):
    len_arr = []
    for i, row in df.iterrows():
        notes = row['ner_cleaned_notes'].replace(' ##', '')
        lines = notes.split('\n')
        len_lines = len(lines)
        len_arr.append(len_lines)
    return len_arr

def get_note_lines_from_file():
    in_file = open('all_notes_label_lines.txt')
    lines = in_file.readlines()
    in_file.close()
    return lines

def create_labeled_notes_column():
    lines = get_note_lines_from_file()

    df_json_encoded = standard_read_from_db('ner_cleaned_notes')
    df = pd.read_json(df_json_encoded.decode())
    length_array = get_line_length_array(df)

    begin = 0
    end = 0
    labeled_notes = []
    for length in length_array:
        end += length
        note_lines = lines[begin:end]
        begin += length
        note = ''
        for line in note_lines:
            note += '\n' + line
        labeled_notes.append(note)

    df['labeled_notes'] = labeled_notes
    df_json_encoded = df.to_json().encode()
    standard_write_to_db('ner_labeled_notes',df_json_encoded)
