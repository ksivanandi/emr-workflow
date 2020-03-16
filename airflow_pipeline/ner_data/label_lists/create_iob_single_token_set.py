from nltk import word_tokenize, sent_tokenize
import re

#in_file = open('mimic_iob_test.txt')
#out_file = open('test_out.txt', 'w+')
in_file = open('all_notes.txt')
out_file = open('all_notes_iob.txt', 'w+')

medication_file = open('medication_set.txt')
frequency_file = open('frequency.txt')
diagnosis_file = open('icd10_set.txt')
type_of_route_file = open('type_of_route.txt')
unit_of_form_file = open('unit_of_form.txt')
unit_of_mass_file = open('unit_of_mass.txt')
unit_of_time_file = open('unit_of_time.txt')
unit_of_volume_file = open('unit_of_volume.txt')

medication_set = set({})
for line in medication_file.readlines():
    word = re.sub('\n', '', line)
    medication_set.add(word)

frequency_set = set({})
for line in frequency_file.readlines():
    word = re.sub('\n', '', line)
    frequency_set.add(word)

diagnosis_set = set({})
for line in diagnosis_file.readlines():
    word = re.sub('\n', '', line)
    diagnosis_set.add(word)

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

for line in in_file.readlines():
    if line != '\n' and '____' not in line:
        line = re.sub('\[','',line)
        line = re.sub('\]','',line)
        line = re.sub('\*','',line)
        sentences = sent_tokenize(line)
        for sentence in sentences:
            prev_label = ''
            for word in word_tokenize(sentence):
                # place logic to figure out the label
                if word.lower() in diagnosis_set:
                    label = 'DIAGNOSIS'
                elif word.lower() in medication_set:
                    label = 'MEDICATION'
                elif word.lower() in type_of_route_set:
                    label = 'ROUTE_TYPE'
                elif word.lower() in unit_of_form_set:
                    label = 'FORM_UNIT'
                elif word.lower() in unit_of_mass_set:
                    label = 'MASS_UNIT'
                elif word.lower() in unit_of_time_set:
                    label = 'TIME_UNIT'
                elif word.lower() in unit_of_volume_set:
                    label = 'VOLUME_UNIT'
                elif has_numbers(word):
                    label = 'NUMBER'
                else:
                    label = 'O'
                
                #add beginning 'B' or inside 'I' to the front of the label
                if label != 'O':
                    if label != prev_label:
                        i_or_b = 'B'
                    else:
                        i_or_b = 'I'
                    print(word + ' ' + i_or_b + '-' + label, file = out_file)
                else:
                    print(word + ' ' + label, file = out_file)
                prev_label = label

            print('', file = out_file)

