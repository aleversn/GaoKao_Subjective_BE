# %%
import os
import json
from tools import *

SOURCE_DIR = '../ProceedDataset/Bad_Student_Answer_Dataset'
files = os.listdir(SOURCE_DIR)

def denoise(ori, mask_newline=False):
    ori = extract_and_replace_tables(ori)
    if mask_newline:
        ori = replace_table_newline(ori) # 其中表格中的\n被替换成了#@n#
    ori = replace_display_math(ori)
    ori = replace_math_newline(ori)
    ori = replace_uns_newline(ori)
    return ori

c_id = 0
ID_DICT = {}
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
        json_data[idx]['question'] = denoise(json_data[idx]['question'])
        json_data[idx]['answer'] = denoise(json_data[idx]['answer'])
        json_data[idx]['bad_student_answer'] = denoise(json_data[idx]['bad_student_answer'], True)
        segs = json_data[idx]['bad_student_answer'].split('\n')
        json_data[idx]['bad_student_answer_segs'] = []
        for seg in segs:
            if seg.strip() == '':
                continue
            seg = seg.strip()
            seg = seg.replace('#@n#', '\n')
            json_data[idx]['bad_student_answer_segs'].append(seg)
        json_data[idx]['bad_student_answer'] = json_data[idx]['bad_student_answer'].replace('#@n#', '\n')
    q_id = 0
    for item in json_data:
        item['id'] = f'{course}_{question_type}_{q_id}'
        q_id += 1
    if not os.path.exists(os.path.join('backend_data', 'question')):
        os.makedirs(os.path.join('backend_data', 'question'))
    if not os.path.exists(os.path.join('backend_data', 'scores')):
        os.makedirs(os.path.join('backend_data', 'scores'))
    with open(os.path.join('backend_data', 'question', f'{c_id}_{course}_{question_type}.jsonl'), mode='w+') as f:
        for item in json_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    with open(os.path.join('backend_data', 'scores', f'{c_id}_{course}_{question_type}.jsonl'), mode='w+') as f:
        for item in json_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    ID_DICT[f'{course}_{question_type}'] = c_id
    c_id += 1

with open(os.path.join('backend_data', 'ID_DICT.json'), mode='w+') as f:
    json.dump(ID_DICT, f)

# %%
