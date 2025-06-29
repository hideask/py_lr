#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多线程数据库处理器使用示例

本文件展示了如何使用改进后的多线程数据库处理器来处理不同类型的数据表。
包含了各种配置选项和使用场景的示例。
"""

from abstract_db_processor import (
    DatabaseProcessor, 
    ResumeProcessor, 
    TableConfig,
    JSONTranslator,
    TrainingDataBuilder
)
from typing import Dict, Any
import time


class JobProcessor(DatabaseProcessor):
    """职位信息处理器示例"""
    
    def __init__(self):
        db_config = {
            "dbname": "yhaimg",
            "user": "yhaimg",
            "password": "Zq*6^pD6g2%JJ!z8",
            "host": "172.31.255.227",
            "port": "5588"
        }
        super().__init__(db_config)
    
    def process_job_data(self, batch_size: int = 50, max_workers: int = 8, use_multithread: bool = True):
        """处理职位数据"""
        config = TableConfig(
            table_name="zhilian_job",
            json_source_field="processed_info",
            description_field="job_description_detail",
            batch_size=batch_size
        )
        
        if use_multithread:
            print(f"使用多线程模式处理职位数据，线程数: {max_workers}")
            self.process_table(config, max_workers=max_workers)
        else:
            print("使用单线程模式处理职位数据")
            self.process_table_single_thread(config)


class CustomProcessor(DatabaseProcessor):
    """自定义处理器示例"""
    
    def __init__(self, db_config: Dict[str, str]):
        super().__init__(db_config)
    
    def process_custom_table(self, table_name: str, json_field: str, desc_field: str, 
                           batch_size: int = 30, max_workers: int = 6):
        """处理自定义表"""
        config = TableConfig(
            table_name=table_name,
            json_source_field=json_field,
            description_field=desc_field,
            batch_size=batch_size
        )
        
        print(f"开始处理自定义表 {table_name}")
        self.process_table(config, max_workers=max_workers)


def performance_comparison_example():
    """性能对比示例"""
    print("\n=== 性能对比示例 ===")
    
    processor = ResumeProcessor()
    
    # 小批量单线程处理
    print("\n1. 小批量单线程处理:")
    start_time = time.time()
    processor.process_zhilian_resume(
        batch_size=10,
        use_multithread=False
    )
    single_thread_time = time.time() - start_time
    print(f"单线程处理耗时: {single_thread_time:.2f} 秒")
    
    # 小批量多线程处理
    print("\n2. 小批量多线程处理:")
    start_time = time.time()
    processor.process_zhilian_resume(
        batch_size=10,
        max_workers=4,
        use_multithread=True
    )
    multi_thread_time = time.time() - start_time
    print(f"多线程处理耗时: {multi_thread_time:.2f} 秒")
    
    if single_thread_time > 0:
        speedup = single_thread_time / multi_thread_time
        print(f"加速比: {speedup:.2f}x")


def different_thread_counts_example():
    """不同线程数量测试示例"""
    print("\n=== 不同线程数量测试 ===")
    
    processor = JobProcessor()
    thread_counts = [2, 4, 6, 8]
    
    for thread_count in thread_counts:
        print(f"\n使用 {thread_count} 个线程处理:")
        start_time = time.time()
        
        processor.process_job_data(
            batch_size=20,
            max_workers=thread_count,
            use_multithread=True
        )
        
        elapsed_time = time.time() - start_time
        print(f"{thread_count} 线程处理耗时: {elapsed_time:.2f} 秒")


def batch_size_optimization_example():
    """批次大小优化示例"""
    print("\n=== 批次大小优化示例 ===")
    
    processor = ResumeProcessor()
    batch_sizes = [10, 20, 50, 100]
    
    for batch_size in batch_sizes:
        print(f"\n批次大小 {batch_size}:")
        start_time = time.time()
        
        processor.process_zhilian_resume(
            batch_size=batch_size,
            max_workers=4,
            use_multithread=True
        )
        
        elapsed_time = time.time() - start_time
        print(f"批次大小 {batch_size} 处理耗时: {elapsed_time:.2f} 秒")


def custom_table_example():
    """自定义表处理示例"""
    print("\n=== 自定义表处理示例 ===")
    
    db_config = {
        "dbname": "yhaimg",
        "user": "yhaimg",
        "password": "Zq*6^pD6g2%JJ!z8",
        "host": "172.31.255.227",
        "port": "5588"
    }
    
    processor = CustomProcessor(db_config)
    
    # 处理多个不同的表
    tables_to_process = [
        {
            "table_name": "user_profiles",
            "json_field": "profile_data",
            "desc_field": "profile_description",
            "batch_size": 25,
            "max_workers": 4
        },
        {
            "table_name": "company_info",
            "json_field": "company_data",
            "desc_field": "company_description",
            "batch_size": 15,
            "max_workers": 6
        }
    ]
    
    for table_config in tables_to_process:
        print(f"\n处理表: {table_config['table_name']}")
        processor.process_custom_table(
            table_name=table_config['table_name'],
            json_field=table_config['json_field'],
            desc_field=table_config['desc_field'],
            batch_size=table_config['batch_size'],
            max_workers=table_config['max_workers']
        )


def error_handling_example():
    """错误处理示例"""
    print("\n=== 错误处理示例 ===")
    
    processor = ResumeProcessor()
    
    try:
        # 尝试使用过多的线程数
        print("测试过多线程数的情况:")
        processor.process_zhilian_resume(
            batch_size=5,
            max_workers=50,  # 过多的线程数
            use_multithread=True
        )
    except Exception as e:
        print(f"捕获到异常: {str(e)}")
    
    try:
        # 尝试处理不存在的表
        print("\n测试不存在表的情况:")
        config = TableConfig(
            table_name="non_existent_table",
            json_source_field="some_field",
            description_field="some_desc",
            batch_size=10
        )
        processor.process_table(config, max_workers=2)
    except Exception as e:
        print(f"捕获到异常: {str(e)}")


def main():
    """主函数 - 运行所有示例"""
    print("多线程数据库处理器使用示例")
    print("=" * 50)
    
    # 基本使用示例
    print("\n=== 基本多线程处理示例 ===")
    processor = ResumeProcessor()
    processor.process_zhilian_resume(
        batch_size=20,
        max_workers=4,
        use_multithread=True
    )
    
    # 运行各种示例（注释掉以避免重复处理数据）
    # performance_comparison_example()
    # different_thread_counts_example()
    # batch_size_optimization_example()
    # custom_table_example()
    # error_handling_example()
    
    print("\n所有示例运行完成！")


if __name__ == "__main__":
    main()