from token_classification_infer import inference

def label_notes():
    print(500)
    in_file = open('all_note_lines.txt')
    lines = in_file.readlines()
    total_length = len(lines)
    print(len(lines))
    for i in range(0, len(lines), 100000):
        end_index = i + 100000
        if end_index < total_length:
            sub_lines = lines[i:end_index]
        else:
            sub_lines = lines[i:total_length]
        print('sub_lines length: '+ str(len(sub_lines)))
        inference(sub_lines)
        print(str(end_index/total_length)+"% lines labeled")

