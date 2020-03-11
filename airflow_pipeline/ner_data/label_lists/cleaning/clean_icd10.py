import re

in_file = open('icd10cm_codes_2020.txt')
out_file = open('icd10_cleaned.txt', 'w+')
stop_word_file = open('diagnosis_stop_words.txt')

def haveNumbers(inputString):
    return any(char.isdigit() for char in inputString)

diagnosis_stop_words = []
for line in stop_word_file.readlines():
    line = re.sub('\'', '', line)
    line = re.sub('\n', '', line)
    diagnosis_stop_words.append(line)

for line in in_file.readlines():
    line = re.sub('\(', '', line)
    line = re.sub('\)', '', line)
    line = re.sub('\[', '', line)
    line = re.sub('\]', '', line)
    line = re.sub(',', '', line)
    line = line.lower()

    new = ''
    for word in line.split()[1:]:
        if len(word) > 2:
            if word not in diagnosis_stop_words and not haveNumbers(word):
                if len(new)==0:
                    new += word
                else:
                    new += ' ' + word

    print(new, file=out_file)

in_file.close()
out_file.close()
stop_word_file.close()
