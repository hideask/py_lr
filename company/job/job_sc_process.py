# -*- coding: utf-8 -*-

import re
import psycopg2
from datetime import datetime
from db_connection import get_db_connection, close_db_connection

import pandas as pd
import os
import requests
import json
import threading
import time
import random

import logging
logging.basicConfig(level=logging.INFO)


retain_fields = {
    "companyName": "",
    "companySize": "",
    "displayPhoneNumber": False,
    "education": "",
    "industryName": "",
    "cardCustomJson": "",
    "jobSummary": "",
    "name": "",
    "needMajor": [],
    "staffCard": {
        "staffName": ""
    },
    "recruitNumber": True,
    "salary60": "",
    "salaryCount": "",
    "salaryReal": "",
    "subJobTypeLevelName": "",
    "welfareTagList": [],
    "workCity": "",
    "cityDistrict": "",
    "streetName": "",
    "workType": "",
    "workingExp": ""
}

import html

def clean_html(text):
    if not text:
        return ""

    # 第一步：自动解码 HTML 实体（如 &lt; → <, &#xa; → \n, &#xff01; → ！）
    text = html.unescape(text)

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

def clean_job_data():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, job_description FROM sc_pub_recruitmentnet_job where job_description like '%<%' or job_description like '%&%' ")

    rows = cursor.fetchall()

    for row in rows:
        job_id = row[0]
        dirty_description = row[1]
        cleaned_description = clean_html(dirty_description)

        cursor.execute(
            "UPDATE sc_pub_recruitmentnet_job SET job_description = %s WHERE id = %s",
            (cleaned_description, job_id)
        )
        connection.commit()
        print(f"Cleaned job description for job ID: {job_id}")
    close_db_connection(cursor, connection)


def process_jobs():
    """处理岗位主函数"""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        zhilian_job = process_job_batch(cursor, connection)

        i = 0
        for id, job_info, category_name, job_name in zhilian_job:
            try:
                job_data = json.loads(job_info)
                filtered_data = filter_job_data(job_data, required_fields=retain_fields)
                filtered_data['category_name'] = category_name
                filtered_data['job_name'] = job_name
                filtered_data['id'] = id
                processed_info = json.dumps(filtered_data, ensure_ascii=False)

                update_job_info(cursor, connection, id, processed_info)
                i += 1
                print(f"已更新岗位id {id}, 成功更新{i}条")
            except Exception as ex:
                connection.rollback()
                print(f"处理岗位id {id} 时出错: {str(ex)}")
                print(f"错误数据: {job_info}")
                continue
    finally:
        close_db_connection(cursor, connection)

def process_job_batch(cursor, connection, batch_size=20000):
    """处理一批岗位数据"""
    cursor.execute("SELECT id, job_info, category_name, job_name FROM sc_pub_recruitmentnet_job LIMIT %s",
                  (batch_size,))
    zhilian_job = cursor.fetchall()
    print(f"获取成功{len(zhilian_job)}条数据")
    return zhilian_job

def filter_job_data(input_data, required_fields):
    ""
    def filter_dict(data, fields):
        if not isinstance(data, dict):
            return data
        result = {}
        for key, value in data.items():
            if key in fields:
                value = deep_clean(value)
                current_key = key
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

def update_job_info(cursor, connection, id, processed_info):
    """更新岗位处理信息"""
    update_sql = """UPDATE sc_pub_recruitmentnet_job SET processed_info = %s WHERE id = %s"""
    cursor.execute(update_sql, (processed_info, id))
    connection.commit()

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

def process_salary_range(salary_range):
    """处理薪资范围格式，将类似5001-10000转换为5000-10000"""
    if not salary_range or not isinstance(salary_range, str):
        return salary_range
    
    # 匹配薪资范围格式，如：5001-10000, 10001-25000
    pattern = r'(\d+)-(\d+)'
    match = re.match(pattern, salary_range.strip())
    
    if match:
        min_salary = int(match.group(1))
        max_salary = int(match.group(2))
        
        # 将最小薪资调整为千位整数
        # 如果是x001格式，改为x000
        if min_salary % 1000 == 1:
            min_salary = min_salary - 1
        
        return f"{min_salary}-{max_salary}"
    
    return salary_range

def process_sc_jobs():
    """处理岗位主函数"""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute('SELECT id,company_name as "companyName",company_type as "companyType",'\
                 'industry as "industryName",company_size as "companySize",'\
                 'registration_address as "address",job_category as "job_name",position_name as "name",'\
                       'job_description as "jobSummary",work_location as "cityDistrict",'\
                       'required_staff_count as "recruitNumber",salary_range as "salaryReal",'\
                       'benefits as "welfareTagList",experience_requirement as "workingExp",'\
                       'employment_type as "workType" FROM sc_pub_recruitmentnet_job' )
        zhilian_job = cursor.fetchall()

        columns = [desc[0] for desc in cursor.description]

        i = 0
        for job_info in zhilian_job:
            try:
                row_dict = dict(zip(columns, job_info))
                
                # 处理salaryReal字段格式
                if 'salaryReal' in row_dict:
                    row_dict['salaryReal'] = process_salary_range(row_dict['salaryReal'])
                
                processed_info = json.dumps(row_dict, ensure_ascii=False)

                update_sql = """UPDATE sc_pub_recruitmentnet_job SET processed_info = %s WHERE id = %s"""
                cursor.execute(update_sql, (processed_info, row_dict['id']))
                connection.commit()
                i += 1
                print(f"已更新岗位id {row_dict['id']}, 成功更新{i}条")
            except Exception as ex:
                connection.rollback()
                print(f"处理岗位id {row_dict.get('id', 'unknown')} 时出错: {str(ex)}")
                print(f"错误数据: {job_info}")
                continue
    finally:
        close_db_connection(cursor, connection)

def process_job_excel():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(f"select id,processed_info as info  from sc_pub_recruitmentnet_job  where process_type IS null order by id")
        jobs = cursor.fetchall()
        print(f"获取成功{len(jobs)}条数据")
        # 创建数据列表
        excel_data = []

        # 遍历数据并组装
        for id, info in jobs:
            info = json.loads(info)
            # resume_processed_info['user_id'] = user_id
            info['id'] = id

            row_data = {
                'id': id,
                'info': json.dumps(info, ensure_ascii=False)
            }
            excel_data.append(row_data)

        df = pd.DataFrame(excel_data)

        output_file = f'job_data_json_{len(jobs)}.xlsx'
        df.to_excel(output_file, index=False)
        print(f"数据已保存到 {output_file}")
    finally:
        close_db_connection(cursor, connection)

check_file_exists = False
def process_chunk(chunk, threadName, lock, output_dir):
    # global counter

    thread_output_file = os.path.join(output_dir, f'智能体分发结果_{threading.current_thread().name}.xlsx')

    column_names = chunk.columns.tolist()
    column_names.extend(['序号','introduce', 'threadName', 'startTime', 'endTime', 'startTime_format', 'endTime_format', '耗时(秒)'])

    # 如果文件不存在，先创建文件并写入表头
    if not os.path.exists(thread_output_file):
        df_header = pd.DataFrame(columns=column_names)
        df_header.to_excel(thread_output_file, index=False)
    elif check_file_exists:
        # 读取已有数据，用于判断 id 是否已存在
        existing_df = pd.read_excel(thread_output_file)
        existing_ids = set(existing_df['id'])  # 假设 'id' 是唯一标识字段

    # results = []
    counter = 1
    for index, row in chunk.iterrows():
        try:
            # 新增：判断 id 是否已存在，若存在则跳过
            if check_file_exists & os.path.exists(thread_output_file) and row['id'] in existing_ids:
                logging.info(f"ID {row['id']} 已存在，跳过处理")
                continue

            user_id = threadName + str(random.randint(1_000_000, 9_999_999))
            AppConversationID = getApplicationId(user_id)
            # AppConversationID = getApplicationId(threadName)
            result = api_call(row, AppConversationID, lock, user_id, counter)


            current_row = row.to_list()
            current_row.extend(result)
            df_row = pd.DataFrame([current_row], columns=column_names)
            with pd.ExcelWriter(thread_output_file, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                if 'Sheet1' in writer.book.sheetnames:
                    startrow = writer.sheets['Sheet1'].max_row
                else:
                    startrow = 0
                df_row.to_excel(writer, index=False, header=False, startrow=startrow)

            counter += 1
            if counter % 10 == 0 and counter > 0:
                current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                logging.info(f"[{current_time}]{threading.current_thread().name} 已处理条数：{counter}")

        except Exception as e:
            logging.error(f"处理数据出错: {str(e)}")
            # 添加错误信息并追加保存
            error_row = row.to_list()
            error_row.extend([counter, f"处理出错: {str(e)}", threading.current_thread().name, 0])
            df_error = pd.DataFrame([error_row], columns=column_names)
            with pd.ExcelWriter(thread_output_file, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                if 'Sheet1' in writer.book.sheetnames:
                    startrow = writer.sheets['Sheet1'].max_row
                else:
                    startrow = 0
                df_error.to_excel(writer, index=False, header=False, startrow=startrow)

        # 每处理10条数据保存一次
        # if (index + 1) % 10 == 0:
        #     temp_file = os.path.join(output_dir, f'智能体分发结果_{threading.current_thread().name}_temp.xlsx')
        #     try:
        #         thread_wb.save(temp_file)
        #         final_file = os.path.join(output_dir, f'智能体分发结果_{threading.current_thread().name}.xlsx')
        #         if os.path.exists(final_file):
        #             os.remove(final_file)
        #         os.rename(temp_file, final_file)
        #     except Exception as e:
        #         logging.error(f"保存文件时出错: {str(e)}")
        #         if os.path.exists(temp_file):
        #             os.remove(temp_file)
        # 为每个线程保存独立的文件
    # thread_output_file = os.path.join(output_dir, f'智能体分发结果_{threading.current_thread().name}.xlsx')
    # thread_wb.save(thread_output_file)

    # return results
def read_excel():
    df = pd.read_excel('D:/数字政务/人岗匹配/一句话简历数据/原始数据/job_data_json_13056.xlsx')
    print(f"读取数据成功，共有{df.shape[0]}条数据")
    # 每100行进行切片
    slice_size = 1307
    slices = [df.iloc[i:i + slice_size] for i in range(0, df.shape[0], slice_size)]
    print(f"处理{len(slices)}个块")
    return slices
def format_time(timestamp):
    dt = datetime.fromtimestamp(timestamp)
    millis = int((timestamp - int(timestamp)) * 1000)
    return dt.strftime(f"%Y-%m-%d %H:%M:%S.{millis:03d}")

# 模拟API调用的函数
def api_call(row, AppConversationID, lock, user_id, counter):
    # global counter
    start_time = time.time()  # 开始计时

    url = 'http://10.163.21.201:32300/api/proxy/api/v1/chat_query'
    data = {
        'Apikey': 'd14l347sbfv9olu4aerg',
        "Query": row['info'],
        "AppConversationID": AppConversationID,
        "ResponseMode": "blocking",
        "UserID": user_id
    }

    headers = {
        'Content-Type': 'application/json',
        'Apikey': 'd14l347sbfv9olu4aerg',
    }

    response = requests.post(url, json=data, headers=headers)

    introduce = '无'

    if response.status_code == 200:
        start = response.text.index('{')
        result = json.loads(response.text[start:-1]).get("answer")
        result = result.encode('ISO_8859_1').decode('utf-8')
        try:
            if result != '':
                introduce = result
            else:
                error = json.loads(result[result.index('{'):result.index('}') + 1]).get('error')
                logging.error(f'error:{error}')
        except Exception as e:
            logging.error(f'数据解析失败:{e}')
    else:
        logging.error(f'Failed to post data:{response.text}')

    end_time = time.time()  # 结束计时
    elapsed_time = round(end_time - start_time, 2)  # 精确到小数点后两位

    # lock.acquire()
    # try:
    #     counter += 1
        # logging.info(f"处理数据, user_id: {user_id}")
        # logging.info(f'counter:{counter}')
        # logging.info(f"id:{row['id']}")
        # logging.info(f'耗时:{elapsed_time}秒')
        # logging.info('------------------------------')

    # finally:
    #     lock.release()
    return [counter,introduce, threading.current_thread().name,start_time, end_time, format_time(start_time), format_time(end_time), elapsed_time]


def getApplicationId(user_id):
    url = 'http://10.163.21.201:32300/api/proxy/api/v1/create_conversation'
    data1 = {
        'Apikey': 'd14l347sbfv9olu4aerg',
        "Inputs": {
            "var": "variable"
        },
        "UserID": user_id
    }

    headers = {
        'Content-Type': 'application/json',
        'Apikey': 'd14l347sbfv9olu4aerg'
    }

    response1 = requests.post(url, json=data1, headers=headers)

    if response1.status_code == 200:
        AppConversationID = response1.json().get("Conversation").get('AppConversationID')
    else:
        AppConversationID = ''
        print('Failed to post data:', response1.status_code)
    return AppConversationID

def job_main(output_dir):
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 读取Excel文件
    excel_chunks = read_excel()

    threads = []
    lock = threading.Lock()
    for index, chunk in enumerate(excel_chunks):
        threadName = f'AAThread-{index}'

        thread = threading.Thread(target=process_chunk, args=(chunk, threadName, lock,  output_dir), name=threadName)
        threads.append(thread)
        thread.start()
    # 等待所有线程完成
    for thread in threads:
        thread.join()

    # 将结果写入新的Excel文件
    # output_file = os.path.join(output_dir, '智能体分发结果.xlsx')
    # new_wb.save(output_file)
    print("执行完毕")

def update_job_main():
    file_path = 'D:/数字政务/人岗匹配/一句话简历数据/处理数据/线程文件/job13000'
    files = get_excel_files(file_path)
    file_groups = [files[i:i + 2] for i in range(0, len(files), 2)]
    threads = []
    for group in file_groups:
        thread = threading.Thread(target=thread_task, args=(group,))
        threads.append(thread)
        thread.start()

    for  thread in threads:
        thread.join()

def get_excel_files(folder_path):
    excel_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".xlsx") or file.endswith(".xls"):
                excel_files.append(os.path.join(root, file))
    return excel_files

def thread_task(files):
    for file in files:
        process_excel_file(file)

def process_excel_file(file_path):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        df = pd.read_excel(file_path)
        # 假设有一个'id'字段用于匹配和更新
        for index, row in df.iterrows():
            # 这里可以根据你的需求进行数据库更新或其他操作
            cursor.execute("update sc_pub_recruitmentnet_job set job_description_detail = %s, process_start_time = %s,"
                           "process_end_time = %s,time_consume = %s, process_type = %s where id = %s",
                           (row['introduce'], row['startTime_format'], row['endTime_format'], row['耗时(秒)'], '1', row['id']))
            connection.commit()
            print(f"更新数据成功, id: {row['id']}")
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
    finally:
        close_db_connection(cursor, connection)

def fetch_unprocessed_data_from_db(batch_size=100):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # 查询未处理的数据并标记为正在处理
        cursor.execute("""
            SELECT id, processed_info as info FROM sc_pub_recruitmentnet_job 
            WHERE job_description_detail IS NULL 
            and process_type is null
            ORDER BY id LIMIT %s FOR UPDATE SKIP LOCKED
        """, (batch_size,))

        rows = cursor.fetchall()

        if rows:
            ids = [row[0] for row in rows]
            # 标记这些数据为正在处理
            cursor.execute("""
                UPDATE sc_pub_recruitmentnet_job SET process_type = %s 
                WHERE id = ANY(%s)
            """, (threading.current_thread().name,ids,))
            connection.commit()
        return rows

    except Exception as e:
        logging.error(f"Error fetching data from DB: {e}")
        connection.rollback()
    finally:
        close_db_connection(cursor, connection)
    return []

def update_result_in_db(id, result):
    connection = get_db_connection()
    cursor = connection.cursor()
    # return [counter,introduce, threading.current_thread().name,start_time, end_time, format_time(start_time), format_time(end_time), elapsed_time]

    try:
        introduce, start_time, end_time, elapsed_time = result[1], result[5], result[6], result[7]
        cursor.execute("""
            UPDATE sc_pub_recruitmentnet_job SET 
                job_description_detail = %s,
                process_start_time = %s,
                process_end_time = %s,
                time_consume = %s,
                process_type = '1'
            WHERE id = %s
        """, (introduce, start_time, end_time, elapsed_time, id))
        connection.commit()
        logging.info(f"线程:{threading.current_thread().name}已更新 id：{id}...耗时：{elapsed_time}")
    except Exception as e:
        logging.error(f"Error updating database for ID {id}: {e}")
        connection.rollback()
    finally:
        close_db_connection(cursor, connection)

def worker_thread(lock, batch_size=100):
    while True:
        with lock:
            rows = fetch_unprocessed_data_from_db(batch_size)
        if not rows:
            break  # 没有更多数据了，退出循环
        logging.info(f"线程:{threading.current_thread().name}正在处理 {len(rows)} 条数据...")
        for row in rows:
            id = row[0]  # 第一个字段是 id
            info = row[1]  # 第二个字段是 processed_info
            call_data = {'id': id, 'info': info}
            try:
                user_id = threading.current_thread().name + str(random.randint(1_000_000, 9_999_999))
                AppConversationID = getApplicationId(user_id)
                # AppConversationID = getApplicationId(threadName)
                result = api_call(call_data, AppConversationID, lock, user_id, 0)
                update_result_in_db(id, result)  # 将结果写回数据库
            except Exception as e:
                logging.error(f"Error processing ID {id}: {e}")
                # 可以在这里选择重新放回未处理状态或跳过

def start_processing_with_threads(num_threads=20, batch_size=10):
    lock = threading.Lock()
    threads = []

    for i in range(num_threads):
        thread = threading.Thread(target=worker_thread, args=(lock, batch_size), name=f"Worker-{i+1}")
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

    print("All data has been processed.")


from concurrent.futures import ThreadPoolExecutor, as_completed


def start_with_restarting_pool(num_threads=20, max_retries=5, batch_size=10):
    lock = threading.Lock()

    def run_task(retry_count=0):
        if retry_count > max_retries:
            logging.warning("超过最大重试次数，放弃任务")
            return
        try:
            worker_thread(lock, batch_size)
        except Exception as e:
            logging.error(f"任务失败，第 {retry_count} 次重试: {e}")
            run_task(retry_count + 1)

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(run_task, 0) for _ in range(num_threads)]

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logging.error(f"任务执行失败: {e}")

if __name__ == "__main__":
    # clean_job_data()
    # process_jobs()
    process_sc_jobs()
    # process_job_excel()
    # output_dir = 'D:/数字政务/人岗匹配/一句话简历数据/处理数据/线程文件/job13000'  # 输出目录
    # job_main(output_dir)

    # update_job_main()

    # num_threads = 20
    # batch_size = 10
    # max_retries = 5
    # start_with_restarting_pool(num_threads=num_threads, max_retries=5, batch_size=batch_size)

    # json_str = '{"user": {"name": "罗先生", "genderLabel": "男", "email": "", "age": 29, "ageLabel": "29岁", "maxEducationLabel": "硕士", "workYears": 5, "workYearsLabel": "4年", "cityLabel": "现居成都 成华区", "phone": "180****1345"}, "resume": {"skillTags": ["人力资源管理师", "b1"], "educationExperiences": [{"schoolName": "杜伦大学", "beginTime": 1567267200000, "endTime": 1609430400000, "educationTimeLabel": "2019.09 - 2021.01", "major": "会计学", "educationLabel": "硕士"}, {"schoolName": "杜伦大学", "beginTime": 1546272000000, "endTime": 1609430400000, "educationTimeLabel": "2019.01 - 2021.01", "major": "会计学", "educationLabel": "硕士"}, {"schoolName": "赫尔大学", "beginTime": 1501516800000, "endTime": 1559318400000, "educationTimeLabel": "2017.08 - 2019.06", "major": "会计学(2+2)", "educationLabel": "本科"}, {"schoolName": "赫尔大学", "beginTime": 1483200000000, "endTime": 1546272000000, "educationTimeLabel": "2017.01 - 2019.01", "major": "会计学", "educationLabel": "本科"}, {"schoolName": "上海外国语大学", "beginTime": 1441036800000, "endTime": 1496246400000, "educationTimeLabel": "2015.09 - 2017.06", "major": "工商管理(2+2)", "educationLabel": "本科"}, {"schoolName": "上海外国语大学", "beginTime": 1420041600000, "endTime": 1483200000000, "educationTimeLabel": "2015.01 - 2017.01", "major": "工商管理", "educationLabel": "本科"}], "workExperiences": [{"orgName": "领展商业管理（上海）有限公司", "description": "七宝领展广场 \n项目总经理助理 兼项目采购经理\n主要工作贡献：\n\n1、协助项目总安排项目内外部各项重要会议，下达项目总指示，统筹协调项目内各业务及职能部门负责人之间的配合。\n2、对项目总的审批文件、流程等项目内部管理工作，进行预先审批。\n3、负责对接领展中国大陆区域中心资管及管理层对项目的重点工作事项进度跟进、复盘、及汇报。\n4、作为项目采购，除对接香港总部采购总监下达的各项要求外，主要对项目各项采购流程进行把控，包括供应商资源整合维护，资质查验，价格谈判，在保证业务效率及品质呈现的条件下，对项目支出成本进行控制，提升项目年底NOI指标达成率。", "jobTitle": "物业招商管理", "timeLabel": "2024.06 - 2024.12 (6个月)", "workSkillTags": [{"name": "休闲娱乐招商"}, {"name": "餐饮业态招商"}, {"name": "商业地产"}]}, {"orgName": "上海印力企业管理有限公司", "description": "印力上海平台目标管理部 资产管理岗位（轮岗）\n主要工作贡献:1、协助总部梳理城市公司系统流程节点并统计公示; 协调平台、总部、股东方及项目管理团队间的事项沟通; \n2、负责22年城市公司八大战役进度及城市公司流程管理节点梳理并公示; \n3、协助部门负责人完成《城市公司验收管理办法》、《筹开项目全周期计划节点》制定工作。 \n\n上海七宝万科广场\n项目总经理助理 兼项目招商 （定岗）\n主要工作贡献: \n1、统筹平台及总部给项目下达的各项工作报告制作及项目内部重大会议安排; \n2、负责股东方领展对项目的业务审批，并依照资管协议对项目运营情况对股东进行汇报; \n3、参与七宝万科广场B1层新鲜市区域改造焕新开业，销售业绩及租金提升显著300%; \n4、22年上海封闭两个月，所负责的B1层减租租户数仅占楼层总数一半，减租金额仅占全场30%。", "jobTitle": "物业招商管理", "timeLabel": "2022.01 - 2024.05 (2年 4个月)", "workSkillTags": [{"name": "休闲娱乐招商"}, {"name": "餐饮业态招商"}, {"name": "商业地产"}]}, {"orgName": "上海西岸印力商业管理有限公司", "description": "上海西岸凤巢 AI PLAZA 项目招商 （轮岗）\n主要工作贡献: \n1、参与上海龙华会前期商业定位规划，并协助资管完成该项目轻资产运营管理协议内，股东方对项目管理权限划分、业绩指标等条款拟定；2、深度参与AI PLAZA 项目筹开，负责项目筹开招商进度统筹、印资管系统合同管理等工作; \n3、协调业主方签约项目娱乐体验业态主力店-三体沉浸式体验剧场。", "jobTitle": "物业招商管理", "timeLabel": "2021.04 - 2021.12 (8个月)", "workSkillTags": [{"name": "餐饮业态招商"}, {"name": "商业地产"}, {"name": "休闲娱乐招商"}]}, {"orgName": "印力商用置业有限公司", "description": "2022.6-2024.5上海七宝万科广场项目总经理助理 兼项目招商 (定岗)主要工作贡献:1、统筹平台及总部给项目下达的各项工作报告制作及项目内部重大会议安排;2、负责股东方领展对项目的业务审批,并依照资管协议对项目运营情况对股东进行汇报;3、参与七宝万科广场B1层新鲜市区域改造焕新开业,销售业绩及租金提升显著300%;4、22年上海封闭两个月,所负责的B1层减租租户数仅占楼层总数一半,减租金额仅占全场30%。2022.1-2022.8印力上海平台目标管理部 资产管理岗位(轮岗)主要工作贡献: 1、协助总部梳理城市公司系统流程节点并统计公示; 协调平台、总部、股东方及项目管理团队间的事项沟通;2、负责22年城市公司八大战役进度及城市公司流程管理节点梳理并公示;3、协助部门负责人完成《城市公司验收管理办法》、《筹开项目全周期计划节点》制定工作。2021.4-2021.12上海西岸凤巢 AI PLAZA 项目招商 (轮岗)主要工作贡献:1、参与上海龙华会前期商业定位规划,并协助资管完成该项目轻资产运营管理协议内,股东方对项目管理权限划分、业绩指标等条款拟定; 2、深度参与AI PLAZA 项目筹开,负责项目筹开招商进度统筹、印资管系统合同管理等工作;3、协调业主方签约项目娱乐体验业态主力店-三体沉浸式体验剧场。", "jobTitle": "地产招商", "timeLabel": "2021.04 - 2024.05 (3年 1个月)", "workSkillTags": [{"name": "商业地产"}, {"name": "投资拓展"}]}, {"orgName": "Target English International", "description": "Main Duties and Responsibilities\n- Assist with the planning, preparation, and organisation of activities under the guidance of the Activity Manager\n- Actively advertise, promote and explain the activity programme to students and their group leaders\n- Lead excursions to tourist destinations either alone or as part of a team\n- Conduct interactive walking tours around cities (information provided)\n- Enthusiastically participate in activities and excursions in order to encourage student participation\n- Engage with and motivate students during activities and excursions, in order to foster positive learning outcomes and use of English\n- Utilise the Activity Books and actively promote the use of them whilst on excursions\n- Set up, monitor and report back on the excursion tasks that students are required to undertake\n- Read and understand risk assessments for all sports, activities and excursions\n- Record attendance on trips and excursions", "jobTitle": "Activity Leader", "timeLabel": "2018.06 - 2018.08 (1个月)", "workSkillTags": [{"name": "培训项目管理"}, {"name": "户外培训策划"}, {"name": "职业培训策划"}]}], "projectExperiences": [{"name": "University Business Challenge", "beginTime": 1509465600000, "endTime": 1522512000000, "timeLabel": "2017.11 - 2018.04 (5个月)", "description": "The UBC is one of the most recognised global simulation-based competitive challenges.  It could improve knowledge of the business world, put theory into practice and develop team-working, leadership employability and entrepreneurial skills by participating in a team-based competitive challenge. And could also contribute to could also contribute to candidates’ understanding of how businesses work, develop their decision-making skills, their team-working abilities and increase their knowledge in key business areas such as marketing, finance, strategy, production, pricing and HR.\nI was participating in this challenge within a team, as a finance specialist member, I use my accounting knowledge for my team to set up financial target and corporate with other member with key business knowledge such marketing, business strategy, and HR. During this challenge I learned how to apply business theory, gleaned from lectures, to the corporate world, and developed team-working, leadership, and entrepreneurial skills.", "responsibility": ""}], "languageSkills": [{"name": "英语", "readWriteSkill": "熟练", "hearSpeakSkill": "精通"}], "certificates": [{"name": "雅思7.0分"}, {"name": "ACCA通过部分科目"}, {"name": "C1驾驶证"}], "purposes": [{"industryLabel": "证券/期货、咨询服务、财务/审计/税务", "jobTypeLabel": "物业招商管理", "jobNatureLabel": "全职", "location": "成都", "salaryLabel": "1万-1.5万/月"}, {"industryLabel": "不限行业", "jobTypeLabel": "事业单位人员", "jobNatureLabel": "全职", "location": "成都", "salaryLabel": "8千-1.6万/月"}, {"industryLabel": "不限行业", "jobTypeLabel": "储备经理人", "jobNatureLabel": "全职", "location": "成都", "salaryLabel": "8千-1.6万/月"}]}}'
    # json_str = json_str.encode('utf-8', errors='ignore').decode('utf-8')
    # json.dumps(json_str)
    # json_data = json.loads(json_str)