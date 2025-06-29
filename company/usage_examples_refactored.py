# -*- coding: utf-8 -*-
"""
重构后处理器的使用示例
展示如何使用新的通用处理器替代原有的处理逻辑
"""

import logging
from refactored_processors import (
    JobProcessor, 
    ResumeProcessor, 
    DataSyncProcessor, 
    CompareProcessor
)
from db_connection import DatabaseConnection

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def example_job_processing():
    """
    岗位处理示例
    替代原job_process.py中的处理逻辑
    """
    print("=== 岗位处理示例 ===")
    
    # 创建岗位处理器
    job_processor = JobProcessor()
    
    # 1. 清理HTML标签
    print("1. 清理岗位描述中的HTML标签...")
    cleaned_count = job_processor.clean_job_descriptions("sc_pub_recruitmentnet_job")
    print(f"清理了 {cleaned_count} 条记录")
    
    # 2. 处理岗位信息
    print("2. 处理岗位信息...")
    processed_count = job_processor.process_job_info("zhilian_job", limit=1000)
    print(f"处理了 {processed_count} 条记录")
    
    # 3. 使用通用查询方法
    print("3. 查询未处理的岗位数量...")
    unprocessed_jobs = job_processor.simple_query(
        "SELECT COUNT(*) FROM zhilian_job WHERE processed_info IS NULL"
    )
    print(f"未处理的岗位数量: {unprocessed_jobs[0][0] if unprocessed_jobs else 0}")


def example_resume_processing():
    """
    简历处理示例
    替代原resume_process.py中的处理逻辑
    """
    print("\n=== 简历处理示例 ===")
    
    # 创建简历处理器
    resume_processor = ResumeProcessor()
    
    # 1. 处理简历信息
    print("1. 处理简历信息...")
    processed_count = resume_processor.process_resume_info("zhilian_resume", limit=1000)
    print(f"处理了 {processed_count} 条记录")
    
    # 2. 查询处理进度
    print("2. 查询处理进度...")
    total_resumes = resume_processor.simple_query(
        "SELECT COUNT(*) FROM zhilian_resume"
    )
    processed_resumes = resume_processor.simple_query(
        "SELECT COUNT(*) FROM zhilian_resume WHERE resume_processed_info IS NOT NULL"
    )
    
    total = total_resumes[0][0] if total_resumes else 0
    processed = processed_resumes[0][0] if processed_resumes else 0
    progress = (processed / total * 100) if total > 0 else 0
    
    print(f"总简历数: {total}, 已处理: {processed}, 进度: {progress:.2f}%")


def example_data_sync():
    """
    数据同步示例
    替代原data_syn.py中的同步逻辑
    """
    print("\n=== 数据同步示例 ===")
    
    # 创建源数据库和目标数据库连接
    source_db = DatabaseConnection(
        dbname="source_db", 
        user="user", 
        password="password", 
        host="source_host", 
        port="5432"
    )
    
    target_db = DatabaseConnection(
        dbname="target_db", 
        user="user", 
        password="password", 
        host="target_host", 
        port="5432"
    )
    
    # 创建数据同步处理器
    sync_processor = DataSyncProcessor(source_db, target_db)
    
    # 同步表数据
    print("1. 同步岗位表...")
    try:
        sync_processor.sync_table(
            table_name="zhilian_job",
            source_columns=["id", "job_info", "processed_info"],
            target_columns=["id", "job_info", "processed_info"]
        )
        print("岗位表同步完成")
    except Exception as e:
        print(f"岗位表同步失败: {str(e)}")


def example_job_comparison():
    """
    岗位比较示例
    替代原job_compare.py中的比较逻辑
    """
    print("\n=== 岗位比较示例 ===")
    
    # 创建比较处理器
    compare_processor = CompareProcessor()
    
    # 1. 处理岗位比较
    print("1. 执行岗位比较...")
    compared_count = compare_processor.process_job_comparison("zhilian_job")
    print(f"比较了 {compared_count} 条记录")
    
    # 2. 查询比较结果统计
    print("2. 查询比较结果统计...")
    comparison_stats = compare_processor.simple_query(
        "SELECT COUNT(*) FROM zhilian_job WHERE compare_result IS NOT NULL"
    )
    print(f"已完成比较的记录数: {comparison_stats[0][0] if comparison_stats else 0}")


def example_custom_processing():
    """
    自定义处理示例
    展示如何扩展通用处理器实现特定需求
    """
    print("\n=== 自定义处理示例 ===")
    
    from common_db_processor import BaseQueryProcessor, CommonQueryBuilder
    
    class CustomProcessor(BaseQueryProcessor):
        """自定义处理器示例"""
        
        def process_record(self, record):
            """自定义记录处理逻辑"""
            record_id, data = record
            # 实现自定义处理逻辑
            processed_data = f"processed_{data}"
            return (record_id, processed_data)
    
    # 使用自定义处理器
    custom_processor = CustomProcessor()
    
    # 构建自定义查询
    query_sql = CommonQueryBuilder.build_select_with_condition(
        table_name="custom_table",
        fields=["id", "data"],
        where_condition="status = 'pending'",
        limit=100
    )
    
    update_sql = CommonQueryBuilder.build_update_by_id(
        table_name="custom_table",
        update_fields=["processed_data"]
    )
    
    print("执行自定义处理...")
    # 注意：这里只是示例，实际运行需要确保表存在
    # updated_count = custom_processor.batch_query_and_update(
    #     query_sql=query_sql,
    #     update_sql=update_sql
    # )
    # print(f"处理了 {updated_count} 条记录")
    print("自定义处理逻辑已定义（需要实际表结构支持）")


def example_batch_operations():
    """
    批量操作示例
    展示如何使用通用处理器进行批量操作
    """
    print("\n=== 批量操作示例 ===")
    
    from common_db_processor import BaseQueryProcessor
    
    processor = BaseQueryProcessor()
    
    # 1. 批量更新示例
    print("1. 批量更新示例...")
    affected_rows = processor.simple_update(
        "UPDATE zhilian_job SET process_start_time = NOW() WHERE processed_info IS NULL",
    )
    print(f"更新了 {affected_rows} 条记录的处理开始时间")
    
    # 2. 批量查询示例
    print("2. 批量查询示例...")
    recent_jobs = processor.simple_query(
        "SELECT id, name FROM zhilian_job WHERE created_at > NOW() - INTERVAL '7 days' LIMIT 10"
    )
    print(f"查询到 {len(recent_jobs)} 条最近7天的岗位记录")
    
    # 3. 条件查询示例
    print("3. 条件查询示例...")
    high_salary_jobs = processor.simple_query(
        "SELECT COUNT(*) FROM zhilian_job WHERE salary_real > %s",
        (10000,)
    )
    print(f"高薪岗位数量: {high_salary_jobs[0][0] if high_salary_jobs else 0}")


def main():
    """
    主函数，运行所有示例
    """
    print("重构后处理器使用示例")
    print("=" * 50)
    
    try:
        # 运行各种示例
        example_job_processing()
        example_resume_processing()
        # example_data_sync()  # 需要配置实际的数据库连接
        example_job_comparison()
        example_custom_processing()
        example_batch_operations()
        
        print("\n=== 所有示例执行完成 ===")
        
    except Exception as e:
        print(f"执行示例时出错: {str(e)}")
        logging.error(f"示例执行失败: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main()