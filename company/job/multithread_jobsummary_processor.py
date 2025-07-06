#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多线程处理智联招聘数据 - 将processed_jobsummary替换到processed_info的jobSummary中

功能说明:
1. 从PostgreSQL数据库查询train_type='3'的智联招聘数据
2. 将processed_jobsummary字段的值替换到processed_info JSON中的jobSummary字段
3. 使用多线程并发处理，提高处理效率
4. 支持批量更新数据库
"""

import json
import psycopg2
import threading
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from db_connection import DatabaseConnection

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jobsummary_processor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class ProcessConfig:
    """处理配置类"""
    batch_size: int = 100  # 每批处理的记录数
    max_workers: int = 8   # 最大线程数
    train_type: str = '3'  # 训练类型
    table_name: str = 'zhilian_job'  # 表名
    

class JobSummaryProcessor:
    """智联招聘jobSummary处理器"""
    
    def __init__(self, db_config: Optional[Dict[str, str]] = None):
        """
        初始化处理器
        
        Args:
            db_config: 数据库配置，如果为None则使用默认配置
        """
        if db_config:
            self.db_connection = DatabaseConnection(**db_config)
        else:
            self.db_connection = DatabaseConnection()
        
        self._lock = threading.Lock()
        self.processed_count = 0
        self.error_count = 0
        
    def get_connection(self):
        """获取数据库连接"""
        return self.db_connection.get_connection()
    
    def fetch_data_to_process(self, config: ProcessConfig) -> List[Tuple[int, str, str]]:
        """
        获取需要处理的数据
        
        Args:
            config: 处理配置
            
        Returns:
            List[Tuple[int, str, str]]: (id, processed_info, processed_jobsummary)的列表
        """
        connection = None
        cursor = None
        data = []
        
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            # 查询需要处理的数据
            sql = f"""
                SELECT id, processed_info, processed_jobsummary 
                FROM {config.table_name} 
                WHERE train_type = %s 
                AND processed_info IS NOT NULL 
                AND processed_jobsummary IS NOT NULL
                AND processed_jobsummary != ''
                ORDER BY id
            """
            
            cursor.execute(sql, (config.train_type,))
            data = cursor.fetchall()
            
            logger.info(f"查询到 {len(data)} 条需要处理的记录")
            
        except Exception as e:
            logger.error(f"查询数据时出错: {str(e)}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
                
        return data
    
    def process_single_record(self, record_data: Tuple[int, str, str]) -> Optional[Tuple[int, str]]:
        """
        处理单条记录
        
        Args:
            record_data: (id, processed_info, processed_jobsummary)
            
        Returns:
            Optional[Tuple[int, str]]: (id, updated_processed_info) 或 None（如果处理失败）
        """
        try:
            record_id, processed_info, processed_jobsummary = record_data
            
            # 解析processed_info JSON
            if isinstance(processed_info, str):
                info_data = json.loads(processed_info)
            else:
                info_data = processed_info
            
            # 将processed_jobsummary替换到jobSummary字段
            info_data['jobSummary'] = processed_jobsummary
            
            # 转换回JSON字符串
            updated_info = json.dumps(info_data, ensure_ascii=False, indent=2)
            
            with self._lock:
                self.processed_count += 1
                if self.processed_count % 100 == 0:
                    logger.info(f"已处理 {self.processed_count} 条记录")
            
            return (record_id, updated_info)
            
        except Exception as e:
            with self._lock:
                self.error_count += 1
            logger.error(f"处理记录 {record_data[0] if record_data else 'unknown'} 时出错: {str(e)}")
            return None
    
    def batch_update_database(self, results: List[Tuple[int, str]], config: ProcessConfig) -> int:
        """
        批量更新数据库
        
        Args:
            results: 处理结果列表 [(id, updated_processed_info), ...]
            config: 处理配置
            
        Returns:
            int: 成功更新的记录数
        """
        if not results:
            return 0
            
        connection = None
        cursor = None
        updated_count = 0
        
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            # 批量更新SQL
            update_sql = f"""
                UPDATE {config.table_name} 
                SET processed_info = %s
                WHERE id = %s
            """
            
            # 执行批量更新
            for record_id, updated_info in results:
                cursor.execute(update_sql, (updated_info, record_id))
                updated_count += 1
            
            connection.commit()
            logger.info(f"批量更新 {updated_count} 条记录成功")
            
        except Exception as e:
            logger.error(f"批量更新数据库时出错: {str(e)}")
            if connection:
                connection.rollback()
            updated_count = 0
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
                
        return updated_count
    
    def process_data_multithread(self, config: ProcessConfig) -> Dict[str, int]:
        """
        多线程处理数据
        
        Args:
            config: 处理配置
            
        Returns:
            Dict[str, int]: 处理统计信息
        """
        start_time = datetime.now()
        logger.info(f"开始多线程处理，配置: 批次大小={config.batch_size}, 最大线程数={config.max_workers}")
        
        # 获取需要处理的数据
        data_to_process = self.fetch_data_to_process(config)
        
        if not data_to_process:
            logger.info("没有需要处理的数据")
            return {'total': 0, 'processed': 0, 'updated': 0, 'errors': 0}
        
        total_records = len(data_to_process)
        total_updated = 0
        
        # 分批处理
        for i in range(0, total_records, config.batch_size):
            batch_data = data_to_process[i:i + config.batch_size]
            batch_num = i // config.batch_size + 1
            
            logger.info(f"处理第 {batch_num} 批，共 {len(batch_data)} 条记录")
            
            # 多线程处理当前批次
            batch_results = []
            with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
                # 提交任务
                future_to_record = {
                    executor.submit(self.process_single_record, record): record 
                    for record in batch_data
                }
                
                # 收集结果
                for future in as_completed(future_to_record):
                    result = future.result()
                    if result:
                        batch_results.append(result)
            
            # 批量更新数据库
            if batch_results:
                updated_count = self.batch_update_database(batch_results, config)
                total_updated += updated_count
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 统计信息
        stats = {
            'total': total_records,
            'processed': self.processed_count,
            'updated': total_updated,
            'errors': self.error_count,
            'duration_seconds': duration
        }
        
        logger.info(f"处理完成！统计信息: {stats}")
        return stats
    
    def process_data_single_thread(self, config: ProcessConfig) -> Dict[str, int]:
        """
        单线程处理数据（用于对比测试）
        
        Args:
            config: 处理配置
            
        Returns:
            Dict[str, int]: 处理统计信息
        """
        start_time = datetime.now()
        logger.info("开始单线程处理")
        
        # 获取需要处理的数据
        data_to_process = self.fetch_data_to_process(config)
        
        if not data_to_process:
            logger.info("没有需要处理的数据")
            return {'total': 0, 'processed': 0, 'updated': 0, 'errors': 0}
        
        total_records = len(data_to_process)
        total_updated = 0
        
        # 分批处理
        for i in range(0, total_records, config.batch_size):
            batch_data = data_to_process[i:i + config.batch_size]
            batch_num = i // config.batch_size + 1
            
            logger.info(f"处理第 {batch_num} 批，共 {len(batch_data)} 条记录")
            
            # 单线程处理当前批次
            batch_results = []
            for record in batch_data:
                result = self.process_single_record(record)
                if result:
                    batch_results.append(result)
            
            # 批量更新数据库
            if batch_results:
                updated_count = self.batch_update_database(batch_results, config)
                total_updated += updated_count
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 统计信息
        stats = {
            'total': total_records,
            'processed': self.processed_count,
            'updated': total_updated,
            'errors': self.error_count,
            'duration_seconds': duration
        }
        
        logger.info(f"处理完成！统计信息: {stats}")
        return stats


def main():
    """主函数"""
    # 创建处理器
    processor = JobSummaryProcessor()
    
    # 配置处理参数
    config = ProcessConfig(
        batch_size=50,      # 每批处理50条记录
        max_workers=6,      # 使用6个线程
        train_type='3',     # 处理train_type='3'的数据
        table_name='zhilian_job'
    )
    
    try:
        # 执行多线程处理
        logger.info("开始执行智联招聘jobSummary处理任务")
        stats = processor.process_data_multithread(config)
        
        # 输出最终统计
        logger.info("=" * 50)
        logger.info("处理完成！最终统计:")
        logger.info(f"总记录数: {stats['total']}")
        logger.info(f"成功处理: {stats['processed']}")
        logger.info(f"成功更新: {stats['updated']}")
        logger.info(f"错误数量: {stats['errors']}")
        logger.info(f"处理耗时: {stats['duration_seconds']:.2f} 秒")
        
        if stats['total'] > 0:
            success_rate = (stats['updated'] / stats['total']) * 100
            logger.info(f"成功率: {success_rate:.2f}%")
        
    except Exception as e:
        logger.error(f"处理过程中发生错误: {str(e)}")
        raise


if __name__ == "__main__":
    main()