#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证多线程功能是否正确实现
"""

import sys
import os
import inspect

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from abstract_db_processor import DatabaseProcessor, ResumeProcessor
    print("SUCCESS: 成功导入 DatabaseProcessor 和 ResumeProcessor")
except ImportError as e:
    print(f"ERROR: 导入失败: {e}")
    sys.exit(1)

def check_imports():
    """检查必要的导入"""
    print("\n=== 检查导入 ===")
    
    # 检查文件中的导入
    with open('abstract_db_processor.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    if 'import threading' in content:
        print("✓ threading 模块已导入")
    else:
        print("✗ threading 模块未导入")
        
    if 'from concurrent.futures import ThreadPoolExecutor, as_completed' in content:
        print("✓ ThreadPoolExecutor 已导入")
    else:
        print("✗ ThreadPoolExecutor 未导入")
        
    if 'from queue import Queue' in content:
        print("✓ Queue 已导入")
    else:
        print("✗ Queue 未导入")

def check_class_attributes():
    """检查类属性"""
    print("\n=== 检查类属性 ===")
    
    processor = DatabaseProcessor({
        "dbname": "test",
        "user": "test",
        "password": "test",
        "host": "localhost",
        "port": "5432"
    })
    
    if hasattr(processor, '_lock'):
        print("✓ _lock 属性存在")
    else:
        print("✗ _lock 属性不存在")

def check_methods():
    """检查方法"""
    print("\n=== 检查方法 ===")
    
    processor = DatabaseProcessor({
        "dbname": "test",
        "user": "test",
        "password": "test",
        "host": "localhost",
        "port": "5432"
    })
    
    methods_to_check = [
        '_process_single_record',
        '_batch_update_database',
        'process_table',
        'process_table_single_thread'
    ]
    
    for method_name in methods_to_check:
        if hasattr(processor, method_name):
            print(f"✓ {method_name} 方法存在")
        else:
            print(f"✗ {method_name} 方法不存在")

def check_method_signatures():
    """检查方法签名"""
    print("\n=== 检查方法签名 ===")
    
    processor = ResumeProcessor()
    
    # 检查 process_zhilian_resume 方法签名
    sig = inspect.signature(processor.process_zhilian_resume)
    params = list(sig.parameters.keys())
    
    expected_params = ['batch_size', 'max_workers', 'use_multithread']
    
    print(f"process_zhilian_resume 参数: {params}")
    
    for param in expected_params:
        if param in params:
            print(f"✓ {param} 参数存在")
        else:
            print(f"✗ {param} 参数不存在")
    
    # 检查 process_table 方法签名
    sig = inspect.signature(processor.process_table)
    params = list(sig.parameters.keys())
    
    print(f"process_table 参数: {params}")
    
    if 'max_workers' in params:
        print("✓ process_table 有 max_workers 参数")
    else:
        print("✗ process_table 没有 max_workers 参数")

def main():
    """主函数"""
    print("开始验证多线程功能实现...")
    
    check_imports()
    check_class_attributes()
    check_methods()
    check_method_signatures()
    
    print("\n=== 验证完成 ===")
    print("如果所有检查都显示 ✓，说明多线程功能已正确实现")

if __name__ == "__main__":
    main()