file_in = open('combined_dx_terms.csv')
file_out = open('combined_dx_terms_cleaned.txt','w+')

import re

for line in file_in.readlines():
    line = line.strip()
    line = re.sub('\"', '', line)
    if len(line) > 0:
        print(line, file=file_out)

