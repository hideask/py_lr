import pandas as pd
import os
import requests
import json
import threading
import logging
import time
import random
import uuid
import psycopg2
from db_connection import get_db_connection, close_db_connection
from datetime import datetime

# 创建 logger 对象
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 创建一个用于写入文件的 handler
file_handler = logging.FileHandler('job_analysis.log')
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# 创建一个用于输出到控制台的 handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

# 将两个 handler 添加到 logger 中
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Coze API配置
COZE_BOT_ID = '7522477054722572288'
COZE_API_URL = 'https://api.coze.cn/open_api/v2/chat'
COZE_HEADERS = {
    "Content-Type": "application/json",
    "Connection": "keep-alive",
    "Accept": "*/*",
    "Authorization": "Bearer pat_Gg8YY6O4kYqiZiFOU20ZwvTLlIh8c6IdtDW2F2n20rfPexIXdgcBVnVTk4hOQCP0",
    "Host": "api.coze.cn",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

def format_time(timestamp):
    """格式化时间戳"""
    dt = datetime.fromtimestamp(timestamp)
    millis = int((timestamp - int(timestamp)) * 1000)
    return dt.strftime(f"%Y-%m-%d %H:%M:%S.{millis:03d}")

def generate_conversation_id():
    """生成随机的conversation_id"""
    return str(uuid.uuid4())

def generate_user_id(thread_name):
    """生成随机的user_id"""
    return thread_name + str(random.randint(1_000_000, 9_999_999))

def extract_job_summary(processed_info):
    """从processed_info JSON中提取jobSummary"""
    try:
        if isinstance(processed_info, str):
            data = json.loads(processed_info)
        else:
            data = processed_info
        
        job_summary = data.get('jobSummary', '')
        return job_summary
    except (json.JSONDecodeError, AttributeError, TypeError) as e:
        logging.error(f"解析processed_info失败: {e}")
        return ''

def call_coze_api(job_summary, conversation_id, user_id):
    """调用Coze API处理jobSummary数据"""
    start_time = time.time()
    
    data = {
        "conversation_id": conversation_id,
        "bot_id": COZE_BOT_ID,
        "user": user_id,
        "query": job_summary,
        "stream": False,
        "custom_variables": {}
    }
    
    try:
        response = requests.post(COZE_API_URL, json=data, headers=COZE_HEADERS)
        
        if response.status_code == 200:
            try:
                response_json = response.json()
                
                # 提取content内容
                if 'messages' in response_json:
                    messages = response_json['messages']
                    content_parts = []
                    
                    for message in messages:
                        if message.get('type') == 'answer' and 'content' in message:
                            content_parts.append(message['content'])
                    
                    if content_parts:
                        result = ''.join(content_parts)
                    else:
                        logging.warning("未找到有效的answer内容")
                        result = '无'
                else:
                    logging.warning("响应中没有找到messages字段")
                    result = '无'
                    
            except json.JSONDecodeError as e:
                logging.error(f"JSON解析失败: {e}")
                result = '无'
        else:
            logging.error(f'API调用失败: {response.status_code} - {response.text}')
            result = '无'
            
    except Exception as e:
        logging.error(f'API调用异常: {e}')
        result = '无'
    
    end_time = time.time()
    elapsed_time = round(end_time - start_time, 2)
    
    return {
        'result': result,
        'start_time': format_time(start_time),
        'end_time': format_time(end_time),
        'elapsed_time': elapsed_time
    }

def fetch_job_data_from_db(batch_size=100):
    """从数据库获取岗位数据"""
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        # 查询未处理的岗位数据并标记为正在处理
        cursor.execute("""
            SELECT id, processed_info FROM zhilian_job
            WHERE train_type = '3'
            AND processed_jobsummary IS NULL
            AND process_type IS NULL
            ORDER BY id LIMIT %s FOR UPDATE SKIP LOCKED
        """, (batch_size,))

        
        rows = cursor.fetchall()
        
        if rows:
            ids = [row[0] for row in rows]
            # 标记这些数据为正在处理
            cursor.execute("""
                UPDATE zhilian_job SET process_type = %s 
                WHERE id = ANY(%s)
            """, (threading.current_thread().name, ids))
            connection.commit()
            
        return rows
        
    except Exception as e:
        logging.error(f"从数据库获取数据失败: {e}")
        connection.rollback()
        return []
    finally:
        close_db_connection(cursor, connection)

def update_job_result_in_db(job_id, api_result):
    """更新处理结果到数据库"""
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("""
            UPDATE zhilian_job SET 
                processed_jobsummary = %s,
                process_start_time = %s,
                process_end_time = %s,
                time_consume = %s,
                bot_id = %s,
                process_type = '3'
            WHERE id = %s
        """, (
            api_result['result'],
            api_result['start_time'],
            api_result['end_time'],
            api_result['elapsed_time'],
            COZE_BOT_ID,
            job_id
        ))
        
        connection.commit()
        logging.info(f"线程:{threading.current_thread().name}已更新岗位ID：{job_id}...耗时：{api_result['elapsed_time']}秒")
        
    except Exception as e:
        logging.error(f"更新数据库失败，岗位ID {job_id}: {e}")
        connection.rollback()
    finally:
        close_db_connection(cursor, connection)

def worker_thread(lock, batch_size=50):
    """工作线程函数"""
    thread_name = threading.current_thread().name
    
    while True:
        with lock:
            rows = fetch_job_data_from_db(batch_size)
        
        if not rows:
            logging.info(f"线程 {thread_name} 没有更多数据，退出")
            break
        
        logging.info(f"线程 {thread_name} 正在处理 {len(rows)} 条岗位数据...")
        
        for row in rows:
            job_id = row[0]
            processed_info = row[1]
            
            try:
                # 提取jobSummary
                job_summary = extract_job_summary(processed_info)
                
                if not job_summary:
                    logging.warning(f"岗位ID {job_id} 的jobSummary为空，跳过处理")
                    continue
                
                # 生成随机ID
                conversation_id = generate_conversation_id()
                user_id = generate_user_id(thread_name)
                
                # 调用Coze API
                api_result = call_coze_api(job_summary, conversation_id, user_id)
                
                # 更新数据库
                update_job_result_in_db(job_id, api_result)
                
            except Exception as e:
                logging.error(f"处理岗位ID {job_id} 时出错: {e}")
                # 可以选择将错误状态写回数据库
                try:
                    connection = get_db_connection()
                    cursor = connection.cursor()
                    cursor.execute("""
                        UPDATE zhilian_job SET 
                            processed_jobsummary = %s,
                            process_type = 'error'
                        WHERE id = %s
                    """, (f"处理出错: {str(e)}", job_id))
                    connection.commit()
                    close_db_connection(cursor, connection)
                except Exception as db_error:
                    logging.error(f"更新错误状态失败: {db_error}")

def start_job_processing(num_threads=10, batch_size=50):
    """启动多线程处理岗位数据"""
    lock = threading.Lock()
    threads = []
    
    logging.info(f"启动 {num_threads} 个线程处理岗位数据，每批处理 {batch_size} 条")
    
    for i in range(num_threads):
        thread = threading.Thread(
            target=worker_thread, 
            args=(lock, batch_size), 
            name=f"JobWorker-{i+1}"
        )
        threads.append(thread)
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    logging.info("所有岗位数据处理完成")

if __name__ == "__main__":
    # 配置参数
    num_threads = 40  # 线程数量
    batch_size = 10  # 每批处理的数据量
    
    start_job_processing(num_threads=num_threads, batch_size=batch_size)