#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智联招聘岗位处理主执行脚本

本脚本提供交互式的岗位数据处理流程，
包括配置确认、数据预览、处理执行和结果统计。
"""

import os
import time
from datetime import datetime
from company.job.multithread_job_processor import JobProcessor, JobProcessorConfig


def print_banner():
    """打印程序横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                智联招聘岗位信息处理器                          ║
    ║                                                              ║
    ║  功能: 多线程处理岗位数据，调用Coze API生成岗位描述           ║
    ║  版本: 1.0.0                                                ║
    ║  作者: AI Assistant                                          ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def get_user_confirmation():
    """获取用户确认"""
    print("\n⚠️  重要提示:")
    print("   本程序将处理数据库中的真实数据")
    print("   处理过程中会调用Coze API接口")
    print("   请确保已经备份重要数据")
    
    while True:
        confirm = input("\n是否继续执行? (y/n): ").strip().lower()
        if confirm in ['y', 'yes', '是']:
            return True
        elif confirm in ['n', 'no', '否']:
            return False
        else:
            print("请输入 y 或 n")


def configure_processor():
    """配置处理器参数"""
    print("\n" + "=" * 50)
    print("配置处理器参数")
    print("=" * 50)
    
    config = JobProcessorConfig()
    
    # 显示默认配置
    print(f"\n当前默认配置:")
    print(f"  线程数量: {config.max_workers}")
    print(f"  批次大小: {config.batch_size}")
    print(f"  最大重试: {config.max_retries}")
    print(f"  请求超时: {config.request_timeout}秒")
    print(f"  训练类型: {config.train_type}")
    print(f"  表名: {config.table_name}")
    print(f"  Bot IDs数量: {len(config.bot_ids)}")
    
    # 询问是否使用自定义配置
    use_custom = input("\n是否使用自定义配置? (y/n, 默认n): ").strip().lower()
    
    if use_custom in ['y', 'yes', '是']:
        print("\n请输入自定义配置 (直接回车使用默认值):")
        
        # 线程数量
        threads_input = input(f"线程数量 (默认{config.max_workers}): ").strip()
        if threads_input.isdigit():
            config.max_workers = int(threads_input)
        
        # 批次大小
        batch_input = input(f"批次大小 (默认{config.batch_size}): ").strip()
        if batch_input.isdigit():
            config.batch_size = int(batch_input)
        
        # 最大重试
        retry_input = input(f"最大重试次数 (默认{config.max_retries}): ").strip()
        if retry_input.isdigit():
            config.max_retries = int(retry_input)
        
        # 请求超时
        timeout_input = input(f"请求超时时间/秒 (默认{config.request_timeout}): ").strip()
        if timeout_input.isdigit():
            config.request_timeout = int(timeout_input)
        
        # 训练类型
        train_type_input = input(f"训练类型 (默认{config.train_type}): ").strip()
        if train_type_input:
            config.train_type = train_type_input
        
        print(f"\n更新后的配置:")
        print(f"  线程数量: {config.max_workers}")
        print(f"  批次大小: {config.batch_size}")
        print(f"  最大重试: {config.max_retries}")
        print(f"  请求超时: {config.request_timeout}秒")
        print(f"  训练类型: {config.train_type}")
    
    return config


def preview_data(processor):
    """预览待处理数据"""
    print("\n" + "=" * 50)
    print("数据预览")
    print("=" * 50)
    
    try:
        # 获取统计信息
        stats = processor.get_processing_stats()
        
        if stats:
            print(f"\n数据库统计信息:")
            print(f"  总记录数: {stats['total_count']:,}")
            print(f"  待处理记录: {stats['pending_count']:,}")
            print(f"  已处理记录: {stats['processed_count']:,}")
            print(f"  失败记录: {stats['failed_count']:,}")
            print(f"  成功率: {stats['success_rate']:.2f}%")
            
            if stats['total_count'] > 0:
                progress = (stats['processed_count'] + stats['failed_count']) / stats['total_count'] * 100
                print(f"  总进度: {progress:.2f}%")
        
        # 获取样本数据
        print("\n获取样本数据...")
        sample_rows = processor.fetch_unprocessed_data(3)
        
        if sample_rows:
            print(f"\n样本数据 (前3条):")
            for i, (record_id, processed_info) in enumerate(sample_rows, 1):
                print(f"\n  样本 {i}:")
                print(f"    ID: {record_id}")
                
                # 尝试解析JSON并显示关键信息
                try:
                    import json
                    info_data = json.loads(processed_info)
                    
                    # 显示关键字段
                    key_fields = ['jobTitle', 'company', 'salary', 'location']
                    for field in key_fields:
                        if field in info_data:
                            value = info_data[field]
                            if isinstance(value, str) and len(value) > 50:
                                value = value[:50] + "..."
                            print(f"    {field}: {value}")
                    
                except json.JSONDecodeError:
                    # 如果不是JSON，显示前100个字符
                    preview = processed_info[:100] + "..." if len(processed_info) > 100 else processed_info
                    print(f"    内容: {preview}")
        else:
            print("\n没有找到待处理的数据")
            return False
        
        return True
        
    except Exception as e:
        print(f"\n数据预览失败: {str(e)}")
        return False


def estimate_processing_time(stats, config):
    """估算处理时间"""
    if not stats or stats['pending_count'] == 0:
        return
    
    print("\n" + "=" * 50)
    print("处理时间估算")
    print("=" * 50)
    
    pending_count = stats['pending_count']
    
    # 估算参数
    avg_api_time = 5  # 平均API调用时间(秒)
    avg_db_time = 0.1  # 平均数据库操作时间(秒)
    avg_record_time = avg_api_time + avg_db_time
    
    # 考虑并发处理
    concurrent_factor = min(config.max_workers, pending_count)
    
    # 估算总时间
    estimated_seconds = (pending_count * avg_record_time) / concurrent_factor
    
    # 转换为小时和分钟
    hours = int(estimated_seconds // 3600)
    minutes = int((estimated_seconds % 3600) // 60)
    seconds = int(estimated_seconds % 60)
    
    print(f"估算参数:")
    print(f"  待处理记录: {pending_count:,}")
    print(f"  并发线程数: {concurrent_factor}")
    print(f"  平均处理时间/记录: {avg_record_time}秒")
    
    print(f"\n预计处理时间: {hours}小时 {minutes}分钟 {seconds}秒")
    
    if hours > 24:
        days = hours // 24
        remaining_hours = hours % 24
        print(f"约 {days}天 {remaining_hours}小时")
    
    print("\n注意: 这只是粗略估算，实际时间可能因网络状况、API响应速度等因素而有所不同")


def start_processing(processor, config):
    """开始处理"""
    print("\n" + "=" * 50)
    print("开始处理")
    print("=" * 50)
    
    # 记录开始时间
    start_time = time.time()
    start_datetime = datetime.now()
    
    print(f"处理开始时间: {start_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"配置: {config.max_workers}线程, {config.batch_size}批次大小")
    print("\n处理中... (可以按 Ctrl+C 中断)")
    
    try:
        # 开始处理
        processor.start_processing()
        
        # 记录结束时间
        end_time = time.time()
        end_datetime = datetime.now()
        total_time = end_time - start_time
        
        print(f"\n处理完成!")
        print(f"结束时间: {end_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"总耗时: {total_time:.2f}秒 ({total_time/60:.2f}分钟)")
        
        return True
        
    except KeyboardInterrupt:
        print("\n\n用户中断处理")
        return False
    except Exception as e:
        print(f"\n处理过程中出错: {str(e)}")
        return False


def show_final_stats(processor):
    """显示最终统计信息"""
    print("\n" + "=" * 50)
    print("最终统计信息")
    print("=" * 50)
    
    try:
        stats = processor.get_processing_stats()
        
        if stats:
            print(f"\n处理结果:")
            print(f"  总记录数: {stats['total_count']:,}")
            print(f"  已处理记录: {stats['processed_count']:,}")
            print(f"  失败记录: {stats['failed_count']:,}")
            print(f"  剩余待处理: {stats['pending_count']:,}")
            print(f"  成功率: {stats['success_rate']:.2f}%")
            
            if stats['total_count'] > 0:
                completion_rate = (stats['processed_count'] + stats['failed_count']) / stats['total_count'] * 100
                print(f"  完成率: {completion_rate:.2f}%")
        
        # 检查日志文件
        log_file = 'job_processor.log'
        if os.path.exists(log_file):
            file_size = os.path.getsize(log_file)
            print(f"\n日志文件: {log_file} ({file_size:,} 字节)")
        
    except Exception as e:
        print(f"获取最终统计信息失败: {str(e)}")


def cleanup_and_recommendations():
    """清理和建议"""
    print("\n" + "=" * 50)
    print("清理和建议")
    print("=" * 50)
    
    print("\n处理完成后的建议:")
    print("1. 检查日志文件 job_processor.log 查看详细处理记录")
    print("2. 验证数据库中的处理结果")
    print("3. 如有失败记录，可以重新运行程序处理")
    print("4. 定期清理日志文件以节省磁盘空间")
    print("5. 监控系统资源使用情况")
    
    print("\n故障排除:")
    print("- 如果处理速度过慢，可以增加线程数")
    print("- 如果出现大量失败，检查网络连接和API配置")
    print("- 如果数据库连接问题，检查连接池配置")
    print("- 如果内存不足，减少线程数和批次大小")


def main():
    """主函数"""
    try:
        # 打印横幅
        print_banner()
        
        # 获取用户确认
        if not get_user_confirmation():
            print("\n用户取消操作，程序退出")
            return
        
        # 配置处理器
        config = configure_processor()
        processor = JobProcessor(config)
        
        # 预览数据
        if not preview_data(processor):
            print("\n数据预览失败或无待处理数据，程序退出")
            return
        
        # 估算处理时间
        stats = processor.get_processing_stats()
        if stats:
            estimate_processing_time(stats, config)
        
        # 最终确认
        final_confirm = input("\n确认开始处理? (y/n): ").strip().lower()
        if final_confirm not in ['y', 'yes', '是']:
            print("\n用户取消操作，程序退出")
            return
        
        # 开始处理
        success = start_processing(processor, config)
        
        # 显示最终统计
        show_final_stats(processor)
        
        # 清理和建议
        cleanup_and_recommendations()
        
        if success:
            print("\n🎉 处理成功完成!")
        else:
            print("\n⚠️ 处理未完全完成，请检查日志")
    
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n程序执行出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n程序结束")


if __name__ == "__main__":
    main()