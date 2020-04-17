import re
from nltk import sent_tokenize

in_file = open('ner_note_test.txt')
out_file = open('cleaned_ner_note_test.txt', 'w+')
for line in in_file.readlines():
    if line != '\n' and '____' not in line:
        line = re.sub('\[','',line)
        line = re.sub('\]','',line)
        line = re.sub('\*','',line)
        sentences = sent_tokenize(line)
        new_line = ''
        for sentence in sentences:
            new_line += ' ' + sentence
        print(new_line, file=out_file)

