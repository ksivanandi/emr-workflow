in_file = open('icd10_cleaned.txt')
out_file = open('icd10_set.txt', 'w+')

word_set = set({})
for line in in_file.readlines():
    for word in line.split():
        word_set.add(word)
#out_file.write(str(word_set))
for word in word_set:
    print(word, file=out_file)

in_file.close()
out_file.close()
