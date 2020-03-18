from nltk import word_tokenize, sent_tokenize
import re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

in_file = open('mimic_iob_test.txt')
out_file = open('test_out.txt', 'w+')
#in_file = open('all_notes.txt')
#out_file = open('all_notes_iob.txt', 'w+')

#medication_file = open('medication_set.txt')
frequency_file = open('frequency.txt')
diagnosis_file = open('icd10_set.txt')
type_of_route_file = open('type_of_route.txt')
unit_of_form_file = open('unit_of_form.txt')
unit_of_mass_file = open('unit_of_mass.txt')
unit_of_time_file = open('unit_of_time.txt')
unit_of_volume_file = open('unit_of_volume.txt')

diagnoses_file = open('diagnoses_list.txt')
medication_file = open('medication_list.txt')

frequency_set = set({})
for line in frequency_file.readlines():
    word = re.sub('\n', '', line)
    frequency_set.add(word)

type_of_route_set = set({})
for line in type_of_route_file.readlines():
    word = re.sub('\n', '', line)
    type_of_route_set.add(word)

unit_of_form_set = set({})
for line in unit_of_form_file.readlines():
    word = re.sub('\n', '', line)
    unit_of_form_set.add(word)

unit_of_mass_set = set({})
for line in unit_of_mass_file.readlines():
    word = re.sub('\n', '', line)
    unit_of_mass_set.add(word)

unit_of_time_set = set({})
for line in unit_of_time_file.readlines():
    word = re.sub('\n', '', line)
    unit_of_time_set.add(word)

unit_of_volume_set = set({})
for line in unit_of_volume_file.readlines():
    word = re.sub('\n', '', line)
    unit_of_volume_set.add(word)

def has_numbers(inputString):
        return any(char.isdigit() for char in inputString)

diagnoses = diagnosis_file.readlines()
medications = medication_file.readlines()

for line in in_file.readlines():
    if line != '\n' and '____' not in line:
        line = re.sub('\[','',line)
        line = re.sub('\]','',line)
        line = re.sub('\*','',line)
        sentences = sent_tokenize(line)
        for sentence in sentences:
            words = word_tokenize(sentence)
            labels = []
            for word in words:
                labels.append('O')

            for diagnosis in diagnoses:
                diag_length = len(diagnosis.split())
                if diag_length >= len(words):
                    ratio=fuzz.ratio(sentence, diagnosis)
                    if ratio > 61:
                        labels[0] = 'B-DIAGNOSIS'
                        for i in range(1,len(labels)):
                            labels[i] = 'I-DIAGNOSIS'
                else:
                    max_ratio = 0
                    max_begin = -1
                    max_end = -1
                    for i in range(0, len(words)-diag_length+1):
                        substring = ''
                        for j in range(i, i + diag_length):
                            substring += ' ' + words[j]
                        substring = substring.strip()
                        ratio = fuzz.ratio(diagnosis, substring)
                        if ratio > max_ratio and ratio > 61:
                            max_ratio = ratio
                            max_begin = i
                            max_end = i + diag_length

                    if max_begin >= 0:
                        for i in range(max_begin, max_end):
                            if i == max_begin:
                                if labels[i] == 'O':
                                    labels[i] = 'B-DIAGNOSIS'
                            else:
                                if labels[i] == 'O':
                                    labels[i] = 'I-DIAGNOSIS'

            for medication in medications:
                med_length = len(medication.split())
                if med_length >= len(words):
                    ratio=fuzz.ratio(sentence, medication)
                    if ratio > 61:
                        labels[0] = 'B-MEDICATION'
                        for i in range(1,len(labels)):
                            labels[i] = 'I-MEDICATION'
                else:
                    max_ratio = 0
                    max_begin = -1
                    max_end = -1
                    for i in range(0, len(words)-med_length+1):
                        substring = ''
                        for j in range(i, i + med_length):
                            substring += ' ' + words[j]
                        substring = substring.strip()
                        ratio = fuzz.ratio(medication, substring)
                        if ratio > max_ratio and ratio > 61:
                            max_ratio = ratio
                            max_begin = i
                            max_end = i + med_length
                        
                    if max_begin >= 0:
                        for i in range(max_begin, max_end):
                            if i == max_begin:
                                labels[i] = 'B-MEDICATION'
                            else:
                                labels[i] = 'I-MEDICATION'

            for i, word in enumerate(words):
                print(word + ' ' + labels[i], file = out_file)

            print('', file = out_file)

