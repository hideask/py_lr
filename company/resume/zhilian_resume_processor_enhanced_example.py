# -*- coding: utf-8 -*-
"""
智联招聘简历数据处理器增强示例
展示合并resume_process.py后的新功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from zhilian_resume_processor import ZhilianResumeProcessor, ZhilianResumeProcessorConfig

def example_excel_export():
    """Excel导出功能示例"""
    print("=== Excel导出功能示例 ===")
    
    # 创建配置
    config = ZhilianResumeProcessorConfig()
    config.enable_excel_export = True
    config.excel_start_id = 1000
    config.excel_end_id = 2000
    config.excel_output_dir = "./output/"
    
    # 创建处理器
    processor = ZhilianResumeProcessor(config)
    
    try:
        # 导出智联招聘简历
        print("导出智联招聘简历数据...")
        output_file = processor.export_resumes_to_excel(platform="", limit=100)
        print(f"导出完成，文件路径: {output_file}")
        
        # 导出SC平台简历
        print("\n导出SC平台简历数据...")
        output_file = processor.export_resumes_to_excel(platform="sc", limit=50)
        print(f"导出完成，文件路径: {output_file}")
        
    except Exception as e:
        print(f"导出失败: {e}")

def example_job_info_extraction():
    """工作信息提取功能示例"""
    print("\n=== 工作信息提取功能示例 ===")
    
    # 创建配置
    config = ZhilianResumeProcessorConfig()
    
    # 创建处理器
    processor = ZhilianResumeProcessor(config)
    
    try:
        # 多线程提取工作信息
        print("开始提取简历工作信息...")
        result = processor.process_job_info_extraction(max_workers=5)
        
        if result['success']:
            print(f"工作信息提取完成！")
            print(f"成功处理: {result['processed_count']} 条")
            print(f"失败: {result['failed_count']} 条")
            print(f"总耗时: {result['total_time']:.2f} 秒")
        else:
            print(f"工作信息提取失败: {result['message']}")
            
    except Exception as e:
        print(f"工作信息提取异常: {e}")

def example_data_filtering_only():
    """仅数据过滤功能示例"""
    print("\n=== 仅数据过滤功能示例 ===")
    
    # 创建配置
    config = ZhilianResumeProcessorConfig()
    config.enable_data_filtering = True
    config.enable_deduplication = False
    config.enable_zhijin_processing = False
    config.enable_certificate_splitting = False
    
    # 自定义保留字段
    config.retain_fields = {
        "user": {
            "name": True,
            "genderLabel": True,
            "age": True,
            "maxEducationLabel": True
        },
        "resume": {
            "workExperiences": {
                "orgName": True,
                "jobTitle": True,
                "timeLabel": True
            }
        }
    }
    
    # 创建处理器
    processor = ZhilianResumeProcessor(config)
    
    try:
        # 仅执行数据过滤
        print("开始执行数据过滤...")
        result = processor.process_data_filtering_only(limit=100)
        
        if result['success']:
            print(f"数据过滤完成！")
            print(f"成功处理: {result['processed_count']} 条")
            print(f"失败: {result['failed_count']} 条")
            print(f"总耗时: {result['total_time']:.2f} 秒")
        else:
            print(f"数据过滤失败: {result['message']}")
            
    except Exception as e:
        print(f"数据过滤异常: {e}")

def example_sc_platform_processing():
    """SC平台简历处理示例"""
    print("\n=== SC平台简历处理示例 ===")
    
    # 创建配置
    config = ZhilianResumeProcessorConfig()
    config.enable_html_cleaning = True
    config.enable_data_filtering = True
    
    # 创建处理器
    processor = ZhilianResumeProcessor(config)
    
    try:
        # 处理SC平台简历
        print("开始处理SC平台简历...")
        result = processor.process_sc_platform_resumes()
        
        if result['success']:
            print(f"SC平台简历处理完成！")
            print(f"成功处理: {result['processed_count']} 条")
            print(f"失败: {result['failed_count']} 条")
            print(f"总耗时: {result['total_time']:.2f} 秒")
        else:
            print(f"SC平台简历处理失败: {result['message']}")
            
    except Exception as e:
        print(f"SC平台简历处理异常: {e}")

def example_comprehensive_processing():
    """综合处理功能示例"""
    print("\n=== 综合处理功能示例 ===")
    
    # 创建配置
    config = ZhilianResumeProcessorConfig()
    
    # 启用所有功能
    config.enable_deduplication = True
    config.enable_zhijin_processing = True
    config.enable_certificate_splitting = True
    config.enable_format_cleaning = True
    config.enable_data_filtering = True
    config.enable_html_cleaning = True
    
    # 设置线程和批次
    config.num_threads = 8
    config.batch_size = 50
    
    # 创建处理器
    processor = ZhilianResumeProcessor(config)
    
    try:
        # 启动综合处理
        print("开始综合处理简历数据...")
        processor.start_processing()
        
    except Exception as e:
        print(f"综合处理异常: {e}")

def example_single_resume_processing():
    """单个简历处理示例"""
    print("\n=== 单个简历处理示例 ===")
    
    # 创建配置
    config = ZhilianResumeProcessorConfig()
    
    # 创建处理器
    processor = ZhilianResumeProcessor(config)
    
    try:
        # 处理指定ID的简历
        resume_id = 12345  # 替换为实际的简历ID
        print(f"处理简历ID: {resume_id}")
        result = processor.process_single_resume_by_id(resume_id)
        
        if result['success']:
            print(f"简历处理完成: {result['message']}")
            print(f"数据是否有变化: {result.get('data_changed', 'Unknown')}")
        else:
            print(f"简历处理失败: {result['message']}")
            
    except Exception as e:
        print(f"单个简历处理异常: {e}")

def main():
    """主函数"""
    print("智联招聘简历数据处理器增强功能演示")
    print("=" * 50)
    
    # 注意：以下示例需要数据库连接，请确保数据库配置正确
    
    # 1. Excel导出功能
    # example_excel_export()
    
    # 2. 工作信息提取功能
    # example_job_info_extraction()
    
    # 3. 仅数据过滤功能
    # example_data_filtering_only()
    
    # 4. SC平台简历处理
    # example_sc_platform_processing()
    
    # 5. 综合处理功能
    # example_comprehensive_processing()
    
    # 6. 单个简历处理
    # example_single_resume_processing()
    
    print("\n演示完成！")
    print("\n注意事项:")
    print("1. 请确保数据库连接配置正确")
    print("2. 根据实际需要取消相应示例的注释")
    print("3. 调整配置参数以适应您的环境")
    print("4. 建议先在测试环境中运行")

if __name__ == "__main__":
    main()