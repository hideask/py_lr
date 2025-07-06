#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智联招聘jobSummary多线程处理器使用示例

本文件展示了如何使用JobSummaryProcessor来处理不同场景的数据。
包含了各种配置选项和使用场景的示例。
"""

from multithread_jobsummary_processor import JobSummaryProcessor, ProcessConfig
import logging
import time
from typing import Dict, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def basic_usage_example():
    """基本使用示例"""
    logger.info("=== 基本使用示例 ===")
    
    # 创建处理器
    processor = JobSummaryProcessor()
    
    # 基本配置
    config = ProcessConfig(
        batch_size=50,
        max_workers=6,
        train_type='3',
        table_name='zhilian_job'
    )
    
    try:
        # 执行处理
        logger.info("开始处理智联招聘数据...")
        stats = processor.process_data_multithread(config)
        
        # 输出结果
        logger.info("处理完成！")
        logger.info(f"总记录数: {stats['total']}")
        logger.info(f"成功处理: {stats['processed']}")
        logger.info(f"成功更新: {stats['updated']}")
        logger.info(f"错误数量: {stats['errors']}")
        logger.info(f"处理耗时: {stats['duration_seconds']:.2f} 秒")
        
    except Exception as e:
        logger.error(f"处理失败: {str(e)}")


def custom_config_example():
    """自定义配置示例"""
    logger.info("=== 自定义配置示例 ===")
    
    # 自定义数据库配置
    custom_db_config = {
        "dbname": "yhaimg",
        "user": "yhaimg",
        "password": "Zq*6^pD6g2%JJ!z8",
        "host": "172.31.255.227",
        "port": "5588"
    }
    
    # 创建处理器（使用自定义数据库配置）
    processor = JobSummaryProcessor(custom_db_config)
    
    # 高性能配置
    high_performance_config = ProcessConfig(
        batch_size=100,    # 大批次
        max_workers=12,    # 更多线程
        train_type='3',
        table_name='zhilian_job'
    )
    
    try:
        logger.info("使用高性能配置处理数据...")
        stats = processor.process_data_multithread(high_performance_config)
        logger.info(f"高性能处理完成，耗时: {stats['duration_seconds']:.2f} 秒")
        
    except Exception as e:
        logger.error(f"高性能处理失败: {str(e)}")


def batch_size_optimization_example():
    """批次大小优化示例"""
    logger.info("=== 批次大小优化示例 ===")
    
    processor = JobSummaryProcessor()
    batch_sizes = [20, 50, 100, 200]
    
    # 测试不同批次大小的性能
    for batch_size in batch_sizes:
        config = ProcessConfig(
            batch_size=batch_size,
            max_workers=6,
            train_type='3',
            table_name='zhilian_job'
        )
        
        try:
            logger.info(f"测试批次大小: {batch_size}")
            
            # 只获取数据，不实际处理（避免重复更新）
            data = processor.fetch_data_to_process(config)
            logger.info(f"批次大小 {batch_size}: 可处理 {len(data)} 条记录")
            
            # 如果需要实际处理，取消注释下面的代码
            # start_time = time.time()
            # stats = processor.process_data_multithread(config)
            # duration = time.time() - start_time
            # logger.info(f"批次大小 {batch_size}: 耗时 {duration:.2f} 秒")
            
        except Exception as e:
            logger.error(f"批次大小 {batch_size} 测试失败: {str(e)}")


def thread_count_optimization_example():
    """线程数量优化示例"""
    logger.info("=== 线程数量优化示例 ===")
    
    processor = JobSummaryProcessor()
    thread_counts = [2, 4, 6, 8, 10]
    
    # 测试不同线程数量的性能
    for thread_count in thread_counts:
        config = ProcessConfig(
            batch_size=50,
            max_workers=thread_count,
            train_type='3',
            table_name='zhilian_job'
        )
        
        try:
            logger.info(f"测试线程数量: {thread_count}")
            
            # 只获取数据，不实际处理
            data = processor.fetch_data_to_process(config)
            logger.info(f"线程数 {thread_count}: 可处理 {len(data)} 条记录")
            
            # 如果需要实际处理，取消注释下面的代码
            # start_time = time.time()
            # stats = processor.process_data_multithread(config)
            # duration = time.time() - start_time
            # logger.info(f"线程数 {thread_count}: 耗时 {duration:.2f} 秒")
            
        except Exception as e:
            logger.error(f"线程数 {thread_count} 测试失败: {str(e)}")


def single_vs_multithread_comparison():
    """单线程 vs 多线程性能对比"""
    logger.info("=== 单线程 vs 多线程性能对比 ===")
    
    processor = JobSummaryProcessor()
    
    # 小批量配置用于测试
    config = ProcessConfig(
        batch_size=20,
        max_workers=4,
        train_type='3',
        table_name='zhilian_job'
    )
    
    try:
        # 获取待处理数据
        data = processor.fetch_data_to_process(config)
        logger.info(f"待处理数据量: {len(data)} 条")
        
        if len(data) == 0:
            logger.info("没有待处理数据，跳过性能对比")
            return
        
        # 注意：实际运行时请谨慎，避免重复更新数据
        logger.warning("注意：性能对比将实际修改数据库数据")
        logger.warning("如需执行，请取消注释下面的代码")
        
        # 取消注释下面的代码来执行实际的性能对比
        # logger.info("开始单线程处理...")
        # single_stats = processor.process_data_single_thread(config)
        # 
        # logger.info("开始多线程处理...")
        # multi_stats = processor.process_data_multithread(config)
        # 
        # # 对比结果
        # logger.info("性能对比结果:")
        # logger.info(f"单线程耗时: {single_stats['duration_seconds']:.2f} 秒")
        # logger.info(f"多线程耗时: {multi_stats['duration_seconds']:.2f} 秒")
        # 
        # if single_stats['duration_seconds'] > 0:
        #     speedup = single_stats['duration_seconds'] / multi_stats['duration_seconds']
        #     logger.info(f"加速比: {speedup:.2f}x")
        
    except Exception as e:
        logger.error(f"性能对比失败: {str(e)}")


def error_handling_example():
    """错误处理示例"""
    logger.info("=== 错误处理示例 ===")
    
    # 测试无效数据库配置
    try:
        logger.info("测试无效数据库配置...")
        invalid_db_config = {
            "dbname": "invalid_db",
            "user": "invalid_user",
            "password": "invalid_password",
            "host": "invalid_host",
            "port": "5432"
        }
        
        processor = JobSummaryProcessor(invalid_db_config)
        config = ProcessConfig(batch_size=10, max_workers=2)
        
        # 尝试获取数据（应该失败）
        data = processor.fetch_data_to_process(config)
        
    except Exception as e:
        logger.info(f"预期的数据库连接错误: {str(e)}")
    
    # 测试无效表名
    try:
        logger.info("测试无效表名...")
        processor = JobSummaryProcessor()
        invalid_config = ProcessConfig(
            batch_size=10,
            max_workers=2,
            train_type='3',
            table_name='non_existent_table'
        )
        
        # 尝试获取数据（应该失败）
        data = processor.fetch_data_to_process(invalid_config)
        
    except Exception as e:
        logger.info(f"预期的表不存在错误: {str(e)}")


def monitoring_example():
    """监控和日志示例"""
    logger.info("=== 监控和日志示例 ===")
    
    processor = JobSummaryProcessor()
    config = ProcessConfig(
        batch_size=30,
        max_workers=4,
        train_type='3',
        table_name='zhilian_job'
    )
    
    try:
        # 获取处理前的统计
        data = processor.fetch_data_to_process(config)
        logger.info(f"处理前统计: 待处理记录 {len(data)} 条")
        
        if len(data) > 0:
            # 显示处理进度（模拟）
            logger.info("开始处理，将显示进度信息...")
            
            # 实际处理（取消注释来执行）
            # stats = processor.process_data_multithread(config)
            # 
            # # 详细统计
            # logger.info("处理完成统计:")
            # logger.info(f"  总记录数: {stats['total']}")
            # logger.info(f"  成功处理: {stats['processed']}")
            # logger.info(f"  成功更新: {stats['updated']}")
            # logger.info(f"  错误数量: {stats['errors']}")
            # logger.info(f"  处理耗时: {stats['duration_seconds']:.2f} 秒")
            # 
            # if stats['total'] > 0:
            #     success_rate = (stats['updated'] / stats['total']) * 100
            #     throughput = stats['total'] / stats['duration_seconds']
            #     logger.info(f"  成功率: {success_rate:.2f}%")
            #     logger.info(f"  处理速度: {throughput:.2f} 记录/秒")
        
    except Exception as e:
        logger.error(f"监控示例失败: {str(e)}")


def main():
    """主函数 - 运行所有示例"""
    logger.info("智联招聘jobSummary多线程处理器使用示例")
    logger.info("=" * 60)
    
    # 运行各种示例
    examples = [
        ("基本使用", basic_usage_example),
        ("自定义配置", custom_config_example),
        ("批次大小优化", batch_size_optimization_example),
        ("线程数量优化", thread_count_optimization_example),
        ("性能对比", single_vs_multithread_comparison),
        ("错误处理", error_handling_example),
        ("监控和日志", monitoring_example)
    ]
    
    for name, example_func in examples:
        try:
            logger.info(f"\n开始运行: {name}")
            example_func()
            logger.info(f"{name} 示例完成")
        except Exception as e:
            logger.error(f"{name} 示例失败: {str(e)}")
        
        logger.info("-" * 40)
    
    logger.info("\n所有示例运行完成！")
    logger.info("\n使用说明:")
    logger.info("1. 基本使用示例展示了最简单的使用方法")
    logger.info("2. 自定义配置示例展示了如何调整参数")
    logger.info("3. 优化示例帮助找到最佳的批次大小和线程数")
    logger.info("4. 性能对比展示了多线程的优势")
    logger.info("5. 错误处理示例展示了如何处理异常情况")
    logger.info("6. 监控示例展示了如何跟踪处理进度")
    logger.info("\n注意: 实际运行时请根据需要取消注释相关代码")


if __name__ == "__main__":
    main()