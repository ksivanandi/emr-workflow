import pandas as pd
from workflow_read_and_write import standard_read_from_db

df_json_encoded = standard_read_from_db('ner_labeled_notes')
df = pd.read_json(df_json_encoded.decode())

for i, row in df.iterrows():
    lines_stripped = row['ner_cleaned_notes'].strip().split('\n')
    labeled_lines_stripped = row['labeled_notes'].strip().split('\n')
    if len(lines_stripped) != len(labeled_lines_stripped):
        print('lengths don\'t match for row ' + str(i))
    first_line = lines_stripped[0].replace(' ##','')
    first_labeled_line = ''
    for word in labeled_lines_stripped[0].split():
        first_labeled_line += ' ' + word.split('[')[0]
    first_labeled_line = first_labeled_line.strip()
    if first_line != first_labeled_line:
        print('first lines are not the same for row ' + str(i))
        print('unlabeled: ' + first_line)
        print('labeled: ' + first_labeled_line)
                                                                                        
    last_line = lines_stripped[-1].replace(' ##','')
    last_labeled_line = ''
    for word in labeled_lines_stripped[-1].split():
        last_labeled_line += ' ' + word.split('[')[0]
    last_labeled_line = last_labeled_line.strip()
    if last_line != last_labeled_line:
        print('last lines are not the same for row ' + str(i))
        print('unlabeled: ' + last_line)
        print('labeled: ' + last_labeled_line)

