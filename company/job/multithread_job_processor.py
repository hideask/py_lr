#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智联招聘岗位信息多线程处理器

本脚本用于从PostgreSQL数据库查询智联招聘岗位数据，
调用Coze v2接口进行处理，并更新结果到数据库。

功能特性:
- 多线程并发处理
- Bot ID轮询调用
- 自动重试机制
- 详细日志记录
- 数据库事务管理
"""

import json
import logging
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any

import requests
from db_connection import get_db_connection, close_db_connection


class JobProcessorConfig:
    """处理器配置类"""
    
    def __init__(self):
        # Bot IDs 轮询列表
        self.bot_ids = [
            '7522851405448265762',
            '7522871546680000552', 
            '7522873384196587558',
            '7522870753600716850',
            '7522874567711621160',
            '7522873474025947179'
        ]
        
        # Coze API配置
        self.coze_api_url = 'https://api.coze.cn/open_api/v2/chat'
        self.coze_token = 'Bearer pat_Gg8YY6O4kYqiZiFOU20ZwvTLlIh8c6IdtDW2F2n20rfPexIXdgcBVnVTk4hOQCP0'
        
        # 处理配置
        self.batch_size = 10
        self.max_workers = 20
        self.max_retries = 5
        self.request_timeout = 30
        
        # 数据库配置
        self.table_name = 'zhilian_job'
        self.train_type = '3'


class JobProcessor:
    """智联招聘岗位信息处理器"""
    
    def __init__(self, config: Optional[JobProcessorConfig] = None):
        self.config = config or JobProcessorConfig()
        self.bot_id_index = 0
        self.bot_id_lock = threading.Lock()
        self.setup_logging()
    
    def setup_logging(self):
        """设置日志配置"""
        self.logger = logging.getLogger('JobProcessor')
        self.logger.setLevel(logging.INFO)
        
        # 避免重复添加handler
        if not self.logger.handlers:
            # 文件handler
            file_handler = logging.FileHandler('job_processor.log', encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            
            # 控制台handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter(
                '%(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def get_next_bot_id(self) -> str:
        """轮询获取下一个bot_id"""
        with self.bot_id_lock:
            current_bot_id = self.config.bot_ids[self.bot_id_index]
            self.bot_id_index = (self.bot_id_index + 1) % len(self.config.bot_ids)
            return current_bot_id
    
    def generate_random_ids(self, thread_name: str) -> Tuple[str, str]:
        """生成随机的用户ID和对话ID"""
        user_id = f"{thread_name}_{random.randint(1_000_000, 9_999_999)}"
        conversation_id = str(random.randint(10_000_000_000, 99_999_999_999))
        return user_id, conversation_id
    
    def call_coze_api(self, processed_info: str, bot_id: str, user_id: str, conversation_id: str) -> Tuple[str, bool]:
        """调用Coze API
        
        Args:
            processed_info: 处理的信息内容
            bot_id: Bot ID
            user_id: 用户ID
            conversation_id: 对话ID
            
        Returns:
            Tuple[str, bool]: (响应内容, 是否成功)
        """
        headers = {
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Accept": "*/*",
            "Authorization": self.config.coze_token,
            "Host": "api.coze.cn",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }
        
        data = {
            "conversation_id": conversation_id,
            "bot_id": bot_id,
            "user": user_id,
            "query": processed_info,
            "stream": False,
            "custom_variables": {}
        }
        
        try:
            response = requests.post(
                self.config.coze_api_url,
                json=data,
                headers=headers,
                timeout=self.config.request_timeout
            )
            
            if response.status_code == 200:
                response_json = response.json()
                
                # 提取content内容
                if 'messages' in response_json:
                    messages = response_json['messages']
                    content_parts = []
                    
                    for message in messages:
                        if message.get('type') == 'answer' and 'content' in message:
                            content_parts.append(message['content'])
                    
                    if content_parts:
                        return ''.join(content_parts), True
                    else:
                        self.logger.warning("未找到有效的answer内容")
                        return "无有效内容", False
                else:
                    self.logger.warning("响应中没有找到messages字段")
                    return "响应格式错误", False
            else:
                self.logger.error(f"API调用失败: {response.status_code}, {response.text}")
                return f"API调用失败: {response.status_code}", False
                
        except requests.exceptions.Timeout:
            self.logger.error("API调用超时")
            return "API调用超时", False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API调用异常: {str(e)}")
            return f"API调用异常: {str(e)}", False
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON解析失败: {str(e)}")
            return "JSON解析失败", False
        except Exception as e:
            self.logger.error(f"处理响应时出错: {str(e)}")
            return f"处理响应时出错: {str(e)}", False
    
    def fetch_unprocessed_data(self, batch_size: int) -> List[Tuple[int, str]]:
        """从数据库获取未处理的数据
        
        Args:
            batch_size: 批次大小
            
        Returns:
            List[Tuple[int, str]]: [(id, processed_info), ...]
        """
        connection = get_db_connection()
        cursor = connection.cursor()
        
        try:
            # 查询未处理的数据并标记为正在处理
            query = f"""
                SELECT id, processed_info 
                FROM {self.config.table_name} 
                WHERE train_type = %s 
                  AND job_description_detail IS NULL 
                  AND process_type IS NULL
                ORDER BY id 
                LIMIT %s 
                FOR UPDATE SKIP LOCKED
            """
            
            cursor.execute(query, (self.config.train_type, batch_size))
            rows = cursor.fetchall()
            
            if rows:
                ids = [row[0] for row in rows]
                # 标记这些数据为正在处理
                update_query = f"""
                    UPDATE {self.config.table_name} 
                    SET process_type = %s 
                    WHERE id = ANY(%s)
                """
                cursor.execute(update_query, (threading.current_thread().name, ids))
                connection.commit()
                
                self.logger.info(f"线程 {threading.current_thread().name} 获取到 {len(rows)} 条待处理数据")
            
            return rows
            
        except Exception as e:
            self.logger.error(f"获取数据库数据失败: {str(e)}")
            connection.rollback()
            return []
        finally:
            close_db_connection(cursor, connection)
    
    def update_result_to_db(self, record_id: int, job_description_detail: str, 
                           bot_id: str, start_time: str, end_time: str, 
                           elapsed_time: float, success: bool) -> bool:
        """更新处理结果到数据库
        
        Args:
            record_id: 记录ID
            job_description_detail: 处理结果
            bot_id: 使用的Bot ID
            start_time: 开始时间
            end_time: 结束时间
            elapsed_time: 耗时(秒)
            success: 是否成功
            
        Returns:
            bool: 更新是否成功
        """
        connection = get_db_connection()
        cursor = connection.cursor()
        
        try:
            process_type = '2' if success else '3'  # 2=成功, 3=失败
            
            update_query = f"""
                UPDATE {self.config.table_name} 
                SET job_description_detail = %s,
                    process_type = %s,
                    bot_id = %s,
                    process_start_time = %s,
                    process_end_time = %s,
                    time_consume = %s
                WHERE id = %s
            """
            
            cursor.execute(update_query, (
                job_description_detail,
                process_type,
                bot_id,
                start_time,
                end_time,
                elapsed_time,
                record_id
            ))
            
            connection.commit()
            
            status = "成功" if success else "失败"
            self.logger.info(
                f"线程 {threading.current_thread().name} 更新记录 {record_id} {status}, "
                f"耗时: {elapsed_time:.2f}s, Bot ID: {bot_id}"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"更新数据库失败 (ID: {record_id}): {str(e)}")
            connection.rollback()
            return False
        finally:
            close_db_connection(cursor, connection)
    
    def format_timestamp(self, timestamp: float) -> str:
        """格式化时间戳"""
        dt = datetime.fromtimestamp(timestamp)
        millis = int((timestamp - int(timestamp)) * 1000)
        return dt.strftime(f"%Y-%m-%d %H:%M:%S.{millis:03d}")
    
    def process_single_record(self, record_id: int, processed_info: str) -> bool:
        """处理单条记录
        
        Args:
            record_id: 记录ID
            processed_info: 处理信息
            
        Returns:
            bool: 处理是否成功
        """
        start_time = time.time()
        thread_name = threading.current_thread().name
        
        # 获取Bot ID和生成随机ID
        bot_id = self.get_next_bot_id()
        user_id, conversation_id = self.generate_random_ids(thread_name)
        
        self.logger.info(f"线程 {thread_name} 开始处理记录 {record_id}, Bot ID: {bot_id}")
        
        # 调用API
        job_description_detail, success = self.call_coze_api(
            processed_info, bot_id, user_id, conversation_id
        )
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # 格式化时间
        start_time_str = self.format_timestamp(start_time)
        end_time_str = self.format_timestamp(end_time)
        
        # 更新数据库
        update_success = self.update_result_to_db(
            record_id, job_description_detail, bot_id,
            start_time_str, end_time_str, elapsed_time, success
        )
        
        return success and update_success
    
    def worker_thread(self, lock: threading.Lock) -> None:
        """工作线程函数
        
        Args:
            lock: 线程锁
        """
        thread_name = threading.current_thread().name
        processed_count = 0
        
        while True:
            # 获取数据需要加锁
            with lock:
                rows = self.fetch_unprocessed_data(self.config.batch_size)
            
            if not rows:
                self.logger.info(f"线程 {thread_name} 没有更多数据，退出")
                break
            
            # 处理每条记录
            for record_id, processed_info in rows:
                try:
                    success = self.process_single_record(record_id, processed_info)
                    if success:
                        processed_count += 1
                    
                    # 每处理10条记录输出一次统计
                    if processed_count % 10 == 0 and processed_count > 0:
                        self.logger.info(f"线程 {thread_name} 已成功处理 {processed_count} 条记录")
                        
                except Exception as e:
                    self.logger.error(f"线程 {thread_name} 处理记录 {record_id} 时出错: {str(e)}")
        
        self.logger.info(f"线程 {thread_name} 完成，共处理 {processed_count} 条记录")
    
    def start_processing(self) -> None:
        """开始多线程处理"""
        self.logger.info(f"开始多线程处理，线程数: {self.config.max_workers}, 批次大小: {self.config.batch_size}")
        
        lock = threading.Lock()
        
        def run_task_with_retry(retry_count: int = 0) -> None:
            """带重试的任务执行"""
            if retry_count > self.config.max_retries:
                self.logger.warning(f"超过最大重试次数 ({self.config.max_retries})，放弃任务")
                return
            
            try:
                self.worker_thread(lock)
            except Exception as e:
                self.logger.error(f"任务失败，第 {retry_count} 次重试: {str(e)}")
                run_task_with_retry(retry_count + 1)
        
        # 使用线程池执行任务
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            futures = [executor.submit(run_task_with_retry, 0) for _ in range(self.config.max_workers)]
            
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    self.logger.error(f"任务执行失败: {str(e)}")
        
        self.logger.info("所有数据处理完成")
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        connection = get_db_connection()
        cursor = connection.cursor()
        
        try:
            # 总记录数
            cursor.execute(f"""
                SELECT COUNT(*) FROM {self.config.table_name} 
                WHERE train_type = %s
            """, (self.config.train_type,))
            total_count = cursor.fetchone()[0]
            
            # 待处理记录数
            cursor.execute(f"""
                SELECT COUNT(*) FROM {self.config.table_name} 
                WHERE train_type = %s 
                  AND job_description_detail IS NULL 
                  AND process_type IS NULL
            """, (self.config.train_type,))
            pending_count = cursor.fetchone()[0]
            
            # 已处理记录数
            cursor.execute(f"""
                SELECT COUNT(*) FROM {self.config.table_name} 
                WHERE train_type = %s 
                  AND job_description_detail IS NOT NULL
            """, (self.config.train_type,))
            processed_count = cursor.fetchone()[0]
            
            # 处理失败记录数
            cursor.execute(f"""
                SELECT COUNT(*) FROM {self.config.table_name} 
                WHERE train_type = %s 
                  AND process_type = '3'
            """, (self.config.train_type,))
            failed_count = cursor.fetchone()[0]
            
            return {
                'total_count': total_count,
                'pending_count': pending_count,
                'processed_count': processed_count,
                'failed_count': failed_count,
                'success_rate': (processed_count / total_count * 100) if total_count > 0 else 0
            }
            
        except Exception as e:
            self.logger.error(f"获取统计信息失败: {str(e)}")
            return {}
        finally:
            close_db_connection(cursor, connection)


def main():
    """主函数"""
    # 创建配置
    config = JobProcessorConfig()
    
    # 可以根据需要调整配置
    config.max_workers = 30  # 线程数
    config.batch_size = 10   # 批次大小
    config.max_retries = 5   # 最大重试次数
    
    # 创建处理器
    processor = JobProcessor(config)
    
    # 显示处理前统计信息
    stats = processor.get_processing_stats()
    if stats:
        processor.logger.info(f"处理前统计: 总计 {stats['total_count']} 条, "
                            f"待处理 {stats['pending_count']} 条, "
                            f"已处理 {stats['processed_count']} 条, "
                            f"失败 {stats['failed_count']} 条")
    
    # 开始处理
    start_time = time.time()
    processor.start_processing()
    end_time = time.time()
    
    # 显示处理后统计信息
    stats = processor.get_processing_stats()
    if stats:
        processor.logger.info(f"处理后统计: 总计 {stats['total_count']} 条, "
                            f"待处理 {stats['pending_count']} 条, "
                            f"已处理 {stats['processed_count']} 条, "
                            f"失败 {stats['failed_count']} 条, "
                            f"成功率 {stats['success_rate']:.2f}%")
    
    total_time = end_time - start_time
    processor.logger.info(f"总处理时间: {total_time:.2f} 秒")


if __name__ == "__main__":
    main()