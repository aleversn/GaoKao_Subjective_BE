# %%
import os
import json
import random

BAD_DIR = '../Bad_Student_Answer_Dataset'
GOOD_DIR = '../Good_Student_Answer_Dataset'
files = os.listdir(BAD_DIR)

for file_item in files:
    if not (file_item.endswith('json') or file_item.endswith('jsonl')):
        continue
    path = os.path.join(BAD_DIR, file_item)
    file_info = file_item.split('_')
    good_file = file_item.split('bad_answer')[0] + 'good_answer.json'
    save_file = file_item.split('bad_answer')[0] + 'total_answer.json'
    good_path = os.path.join(GOOD_DIR, good_file)
    if not os.path.exists(good_path):
        continue
    with open(path, 'r', encoding='utf-8') as f:
        bad_data = f.readlines()
    bad_data = [json.loads(line) for line in bad_data]
    with open(good_path, 'r', encoding='utf-8') as f:
        good_data = f.readlines()
    good_data = [json.loads(line) for line in good_data]
    good_groups = {}
    for item in good_data:
        if item['question'] not in good_groups:
            good_groups[item['question']] = []
            good_groups[item['question']].append(item)
    good_sample = []
    for key in good_groups.keys():
        sample = random.choice(good_groups[key])
        sample['bad_student_answer'] = sample['good_student_answer']
        good_sample.append(sample)
    bad_data.extend(good_sample)
    with open(save_file, 'w', encoding='utf-8') as f:
        for item in bad_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

# %%
