import json
import re
from nltk.translate.bleu_score import sentence_bleu
from nltk.translate.bleu_score import SmoothingFunction
import jieba
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus']=False

input_json=r"/root/autodl-tmp/code/SOSD/GaoKao-Subjective-Dataset-Classification--main/score_bad_ans/Chinese/Chinese_ShortAns_bad_answer_score_score.json"

# 读取jsonl文件
def read_jsonl(input_json) -> list:
    data = []
    with open(input_json, 'r') as f:
        for line in f:
            content = json.loads(line)
            data.append(content)
    return data

# 每四行一组
def group_data(data: list) -> list:
    group = []
    for i in range(0, len(data), 4):
        group.append(data[i:i+4])
    return group

# 使用正则提取每一行的分数并转为float
def extract_score(bad_student_answer_score: str) -> float:
    match = re.search(r'.*【总分】\s*([\d.]+)分', bad_student_answer_score)
    if match:
        return float(match[1])
    return None

# jieba 中文分词 BLEU
def compute_bleu(reference: str, candidate: str) -> float:
    reference_tokens = list(jieba.cut(reference))
    candidate_tokens = list(jieba.cut(candidate))
    smoothing_function=SmoothingFunction().method4
    return sentence_bleu([reference_tokens], candidate_tokens,smoothing_function=smoothing_function,weights=(1,1,0,0))

# jaccard
def compute_jaccard(reference: str, candidate: str) -> float:
    reference_tokens = set(jieba.cut(reference))
    candidate_tokens = set(jieba.cut(candidate))
    intersection = len(reference_tokens & candidate_tokens)
    union = len(reference_tokens | candidate_tokens)
    return intersection / union if union != 0 else 0

# 对于相同的题目，保留不同的分数，并对相同的分数使用相似度筛选
def filter_best_answer(group: list) -> list:
    filtered_group = []
    
    # 按照分数分组
    score_groups = {}
    for item in group:
        score_value = extract_score(item["bad_student_answer_score"])
        if score_value is not None:
            if score_value not in score_groups:
                score_groups[score_value] = []
            score_groups[score_value].append(item)
    
    # 遍历每个分数组
    for score_value, answers in score_groups.items():
        if len(answers) > 1:
            best_answer = answers[0]["bad_student_answer"]  # 初始假设第一个答案为最佳答案
            max_similarity = 0
            best_answer_item = answers[0]  # 保留最佳答案的字典
            
            # 轮流将每个答案作为参考答案
            for i in range(1, len(answers)):
                candidate = answers[i]["bad_student_answer"]
                # 计算 BLEU 或 Jaccard 相似度，选择最高的那个
                bleu_score = compute_bleu(best_answer, candidate)  # 也可以替换为compute_jaccard
                if bleu_score > max_similarity:
                    max_similarity = bleu_score
                    best_answer = candidate
                    best_answer_item = answers[i]  # 更新为字典中的完整答案
            filtered_group.append(best_answer_item)  # 保留包含最佳答案的完整字典
        else:
            filtered_group.append(answers[0])  # 如果只有一个答案，直接保留整个字典
    
    return filtered_group

# 主函数，处理数据
def process_data(input_json):
    data = read_jsonl(input_json)
    grouped_data = group_data(data)
    
    # 筛选每个问题组中的最佳答案
    final_answers = []
    for group in grouped_data:
        best_answers = filter_best_answer(group)
        final_answers.extend(best_answers)
    
    return final_answers

def plot_score_distribution(ans:list):
    scores = []
    for item in ans:
        score = extract_score(item)
        if score is not None:
            scores.append(score)
    # 设置图形大小
    plt.figure(figsize=(8,6))

    # 绘制直方图，bins数量根据数据调整
    plt.hist(scores, bins=50)  # 你可以根据数据适当调整 bins 数量

    # 添加标签
    plt.xlabel('Score')
    plt.ylabel('Frequency')

    # 计算并标出均值和中位数
    mean_score = sum(scores) / len(scores)
    median_score = np.median(scores)
    plt.axvline(mean_score, color='red', linestyle='dashed', linewidth=1, label=f'Mean: {mean_score:.2f}')
    plt.axvline(median_score, color='green', linestyle='dashed', linewidth=1, label=f'Median: {median_score:.2f}')
    
    # 显示图例
    plt.legend()
    
    # 设置网格
    plt.grid(True, alpha=0.45)

    # 调整x轴刻度
    plt.xticks(np.arange(min(scores), max(scores) + 1, step=1))  # 设置间隔为1，确保更多刻度显示

    # 显示图表
    plt.tight_layout()

    # 保存并显示图片
    plt.savefig('score_distribution.png')
    plt.show()

def jaccard_similarity(answer1: str, answer2: str) -> float:
    words1 = set(jieba.cut(answer1))
    words2 = set(jieba.cut(answer2))
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    return len(intersection) / len(union) if union else 0.0

def delete_similar_question(data: list, threshold=0.47) -> list:
    to_remove = set()
    for i in range(len(data)):
        j = i + 1
        while j < len(data):
            similarity = jaccard_similarity(data[i]['bad_student_answer'], data[j]['bad_student_answer'])
            if similarity > threshold:
                to_remove.add(j)
            j += 1
    filtered_data = [ans for idx, ans in enumerate(data) if idx not in to_remove]
    return filtered_data

def save_to_jsonl(data, file_path):
    with open(file_path, 'w') as f:
        for item in data:
            json.dump(item, f, ensure_ascii=False)
            f.write('\n')

# 调用函数
final_answers = process_data(input_json)
final_answers=delete_similar_question(final_answers)

# 输出结果
for answer in final_answers:
    print(answer)

print(len(final_answers))

output_file = r"/root/autodl-tmp/code/SOSD/GaoKao-Subjective-Dataset-Classification--main/dealwithdata/cleared_Chineae_ShortAns_bad_answer_score.jsonl"
save_to_jsonl(final_answers, output_file)
    
print(f"数据已保存到 {output_file}")

plot_score_distribution([].append(ans_scor) for ans_scor in final_answers[["bad_student_answer_score"]] )

