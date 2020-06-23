in_file = open('clean_drugs_list.txt')
out_file = open('medication_set.txt', 'w+')

word_set = set({})
for line in in_file.readlines():
    for word in line.split():
        word_set.add(word)
#out_file.write(str(word_set))
for word in word_set:
    if len(word) > 2:
        print(word, file=out_file)

print(len(word_set))
in_file.close()
out_file.close()
