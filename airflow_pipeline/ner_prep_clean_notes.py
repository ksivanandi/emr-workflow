import re
import pandas as pd
from nltk import sent_tokenize, word_tokenize
from workflow_read_and_write import standard_write_to_db, standard_read_from_db

MAX_SEQ_LENGTH = 100

def clean_ner_notes():
    #df_json_encoded = standard_read_from_db('first_dataframe')
    #df_json = df_json_encoded.decode()
    #df = pd.read_json(df_json)
    
    df = pd.read_parquet('short_ner_test.parquet')

    cleaned_notes = []
    for note in df['notes']:
        note = re.sub('\[','',note)
        note = re.sub('\]','',note)
        note = re.sub('\*','',note)

        cleaned_note = ''

        lines = note.split('\n')
        for line in lines:
            if line != '' and '____' not in line:
                sentences = sent_tokenize(line)
                for sentence in sentences:
                    words = word_tokenize(sentence)
                    #Chunked according to this approach:
                    # https://stackoverflow.com/questions/9671224/split-a-python-list-into-other-sublists-i-e-smaller-lists
                    max_len_chunks = [words[x:x+MAX_SEQ_LENGTH] for x in range (0, len(words), MAX_SEQ_LENGTH)]
                    for chunk in max_len_chunks:
                        new_line = ''
                        for word in chunk:
                            new_line += ' ' + word
                        cleaned_note += '\n' + new_line.strip()

        cleaned_notes.append(cleaned_note)

    df['ner_cleaned_notes'] = cleaned_notes
    df_json_encoded = df.to_json().encode()
    standard_write_to_db('ner_cleaned_notes', df_json_encoded)

