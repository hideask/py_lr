#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简历处理器使用示例

本脚本展示了简历处理器的各种使用场景和配置选项。
"""

import json
import time
import os
import sys

# 导入公共数据库连接模块
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db_connection import get_db_connection, close_db_connection
from multithread_resume_processor import ResumeProcessor, ResumeProcessorConfig


def example_1_basic_usage():
    """示例1: 基本使用"""
    print("\n" + "=" * 50)
    print("示例1: 基本使用")
    print("=" * 50)
    
    try:
        # 使用默认配置
        processor = ResumeProcessor()
        
        # 获取统计信息
        stats = processor.get_processing_stats()
        print(f"数据库中共有 {stats['total_count']} 条记录")
        
        if stats['total_count'] > 0:
            print("开始处理...")
            # 限制处理前10条记录作为示例
            processor.start_processing(limit=10)
            
            # 显示处理结果
            final_stats = processor.get_processing_stats()
            print(f"处理完成: {processor.processed_count} 条成功, {processor.failed_count} 条失败")
        else:
            print("没有找到需要处理的记录")
            
    except Exception as e:
        print(f"基本使用示例失败: {e}")


def example_2_custom_config():
    """示例2: 自定义配置"""
    print("\n" + "=" * 50)
    print("示例2: 自定义配置")
    print("=" * 50)
    
    try:
        # 创建自定义配置
        config = ResumeProcessorConfig()
        config.max_workers = 8  # 8个线程
        config.batch_size = 50  # 批次大小50
        config.train_type = None  # 处理所有记录，不限制训练类型
        config.log_file = 'custom_resume_processor.log'
        
        print(f"自定义配置:")
        print(f"  线程数: {config.max_workers}")
        print(f"  批次大小: {config.batch_size}")
        print(f"  训练类型: {config.train_type or '全部'}")
        print(f"  日志文件: {config.log_file}")
        
        # 创建处理器
        processor = ResumeProcessor(config)
        
        # 获取统计信息
        stats = processor.get_processing_stats()
        print(f"\n待处理记录数: {stats['total_count']}")
        
        # 注意：这里只是演示配置，不实际处理大量数据
        print("配置演示完成（未实际处理数据）")
        
    except Exception as e:
        print(f"自定义配置示例失败: {e}")


def example_3_city_label_processing():
    """示例3: cityLabel处理演示"""
    print("\n" + "=" * 50)
    print("示例3: cityLabel处理演示")
    print("=" * 50)
    
    # 测试数据
    test_cases = [
        {
            "name": "张三",
            "user": {
                "cityLabel": "现居成都 崇州市",
                "age": 25,
                "education": "本科"
            }
        },
        {
            "name": "李四",
            "user": {
                "cityLabel": "现居北京 朝阳区",
                "age": 30,
                "experience": "5年"
            }
        },
        {
            "name": "王五",
            "user": {
                "cityLabel": "上海 浦东区",  # 没有'现居'前缀
                "age": 28
            }
        },
        {
            "name": "赵六",
            "user": {
                "cityLabel": "现居深圳",
                "age": 32
            }
        },
        {
            "name": "钱七",
            "user": {
                "age": 29
                # 没有cityLabel字段
            }
        }
    ]
    
    try:
        processor = ResumeProcessor()
        
        print("处理结果:")
        for i, test_data in enumerate(test_cases, 1):
            processed_info = json.dumps(test_data, ensure_ascii=False)
            
            print(f"\n测试 {i}: {test_data.get('name')}")
            user_data = test_data.get('user', {})
            original_city_label = user_data.get('cityLabel', '无')
            print(f"  原始cityLabel: {original_city_label}")
            
            success, result, error = processor.process_city_label(processed_info)
            
            if success:
                if result != processed_info:
                    result_data = json.loads(result)
                    new_city_label = result_data.get('user', {}).get('cityLabel', '无')
                    print(f"  处理后cityLabel: {new_city_label}")
                    print(f"  状态: 已更新")
                else:
                    print(f"  状态: {error or '无变化'}")
            else:
                print(f"  状态: 处理失败 - {error}")
                
    except Exception as e:
        print(f"cityLabel处理演示失败: {e}")


def example_4_batch_processing():
    """示例4: 批次处理演示"""
    print("\n" + "=" * 50)
    print("示例4: 批次处理演示")
    print("=" * 50)
    
    try:
        # 创建测试数据
        test_batch = [
            (1, json.dumps({"name": "用户1", "user": {"cityLabel": "现居成都 高新区"}}, ensure_ascii=False)),
            (2, json.dumps({"name": "用户2", "user": {"cityLabel": "现居北京 海淀区"}}, ensure_ascii=False)),
            (3, json.dumps({"name": "用户3", "user": {"cityLabel": "上海 徐汇区"}}, ensure_ascii=False)),
            (4, json.dumps({"name": "用户4", "user": {"cityLabel": "现居广州"}}, ensure_ascii=False)),
            (5, json.dumps({"name": "用户5", "user": {"age": 25}}, ensure_ascii=False))  # 无cityLabel
        ]
        
        processor = ResumeProcessor()
        
        print(f"批次数据 ({len(test_batch)} 条记录):")
        for record_id, data in test_batch:
            parsed_data = json.loads(data)
            user_data = parsed_data.get('user', {})
            city_label = user_data.get('cityLabel', '无')
            print(f"  记录 {record_id}: {parsed_data['name']}, cityLabel='{city_label}'")
        
        print("\n开始批次处理...")
        start_time = time.time()
        
        # 注意：这里模拟批次处理，不实际更新数据库
        results = []
        for record_id, processed_info in test_batch:
            success, error = processor.process_single_record(record_id, processed_info)
            results.append((record_id, success, error))
        
        end_time = time.time()
        
        print(f"\n批次处理结果:")
        success_count = 0
        for record_id, success, error in results:
            status = "成功" if success else f"失败({error})"
            print(f"  记录 {record_id}: {status}")
            if success:
                success_count += 1
        
        print(f"\n统计: {success_count}/{len(test_batch)} 成功")
        print(f"耗时: {end_time - start_time:.3f}秒")
        
    except Exception as e:
        print(f"批次处理演示失败: {e}")


def example_5_performance_comparison():
    """示例5: 性能对比"""
    print("\n" + "=" * 50)
    print("示例5: 性能对比")
    print("=" * 50)
    
    try:
        # 生成测试数据
        test_data = []
        for i in range(100):
            data = {
                "name": f"测试用户{i+1}",
                "user": {
                    "cityLabel": f"现居城市{i%10} 区域{i%5}",
                    "age": 20 + (i % 30),
                    "education": "本科",
                    "experience": f"{i%10}年"
                }
            }
            test_data.append(json.dumps(data, ensure_ascii=False))
        
        processor = ResumeProcessor()
        
        print(f"测试数据: {len(test_data)} 条记录")
        
        # 单线程处理
        print("\n单线程处理:")
        start_time = time.time()
        
        single_thread_results = []
        for i, processed_info in enumerate(test_data):
            success, result, error = processor.process_city_label(processed_info)
            single_thread_results.append(success)
        
        single_thread_time = time.time() - start_time
        single_thread_rate = len(test_data) / single_thread_time
        
        print(f"  耗时: {single_thread_time:.3f}秒")
        print(f"  速度: {single_thread_rate:.2f}记录/秒")
        print(f"  成功: {sum(single_thread_results)}/{len(test_data)}")
        
        # 多线程配置对比
        thread_configs = [2, 4, 8]
        
        for thread_count in thread_configs:
            print(f"\n{thread_count}线程处理:")
            
            config = ResumeProcessorConfig()
            config.max_workers = thread_count
            config.batch_size = 20
            
            # 这里只是演示配置，实际多线程处理需要真实数据库
            estimated_time = single_thread_time / thread_count * 0.8  # 估算时间（考虑开销）
            estimated_rate = len(test_data) / estimated_time
            
            print(f"  预估耗时: {estimated_time:.3f}秒")
            print(f"  预估速度: {estimated_rate:.2f}记录/秒")
            print(f"  加速比: {single_thread_time/estimated_time:.2f}x")
        
    except Exception as e:
        print(f"性能对比演示失败: {e}")


def example_6_error_handling():
    """示例6: 错误处理演示"""
    print("\n" + "=" * 50)
    print("示例6: 错误处理演示")
    print("=" * 50)
    
    try:
        processor = ResumeProcessor()
        
        # 测试各种错误情况
        error_cases = [
            ("无效JSON", "{'name': '张三', 'cityLabel': '现居成都'}"),  # 单引号JSON
            ("空字符串", ""),
            ("非JSON字符串", "这不是JSON"),
            ("cityLabel非字符串", json.dumps({"cityLabel": 123}, ensure_ascii=False)),
            ("正常数据", json.dumps({"name": "张三", "cityLabel": "现居成都"}, ensure_ascii=False))
        ]
        
        print("错误处理测试:")
        for case_name, test_data in error_cases:
            print(f"\n测试: {case_name}")
            print(f"  输入: {test_data[:50]}{'...' if len(test_data) > 50 else ''}")
            
            success, result, error = processor.process_city_label(test_data)
            
            if success:
                if result != test_data:
                    print(f"  结果: 处理成功，数据已更新")
                else:
                    print(f"  结果: 处理成功，{error or '无变化'}")
            else:
                print(f"  结果: 处理失败 - {error}")
        
    except Exception as e:
        print(f"错误处理演示失败: {e}")


def example_7_monitoring_and_logging():
    """示例7: 监控和日志记录"""
    print("\n" + "=" * 50)
    print("示例7: 监控和日志记录")
    print("=" * 50)
    
    try:
        # 创建带有详细日志的配置
        config = ResumeProcessorConfig()
        config.log_file = 'detailed_resume_processor.log'
        config.log_level = 10  # DEBUG级别
        
        processor = ResumeProcessor(config)
        
        print(f"日志文件: {config.log_file}")
        print(f"日志级别: DEBUG")
        
        # 模拟一些处理操作
        test_data = json.dumps({
            "name": "监控测试用户",
            "cityLabel": "现居成都 天府新区",
            "age": 28
        }, ensure_ascii=False)
        
        print("\n执行处理操作...")
        success, result, error = processor.process_city_label(test_data)
        
        if success:
            result_data = json.loads(result)
            print(f"处理成功: cityLabel = '{result_data['cityLabel']}'")
        else:
            print(f"处理失败: {error}")
        
        # 检查日志文件
        if os.path.exists(config.log_file):
            file_size = os.path.getsize(config.log_file)
            print(f"\n日志文件大小: {file_size} 字节")
            
            # 读取最后几行日志
            with open(config.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    print("\n最新日志条目:")
                    for line in lines[-3:]:
                        print(f"  {line.strip()}")
        
        # 获取处理统计
        stats = processor.get_processing_stats()
        print(f"\n当前统计:")
        print(f"  数据库总记录: {stats['total_count']}")
        print(f"  已处理: {stats['processed_count']}")
        print(f"  失败: {stats['failed_count']}")
        print(f"  成功率: {stats['success_rate']:.2f}%")
        
    except Exception as e:
        print(f"监控和日志演示失败: {e}")


def example_8_production_deployment():
    """示例8: 生产环境部署建议"""
    print("\n" + "=" * 50)
    print("示例8: 生产环境部署建议")
    print("=" * 50)
    
    print("生产环境配置建议:")
    
    # 生产环境配置
    prod_config = ResumeProcessorConfig()
    prod_config.max_workers = 16  # 根据服务器CPU核心数调整
    prod_config.batch_size = 200  # 较大的批次提高效率
    prod_config.log_file = '/var/log/resume_processor.log'  # 标准日志路径
    
    print(f"\n推荐配置:")
    print(f"  线程数: {prod_config.max_workers} (建议为CPU核心数的2-4倍)")
    print(f"  批次大小: {prod_config.batch_size} (平衡内存使用和效率)")
    print(f"  日志文件: {prod_config.log_file}")
    
    print(f"\n部署检查清单:")
    print(f"  ✓ 设置环境变量 (DB_HOST, DB_USER, DB_PASSWORD 等)")
    print(f"  ✓ 配置日志轮转 (logrotate)")
    print(f"  ✓ 设置监控告警")
    print(f"  ✓ 配置定时任务 (crontab)")
    print(f"  ✓ 准备数据备份策略")
    
    print(f"\n监控指标:")
    print(f"  - 处理速度 (记录/秒)")
    print(f"  - 成功率 (%)")
    print(f"  - 内存使用率")
    print(f"  - 数据库连接数")
    print(f"  - 错误日志数量")
    
    print(f"\n定时任务示例:")
    print(f"  # 每小时执行一次简历处理")
    print(f"  0 * * * * /usr/bin/python3 /path/to/multithread_resume_processor.py")
    
    print(f"\n告警规则示例:")
    print(f"  - 成功率低于95%")
    print(f"  - 处理速度低于预期")
    print(f"  - 连续失败超过100条")
    print(f"  - 内存使用率超过80%")


def main():
    """主函数"""
    print("简历处理器使用示例")
    print("=" * 60)
    
    examples = [
        ("基本使用", example_1_basic_usage),
        ("自定义配置", example_2_custom_config),
        ("cityLabel处理演示", example_3_city_label_processing),
        ("批次处理演示", example_4_batch_processing),
        ("性能对比", example_5_performance_comparison),
        ("错误处理演示", example_6_error_handling),
        ("监控和日志记录", example_7_monitoring_and_logging),
        ("生产环境部署建议", example_8_production_deployment)
    ]
    
    print(f"\n可用示例:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    print(f"  0. 运行所有示例")
    
    try:
        choice = input("\n请选择要运行的示例 (0-8): ").strip()
        
        if choice == '0':
            # 运行所有示例
            for name, func in examples:
                print(f"\n正在运行: {name}")
                try:
                    func()
                except Exception as e:
                    print(f"示例 '{name}' 运行失败: {e}")
                
                # 短暂暂停
                time.sleep(1)
        
        elif choice.isdigit() and 1 <= int(choice) <= len(examples):
            # 运行指定示例
            name, func = examples[int(choice) - 1]
            print(f"\n运行示例: {name}")
            func()
        
        else:
            print("无效选择")
            return
    
    except KeyboardInterrupt:
        print("\n\n用户中断操作")
    except Exception as e:
        print(f"\n运行示例时出错: {e}")
    
    print("\n示例运行完成!")
    print("\n使用说明:")
    print("1. 在生产环境使用前，请先配置数据库连接")
    print("2. 建议先在测试环境验证处理逻辑")
    print("3. 监控处理过程中的系统资源使用")
    print("4. 定期检查日志文件和处理统计")


if __name__ == "__main__":
    main()