# -*- coding: utf-8 -*-
"""
测试教育经历处理器与简历数据去重处理脚本的集成
"""

from 简历数据去重处理脚本 import ResumeDataProcessor
import json

def test_education_integration():
    """测试教育经历处理集成"""
    
    # 创建处理器实例
    processor = ResumeDataProcessor()
    
    # 测试数据
    test_education_experiences = [
        {
            "schoolName": "北京大学",
            "educationTimeLabel": "2013.09 - 至今",
            "major": "计算机科学与技术",
            "educationLabel": "本科"
        },
        {
            "schoolName": "清华大学",
            "educationTimeLabel": "2015.09 - 至今",
            "major": "软件工程",
            "educationLabel": "硕士"
        },
        {
            "schoolName": "深圳职业技术学院",
            "educationTimeLabel": "2020.09 - 至今",
            "major": "计算机应用技术",
            "educationLabel": "大专"
        },
        {
            "schoolName": "上海交通大学",
            "educationTimeLabel": "2018.09 - 2022.06",
            "major": "电子信息工程",
            "educationLabel": "本科"
        },
        {
            "schoolName": "北京大学",  # 重复的教育经历
            "educationTimeLabel": "2013.09 - 至今",
            "major": "计算机科学与技术",
            "educationLabel": "本科"
        }
    ]
    
    print("=== 测试教育经历处理集成 ===")
    print(f"原始教育经历数量: {len(test_education_experiences)}")
    
    # 处理教育经历
    processed_experiences = processor.deduplicate_education_experiences(test_education_experiences)
    
    print(f"处理后教育经历数量: {len(processed_experiences)}")
    print("\n=== 处理结果 ===")
    
    for i, exp in enumerate(processed_experiences):
        print(f"{i+1}. {exp['schoolName']} - {exp['major']}")
        print(f"   学历: {exp.get('educationLabel', '未知')}")
        print(f"   时间: {exp.get('educationTimeLabel', '未知')}")
        print()
    
    # 验证"至今"是否被正确处理
    has_zhijin = any('至今' in str(exp.get('educationTimeLabel', '')) for exp in processed_experiences)
    print(f"是否还有'至今'未处理: {has_zhijin}")
    
    # 验证去重是否正确
    unique_count = len(set((exp['schoolName'], exp['major']) for exp in processed_experiences))
    print(f"去重后唯一教育经历数量: {unique_count}")
    
    return processed_experiences

if __name__ == "__main__":
    test_education_integration()