in_file = open('_drug_list.txt')
out_file = open('clean_drugs_list.txt', 'w+')

for line in in_file.readlines():
    out_file.write(line.split(',')[1])

in_file.close()
out_file.close()
