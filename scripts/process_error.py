# %%
import os
import json
from tools import *

SOURCE_DIR = '../ProceedDataset/Bad_Student_Answer_Score_Dataset/ErrorType'
files = os.listdir(SOURCE_DIR)

ID_FILE = '../backend_data/ID_DICT.json'
with open(ID_FILE, 'r') as f:
    ID_DATA = json.load(f)

def denoise(ori):
    ori = extract_and_replace_tables(ori)
    ori = replace_display_math(ori)
    ori = replace_uns_newline(ori)
    return ori

result = []
for file_item in files:
    if not (file_item.endswith('txt')):
        continue
    path = os.path.join(SOURCE_DIR, file_item)
    file_info = file_item.split('_')
    course, question_type = file_info[0], file_info[1]
    item_data = {
        'q_id': ID_DATA[f'{course}_{question_type}'],  # 根据文件名获取问题ID
        'course': course,
        'question_type': question_type,
        'errors': []
    }
    with open(path) as f:
        dict_data = f.readlines()
    for idx, item in enumerate(dict_data):
        if item.strip() == '':
            continue
        if len(item.split('：')) > 1:
            name, description = item.split('：')
        else:
            name, description = item.strip(), ''
        item_data['errors'].append({
            'name': name.strip(),
            'description': description.strip()
        })
    result.append(item_data)

if not os.path.exists(os.path.join('backend_data')):
    os.makedirs(os.path.join('backend_data'))
with open(os.path.join('backend_data', f'error_type.jsonl'), mode='w+') as f:
    for item in result:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

# %%
