import re
import pandas as pd
from nltk import sent_tokenize
import nemo
from workflow_read_and_write import standard_write_to_db, standard_read_from_db

MAX_SEQ_LENGTH = 100

def clean_ner_notes():
    df_json_encoded = standard_read_from_db('structured_data_features')
    df_json = df_json_encoded.decode()
    df = pd.read_json(df_json)

    #df = pd.read_parquet('short_ner_test.parquet')

    nemo_tokenizer = nemo.collections.nlp.data.tokenizers.get_tokenizer(tokenizer_name='nemobert',pretrained_model_name='bert-base-uncased', tokenizer_model=None)

    cleaned_notes = []
    notes_length = len(df['notes'])
    num_cleaned = 0
    for note in df['notes']:
        note = re.sub('\[','',note)
        note = re.sub('\]','',note)
        note = re.sub('\*','',note)
        note = re.sub(',','',note)
        note = re.sub(';','',note)

        cleaned_note = ''

        lines = note.split('\n')
        for line in lines:
            if line != '' and '____' not in line:
                sentences = sent_tokenize(line)
                for sentence in sentences:
                    words = nemo_tokenizer.text_to_tokens(sentence)
                    #Chunked according to this approach:
                    # https://stackoverflow.com/questions/9671224/split-a-python-list-into-other-sublists-i-e-smaller-lists
                    max_len_chunks = [words[x:x+MAX_SEQ_LENGTH] for x in range (0, len(words), MAX_SEQ_LENGTH)]
                    for chunk in max_len_chunks:
                        new_line = ''
                        for word in chunk:
                            new_line += ' ' + word
                        cleaned_note += '\n' + new_line.strip()
        num_cleaned += 1
        cleaned_notes.append(cleaned_note)
        print(str(num_cleaned/notes_length*100) + "% notes cleaned")


    df['ner_cleaned_notes'] = cleaned_notes
    df_json_encoded = df.to_json().encode()
    standard_write_to_db('ner_cleaned_notes', df_json_encoded)

