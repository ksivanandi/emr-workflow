file_in = open('dx-terms-032420.csv')
file_out = open('dx_terms_cleaned.txt','w+')

import re

for line in file_in.readlines():
    line = line.split(',')[1].strip().lower()
    line = re.sub('\"', '', line)
    if len(line) > 2:
        print(line, file=file_out)

