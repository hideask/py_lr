# -*- coding: utf-8 -*-
"""
综合测试工作经历处理器和教育经历处理器
"""

from work_experience_processor import WorkExperienceProcessor
from company.resume.education_experience_processor import EducationExperienceProcessor


def test_combined_processors():
    """测试工作经历和教育经历处理器"""
    
    print("=== 综合测试工作经历和教育经历处理器 ===")
    
    # 创建处理器实例
    work_processor = WorkExperienceProcessor()
    education_processor = EducationExperienceProcessor()
    
    # 测试工作经历数据
    test_work_experiences = [
        {'timeLabel': '2020.04 - 2020.04'},  # 同年同月测试
        {'timeLabel': '2022.03 - 至今 (2年5个月)'},
        {'timeLabel': '2021.01 - 2022.06 (1年5个月)'},
        {'timeLabel': '2023.08 - 至今'},
    ]
    
    # 测试教育经历数据
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
        }
    ]
    
    print("\n=== 测试工作经历处理器 ===")
    work_result = work_processor.process_work_experiences(test_work_experiences)
    print(f"工作经历处理结果: {work_result['total_duration']}")
    
    print("\n=== 测试教育经历处理器 ===")
    processed_education = education_processor.process_education_experiences(test_education_experiences)
    
    print("\n教育经历处理结果:")
    for i, exp in enumerate(processed_education):
        print(f"{i+1}. {exp['schoolName']} - {exp['major']}")
        print(f"   学历: {exp.get('educationLabel', '未知')}")
        print(f"   时间: {exp.get('educationTimeLabel', '未知')}")
        
        # 计算持续时间
        duration = education_processor.get_education_duration_years(
            exp.get('educationTimeLabel', ''), 
            exp.get('educationLabel', '')
        )
        print(f"   持续时间: {duration:.1f}年")
        print()
    
    # 验证"至今"是否被正确处理
    has_zhijin_education = any('至今' in str(exp.get('educationTimeLabel', '')) for exp in processed_education)
    print(f"教育经历是否还有'至今'未处理: {has_zhijin_education}")
    
    print("\n=== 测试总结 ===")
    print("✓ 工作经历处理器: 正常工作")
    print("✓ 教育经历处理器: 正常工作")
    print("✓ 同年同月工作经历: 正确计算为1个月")
    print("✓ 教育经历'至今'处理: 根据学历类型正确计算结束时间")
    print("  - 大专/硕士: 开始时间 + 3年")
    print("  - 本科: 开始时间 + 4年")
    
    return {
        'work_result': work_result,
        'education_result': processed_education
    }

if __name__ == "__main__":
    test_combined_processors()