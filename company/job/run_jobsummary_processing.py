#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
执行智联招聘jobSummary处理的主脚本

使用说明:
1. 确保数据库连接配置正确
2. 根据需要调整处理配置参数
3. 运行脚本开始处理

注意: 此脚本会实际修改数据库数据，请在使用前备份重要数据
"""

import sys
import logging
from datetime import datetime
from company.job.multithread_jobsummary_processor import JobSummaryProcessor, ProcessConfig

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jobsummary_processing.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def confirm_processing():
    """确认是否继续处理"""
    print("\n" + "=" * 60)
    print("⚠️  重要提醒 ⚠️")
    print("=" * 60)
    print("此操作将修改数据库中的数据！")
    print("操作内容: 将processed_jobsummary字段的值更新到processed_info的jobSummary字段")
    print("影响范围: zhilian_job表中train_type='3'的记录")
    print("\n建议在执行前：")
    print("1. 备份相关数据表")
    print("2. 在测试环境中验证")
    print("3. 确认处理逻辑正确")
    print("=" * 60)
    
    while True:
        response = input("\n是否继续执行处理？(yes/no): ").strip().lower()
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            return False
        else:
            print("请输入 'yes' 或 'no'")


def get_processing_config():
    """获取处理配置"""
    print("\n配置处理参数:")
    print("-" * 30)
    
    # 批次大小
    while True:
        try:
            batch_size = input("批次大小 (默认50): ").strip()
            batch_size = int(batch_size) if batch_size else 50
            if batch_size > 0:
                break
            else:
                print("批次大小必须大于0")
        except ValueError:
            print("请输入有效的数字")
    
    # 线程数
    while True:
        try:
            max_workers = input("最大线程数 (默认6): ").strip()
            max_workers = int(max_workers) if max_workers else 6
            if max_workers > 0:
                break
            else:
                print("线程数必须大于0")
        except ValueError:
            print("请输入有效的数字")
    
    # 训练类型
    train_type = input("训练类型 (默认'3'): ").strip()
    train_type = train_type if train_type else '3'
    
    # 表名
    table_name = input("表名 (默认'zhilian_job'): ").strip()
    table_name = table_name if table_name else 'zhilian_job'
    
    config = ProcessConfig(
        batch_size=batch_size,
        max_workers=max_workers,
        train_type=train_type,
        table_name=table_name
    )
    
    print("\n配置确认:")
    print(f"  批次大小: {config.batch_size}")
    print(f"  最大线程数: {config.max_workers}")
    print(f"  训练类型: {config.train_type}")
    print(f"  表名: {config.table_name}")
    
    return config


def preview_data(processor, config):
    """预览待处理数据"""
    logger.info("正在查询待处理数据...")
    
    try:
        data = processor.fetch_data_to_process(config)
        
        logger.info(f"查询结果: 共找到 {len(data)} 条待处理记录")
        
        if len(data) == 0:
            logger.warning("没有找到需要处理的数据")
            logger.info("可能的原因:")
            logger.info(f"1. train_type='{config.train_type}' 的记录不存在")
            logger.info("2. processed_info 或 processed_jobsummary 字段为空")
            logger.info("3. 数据已经处理过")
            return False
        
        # 显示前几条记录的信息
        logger.info("\n前5条记录预览:")
        for i, (record_id, processed_info, processed_jobsummary) in enumerate(data[:5]):
            logger.info(f"记录 {i+1}:")
            logger.info(f"  ID: {record_id}")
            logger.info(f"  processed_info长度: {len(processed_info) if processed_info else 0}")
            logger.info(f"  processed_jobsummary长度: {len(processed_jobsummary) if processed_jobsummary else 0}")
        
        if len(data) > 5:
            logger.info(f"... 还有 {len(data) - 5} 条记录")
        
        return True
        
    except Exception as e:
        logger.error(f"查询数据时出错: {str(e)}")
        return False


def execute_processing(processor, config):
    """执行处理"""
    logger.info("开始执行数据处理...")
    start_time = datetime.now()
    
    try:
        # 执行多线程处理
        stats = processor.process_data_multithread(config)
        
        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()
        
        # 输出详细统计
        logger.info("\n" + "=" * 50)
        logger.info("处理完成！详细统计:")
        logger.info("=" * 50)
        logger.info(f"总记录数: {stats['total']}")
        logger.info(f"成功处理: {stats['processed']}")
        logger.info(f"成功更新: {stats['updated']}")
        logger.info(f"错误数量: {stats['errors']}")
        logger.info(f"处理耗时: {stats['duration_seconds']:.2f} 秒")
        logger.info(f"总耗时: {total_duration:.2f} 秒")
        
        if stats['total'] > 0:
            success_rate = (stats['updated'] / stats['total']) * 100
            throughput = stats['total'] / stats['duration_seconds'] if stats['duration_seconds'] > 0 else 0
            logger.info(f"成功率: {success_rate:.2f}%")
            logger.info(f"处理速度: {throughput:.2f} 记录/秒")
        
        # 处理结果评估
        if stats['errors'] == 0:
            logger.info("✅ 所有记录处理成功！")
        elif stats['errors'] < stats['total'] * 0.1:  # 错误率小于10%
            logger.warning(f"⚠️  处理完成，但有 {stats['errors']} 个错误（错误率较低）")
        else:
            logger.error(f"❌ 处理完成，但错误较多: {stats['errors']} 个错误")
        
        return stats
        
    except Exception as e:
        logger.error(f"处理过程中发生严重错误: {str(e)}")
        return None


def main():
    """主函数"""
    logger.info("智联招聘jobSummary处理器")
    logger.info("=" * 40)
    
    try:
        # 1. 确认处理
        if not confirm_processing():
            logger.info("用户取消操作")
            return
        
        # 2. 获取配置
        config = get_processing_config()
        
        # 3. 创建处理器
        logger.info("\n初始化处理器...")
        processor = JobSummaryProcessor()
        
        # 4. 预览数据
        logger.info("\n预览待处理数据...")
        if not preview_data(processor, config):
            logger.info("没有数据需要处理，程序退出")
            return
        
        # 5. 最终确认
        print("\n" + "-" * 40)
        final_confirm = input("确认开始处理？(yes/no): ").strip().lower()
        if final_confirm not in ['yes', 'y']:
            logger.info("用户取消操作")
            return
        
        # 6. 执行处理
        stats = execute_processing(processor, config)
        
        if stats:
            logger.info("\n处理任务完成！")
            logger.info("请检查日志文件 'jobsummary_processing.log' 获取详细信息")
        else:
            logger.error("处理任务失败！")
            sys.exit(1)
        
    except KeyboardInterrupt:
        logger.warning("\n用户中断操作")
        sys.exit(1)
    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()