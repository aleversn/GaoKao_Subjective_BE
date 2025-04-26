import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import shutil
import asyncio
from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from api.body import response_body, scoreItem, answerItem

backend_data_dir = '../backend_data'
question_types = []
question_dict = {}
error_type_list = []
question_file_lock = asyncio.Lock()
score_file_lock = asyncio.Lock()


with open('./app_config.json') as f:
    app_config = json.load(f)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许的前端地址
    allow_credentials=True,  # 是否允许发送 Cookie
    allow_methods=["*"],  # 允许的 HTTP 方法
    allow_headers=["*"],  # 允许的请求头
)


@app.get("/")
def home():
    res = response_body(message='SAS Benchmark API')
    return res()


@app.get("/get_question_types")
async def get_types():
    global question_types
    global backend_data_dir
    if len(question_types) == 0:
        question_types = []
        files = os.listdir(os.path.join(backend_data_dir, 'question'))
        for file_item in files:
            file_item = file_item.split('_')
            id, course, ct = file_item[0], file_item[1], file_item[2]
            ct = ct.split('.')[0]
            if course in app_config['course_map']:
                course_name = app_config['course_map'][course]
            else:
                course_name = course
            if ct in app_config['course_map']:
                ct_name = app_config['course_map'][ct]
            else:
                ct_name = ct
            question_types.append({
                'id': id,
                'name': course_name,
                'type': ct_name,
                'course': course,
                'course_type': ct
            })

    res = response_body(message='success', data=question_types)
    return res()


@app.get("/get_question_list")
async def get_list(id):
    id = str(id)
    global question_dict
    global backend_data_dir
    if id not in question_dict:
        files = os.listdir(os.path.join(backend_data_dir, 'question'))
        for file_item in files:
            file_item_list = file_item.split('_')
            if file_item_list[0] == id:
                path = os.path.join(backend_data_dir, 'question', file_item)
                with open(path, encoding='utf-8') as f:
                    ori_json = f.readlines()
                ori_json = [json.loads(item) for item in ori_json]
                question_dict[id] = ori_json
                break
    if id not in question_dict:
        res = response_body(message='not found', data=[])
    else:
        res = response_body(message='success', data=question_dict[id])
    return res()


@app.get("/get_error_types")
async def get_error_types():
    global error_type_list
    global backend_data_dir
    if len(list(error_type_list)) <= 0:
        file_name = os.path.join(backend_data_dir, 'error_type.jsonl')
        with open(file_name, encoding='utf-8') as f:
            ori_json = f.readlines()
        ori_json = [json.loads(item) for item in ori_json]
        error_type_list = ori_json
    res = response_body(message='success', data=error_type_list)
    return res()


@app.get("/get_scores")
async def get_scores(id, course, c_type):
    path = os.path.join(backend_data_dir, 'scores',
                        f'{str(id)}_{course}_{c_type}.jsonl')
    if os.path.exists(path):
        async with score_file_lock:
            with open(path, encoding='utf-8') as f:
                ori_json = f.readlines()
            ori_json = [json.loads(item) for item in ori_json]

        res = response_body(message='success', data=ori_json)
        return res()
    res = response_body(message='File Not Found', code=404, status='failed')
    return res()


@app.post("/update_score")
async def update_score(score_item: scoreItem, api_key=Header(None)):
    valid = False
    if len(app_config['api_key']) == 0:
        valid = True
    for key in app_config['api_key']:
        if key == api_key:
            valid = True
            break
    if not valid:
        res = response_body(message='Invalid API Key', status=401)
        return res()
    path = os.path.join(backend_data_dir, 'scores',
                        f'{score_item.course_id}_{score_item.course}_{score_item.course_type}.jsonl')
    if os.path.exists(path):
        async with score_file_lock:
            with open(path, encoding='utf-8') as f:
                ori_json = f.readlines()
            ori_json = [json.loads(line) for line in ori_json]
            for item in ori_json:
                if item['id'] == score_item.question_id:
                    item['scoreItem'] = {
                        'label': score_item.label,
                        'comments': score_item.comments,
                        'user_id': score_item.user_id,
                        'user_name': score_item.user_name,
                        'seg_labels': score_item.seg_labels
                    }
                    break
            
            with open(path, 'w', encoding='utf-8') as f:
                for item in ori_json:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
        res = response_body(message='success', data=score_item)
    else:
        res = response_body(message=f'File Not Found, path: {path}', code=404, status='failed')
    return res()

@app.post("/update_answer")
async def update_answer(answer_item: answerItem, api_key=Header(None)):
    valid = False
    if len(app_config['api_key']) == 0:
        valid = True
    for key in app_config['api_key']:
        if key == api_key:
            valid = True
            break
    if not valid:
        res = response_body(message='Invalid API Key', status=401)
        return res()
    global question_dict
    path = os.path.join(backend_data_dir, 'scores',
                        f'{answer_item.course_id}_{answer_item.course}_{answer_item.course_type}.jsonl')
    ori_path = os.path.join(backend_data_dir, 'question', f'{answer_item.course_id}_{answer_item.course}_{answer_item.course_type}.jsonl')
    if os.path.exists(path):
        async with score_file_lock:
            with open(path, encoding='utf-8') as f:
                ori_json = f.readlines()
            ori_json = [json.loads(line) for line in ori_json]
            for item in ori_json:
                if item['id'] == answer_item.question_id:
                    idx = answer_item.answer_idx
                    bad_student_answer_segs = item['bad_student_answer_segs']
                    if len(bad_student_answer_segs) < idx + 1:
                        break
                    bad_student_answer_segs[idx] = answer_item.answer
                    item['bad_student_answer_segs'] = bad_student_answer_segs
                    break
            
            with open(path, 'w', encoding='utf-8') as f:
                for item in ori_json:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
    else:
        res = response_body(message=f'File Not Found, path: {path}', code=404, status='failed')
    if os.path.exists(ori_path):
        async with question_file_lock:
            with open(ori_path, encoding='utf-8') as f:
                ori_json = f.readlines()
            ori_json = [json.loads(line) for line in ori_json]
            for item in ori_json:
                if item['id'] == answer_item.question_id:
                    idx = answer_item.answer_idx
                    bad_student_answer_segs = item['bad_student_answer_segs']
                    if len(bad_student_answer_segs) < idx + 1:
                        break
                    bad_student_answer_segs[idx] = answer_item.answer
                    item['bad_student_answer_segs'] = bad_student_answer_segs
                    break
            
            with open(ori_path, 'w', encoding='utf-8') as f:
                for item in ori_json:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
            id = str(answer_item.course_id)
            if id in question_dict:
                del question_dict[answer_item.course_id]
    else:
        res = response_body(message=f'File Not Found, path: {ori_path}', code=404, status='failed')
    res = response_body(message='success', data=answer_item)
    return res()

@app.post("/update_reference")
async def update_reference(answer_item: answerItem, api_key=Header(None)):
    valid = False
    if len(app_config['api_key']) == 0:
        valid = True
    for key in app_config['api_key']:
        if key == api_key:
            valid = True
            break
    if not valid:
        res = response_body(message='Invalid API Key', status=401)
        return res()
    global question_dict
    path = os.path.join(backend_data_dir, 'scores',
                        f'{answer_item.course_id}_{answer_item.course}_{answer_item.course_type}.jsonl')
    ori_path = os.path.join(backend_data_dir, 'question', f'{answer_item.course_id}_{answer_item.course}_{answer_item.course_type}.jsonl')
    if os.path.exists(path):
        async with score_file_lock:
            with open(path, encoding='utf-8') as f:
                ori_json = f.readlines()
            ori_json = [json.loads(line) for line in ori_json]
            for item in ori_json:
                if item['id'] == answer_item.question_id:
                    item['answer'] = answer_item.answer
                    break
            with open(path, 'w', encoding='utf-8') as f:
                for item in ori_json:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
    else:
        res = response_body(message=f'File Not Found, path: {path}', code=404, status='failed')
    if os.path.exists(ori_path):
        async with question_file_lock:
            with open(ori_path, encoding='utf-8') as f:
                ori_json = f.readlines()
            ori_json = [json.loads(line) for line in ori_json]
            for item in ori_json:
                if item['id'] == answer_item.question_id:
                    item['answer'] = answer_item.answer
                    break
            with open(ori_path, 'w', encoding='utf-8') as f:
                for item in ori_json:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
            id = str(answer_item.course_id)
            if id in question_dict:
                del question_dict[answer_item.course_id]
    else:
        res = response_body(message=f'File Not Found, path: {ori_path}', code=404, status='failed')
    res = response_body(message='success', data=answer_item)
    return res()

@app.post("/update_question")
async def update_question(answer_item: answerItem, api_key=Header(None)):
    valid = False
    if len(app_config['api_key']) == 0:
        valid = True
    for key in app_config['api_key']:
        if key == api_key:
            valid = True
            break
    if not valid:
        res = response_body(message='Invalid API Key', status=401)
        return res()
    global question_dict
    path = os.path.join(backend_data_dir, 'scores',
                        f'{answer_item.course_id}_{answer_item.course}_{answer_item.course_type}.jsonl')
    ori_path = os.path.join(backend_data_dir, 'question', f'{answer_item.course_id}_{answer_item.course}_{answer_item.course_type}.jsonl')
    if os.path.exists(path):
        async with score_file_lock:
            with open(path, encoding='utf-8') as f:
                ori_json = f.readlines()
            ori_json = [json.loads(line) for line in ori_json]
            ori_question = 'undefined'
            for item in ori_json:
                if item['id'] == answer_item.question_id or item['question'] == ori_question:
                    if ori_question == 'undefined':
                        ori_question = item['question']
                    item['question'] = answer_item.answer
            with open(path, 'w', encoding='utf-8') as f:
                for item in ori_json:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
    else:
        res = response_body(message=f'File Not Found, path: {path}', code=404, status='failed')
    if os.path.exists(ori_path):
        async with question_file_lock:
            with open(ori_path, encoding='utf-8') as f:
                ori_json = f.readlines()
            ori_json = [json.loads(line) for line in ori_json]
            ori_question = 'undefined'
            for item in ori_json:
                if item['id'] == answer_item.question_id or item['question'] == ori_question:
                    if ori_question == 'undefined':
                        ori_question = item['question']
                    item['question'] = answer_item.answer
            with open(ori_path, 'w', encoding='utf-8') as f:
                for item in ori_json:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
            id = str(answer_item.course_id)
            if id in question_dict:
                del question_dict[answer_item.course_id]
    else:
        res = response_body(message=f'File Not Found, path: {ori_path}', code=404, status='failed')
    res = response_body(message='success', data=answer_item)
    return res()