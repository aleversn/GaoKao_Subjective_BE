# %%
import os
import json

SOURCE_DIR = '../ProceedDataset/Bad_Student_Answer_Dataset'
files = os.listdir(SOURCE_DIR)

c_id = 0
for file_item in files:
    if not (file_item.endswith('json') or file_item.endswith('jsonl')):
        continue
    path = os.path.join(SOURCE_DIR, file_item)
    file_info = file_item.split('_')
    course, question_type = file_info[0], file_info[1]
    with open(path) as f:
        json_data = f.readlines()
    for idx, item in enumerate(json_data):
        json_data[idx] = json.loads(item)
    q_id = 0
    for item in json_data:
        item['id'] = f'{course}_{question_type}_{q_id}'
        q_id += 1
    if not os.path.exists(os.path.join('backend_data', 'question')):
        os.makedirs(os.path.join('backend_data', 'question'))
    with open(os.path.join('backend_data', 'question', f'{c_id}_{course}_{question_type}.jsonl'), mode='w+') as f:
        for item in json_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    c_id += 1

# %%
