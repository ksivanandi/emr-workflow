from token_classification_infer import inference

in_file = open('all_note_lines.txt')
lines = in_file.readlines()
total_length = len(lines)
for i in range(33109815, len(lines), 100000):
    end_index = i + 100000
    if end_index < total_length:
        sub_lines = lines[i:end_index]
    else:
        sub_lines = lines[i:total_length]

    inference(sub_lines)
    print(str(end_index/total_length)+"% lines labeled")

