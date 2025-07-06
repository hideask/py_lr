# -*- coding: utf-8 -*-
"""
智联招聘简历数据处理器使用示例
展示如何使用ZhilianResumeProcessor工具类的不同功能
"""

import logging
from zhilian_resume_processor import ZhilianResumeProcessor, ZhilianResumeProcessorConfig

def example_basic_usage():
    """
    基础使用示例：使用默认配置处理所有数据
    """
    print("=== 基础使用示例 ===")
    
    # 使用默认配置
    processor = ZhilianResumeProcessor()
    
    # 开始处理
    processor.start_processing()

def example_custom_config():
    """
    自定义配置示例：根据需要启用或禁用特定功能
    """
    print("=== 自定义配置示例 ===")
    
    # 创建自定义配置
    config = ZhilianResumeProcessorConfig()
    
    # 基础配置
    config.num_threads = 8  # 使用8个线程
    config.batch_size = 100  # 每批处理100条数据
    
    # 功能开关
    config.enable_deduplication = True  # 启用去重
    config.enable_zhijin_processing = True  # 启用"至今"处理
    config.enable_certificate_splitting = True  # 启用证书分割
    config.enable_format_cleaning = True  # 启用格式清洗
    
    # 去重配置
    config.deduplicate_education = True
    config.deduplicate_work = True
    config.deduplicate_project = True
    
    # "至今"处理配置
    config.zhijin_end_date = '2025.06'  # 自定义"至今"替换日期
    config.process_work_zhijin = True
    config.process_project_zhijin = True
    config.process_education_zhijin = True
    
    # 日志配置
    config.log_level = logging.DEBUG
    config.log_file = 'custom_processor.log'
    config.enable_console_log = True
    
    # 创建处理器
    processor = ZhilianResumeProcessor(config)
    
    # 开始处理
    processor.start_processing()

def example_deduplication_only():
    """
    仅去重示例：只启用去重功能，不处理"至今"数据
    """
    print("=== 仅去重示例 ===")
    
    config = ZhilianResumeProcessorConfig()
    
    # 只启用去重功能
    config.enable_deduplication = True
    config.enable_zhijin_processing = False  # 禁用"至今"处理
    config.enable_certificate_splitting = False  # 禁用证书分割
    
    # 去重配置
    config.deduplicate_education = True
    config.deduplicate_work = True
    config.deduplicate_project = True
    
    processor = ZhilianResumeProcessor(config)
    processor.start_processing()

def example_zhijin_only():
    """
    仅"至今"处理示例：只处理"至今"数据，不进行去重
    """
    print("=== 仅'至今'处理示例 ===")
    
    config = ZhilianResumeProcessorConfig()
    
    # 只启用"至今"处理
    config.enable_deduplication = False  # 禁用去重
    config.enable_zhijin_processing = True
    config.enable_certificate_splitting = False  # 禁用证书分割
    
    # "至今"处理配置
    config.zhijin_end_date = '2025.05'
    config.process_work_zhijin = True
    config.process_project_zhijin = True
    config.process_education_zhijin = True
    config.update_work_years = True  # 更新work_years字段
    
    processor = ZhilianResumeProcessor(config)
    processor.start_processing()

def example_certificate_splitting_only():
    """
    仅证书分割示例：只处理证书分割，不进行其他处理
    """
    print("=== 仅证书分割示例 ===")
    
    config = ZhilianResumeProcessorConfig()
    
    # 只启用证书分割
    config.enable_deduplication = False
    config.enable_zhijin_processing = False
    config.enable_certificate_splitting = True
    
    processor = ZhilianResumeProcessor(config)
    processor.start_processing()

def example_single_resume_processing():
    """
    单个简历处理示例：处理指定ID的简历
    """
    print("=== 单个简历处理示例 ===")
    
    config = ZhilianResumeProcessorConfig()
    config.enable_deduplication = True
    config.enable_zhijin_processing = True
    config.enable_certificate_splitting = True
    
    processor = ZhilianResumeProcessor(config)
    
    # 处理指定ID的简历
    resume_id = 12345  # 替换为实际的简历ID
    result = processor.process_single_resume_by_id(resume_id)
    
    print(f"处理结果: {result}")

def example_high_performance_config():
    """
    高性能配置示例：适用于大量数据处理
    """
    print("=== 高性能配置示例 ===")
    
    config = ZhilianResumeProcessorConfig()
    
    # 高性能配置
    config.num_threads = 20  # 增加线程数
    config.batch_size = 200  # 增加批次大小
    
    # 启用所有功能
    config.enable_deduplication = True
    config.enable_zhijin_processing = True
    config.enable_certificate_splitting = True
    
    # 日志配置（减少日志输出以提高性能）
    config.log_level = logging.WARNING
    config.enable_console_log = False  # 禁用控制台日志
    config.log_file = 'high_performance.log'
    
    processor = ZhilianResumeProcessor(config)
    processor.start_processing()

def example_debug_config():
    """
    调试配置示例：适用于开发和调试
    """
    print("=== 调试配置示例 ===")
    
    config = ZhilianResumeProcessorConfig()
    
    # 调试配置
    config.num_threads = 1  # 单线程便于调试
    config.batch_size = 10  # 小批次
    
    # 启用所有功能
    config.enable_deduplication = True
    config.enable_zhijin_processing = True
    config.enable_certificate_splitting = True
    
    # 详细日志
    config.log_level = logging.DEBUG
    config.enable_console_log = True
    config.log_file = 'debug.log'
    
    processor = ZhilianResumeProcessor(config)
    processor.start_processing()

def example_selective_processing():
    """
    选择性处理示例：只处理特定类型的数据
    """
    print("=== 选择性处理示例 ===")
    
    config = ZhilianResumeProcessorConfig()
    
    # 启用去重，但只处理工作经历和项目经历
    config.enable_deduplication = True
    config.deduplicate_education = False  # 不处理教育经历
    config.deduplicate_work = True  # 处理工作经历
    config.deduplicate_project = True  # 处理项目经历
    
    # 启用"至今"处理，但只处理工作经历
    config.enable_zhijin_processing = True
    config.process_work_zhijin = True  # 处理工作经历的"至今"
    config.process_project_zhijin = False  # 不处理项目经历的"至今"
    config.process_education_zhijin = False  # 不处理教育经历的"至今"
    
    # 禁用证书分割
    config.enable_certificate_splitting = False
    
    processor = ZhilianResumeProcessor(config)
    processor.start_processing()

if __name__ == "__main__":
    print("智联招聘简历数据处理器使用示例")
    print("请选择要运行的示例:")
    print("1. 基础使用示例")
    print("2. 自定义配置示例")
    print("3. 仅去重示例")
    print("4. 仅'至今'处理示例")
    print("5. 仅证书分割示例")
    print("6. 单个简历处理示例")
    print("7. 高性能配置示例")
    print("8. 调试配置示例")
    print("9. 选择性处理示例")
    
    choice = input("请输入选择 (1-9): ").strip()
    
    examples = {
        '1': example_basic_usage,
        '2': example_custom_config,
        '3': example_deduplication_only,
        '4': example_zhijin_only,
        '5': example_certificate_splitting_only,
        '6': example_single_resume_processing,
        '7': example_high_performance_config,
        '8': example_debug_config,
        '9': example_selective_processing
    }
    
    if choice in examples:
        examples[choice]()
    else:
        print("无效选择，运行基础使用示例")
        example_basic_usage()