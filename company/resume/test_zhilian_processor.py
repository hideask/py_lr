# -*- coding: utf-8 -*-
"""
智联招聘简历数据处理器测试脚本
用于验证ZhilianResumeProcessor工具类的功能
"""

import json
import logging
from zhilian_resume_processor import ZhilianResumeProcessor, ZhilianResumeProcessorConfig

def test_data_processing():
    """
    测试数据处理功能
    """
    print("=== 测试数据处理功能 ===")
    
    # 创建测试配置
    config = ZhilianResumeProcessorConfig()
    config.log_level = logging.DEBUG
    config.enable_console_log = True
    
    # 创建处理器
    processor = ZhilianResumeProcessor(config)
    
    # 测试数据
    test_resume_data = {
        "resume": {
            "educationExperiences": [
                {
                    "schoolName": "北京大学",
                    "major": "计算机科学",
                    "educationTimeLabel": "2018.09 - 至今 (3年 8个月)"
                },
                {
                    "schoolName": "北京大学",
                    "major": "计算机科学",
                    "educationTimeLabel": "2018.09 - 2022.06"
                },
                {
                    "schoolName": "清华大学",
                    "major": "软件工程",
                    "educationTimeLabel": "2016.09 - 2018.06"
                }
            ],
            "workExperiences": [
                {
                    "orgName": "腾讯科技",
                    "jobTitle": "软件工程师",
                    "timeLabel": "2022.07 - 至今 (2年 10个月)"
                },
                {
                    "orgName": "腾讯科技",
                    "jobTitle": "软件工程师",
                    "timeLabel": "2022.07 - 至今 (2年 10个月)"
                },
                {
                    "orgName": "阿里巴巴",
                    "jobTitle": "前端工程师",
                    "timeLabel": "2020.06 - 2022.06"
                }
            ],
            "projectExperiences": [
                {
                    "name": "电商平台开发",
                    "timeLabel": "2023.01 - 至今 (1年 4个月)"
                },
                {
                    "name": "电商平台开发项目",
                    "timeLabel": "2023.01 - 至今 (1年 4个月)"
                },
                {
                    "name": "移动应用开发",
                    "timeLabel": "2022.03 - 2022.12"
                }
            ],
            "certificates": [
                {
                    "name": "软件设计师，系统分析师，项目管理师",
                    "issueDate": "2023.05"
                },
                {
                    "name": "英语四级；英语六级",
                    "issueDate": "2022.12"
                }
            ]
        }
    }
    
    print("原始数据:")
    print(f"教育经历数量: {len(test_resume_data['resume']['educationExperiences'])}")
    print(f"工作经历数量: {len(test_resume_data['resume']['workExperiences'])}")
    print(f"项目经历数量: {len(test_resume_data['resume']['projectExperiences'])}")
    print(f"证书数量: {len(test_resume_data['resume']['certificates'])}")
    
    # 处理数据
    processed_data = processor.process_resume_data(test_resume_data)
    
    print("\n处理后数据:")
    print(f"教育经历数量: {len(processed_data['resume']['educationExperiences'])}")
    print(f"工作经历数量: {len(processed_data['resume']['workExperiences'])}")
    print(f"项目经历数量: {len(processed_data['resume']['projectExperiences'])}")
    print(f"证书数量: {len(processed_data['resume']['certificates'])}")
    
    # 检查"至今"处理
    print("\n'至今'处理结果:")
    for i, edu in enumerate(processed_data['resume']['educationExperiences']):
        if 'educationTimeLabel' in edu:
            print(f"教育经历 {i+1}: {edu['educationTimeLabel']}")
    
    for i, work in enumerate(processed_data['resume']['workExperiences']):
        if 'timeLabel' in work:
            print(f"工作经历 {i+1}: {work['timeLabel']}")
    
    for i, proj in enumerate(processed_data['resume']['projectExperiences']):
        if 'timeLabel' in proj:
            print(f"项目经历 {i+1}: {proj['timeLabel']}")
    
    # 检查证书分割
    print("\n证书分割结果:")
    for i, cert in enumerate(processed_data['resume']['certificates']):
        print(f"证书 {i+1}: {cert['name']}")
    
    return processed_data

def test_config_options():
    """
    测试不同配置选项
    """
    print("\n=== 测试配置选项 ===")
    
    # 测试仅去重配置
    print("\n--- 测试仅去重配置 ---")
    config1 = ZhilianResumeProcessorConfig()
    config1.enable_deduplication = True
    config1.enable_zhijin_processing = False
    config1.enable_certificate_splitting = False
    config1.log_level = logging.WARNING
    
    processor1 = ZhilianResumeProcessor(config1)
    print(f"去重功能: {config1.enable_deduplication}")
    print(f"至今处理: {config1.enable_zhijin_processing}")
    print(f"证书分割: {config1.enable_certificate_splitting}")
    
    # 测试仅"至今"处理配置
    print("\n--- 测试仅'至今'处理配置 ---")
    config2 = ZhilianResumeProcessorConfig()
    config2.enable_deduplication = False
    config2.enable_zhijin_processing = True
    config2.enable_certificate_splitting = False
    config2.zhijin_end_date = '2025.06'
    config2.log_level = logging.WARNING
    
    processor2 = ZhilianResumeProcessor(config2)
    print(f"去重功能: {config2.enable_deduplication}")
    print(f"至今处理: {config2.enable_zhijin_processing}")
    print(f"至今结束日期: {config2.zhijin_end_date}")
    print(f"证书分割: {config2.enable_certificate_splitting}")
    
    # 测试仅证书分割配置
    print("\n--- 测试仅证书分割配置 ---")
    config3 = ZhilianResumeProcessorConfig()
    config3.enable_deduplication = False
    config3.enable_zhijin_processing = False
    config3.enable_certificate_splitting = True
    config3.log_level = logging.WARNING
    
    processor3 = ZhilianResumeProcessor(config3)
    print(f"去重功能: {config3.enable_deduplication}")
    print(f"至今处理: {config3.enable_zhijin_processing}")
    print(f"证书分割: {config3.enable_certificate_splitting}")

def test_time_processing():
    """
    测试时间处理功能
    """
    print("\n=== 测试时间处理功能 ===")
    
    config = ZhilianResumeProcessorConfig()
    config.log_level = logging.WARNING
    processor = ZhilianResumeProcessor(config)
    
    # 测试时间解析
    test_times = [
        "2022.07 - 至今 (2年 10个月)",
        "2023.01 - 至今 (1年 4个月)",
        "2020.06 - 至今",
        "2022.03 - 2022.12",
        "无效时间格式"
    ]
    
    print("时间解析测试:")
    for time_str in test_times:
        start, end, duration = processor.parse_time_period(time_str)
        print(f"原始: {time_str}")
        print(f"解析: 开始={start}, 结束={end}, 持续时间={duration}")
        
        if '至今' in time_str:
            new_time, updated = processor.update_time_label(time_str)
            print(f"更新: {new_time} (是否更新: {updated})")
        print()

def test_certificate_splitting():
    """
    测试证书分割功能
    """
    print("\n=== 测试证书分割功能 ===")
    
    config = ZhilianResumeProcessorConfig()
    config.log_level = logging.WARNING
    processor = ZhilianResumeProcessor(config)
    
    test_certificates = [
        {"name": "软件设计师，系统分析师，项目管理师", "issueDate": "2023.05"},
        {"name": "英语四级；英语六级", "issueDate": "2022.12"},
        {"name": "驾驶证、会计证、教师资格证", "issueDate": "2021.08"},
        {"name": "单个证书", "issueDate": "2020.06"}
    ]
    
    print("证书分割测试:")
    processed_certs = processor.process_certificates(test_certificates)
    
    print(f"原始证书数量: {len(test_certificates)}")
    print(f"分割后证书数量: {len(processed_certs)}")
    
    print("\n分割结果:")
    for i, cert in enumerate(processed_certs):
        print(f"{i+1}. {cert['name']} (发证日期: {cert['issueDate']})")

def test_data_comparison():
    """
    测试数据变化检测
    """
    print("\n=== 测试数据变化检测 ===")
    
    config = ZhilianResumeProcessorConfig()
    config.log_level = logging.WARNING
    processor = ZhilianResumeProcessor(config)
    
    # 原始数据
    original_data = {
        "resume": {
            "educationExperiences": [
                {"schoolName": "北京大学", "major": "计算机科学"}
            ]
        }
    }
    
    # 相同数据
    same_data = {
        "resume": {
            "educationExperiences": [
                {"schoolName": "北京大学", "major": "计算机科学"}
            ]
        }
    }
    
    # 不同数据
    different_data = {
        "resume": {
            "educationExperiences": [
                {"schoolName": "清华大学", "major": "计算机科学"}
            ]
        }
    }
    
    print(f"原始数据 vs 相同数据: {processor.has_data_changed(original_data, same_data)}")
    print(f"原始数据 vs 不同数据: {processor.has_data_changed(original_data, different_data)}")

def main():
    """
    主测试函数
    """
    print("智联招聘简历数据处理器测试")
    print("=" * 50)
    
    try:
        # 运行各项测试
        test_data_processing()
        test_config_options()
        test_time_processing()
        test_certificate_splitting()
        test_data_comparison()
        
        print("\n=== 所有测试完成 ===")
        print("如果没有错误信息，说明工具类基本功能正常")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()