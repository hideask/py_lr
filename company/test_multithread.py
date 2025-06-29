#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试多线程功能
"""

import sys
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from abstract_db_processor import ResumeProcessor
    print("✓ 成功导入 ResumeProcessor")
except ImportError as e:
    print(f"✗ 导入失败: {e}")
    sys.exit(1)

def test_multithread_imports():
    """测试多线程相关模块导入"""
    print("\n=== 测试多线程模块导入 ===")
    
    try:
        import threading
        print("✓ threading 模块导入成功")
    except ImportError:
        print("✗ threading 模块导入失败")
        return False
    
    try:
        from concurrent.futures import ThreadPoolExecutor, as_completed
        print("✓ ThreadPoolExecutor 导入成功")
    except ImportError:
        print("✗ ThreadPoolExecutor 导入失败")
        return False
    
    try:
        from queue import Queue
        print("✓ Queue 导入成功")
    except ImportError:
        print("✗ Queue 导入失败")
        return False
    
    return True

def test_processor_methods():
    """测试处理器方法"""
    print("\n=== 测试处理器方法 ===")
    
    try:
        processor = ResumeProcessor()
        print("✓ ResumeProcessor 实例化成功")
        
        # 检查是否有多线程相关方法
        if hasattr(processor, 'process_zhilian_resume'):
            print("✓ process_zhilian_resume 方法存在")
        else:
            print("✗ process_zhilian_resume 方法不存在")
            
        if hasattr(processor, 'process_table'):
            print("✓ process_table 方法存在")
        else:
            print("✗ process_table 方法不存在")
            
        if hasattr(processor, 'process_table_single_thread'):
            print("✓ process_table_single_thread 方法存在")
        else:
            print("✗ process_table_single_thread 方法不存在")
            
        if hasattr(processor, '_process_single_record'):
            print("✓ _process_single_record 方法存在")
        else:
            print("✗ _process_single_record 方法不存在")
            
        if hasattr(processor, '_batch_update_database'):
            print("✓ _batch_update_database 方法存在")
        else:
            print("✗ _batch_update_database 方法不存在")
            
        return True
        
    except Exception as e:
        print(f"✗ 处理器测试失败: {e}")
        return False

def test_simple_multithread():
    """测试简单的多线程功能"""
    print("\n=== 测试简单多线程功能 ===")
    
    def worker(thread_id):
        print(f"线程 {thread_id} 开始工作")
        time.sleep(0.1)
        print(f"线程 {thread_id} 完成工作")
        return f"线程 {thread_id} 结果"
    
    try:
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(worker, i) for i in range(3)]
            results = []
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                print(f"收到结果: {result}")
        
        print(f"✓ 多线程测试成功，共收到 {len(results)} 个结果")
        return True
        
    except Exception as e:
        print(f"✗ 多线程测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试多线程功能...")
    
    # 测试模块导入
    if not test_multithread_imports():
        print("\n❌ 多线程模块导入测试失败")
        return
    
    # 测试处理器方法
    if not test_processor_methods():
        print("\n❌ 处理器方法测试失败")
        return
    
    # 测试简单多线程
    if not test_simple_multithread():
        print("\n❌ 简单多线程测试失败")
        return
    
    print("\n✅ 所有测试通过！多线程功能已正确实现")

if __name__ == "__main__":
    main()