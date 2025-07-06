#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智联招聘简历数据处理器

本程序用于多线程处理智联招聘简历数据，主要功能：
1. 从PostgreSQL数据库查询简历数据
2. 处理resume_processed_info中的cityLabel字段，去掉"现居"前缀
3. 将处理后的数据更新回数据库
"""

import json
import logging
import os
import psycopg2
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any

# 导入公共数据库连接模块
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db_connection import get_db_connection, close_db_connection


class ResumeProcessorConfig:
    """简历处理器配置类"""
    
    def __init__(self):
        # 使用公共数据库连接配置
        # 注意：db_connection模块已经包含了默认的数据库配置
        pass
        
        # 处理配置
        self.max_workers = 20  # 最大线程数
        self.batch_size = 100  # 批次大小
        self.train_type = '3'  # 训练类型，None表示处理所有
        self.table_name = 'zhilian_resume'  # 表名
        
        # 日志配置
        self.log_level = logging.INFO
        self.log_file = 'resume_processor.log'


class ResumeProcessor:
    """简历处理器主类"""
    
    def __init__(self, config: ResumeProcessorConfig = None):
        self.config = config or ResumeProcessorConfig()
        self.processed_count = 0
        self.failed_count = 0
        self.lock = threading.Lock()
        
        # 设置日志
        self._setup_logging()
        
        self.logger.info("简历处理器初始化完成")
        self.logger.info(f"配置: {self.config.max_workers}线程, {self.config.batch_size}批次大小")
    
    def _setup_logging(self):
        """设置日志"""
        self.logger = logging.getLogger('ResumeProcessor')
        self.logger.setLevel(self.config.log_level)
        
        # 避免重复添加handler
        if not self.logger.handlers:
            # 文件handler
            file_handler = logging.FileHandler(
                self.config.log_file, 
                encoding='utf-8'
            )
            file_handler.setLevel(self.config.log_level)
            
            # 控制台handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(self.config.log_level)
            
            # 格式化
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def get_connection(self):
        """获取数据库连接"""
        try:
            conn = get_db_connection()
            return conn
        except Exception as e:
            self.logger.error(f"数据库连接失败: {e}")
            raise
    
    def fetch_resume_data(self, limit: int = None) -> List[Tuple[int, str]]:
        """获取简历数据"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # 构建查询SQL
            if self.config.train_type:
                sql = f"SELECT id, resume_processed_info FROM {self.config.table_name} WHERE train_type = %s"
                params = (self.config.train_type,)
            else:
                sql = f"SELECT id, resume_processed_info FROM {self.config.table_name}"
                params = ()
            
            if limit:
                sql += f" LIMIT {limit}"
            
            self.logger.info(f"执行查询: {sql}")
            cursor.execute(sql, params)
            
            results = cursor.fetchall()
            self.logger.info(f"查询到 {len(results)} 条记录")
            
            return results
            
        except Exception as e:
            self.logger.error(f"获取简历数据失败: {e}")
            raise
        finally:
            if conn:
                close_db_connection(None, conn)
    
    def process_city_label(self, resume_processed_info: str) -> Tuple[bool, str, str]:
        """处理cityLabel字段
        
        Args:
            resume_processed_info: JSON字符串
            
        Returns:
            Tuple[bool, str, str]: (是否成功, 处理后的JSON字符串, 错误信息)
        """
        try:
            # 解析JSON
            data = json.loads(resume_processed_info)
            
            # 检查是否有user节点
            if 'user' not in data:
                return True, resume_processed_info, "无user节点"
            
            user_data = data['user']
            
            # 检查user节点是否为字典
            if not isinstance(user_data, dict):
                return True, resume_processed_info, "user节点不是字典类型"
            
            # 检查是否有cityLabel字段
            if 'cityLabel' not in user_data:
                return True, resume_processed_info, "user节点中无cityLabel字段"
            
            city_label = user_data['cityLabel']
            
            # 检查是否为字符串
            if not isinstance(city_label, str):
                return True, resume_processed_info, "cityLabel不是字符串类型"
            
            # 去掉"现居"前缀
            if city_label.startswith('现居'):
                new_city_label = city_label[2:]  # 去掉前两个字符"现居"
                data['user']['cityLabel'] = new_city_label
                
                # 转换回JSON字符串
                new_resume_processed_info = json.dumps(data, ensure_ascii=False)
                
                self.logger.debug(f"cityLabel处理: '{city_label}' -> '{new_city_label}'")
                return True, new_resume_processed_info, None
            else:
                # 没有"现居"前缀，不需要处理
                return True, resume_processed_info, "无需处理"
                
        except json.JSONDecodeError as e:
            error_msg = f"JSON解析失败: {e}"
            self.logger.warning(error_msg)
            return False, resume_processed_info, error_msg
        except Exception as e:
            error_msg = f"处理cityLabel失败: {e}"
            self.logger.error(error_msg)
            return False, resume_processed_info, error_msg
    
    def update_resume_data(self, record_id: int, resume_processed_info: str) -> bool:
        """更新简历数据"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            sql = f"UPDATE {self.config.table_name} SET resume_processed_info = %s WHERE id = %s"
            cursor.execute(sql, (resume_processed_info, record_id))
            
            conn.commit()
            
            if cursor.rowcount > 0:
                self.logger.debug(f"记录 {record_id} 更新成功")
                return True
            else:
                self.logger.warning(f"记录 {record_id} 未找到或未更新")
                return False
                
        except Exception as e:
            self.logger.error(f"更新记录 {record_id} 失败: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                close_db_connection(None, conn)
    
    def process_single_record(self, record_id: int, resume_processed_info: str) -> Tuple[bool, str]:
        """处理单条记录
        
        Args:
            record_id: 记录ID
            resume_processed_info: 原始resume_processed_info
            
        Returns:
            Tuple[bool, str]: (是否成功, 错误信息)
        """
        try:
            # 处理cityLabel
            success, new_resume_processed_info, error_msg = self.process_city_label(resume_processed_info)
            
            if not success:
                return False, error_msg
            
            # 如果数据有变化，更新数据库
            if new_resume_processed_info != resume_processed_info:
                update_success = self.update_resume_data(record_id, new_resume_processed_info)
                if update_success:
                    with self.lock:
                        self.processed_count += 1
                    return True, None
                else:
                    return False, "数据库更新失败"
            else:
                # 数据无变化，也算成功
                with self.lock:
                    self.processed_count += 1
                return True, "无需更新"
                
        except Exception as e:
            error_msg = f"处理记录 {record_id} 失败: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def process_batch(self, batch_data: List[Tuple[int, str]]) -> List[Tuple[int, bool, str]]:
        """处理批次数据
        
        Args:
            batch_data: 批次数据列表
            
        Returns:
            List[Tuple[int, bool, str]]: 处理结果列表 (记录ID, 是否成功, 错误信息)
        """
        results = []
        
        for record_id, resume_processed_info in batch_data:
            success, error_msg = self.process_single_record(record_id, resume_processed_info)
            results.append((record_id, success, error_msg))
            
            if not success:
                with self.lock:
                    self.failed_count += 1
                self.logger.warning(f"记录 {record_id} 处理失败: {error_msg}")
        
        return results
    
    def start_processing(self, limit: int = None):
        """开始多线程处理
        
        Args:
            limit: 限制处理的记录数量，None表示处理所有
        """
        start_time = time.time()
        self.logger.info("开始处理简历数据")
        
        try:
            # 获取数据
            self.logger.info("正在获取简历数据...")
            resume_data = self.fetch_resume_data(limit)
            
            if not resume_data:
                self.logger.info("没有找到需要处理的数据")
                return
            
            total_records = len(resume_data)
            self.logger.info(f"共获取到 {total_records} 条记录")
            
            # 分批处理
            batches = []
            for i in range(0, total_records, self.config.batch_size):
                batch = resume_data[i:i + self.config.batch_size]
                batches.append(batch)
            
            self.logger.info(f"分为 {len(batches)} 个批次处理")
            
            # 重置计数器
            self.processed_count = 0
            self.failed_count = 0
            
            # 多线程处理
            with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
                # 提交任务
                future_to_batch = {
                    executor.submit(self.process_batch, batch): i 
                    for i, batch in enumerate(batches)
                }
                
                # 处理结果
                completed_batches = 0
                for future in as_completed(future_to_batch):
                    batch_index = future_to_batch[future]
                    completed_batches += 1
                    
                    try:
                        batch_results = future.result()
                        self.logger.info(
                            f"批次 {batch_index + 1}/{len(batches)} 完成 "
                            f"(总进度: {completed_batches}/{len(batches)})"
                        )
                        
                        # 记录批次中的失败记录
                        failed_in_batch = sum(1 for _, success, _ in batch_results if not success)
                        if failed_in_batch > 0:
                            self.logger.warning(f"批次 {batch_index + 1} 中有 {failed_in_batch} 条记录处理失败")
                            
                    except Exception as e:
                        self.logger.error(f"批次 {batch_index + 1} 处理异常: {e}")
                        with self.lock:
                            self.failed_count += len(batches[batch_index])
            
            # 处理完成
            end_time = time.time()
            total_time = end_time - start_time
            
            self.logger.info("处理完成!")
            self.logger.info(f"总记录数: {total_records}")
            self.logger.info(f"成功处理: {self.processed_count}")
            self.logger.info(f"处理失败: {self.failed_count}")
            self.logger.info(f"成功率: {(self.processed_count / total_records * 100):.2f}%")
            self.logger.info(f"总耗时: {total_time:.2f}秒")
            
            if total_time > 0:
                rate = self.processed_count / total_time
                self.logger.info(f"处理速度: {rate:.2f}记录/秒")
            
        except Exception as e:
            self.logger.error(f"处理过程中发生错误: {e}")
            raise
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # 获取总记录数
            if self.config.train_type:
                sql = f"SELECT COUNT(*) FROM {self.config.table_name} WHERE train_type = %s"
                cursor.execute(sql, (self.config.train_type,))
            else:
                sql = f"SELECT COUNT(*) FROM {self.config.table_name}"
                cursor.execute(sql)
            
            total_count = cursor.fetchone()[0]
            
            close_db_connection(None, conn)
            
            return {
                'total_count': total_count,
                'processed_count': self.processed_count,
                'failed_count': self.failed_count,
                'success_rate': (self.processed_count / total_count * 100) if total_count > 0 else 0
            }
            
        except Exception as e:
            self.logger.error(f"获取统计信息失败: {e}")
            return {
                'total_count': 0,
                'processed_count': self.processed_count,
                'failed_count': self.failed_count,
                'success_rate': 0
            }


def main():
    """主函数"""
    print("智联招聘简历数据处理器")
    print("=" * 40)
    
    # 创建配置
    config = ResumeProcessorConfig()
    
    # 显示配置
    print(f"配置信息:")
    print(f"  数据库: 使用公共数据库连接配置")
    print(f"  表名: {config.table_name}")
    print(f"  训练类型: {config.train_type or '全部'}")
    print(f"  线程数: {config.max_workers}")
    print(f"  批次大小: {config.batch_size}")
    
    # 确认执行
    confirm = input("\n是否开始处理? (y/n): ").strip().lower()
    if confirm not in ['y', 'yes', '是']:
        print("操作取消")
        return
    
    try:
        # 创建处理器
        processor = ResumeProcessor(config)
        
        # 获取统计信息
        stats = processor.get_processing_stats()
        print(f"\n待处理记录数: {stats['total_count']}")
        
        if stats['total_count'] == 0:
            print("没有找到需要处理的记录")
            return
        
        # 开始处理
        processor.start_processing()
        
        # 显示最终统计
        final_stats = processor.get_processing_stats()
        print(f"\n最终统计:")
        print(f"  总记录数: {final_stats['total_count']}")
        print(f"  成功处理: {final_stats['processed_count']}")
        print(f"  处理失败: {final_stats['failed_count']}")
        print(f"  成功率: {final_stats['success_rate']:.2f}%")
        
        print(f"\n日志文件: {config.log_file}")
        print("处理完成!")
        
    except KeyboardInterrupt:
        print("\n用户中断操作")
    except Exception as e:
        print(f"\n处理失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()