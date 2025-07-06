#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智联招聘岗位处理器使用示例

本脚本展示了如何使用多线程岗位处理器的各种功能和配置选项。
"""

import time
import logging
from multithread_job_processor import JobProcessor, JobProcessorConfig


def example_basic_usage():
    """示例1: 基本使用"""
    print("\n" + "=" * 50)
    print("示例1: 基本使用")
    print("=" * 50)
    
    # 使用默认配置
    processor = JobProcessor()
    
    # 显示当前统计信息
    stats = processor.get_processing_stats()
    if stats:
        print(f"当前状态:")
        print(f"  总记录数: {stats['total_count']}")
        print(f"  待处理: {stats['pending_count']}")
        print(f"  已处理: {stats['processed_count']}")
        print(f"  失败: {stats['failed_count']}")
        print(f"  成功率: {stats['success_rate']:.2f}%")
    
    print("\n使用默认配置开始处理...")
    print("注意: 这将实际处理数据库中的数据！")
    
    # 取消注释下面的行来实际运行处理
    # processor.start_processing()


def example_custom_config():
    """示例2: 自定义配置"""
    print("\n" + "=" * 50)
    print("示例2: 自定义配置")
    print("=" * 50)
    
    # 创建自定义配置
    config = JobProcessorConfig()
    
    # 调整配置参数
    config.max_workers = 10      # 减少线程数
    config.batch_size = 5        # 减少批次大小
    config.max_retries = 3       # 减少重试次数
    config.request_timeout = 20  # 减少超时时间
    
    print(f"自定义配置:")
    print(f"  线程数: {config.max_workers}")
    print(f"  批次大小: {config.batch_size}")
    print(f"  最大重试: {config.max_retries}")
    print(f"  请求超时: {config.request_timeout}秒")
    print(f"  Bot IDs数量: {len(config.bot_ids)}")
    
    # 创建处理器
    processor = JobProcessor(config)
    
    print("\n使用自定义配置...")
    # processor.start_processing()


def example_bot_id_rotation():
    """示例3: Bot ID轮询演示"""
    print("\n" + "=" * 50)
    print("示例3: Bot ID轮询演示")
    print("=" * 50)
    
    processor = JobProcessor()
    
    print("演示Bot ID轮询机制:")
    for i in range(10):
        bot_id = processor.get_next_bot_id()
        print(f"  第{i+1}次调用: {bot_id}")
    
    print("\n可以看到Bot ID按顺序轮询使用")


def example_random_id_generation():
    """示例4: 随机ID生成演示"""
    print("\n" + "=" * 50)
    print("示例4: 随机ID生成演示")
    print("=" * 50)
    
    processor = JobProcessor()
    
    print("演示随机ID生成:")
    for i in range(5):
        user_id, conversation_id = processor.generate_random_ids(f"Thread-{i}")
        print(f"  线程{i}: 用户ID={user_id}, 对话ID={conversation_id}")
    
    print("\n每次生成的ID都是唯一的")


def example_processing_stats():
    """示例5: 处理统计信息"""
    print("\n" + "=" * 50)
    print("示例5: 处理统计信息")
    print("=" * 50)
    
    processor = JobProcessor()
    
    print("获取详细统计信息...")
    stats = processor.get_processing_stats()
    
    if stats:
        print(f"\n详细统计:")
        print(f"  总记录数: {stats['total_count']:,}")
        print(f"  待处理记录: {stats['pending_count']:,}")
        print(f"  已处理记录: {stats['processed_count']:,}")
        print(f"  失败记录: {stats['failed_count']:,}")
        print(f"  成功率: {stats['success_rate']:.2f}%")
        
        # 计算进度
        if stats['total_count'] > 0:
            progress = (stats['processed_count'] + stats['failed_count']) / stats['total_count'] * 100
            print(f"  总进度: {progress:.2f}%")
        
        # 估算剩余时间（假设每条记录平均处理时间为5秒）
        if stats['pending_count'] > 0:
            avg_time_per_record = 5  # 秒
            estimated_time = stats['pending_count'] * avg_time_per_record
            hours = estimated_time // 3600
            minutes = (estimated_time % 3600) // 60
            print(f"  估算剩余时间: {hours}小时{minutes}分钟")
    else:
        print("无法获取统计信息，请检查数据库连接")


def example_batch_size_optimization():
    """示例6: 批次大小优化测试"""
    print("\n" + "=" * 50)
    print("示例6: 批次大小优化测试")
    print("=" * 50)
    
    batch_sizes = [5, 10, 20, 50]
    
    print("测试不同批次大小的数据获取性能...")
    
    for batch_size in batch_sizes:
        config = JobProcessorConfig()
        config.batch_size = batch_size
        processor = JobProcessor(config)
        
        print(f"\n测试批次大小: {batch_size}")
        
        # 测试数据获取时间
        start_time = time.time()
        try:
            rows = processor.fetch_unprocessed_data(batch_size)
            end_time = time.time()
            
            fetch_time = end_time - start_time
            print(f"  获取 {len(rows)} 条数据耗时: {fetch_time:.4f} 秒")
            print(f"  平均每条: {fetch_time/len(rows):.6f} 秒" if len(rows) > 0 else "  无数据")
            
        except Exception as e:
            print(f"  获取数据失败: {str(e)}")
    
    print("\n建议根据实际情况选择合适的批次大小")


def example_thread_count_optimization():
    """示例7: 线程数量优化建议"""
    print("\n" + "=" * 50)
    print("示例7: 线程数量优化建议")
    print("=" * 50)
    
    import os
    
    # 获取系统信息
    cpu_count = os.cpu_count()
    print(f"系统CPU核心数: {cpu_count}")
    
    # 推荐线程数配置
    recommendations = {
        "保守配置": cpu_count,
        "平衡配置": cpu_count * 2,
        "激进配置": cpu_count * 4,
        "最大配置": cpu_count * 6
    }
    
    print("\n线程数量配置建议:")
    for config_name, thread_count in recommendations.items():
        print(f"  {config_name}: {thread_count} 线程")
    
    print("\n注意事项:")
    print("  - 线程数过多可能导致数据库连接池耗尽")
    print("  - 线程数过少可能无法充分利用系统资源")
    print("  - 建议从较小的线程数开始测试")
    print("  - 监控系统资源使用情况")


def example_error_handling():
    """示例8: 错误处理演示"""
    print("\n" + "=" * 50)
    print("示例8: 错误处理演示")
    print("=" * 50)
    
    # 创建一个配置，故意设置错误的参数
    config = JobProcessorConfig()
    config.coze_token = "Bearer invalid_token"  # 无效token
    config.request_timeout = 1  # 极短超时时间
    
    processor = JobProcessor(config)
    
    print("演示API调用错误处理...")
    
    # 测试无效token
    result, success = processor.call_coze_api(
        "测试内容", "test_bot_id", "test_user", "test_conversation"
    )
    
    print(f"API调用结果: {result}")
    print(f"调用成功: {success}")
    
    print("\n错误处理机制:")
    print("  - API调用失败会返回错误信息")
    print("  - 处理失败的记录会标记为process_type='3'")
    print("  - 支持自动重试机制")
    print("  - 详细错误日志记录")


def example_monitoring_and_logging():
    """示例9: 监控和日志记录"""
    print("\n" + "=" * 50)
    print("示例9: 监控和日志记录")
    print("=" * 50)
    
    # 设置详细日志级别
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    processor = JobProcessor()
    
    print("日志文件位置: job_processor.log")
    print("\n日志级别说明:")
    print("  - INFO: 一般处理信息")
    print("  - WARNING: 警告信息")
    print("  - ERROR: 错误信息")
    print("  - DEBUG: 调试信息")
    
    print("\n监控指标:")
    print("  - 处理速度 (记录/秒)")
    print("  - 成功率")
    print("  - API响应时间")
    print("  - 数据库操作时间")
    print("  - 线程状态")
    
    # 演示日志记录
    processor.logger.info("这是一条信息日志")
    processor.logger.warning("这是一条警告日志")
    processor.logger.error("这是一条错误日志")


def example_production_deployment():
    """示例10: 生产环境部署建议"""
    print("\n" + "=" * 50)
    print("示例10: 生产环境部署建议")
    print("=" * 50)
    
    print("生产环境配置建议:")
    print("\n1. 硬件配置:")
    print("   - CPU: 8核心以上")
    print("   - 内存: 16GB以上")
    print("   - 网络: 稳定的网络连接")
    
    print("\n2. 软件配置:")
    print("   - Python 3.8+")
    print("   - PostgreSQL 12+")
    print("   - 连接池配置")
    
    print("\n3. 处理器配置:")
    print("   - 线程数: 20-50 (根据系统性能调整)")
    print("   - 批次大小: 10-20")
    print("   - 超时时间: 30秒")
    print("   - 重试次数: 3-5次")
    
    print("\n4. 监控和维护:")
    print("   - 设置日志轮转")
    print("   - 监控系统资源")
    print("   - 定期检查处理进度")
    print("   - 备份重要数据")
    
    print("\n5. 安全考虑:")
    print("   - 保护API密钥")
    print("   - 数据库访问控制")
    print("   - 网络安全配置")


def main():
    """主函数 - 运行所有示例"""
    print("智联招聘岗位处理器使用示例")
    print("=" * 50)
    
    examples = [
        example_basic_usage,
        example_custom_config,
        example_bot_id_rotation,
        example_random_id_generation,
        example_processing_stats,
        example_batch_size_optimization,
        example_thread_count_optimization,
        example_error_handling,
        example_monitoring_and_logging,
        example_production_deployment
    ]
    
    for i, example_func in enumerate(examples, 1):
        try:
            example_func()
        except Exception as e:
            print(f"\n示例{i}执行出错: {str(e)}")
        
        # 在示例之间暂停
        if i < len(examples):
            input("\n按回车键继续下一个示例...")
    
    print("\n" + "=" * 50)
    print("所有示例演示完成！")
    print("=" * 50)
    
    print("\n快速开始:")
    print("1. 检查数据库连接配置")
    print("2. 调整处理器配置参数")
    print("3. 运行 python multithread_job_processor.py")
    print("4. 监控处理进度和日志")


if __name__ == "__main__":
    main()