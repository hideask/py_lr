# -*- coding: utf-8 -*-
"""
统一经历处理器测试脚本
测试工作经历、项目经历和教育经历的"至今"数据处理功能
"""

import json
import logging
from unified_experience_processor import UnifiedExperienceProcessor
from 简历数据去重处理脚本 import ResumeDataProcessor

def test_unified_processor():
    """
    测试统一处理器的功能
    """
    print("=== 测试统一经历处理器 ===")
    
    # 创建处理器
    processor = UnifiedExperienceProcessor()
    
    # 测试数据 - 包含工作经历、项目经历和教育经历的"至今"数据
    test_resume_data = {
        "resume": {
            "workExperiences": [
                {
                    "orgName": "腾讯科技有限公司",
                    "jobTitle": "高级软件工程师",
                    "timeLabel": "2020.03 - 至今 (4年 8个月)"
                },
                {
                    "orgName": "阿里巴巴集团",
                    "jobTitle": "软件工程师",
                    "timeLabel": "2018.06 - 2020.02 (1年 8个月)"
                }
            ],
            "projectExperiences": [
                {
                    "name": "微信小程序开发平台",
                    "timeLabel": "2021.01 - 至今 (4年 0个月)"
                },
                {
                    "name": "支付宝移动端优化",
                    "timeLabel": "2019.03 - 2020.01 (10个月)"
                }
            ],
            "educationExperiences": [
                {
                    "schoolName": "清华大学",
                    "major": "计算机科学与技术",
                    "educationTimeLabel": "2014.09 - 至今",
                    "education": "本科"
                },
                {
                    "schoolName": "北京理工大学",
                    "major": "软件工程",
                    "educationTimeLabel": "2020.09 - 至今",
                    "education": "硕士"
                }
            ]
        }
    }
    
    print("\n原始数据:")
    print(json.dumps(test_resume_data, ensure_ascii=False, indent=2))
    
    # 处理简历数据
    has_updates = processor.process_single_resume(test_resume_data)
    
    print(f"\n是否有更新: {has_updates}")
    print("\n处理后数据:")
    print(json.dumps(test_resume_data, ensure_ascii=False, indent=2))
    
    # 验证处理结果
    print("\n=== 验证处理结果 ===")
    
    # 检查工作经历
    work_experiences = test_resume_data["resume"]["workExperiences"]
    for i, exp in enumerate(work_experiences):
        time_label = exp.get("timeLabel", "")
        print(f"工作经历 {i+1}: {time_label}")
        if "至今" in time_label:
            print(f"  ❌ 仍包含'至今': {time_label}")
        elif "2025.05" in time_label:
            print(f"  ✅ 已处理'至今': {time_label}")
    
    # 检查项目经历
    project_experiences = test_resume_data["resume"]["projectExperiences"]
    for i, exp in enumerate(project_experiences):
        time_label = exp.get("timeLabel", "")
        print(f"项目经历 {i+1}: {time_label}")
        if "至今" in time_label:
            print(f"  ❌ 仍包含'至今': {time_label}")
        elif "2025.05" in time_label:
            print(f"  ✅ 已处理'至今': {time_label}")
    
    # 检查教育经历
    education_experiences = test_resume_data["resume"]["educationExperiences"]
    for i, exp in enumerate(education_experiences):
        time_label = exp.get("educationTimeLabel", "")
        education = exp.get("education", "")
        print(f"教育经历 {i+1} ({education}): {time_label}")
        if "至今" in time_label:
            print(f"  ❌ 仍包含'至今': {time_label}")
        else:
            print(f"  ✅ 已处理'至今': {time_label}")

def test_integrated_processor():
    """
    测试集成到简历数据去重处理脚本的功能
    """
    print("\n\n=== 测试集成处理器 ===")
    
    # 创建简历数据处理器
    resume_processor = ResumeDataProcessor()
    
    # 测试工作经历去重和"至今"处理
    work_experiences = [
        {
            "orgName": "腾讯科技有限公司",
            "jobTitle": "高级软件工程师",
            "timeLabel": "2020.03 - 至今 (4年 8个月)"
        },
        {
            "orgName": "腾讯科技有限公司",
            "jobTitle": "高级软件工程师",
            "timeLabel": "2020.03 - 至今 (4年 8个月)"  # 重复数据
        },
        {
            "orgName": "阿里巴巴集团",
            "jobTitle": "软件工程师",
            "timeLabel": "2018.06 - 2020.02 (1年 8个月)"
        }
    ]
    
    print("\n原始工作经历数据:")
    for i, exp in enumerate(work_experiences):
        print(f"  {i+1}. {exp['orgName']} - {exp['jobTitle']} - {exp['timeLabel']}")
    
    # 处理工作经历
    processed_work = resume_processor.deduplicate_work_experiences(work_experiences)
    
    print("\n处理后工作经历数据:")
    for i, exp in enumerate(processed_work):
        print(f"  {i+1}. {exp['orgName']} - {exp['jobTitle']} - {exp['timeLabel']}")
    
    # 测试项目经历去重和"至今"处理
    project_experiences = [
        {
            "name": "微信小程序开发平台",
            "timeLabel": "2021.01 - 至今 (4年 0个月)"
        },
        {
            "name": "支付宝移动端优化",
            "timeLabel": "2019.03 - 2020.01 (10个月)"
        },
        {
            "name": "微信小程序开发平台",
            "timeLabel": "2021.01 - 至今 (4年 0个月)"  # 重复数据
        }
    ]
    
    print("\n原始项目经历数据:")
    for i, exp in enumerate(project_experiences):
        print(f"  {i+1}. {exp['name']} - {exp['timeLabel']}")
    
    # 处理项目经历
    processed_project = resume_processor.deduplicate_project_experiences(project_experiences)
    
    print("\n处理后项目经历数据:")
    for i, exp in enumerate(processed_project):
        print(f"  {i+1}. {exp['name']} - {exp['timeLabel']}")
    
    # 测试教育经历去重和"至今"处理
    education_experiences = [
        {
            "schoolName": "清华大学",
            "major": "计算机科学与技术",
            "educationTimeLabel": "2014.09 - 至今",
            "education": "本科"
        },
        {
            "schoolName": "清华大学",
            "major": "计算机科学与技术",
            "educationTimeLabel": "2014.09 - 至今",
            "education": "本科"  # 重复数据
        },
        {
            "schoolName": "北京理工大学",
            "major": "软件工程",
            "educationTimeLabel": "2020.09 - 至今",
            "education": "硕士"
        }
    ]
    
    print("\n原始教育经历数据:")
    for i, exp in enumerate(education_experiences):
        print(f"  {i+1}. {exp['schoolName']} - {exp['major']} - {exp['educationTimeLabel']} ({exp['education']})")
    
    # 处理教育经历
    processed_education = resume_processor.deduplicate_education_experiences(education_experiences)
    
    print("\n处理后教育经历数据:")
    for i, exp in enumerate(processed_education):
        print(f"  {i+1}. {exp['schoolName']} - {exp['major']} - {exp['educationTimeLabel']} ({exp['education']})")

def test_time_calculation():
    """
    测试时间计算功能
    """
    print("\n\n=== 测试时间计算功能 ===")
    
    processor = UnifiedExperienceProcessor()
    
    test_cases = [
        ("2020.03", "2025.05"),
        ("2021.01", "2025.05"),
        ("2023.09", "2025.05"),
        ("2024.12", "2025.05")
    ]
    
    for start_time, end_time in test_cases:
        duration = processor.calculate_duration(start_time, end_time)
        print(f"{start_time} - {end_time}: {duration}")

if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 运行测试
    test_unified_processor()
    test_integrated_processor()
    test_time_calculation()
    
    print("\n=== 测试完成 ===")