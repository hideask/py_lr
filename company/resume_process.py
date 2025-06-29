# -*- coding: utf-8 -*-

import json
import re
from sqlite3 import connect
import psycopg2
import pandas as pd
from openpyxl import Workbook as wb
from db_connection import get_db_connection, close_db_connection

platform = ""

retain_fields = {
        "user": {
            "name": True,
            "genderLabel": True,
            "age": True,
            "ageLabel": True,
            "maxEducationLabel": True,
            "workYears": True,
            "workYearsLabel": True,
            "cityLabel": True,
            "unlockedPhone": True,
            "email": True
        },
        "resume": {
            "skillTags": True,
            "educationExperiences": {
                "schoolName": True,
                "beginTime": True,
                "endTime": True,
                "educationTimeLabel": True,
                "major": True,
                "educationLabel": True
            },
            "workExperiences": {
                "orgName": True,
                "jobTitle": True,
                "description": True,
                "timeLabel": True,
                "workSkillTags": {
                    "name": True
                }
            },
            "projectExperiences": {
                "name": True,
                "beginTime": True,
                "endTime": True,
                "timeLabel": True,
                "description": True,
                "responsibility": True,
            },
            # "professionalSkills": {
            #     "name": True,
            #     "mastery": True,
            #     "usedMonthsLabel": True
            # },
            # "trainingExperiences": {
            #     "name": True,
            #     "machinery": True,
            #     "timeLabel": True
            # },
            "languageSkills": {
                "name": True,
                "readWriteSkill": True,
                "hearSpeakSkill": True
            },
            "certificates": {
                "name": True,
            },
            "purposes": {
                "industryLabel": "",
                "jobTypeLabel": "",
                "jobNatureLabel": "",
                "location": "",
                "salaryLabel": "",
            }
        }
    }

field_mapping = {
    # 用户信息
    "name": "姓名",
    "genderLabel": "性别",
    "age": "年龄",
    "ageLabel": "年龄段",
    "maxEducationLabel": "最高学历",
    "workYears": "工作年限",
    "workYearsLabel": "工作年限描述",
    "cityLabel": "现居地",
    "unlockedPhone": "手机号码",
    "email": "邮箱地址",

    # 简历信息
    "skillTags": "技能标签",
    "educationExperiences": "教育经历",
    "schoolName": "学校名称",
    "beginTime": "开始时间",
    "endTime": "结束时间",
    "educationTimeLabel": "时间段（教育）",
    "major": "专业",
    "educationLabel": "学历",

    "workExperiences": "工作经历",
    "orgName": "公司名称",
    "jobTitle": "职位名称",
    "description": "描述",
    "timeLabel": "时间段（工作）",
    "workSkillTags": "工作技能标签",
    "name": "名称",  # 可用于多个地方，如技能、证书等

    "projectExperiences": "项目经验",
    "responsibility": "职责",

    "languageSkills": "语言能力",
    "readWriteSkill": "读写能力",
    "hearSpeakSkill": "听说能力",

    "certificates": "证书信息",

    "purposes": "求职意向",
    "industryLabel": "行业",
    "jobTypeLabel": "职位类型",
    "jobNatureLabel": "工作性质",
    "location": "地点",
    "salaryLabel": "薪资要求"
}


def filter_resume_data(input_data, required_fields):
    def filter_dict(data, fields, parent_key=""):
        if not isinstance(data, dict):
            return data

        result = {}
        for key, value in data.items():
            if key in fields:
                value = deep_clean(value)

                # 自定义字段映射 + 上下文重命名
                current_key = field_mapping.get(key, key)

                # 特殊字段重命名规则（根据 parent_key 判断上下文）
                if parent_key == "skillTags" and key == "name":
                    current_key = "技能名称"
                elif parent_key == "certificates" and key == "name":
                    current_key = "证书名称"
                elif parent_key == "workSkillTags" and key == "name":
                    current_key = "工作技能名称"
                elif parent_key == "languageSkills" and key == "name":
                    current_key = "语言名称"
                elif key == "unlockedPhone":
                    current_key = "手机号码"
                elif key == "educationExperiences":
                    current_key = "教育经历"
                elif key == "workExperiences":
                    current_key = "工作经历"
                elif key == "projectExperiences":
                    current_key = "项目经验"

                # 递归处理值
                if isinstance(value, dict):
                    result[current_key] = filter_dict(value, fields.get(key, {}), parent_key=key)
                elif isinstance(value, list):
                    result[current_key] = [
                        filter_dict(item, fields.get(key, {}), parent_key=key) if isinstance(item, dict) else item
                        for item in value
                    ]
                else:
                    result[current_key] = value
        return result

    return filter_dict(input_data, required_fields, parent_key="")


def filter_resume_data(input_data, required_fields):
    ""
    def filter_dict(data, fields):
        if not isinstance(data, dict):
            return data 
        result = {}
        for key, value in data.items():
            if key in fields:
                value = deep_clean(value)
                current_key = 'phone' if key == 'unlockedPhone' else key
                if isinstance(value, dict):
                    result[current_key] = filter_dict(value, fields.get(key, {}))
                elif isinstance(value, list):
                    result[current_key] = [filter_dict(item, fields.get(key, {}))
                            if isinstance(item, dict) else item for item in value
                    ]
                else:
                    result[current_key] = value
        return result

    return filter_dict(input_data, required_fields)

def deep_clean(data):
    if isinstance(data, str):
        data = re.sub(r'[\u200b-\u200f\u202c-\u202e\ufeff]', '', data)
        # 如果检测到编号列表，则用空格替换换行符，否则删除
        # if re.search(r'\d+\.', data):  # 检测是否有编号
        #     data = data.replace('\n', ' ')
        # else:
        #     data = data.replace('\n', '')
        return data
    elif isinstance(data, dict):
        return {k: deep_clean(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [deep_clean(i) for i in data]
    else:
        return data



def process_resume_batch(cursor, connection, batch_size=10000):
    """处理一批简历数据"""
    cursor.execute("SELECT id, resume_info FROM zhilian_resume WHERE resume_processed_info IS NULL LIMIT %s",
                  (batch_size,))
    zhilian_resume = cursor.fetchall()
    print(f"获取成功{len(zhilian_resume)}条数据")
    return zhilian_resume

def update_resume_info(cursor, connection, id, processed_info):
    """更新简历处理信息"""
    update_sql = """UPDATE zhilian_resume SET resume_processed_info = %s WHERE id = %s"""
    cursor.execute(update_sql, (processed_info, id))
    connection.commit()

# 简历数据清洗
def process_resumes():
    """处理简历主函数"""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        zhilian_resume = process_resume_batch(cursor, connection)
        
        i = 0
        for id, resume_info in zhilian_resume:
            try:
                resume_data = json.loads(resume_info)
                filtered_data = filter_resume_data(resume_data, required_fields=retain_fields)
                processed_info = json.dumps(filtered_data, ensure_ascii=False)

                update_resume_info(cursor, connection, id, processed_info)
                i += 1
                print(f"已更新简历id {id}, 成功更新{i}条")
            except Exception as ex:
                connection.rollback()
                print(f"处理简历id {id} 时出错: {str(ex)}")
                print(f"错误数据: {resume_info}")
                continue
    finally:
        close_db_connection(cursor, connection)
# systemSetting = "你是一个专业且高效的简历精灵，你将接收到一份以 JSON 格式呈现的简历数据。" \
# "请从输入简历JSON中提取关键信息，并将其整合为概括的一句话简历描述。\n\n"
# prompt = "技能1: 关键信息提取\n 1. 教育背景：明确最高学历，写出毕业院校及所学专业。\n" \
# "2. 工作经历：列出主要工作单位名称、担任的关键职位、主要工作职责和突出成就（若有）。\n " \
# "3. 技能专长：列举与工作或专业相关的重要技能。\n " \
# "4. 项目经验：提及项目名称、在项目中担任的角色以及取得的主要成果（若有）。\n\n" \
# "5. 期望：总结当前的期望。\n " \
# "技能 2: 简历一句话描述\n1. 生成的一句话简历描述需简洁明了，以第一人称的方式描述，逻辑连贯，突出核心要点，避免冗余表述。\n\n" \
# "限制\n- 仅围绕简历进行描述，拒绝处理与简历无关的任何事务。\n" \
# "- 输出内容需严格遵循简历内容，不额外补充\n- 输出一句话描述，概括简历数据，不需要具体简历格式\n\n"
# "### 技能：" \
# "按照如下关键字段组织简历的详细描述，需要将个人信息在开头描述出来"
# "1. 个人信息：姓名、性别、手机号码、 电子邮箱。\n" \
# "2. 求职意向（多条）：期望职位工种、期望月薪范围、期望月薪下限、期望月薪上限,期望地点、行业、工作时间。\n " \
# "3. 工作经历（多条）：工作单位、岗位名称、岗位描述(原样输出)、开始时间、结束时间。\n " \
# "4. 项目经验（多条）：项目名称、担任职责、项目描述(原样输出)、教育背景、开始时间、结束时间。\n" \
# "5. 教育经历（多条）：学校名称、开始时间、结束时间、专业、学历。\n " \
# "6. 语言能力（多条）：语言类别、熟练程度、读写能力、听说能力。\n " \
# "7. 职业证书（多条）：证书名称。\n " \

systemSetting = "你是一个专业且高效的简历精灵，请根据提供的 JSON 格式简历数据，以第一人称视角撰写专业、真实且有说服力的简历自述。撰写时需模拟求职者自然表达的语气，避免模板化、机械化表述。\n\n"
# prompt = \
# "### 生成要求：" \
# "1、整体框架：严格按照 <个人概述 → 求职意向 → 教育经历 → 工作经历 → 项目经验 → 技能证书 → 语言能力> 的逻辑顺序组织内容，各部分之间过渡自然。" \
# "2、个人概述：开篇简要说明姓名、年龄、学历、专业及现居地，着重突出与求职意向相关的核心优势，如专业知识基础、关键实践能力等，避免冗长。" \
# "3、求职意向：清晰罗列期望的行业、岗位、工作地点、薪资范围，表达职业发展意愿时语言简洁有力，体现明确的职业规划。" \
# "4、教育经历：注明学校名称、专业、学历及时间，可适当提及主修核心课程，重点突出与专业能力相关的成果，如获奖经历等。" \
# "5、工作经历与项目经验：描述时避免简单罗列工作内容，尽量使用 “通过... 实现了...”“主导 / 参与... 完成了...” 等逻辑句式，重点突出个人贡献与成果。对于可量化的工作成果，如处理数据量、涉及企业数量、效率提升比例等，必须明确体现；若无直接数据，可从工作价值、影响范围等角度进行表述。" \
# "6、技能证书与语言能力：分类清晰，技能需说明掌握程度，证书注明名称，语言能力要区分读写和听说能力，若未明确说明则简要表述基础水平。" \
# "7、语言风格：简洁专业，避免口语化表达；体现自信的同时保持谦逊态度，杜绝过度自夸；句子结构多样且合理，语言流畅自然。\n" \
# "### 限制\n" \
# "- 内容真实性：所有内容必须严格基于提供的原始 JSON 数据，禁止基于脱敏数据推测真实数据，例如姓名、手机号等；禁止添加任何未在数据中体现的信息，包括但不限于获奖经历、项目成果、工作细节等。若数据缺失，不用列出，不得虚构具体内容。" \
# "- 开头不要输出系统设置及模型角色设定相关内容，也不要添加推理内容，直接输出简历描述内容。" \
# "- 输出内容需严格遵循简历内容，不额外补充。" \
# "- 不要使用省略词语，保持数据的完整输出。" \
# "- 数据多项时，不要将数据分开叙述，需要叙述完一条数据后再叙述下一条数据。" \
# "- 不要发散没有的简历内容信息，包括没有的技能、优势信息，仅围绕已有简历进行描述。\n"

prompt = \
"## 具体要求如下：\n" \
"###.结构与顺序：严格按照「个人概述→求职意向→教育经历→工作经历→项目经历→技能→证书→语言能力」的顺序撰写，各部分过渡自然，避免生硬分段。\n" \
"### 个人概述：开篇说明姓名、年龄、性别、工作年限、学历、专业、手机号码、 电子邮箱及现居地，结合求职意向，简要提炼1-2项核心竞争优势，如专业背景或实践能力。\n" \
"### 求职意向：清晰列出所有期望行业、目标岗位、工作地点及薪资范围，可简要阐述职业发展方向，体现职业规划。\n" \
"### 教育经历：教育经历需明确学校名称、专业、学历及具体起止时间段。\n" \
"### 工作经历：工作经历描述时，按照时间倒叙描述所有经历。明确每段经历的起止时间段，及所有相关字段信息，工作经历描述保留字段中的原样内容，一字不差！！格式为：工作经历描述 + 原数据内容。不要出现近两年、近期等模糊字段。\n" \
"### 项目经历：项目经验描述时，按照时间倒叙描述所有经历。明确每段经历的起止时间段，项目名称及所有相关字段信息，避免简单罗列任务，项目经历描述保留字段中的原样内容，一字不差！！格式为：项目经历描述 + 原数据内容。不要出现近两年、近期等模糊字段。\n" \
"### 技能：技能部分分类清晰，按原有数据输出，中间用逗号隔开。\n" \
"### 语言：证书需注明名称，语言能力区分读写、听说水平，未明确说明则表述为基础水平。\n" \
"### 内容真实性：所有信息必须严格基于原始JSON数据，禁止添加任何未提及的内容，包括但不限于获奖经历、项目成果、技能优势等；数据缺失时，不用列出，不得虚构。\n" \
"### 自然叙事：摒弃模块化、分标题式的表述方式，以流畅连贯的段落自然过渡各部分内容，像讲述个人经历故事一样，用生活化的逻辑串联信息，例如通过时间线、因果关系衔接（例：“这段留学经历让我接触到前沿理念，也让我后来在工作中尝试用数字化工具解决问题...”）。\n" \
# "## 内容架构：仍需包含个人基本情况、求职意向、教育经历、工作经历、项目经验、技能证书、语言能力等核心信息，但无需使用 “个人概述”“求职意向” 等明确标题区分模块。\n" \
# "### 表达规范：采用简洁专业的书面语，避免口语化表达，保持自信谦逊的态度，杜绝过度夸大或自夸性表述，句子结构多样且合理，确保内容流畅自然。\n" \
# "### 格式要求：直接输出简历内容，不添加任何引导性或解释性语句；完整呈现所有数据，不拆分叙述，按顺序依次表述各项内容。\n" \
# "## 数据格式：数据中的时间段保留原有的格式，不要省略月份，更不要使用模糊的语义去表述时间段。\n" \
# "## 内容呈现：工作经历和项目经验中的描述内容，需严格按照 JSON 数据中 'description' 字段的原始表述进行输出，不做任何语序调整、词汇替换或内容增减，确保文字原样呈现。\n\n"


prompt_sc = \
"## 具体要求如下：\n" \
"###.结构与顺序：严格按照「个人概述→求职意向→教育经历→工作经历」的顺序撰写，各部分过渡自然，避免生硬分段，如果没有相关信息就不生成，不补充，例如没有教育经历，就不生成教育经历相关内容，没有工作经历就不生成工作经历相关内容。\n" \
"### 个人概述：开篇说明姓名、年龄、性别、工作年限、学历、专业、手机号码、 及现居地，结合求职意向，简要提炼1-2项核心竞争优势，如专业背景或实践能力。\n" \
"### 求职意向：清晰列出所有期望行业、目标岗位、工作地点及薪资范围。\n" \
"### 教育经历：教育经历需明确学校名称、专业、学历及具体起止时间段。\n" \
"### 工作经历：工作经历描述时，按照时间倒叙描述所有经历。明确每段经历的起止时间段，及所有相关字段信息，工作经历描述保留字段中的原样内容，一字不差！！格式为：工作经历描述 + 原数据内容。不要出现近两年、近期等模糊字段。\n" \
"### 语言：证书需注明名称，语言能力区分读写、听说水平，未明确说明则表述为基础水平。\n" \
"### 内容真实性：所有信息必须严格基于原始JSON数据，禁止添加任何未提及的内容，包括但不限于获奖经历、项目成果、技能优势等；数据缺失时，不用生成，不得虚构。\n" \
"### 自然叙事：摒弃模块化、分标题式的表述方式，以流畅连贯的段落自然过渡各部分内容，像讲述个人经历故事一样，用生活化的逻辑串联信息，例如通过时间线、因果关系衔接）。\n"
input_r = "输入：“```json\n "
input_l = "```”\n"
output = "输出："

#组装大模型识别数据
def assemble_data(data, reture=None):
    # 创建数据列表
    excel_data = []

    # 遍历数据并组装
    for id, info in data:
        info = json.loads(info)
        # resume_processed_info['user_id'] = user_id
        info['id'] = id
        if platform == 'wy':
            row_data = {
                'input': '##' + systemSetting + prompt + input_r + json.dumps(info, ensure_ascii=False) + input_l + output,
                'expectedAnswer': '',
                'systemSetting': systemSetting,
                'modelAnswer': ''
            }
        elif platform == 'sc':
            row_data = {
                'input': '##' + systemSetting + prompt_sc + input_r + json.dumps(info, ensure_ascii=False) + input_l + output,
                'expectedAnswer': '',
                'systemSetting': systemSetting,
                'modelAnswer': ''
            }
        else:
            row_data = {
                'id': id,
                'info': json.dumps(info, ensure_ascii=False)
            }
        excel_data.append(row_data)
    
    df = pd.DataFrame(excel_data)

    if platform == 'wy':
        output_file = f'resume_data_xx_{start}_{end}.xlsx'
    elif platform == 'sc':
        output_file = f'resume_data_sc_{start}_{end}.xlsx'
    else:
        output_file = f'resume_data_json_{start}_{end}.xlsx'
    df.to_excel(output_file, index=False)
    print(f"数据已保存到 {output_file}")

import threading
def process_resumes_multithreaded(num_threads=7):
    """使用多个线程并行处理简历"""
    connection = get_db_connection()
    lock = threading.Lock()  # 线程锁，确保数据库操作线程安全

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id, resume_info FROM zhilian_resume WHERE resume_processed_info IS NULL and resume_info is not NULL LIMIT 35000")
        all_data = cursor.fetchall()
        print(f"获取成功{len(all_data)}条数据")

        # 数据分片
        chunk_size = len(all_data) // num_threads
        threads = []

        for i in range(num_threads):
            start = i * chunk_size
            end = None if i == num_threads - 1 else (i + 1) * chunk_size
            data_chunk = all_data[start:end]

            thread = threading.Thread(
                target=process_resume_batch_thread,
                args=(i + 1, data_chunk, connection, lock)
            )
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

    finally:
        close_db_connection(None, connection)

def process_resume_batch_thread(thread_id, data_chunk, connection, lock):
    """
    线程执行的简历处理函数
    :param thread_id: 线程ID
    :param data_chunk: 当前线程处理的数据片段
    :param connection: 数据库连接对象
    :param lock: 用于线程同步的锁
    """
    cursor = connection.cursor()
    try:
        i = 0
        for id, resume_info in data_chunk:
            try:
                resume_data = json.loads(resume_info)
                filtered_data = filter_resume_data(resume_data, required_fields=retain_fields)
                processed_info = json.dumps(filtered_data, ensure_ascii=False)

                with lock:
                    update_resume_info(cursor, connection, id, processed_info)
                    i += 1
                    print(f"[线程 {thread_id}] 已更新简历id {id}, 成功更新{i}条")
            except Exception as ex:
                connection.rollback()
                print(f"[线程 {thread_id}] 处理简历id {id} 时出错: {str(ex)}")
                continue
        connection.commit()
    finally:
        cursor.close()

start = 5000
end = 15000
def process_resumes_excel():
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        if platform == 'wy' :
            cursor.execute(f"SELECT id, resume_processed_info as info FROM zhilian_resume WHERE resume_processed_info IS NOT NULL and id > {start} and id <= {end} and id != '25048' order by id")

            # cursor.execute(f"SELECT id, resume_processed_info as info FROM zhilian_resume WHERE resume_processed_info IS NOT NULL and id in ('24306','24369') order by id")
        elif platform == 'sc':
            cursor.execute(f"SELECT id, resume_info as info FROM sc_pub_recruitmentnet_resume WHERE resume_info IS NOT NULL and id > {start} and id <= {end} order by id")
        else:
            # cursor.execute(f"SELECT id, resume_processed_info as info FROM zhilian_resume WHERE resume_processed_info IS NOT NULL and id > {start} and id <= {end} order by id")
            cursor.execute(f"SELECT id, resume_processed_info as info "
                           f"FROM zhilian_resume "
                           f"WHERE resume_processed_info IS NOT NULL and id > {start} and id <= {end} and length(resume_processed_info) <= 5000 and id != '25048' order by id")
        resume = cursor.fetchall()
        print(f"获取成功{len(resume)}条数据")
        assemble_data(resume)
    finally:
        close_db_connection(cursor, connection)

def insert_resume_description():
    path = 'D:\数字政务\人岗匹配\一句话简历数据\处理数据\人岗匹配28384_30924_20250526095954.xlsx'

    data = pd.read_excel(path)
    for index, row in data.iterrows():
        input = row['input']
        modelAnswer = row['modelAnswer']
        start_marker = "```json\n"
        end_marker = "```"
        json_start = input.find(start_marker) + len(start_marker)
        json_end = input.find(end_marker, json_start)
        if json_start == -1 or json_end == -1:
            print(f"第{index + 1}条数据没有找到json数据")
            continue

        json_data = json.loads(input[json_start:json_end].strip())
        id = json_data['id']

        connection = None
        cursor = None
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute("UPDATE zhilian_resume SET resume_description = %s WHERE id = %s", (modelAnswer, id))
            connection.commit()
            print(f"第{index + 1}条数据更新成功, id: {id}")
        except Exception as ex:
            connection.rollback()
            print(f"第{index + 1}条数据更新失败: {str(ex)}")
        finally:
            close_db_connection(cursor, connection)

import html

def clean_html(text):
    if not text:
        return ""

    # 第一步：自动解码 HTML 实体（如 &lt; → <, &#xa; → \n, &#xff01; → ！）
    text = html.unescape(html.unescape(text))

    # 第二步：去除所有 HTML 标签
    text = re.sub(r"<[^>]+>", "", text)

    text = re.sub(r"&\s*lt\s*;?", "<", text)
    text = re.sub(r"&\s*gt\s*;?", ">", text)
    text = re.sub(r"&\s*#xa\s*;?", "\n", text)
    text = re.sub(r"&\s*#xd\s*;?", "\r", text)
    text = re.sub(r"&\s*#x9\s*;?", " ", text)

    # 第三步：替换特殊空白字符（零宽空格、软换行等）
    text = re.sub(r"[\xa0\u200b\u200c\u200d\u200e\u200f]", " ", text)

    # 第四步：合并连续空白为单个空格，并去除首尾空格
    text = re.sub(r"\s+", " ", text).strip()

    return text

from datetime import date

# 自定义 JSON 编码器以处理 date 类型
class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')  # 转换为字符串格式
        return super().default(obj)
def process_resume_sc():
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id,name,id_card,gender,ethnicity,education,experience_range,phone,self_evaluation,job_title,desired_location,desired_salary,language,proficiency,reading_writing,listening_speaking,company,previous_job_title,start_date,end_date,job_description,school,edu_start_date,edu_end_date,edu_education,major,courses FROM sc_pub_recruitmentnet_resume")
        sc_resume = cursor.fetchall()
        print(f"获取成功{len(sc_resume)}条数据")
        for row in sc_resume:
            (
                id, name, id_card, gender, ethnicity, education, experience_range, phone, self_evaluation,
                job_title, desired_location, desired_salary, language, proficiency, reading_writing,
                listening_speaking, company, previous_job_title, start_date, end_date, job_description,
                school, edu_start_date, edu_end_date, edu_education, major, courses
             ) = row
            self_evaluation = clean_html(self_evaluation)
            job_title = clean_html(job_title)
            job_description = clean_html(job_description)

            resume_json = {
                "user": {
                    "name": name,
                    "genderLabel": gender,
                    "ethnicity": ethnicity,
                    "idCard": id_card,
                    "phone": phone,
                    "maxEducationLabel": education,
                    "workYearsLabel": experience_range,
                    "selfEvaluation": self_evaluation
                },
                "resume": {
                    "educationExperience": [
                        {
                            "schoolName": school,
                            "beginTime": edu_start_date,
                            "endTime": edu_end_date,
                            "educationLabel": edu_education,
                            "major": major,
                            "courses": courses  # 可选字段，视实际数据情况处理
                        }
                    ],
                    "workExperiences": {
                        "orgName": company,
                        "jobTitle": previous_job_title,
                        "beginTime": start_date,
                        "endTime": end_date,
                        "description": job_description
                    },
                    
                    "purposes": {
                        "jobTypeLabel": job_title,
                        "location": desired_location,
                        "salaryLabel": desired_salary
                    },
                }
            }
            resume_json = replace_none_with_empty(resume_json)
            cursor.execute(
                "UPDATE sc_pub_recruitmentnet_resume SET self_evaluation = %s, job_title = %s, job_description = %s, resume_info = %s WHERE id = %s",
                (self_evaluation, job_title, job_description, json.dumps(resume_json, ensure_ascii=False, cls=DateEncoder), id)
            )
            connection.commit()
            print(f"数据更新成功(id:{id})")
    except  Exception as ex:
        connection.rollback()
        print(f"数据更新失败(id:{id}): {str(ex)}")
    finally:
        close_db_connection(cursor, connection)

def remove_empty_fields(d):
    """
    递归删除字典中值为空（None, '', [], {}, 空白字符串等）的字段
    """
    if isinstance(d, dict):
        return {
            k: remove_empty_fields(v)
            for k, v in d.items()
            if v not in (None, "", [], {}) and not (isinstance(v, str) and v.strip() == "")
        }
    elif isinstance(d, list):
        return [remove_empty_fields(item) for item in d if item not in (None, "", [], {})]
    else:
        return d

def replace_none_with_empty(d):
    """
    递归地将字典或列表中的 None 替换为空字符串 ""
    """
    if isinstance(d, dict):
        return {k: replace_none_with_empty(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [replace_none_with_empty(item) for item in d]
    elif d is None:
        return ""
    elif isinstance(d, str) and str(d) == "null":
        return ""
    else:
        return d

# def process_resumes_sc_excel():
#     connection = None
#     cursor = None
#     try:
#         connection = get_db_connection()
#         cursor = connection.cursor()
#
#         cursor.execute("SELECT id, resume_info FROM sc_pub_recruitmentnet_resume WHERE id > 0 and id <= 6300")
#         sc_resume = cursor.fetchall()
#         print(f"获取成功{len(sc_resume)}条数据")
#         assemble_data_sc(sc_resume)
#     finally:
#         close_db_connection(cursor, connection)


# systemSetting_sc = "你是一个专业且高效的简历精灵，你将接收到一份以 JSON 格式呈现的简历数据。" \
#                "请从输入简历JSON中提取关键信息，并将其整合为概括的一句话简历描述。\n\n"
# prompt_sc = "技能1: 关键信息提取\n 1. 教育背景：明确最高学历，写出毕业院校及所学专业。\n" \
#          "2. 工作经历：列出主要工作单位名称、担任的关键职位、主要工作职责和突出成就（若有）。\n " \
#          "3. 技能专长：列举与工作或专业相关的重要技能（若有）。\n " \
#          "4. 项目经验：提及项目名称、在项目中担任的角色以及取得的主要成果（若有）。\n\n" \
#          "5. 期望：总结当前的期望。\n " \
#          "技能 2: 简历一句话描述\n1. 生成的一句话简历描述需简洁明了，以第一人称的方式描述，逻辑连贯，突出核心要点，避免冗余表述。\n\n" \
#          "限制\n- 仅围绕简历进行描述，拒绝处理与简历无关的任何事务。\n" \
#          "- 输出内容需严格遵循简历内容，不额外补充\n- 输出一句话描述，概括简历数据，不需要具体简历格式\n\n"


# 组装大模型识别数据
# def assemble_data_sc(data, reture=None):
#     # 创建数据列表
#     excel_data = []
#
#     # 遍历数据并组装
#     for id, resume_info in data:
#         resume_info = json.loads(resume_info)
#         resume_info['id'] = id
#         row_data = {
#             'input': systemSetting_sc + prompt_sc + input_r + json.dumps(resume_info,
#                                                                    ensure_ascii=False) + input_l + output,
#             'systemSetting': systemSetting_sc,
#             'expectedAnswer': '',
#             'modelAnswer': ''
#         }
#         excel_data.append(row_data)
#
#     df = pd.DataFrame(excel_data)
#
#     output_file = 'resume_data_sc.xlsx'
#     df.to_excel(output_file, index=False)
#     print(f"数据已保存到 {output_file}")

def process_single_resume(resume_data):
    """处理单个简历的工作函数"""
    id, resume_info = resume_data
    connection = None
    cursor = None
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        job_list = set()
        job_name_list = set()
        
        resume_json = json.loads(resume_info)
        resume_part = resume_json.get('resume')
        workExperiences = resume_part.get('workExperiences')
        for workExp in workExperiences:
            jobSubtype = workExp.get('jobSubtype')
            jobSubtypeHighlight = workExp.get('jobSubtypeHighlight')
            if jobSubtype != None:
                job_list.add(workExp.get('jobSubtype'))
            if jobSubtypeHighlight != None and jobSubtypeHighlight.get('name') != None:
                job_name_list.add(jobSubtypeHighlight.get('name'))
        
        # 将列表转换为用逗号分隔的字符串
        job_list_str = ','.join(job_list) if job_list else ''
        job_name_list_str = ','.join(job_name_list) if job_name_list else ''
        
        cursor.execute("UPDATE zhilian_resume set job_sub_type = %s, job_sub_type_name = %s where id = %s", (job_list_str, job_name_list_str, id))
        connection.commit()
        print(f"成功处理简历ID: {id}")
        
    except Exception as ex:
        print(f"数据更新失败(id:{id}): {str(ex)}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def process_resume_job(max_workers=10):
    """多线程处理简历工作信息"""
    from concurrent.futures import ThreadPoolExecutor
    
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, resume_info FROM zhilian_resume")
    resume = cursor.fetchall()
    close_db_connection(cursor, connection)
    
    print(f"获取成功{len(resume)}条数据，开始多线程处理...")
    
    # 使用线程池执行器进行多线程处理
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        futures = [executor.submit(process_single_resume, resume_data) for resume_data in resume]
        
        # 等待所有任务完成
        for future in futures:
            try:
                future.result()  # 获取结果，如果有异常会抛出
            except Exception as ex:
                print(f"线程执行异常: {str(ex)}")
    
    print("所有简历处理完成！")


if __name__ == "__main__":
    # process_resumes()
    # process_resumes_multithreaded()
    # process_resumes_excel()
    # insert_resume_description()
    # process_resume_sc()
    # process_resumes_sc_excel()
    process_resume_job()


    # data = pd.read_excel("https://p3-bot-workflow-sign.byteimg.com/tos-cn-i-mdko3gqilj/fba2b49cda4944a4bdf8fefdf4bd5f5f.xlsx~tplv-mdko3gqilj-image.image?rk3s=81d4c505&x-expires=1780137943&x-signature=429UE6ODXXvvznI48HsBR3j1Qq4%3D&x-wf-file_name=resume_data_1.xlsx")
    # print(len(data))

    # update_resume_description_sc()



"""
UPDATE zhilian_resume set resume_info = "replace"(resume_info, '"professionalSkills": null', '"professionalSkills": []') where resume_info like '%null%';
UPDATE zhilian_resume set resume_info = "replace"(resume_info, '"languageSkills": null', '"languageSkills": []') where resume_info like '%null%';
UPDATE zhilian_resume set resume_info = "replace"(resume_info, '"trainingExperiences": null', '"trainingExperiences": []') where resume_info like '%null%';
UPDATE zhilian_resume set resume_info = "replace"(resume_info, '"projectExperiences": null', '"projectExperiences": []') where resume_info like '%null%';
UPDATE zhilian_resume set resume_info = "replace"(resume_info, '"workSkillTags": null', '"workSkillTags": []') where resume_info like '%null%';
UPDATE zhilian_resume set resume_info = "replace"(resume_info, '"certificates": null', '"certificates": []') where resume_info like '%null%';
UPDATE zhilian_resume set resume_info = "replace"(resume_info, '"major": null', '"major": ""') where resume_info like '%null%';

UPDATE zhilian_resume set resume_processed_info = "replace"(resume_processed_info, '"professionalSkills": null', '"professionalSkills": []') where resume_processed_info like '%null%';
UPDATE zhilian_resume set resume_processed_info = "replace"(resume_processed_info, '"languageSkills": null', '"languageSkills": []') where resume_processed_info like '%null%';
UPDATE zhilian_resume set resume_processed_info = "replace"(resume_processed_info, '"trainingExperiences": null', '"trainingExperiences": []') where resume_processed_info like '%null%';
UPDATE zhilian_resume set resume_processed_info = "replace"(resume_processed_info, '"projectExperiences": null', '"projectExperiences": []') where resume_processed_info like '%null%';
UPDATE zhilian_resume set resume_processed_info = "replace"(resume_processed_info, '"workSkillTags": null', '"workSkillTags": []') where resume_processed_info like '%null%';
UPDATE zhilian_resume set resume_processed_info = "replace"(resume_processed_info, '"certificates": null', '"certificates": []') where resume_processed_info like '%null%';
UPDATE zhilian_resume set resume_processed_info = "replace"(resume_processed_info, '"major": null', '"major": ""') where resume_processed_info like '%null%';
"""