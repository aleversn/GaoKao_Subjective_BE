import os
import sys
import json
import shutil
from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.body import response_body, scoreItem

backend_data_dir = '../backend_data'
question_types = []
question_dict = {}
error_type_list = []


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
            if course in app_config['course_map']:
                course = app_config['course_map'][course]
            if ct in app_config['course_map']:
                ct = app_config['course_map'][ct]
            question_types.append({
                'id': id,
                'name': course,
                'type': ct
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

@app.post("/update_score")
async def get_types(score_item: scoreItem, api_key = Header(None)):
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
    
    res = response_body(message='success', data=score_item)
    return res()
