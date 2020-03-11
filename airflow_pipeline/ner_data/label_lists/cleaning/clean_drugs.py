import re

in_file = open('_drug_list.txt')
out_file = open('clean_drugs_list.txt', 'w+')
stop_word_file = open('medication_stop_words.txt')

def haveNumbers(inputString):
    return any(char.isdigit() for char in inputString)

medication_stop_words = []
for line in stop_word_file.readlines():
    line = re.sub('\'', '', line)
    line = re.sub('\n', '', line)
    medication_stop_words.append(line)

for line in in_file.readlines():
    line = re.sub('\'', '', line)
    line = re.sub('\"', '', line)
    line = re.sub('\(', '', line)
    line = re.sub('\)', '', line)
    line = re.sub(',', ' ', line)
    line = re.sub(';', '', line)
    line = line.lower()

    new = ''
    for word in line.split()[1:]:
        if len(word) > 2:
            if word not in medication_stop_words:
                if haveNumbers(word):
                    #check if a medication name with a number in it after a hyphen, pretty common in the raw list
                    hyphen_split = word.split('-')
                    if len(hyphen_split) == 2 and not haveNumbers(hyphen_split[0]) and haveNumbers(hyphen_split[1]):
                        word = hyphen_split[0]
                if not haveNumbers(word):
                    if len(new) == 0:
                        new += word
                    else:
                        new += ' ' + word
    print(new, file=out_file)

in_file.close()
out_file.close()
stop_word_file.close()
