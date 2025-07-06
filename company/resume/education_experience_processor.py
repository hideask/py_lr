# -*- coding: utf-8 -*-
"""
教育经历处理器类
用于处理educationExperiences的educationTimeLabel数据，包括格式转换和"至今"类型数据的处理
"""

import re
from datetime import datetime
from typing import List, Tuple, Optional, Dict

class EducationExperienceProcessor:
    """
    教育经历处理器类
    """
    
    def __init__(self):
        """
        初始化处理器
        """
        pass
    
    def parse_education_time_label(self, time_label: str, education_label: str = None) -> Optional[Tuple[str, str]]:
        """
        解析educationTimeLabel，提取开始时间和结束时间
        支持多种格式：
        - "xxxx.xx - xxxx.xx"
        - "xxxx.xx - 至今"
        
        Args:
            time_label: 时间标签字符串
            education_label: 学历标签（大专、本科、硕士等）
            
        Returns:
            tuple: (开始时间, 结束时间) 或 None
        """
        if not time_label:
            return None
        
        # 匹配各种时间格式
        patterns = [
            # 格式1: "xxxx.xx - xxxx.xx"
            r'(\d{4}\.\d{2})\s*-\s*(\d{4}\.\d{2})',
            # 格式2: "xxxx.xx - 至今"
            r'(\d{4}\.\d{2})\s*-\s*至今'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, time_label)
            if match:
                start_time = match.group(1)
                if '至今' in time_label:
                    end_time = self.calculate_end_time_from_start(start_time, education_label)
                else:
                    end_time = match.group(2) if len(match.groups()) > 1 else None
                return start_time, end_time
        
        return None
    
    def calculate_end_time_from_start(self, start_time: str, education_label: str = None) -> str:
        """
        根据开始时间和学历类型计算结束时间
        
        Args:
            start_time: 开始时间，格式为 "yyyy.mm"
            education_label: 学历标签（大专、本科、硕士等）
            
        Returns:
            str: 结束时间，格式为 "yyyy.mm"
        """
        try:
            year, month = map(int, start_time.split('.'))
            
            # 根据学历类型确定学制年限
            if education_label:
                education_lower = education_label.lower().strip()
                if '大专' in education_lower or '专科' in education_lower:
                    years_to_add = 3
                elif '硕士' in education_lower or '研究生' in education_lower:
                    years_to_add = 3
                elif '本科' in education_lower or '学士' in education_lower:
                    years_to_add = 4
                else:
                    # 默认情况，假设为本科
                    years_to_add = 4
            else:
                # 如果没有学历信息，默认为本科4年
                years_to_add = 4
            
            end_year = year + years_to_add
            end_time = f"{end_year:04d}.{month:02d}"
            
            print(f"教育经历时间计算: {start_time} + {years_to_add}年({education_label or '默认本科'}) -> {end_time}")
            
            return end_time
            
        except Exception as e:
            print(f"计算教育结束时间时出错: {e}")
            # 如果计算失败，返回当前时间
            return '2025.05'
    
    def convert_to_standard_format(self, time_label: str, education_label: str = None) -> str:
        """
        将educationTimeLabel转换为标准格式 xxxx.xx - xxxx.xx
        
        Args:
            time_label: 原始时间标签
            education_label: 学历标签
            
        Returns:
            str: 标准格式的时间标签
        """
        parsed = self.parse_education_time_label(time_label, education_label)
        if not parsed:
            return time_label
        
        start_time, end_time = parsed
        return f"{start_time} - {end_time}"
    
    def process_education_experiences(self, education_experiences: List[dict]) -> List[dict]:
        """
        处理教育经历的完整流程，主要处理"至今"类型的数据
        
        Args:
            education_experiences: 教育经历列表
            
        Returns:
            list: 处理后的教育经历列表
        """
        if not education_experiences or not isinstance(education_experiences, list):
            return education_experiences
        
        processed_experiences = []
        
        for exp in education_experiences:
            if not isinstance(exp, dict):
                processed_experiences.append(exp)
                continue
            
            # 复制原始数据
            processed_exp = exp.copy()
            
            # 处理educationTimeLabel
            if 'educationTimeLabel' in exp and '至今' in str(exp['educationTimeLabel']):
                education_label = exp.get('educationLabel', '')
                original_time_label = exp['educationTimeLabel']
                
                # 转换为标准格式
                new_time_label = self.convert_to_standard_format(original_time_label, education_label)
                processed_exp['educationTimeLabel'] = new_time_label
                
                print(f"处理教育经历: {original_time_label} -> {new_time_label} (学历: {education_label})")
            
            processed_experiences.append(processed_exp)
        
        return processed_experiences
    
    def get_education_duration_years(self, time_label: str, education_label: str = None) -> float:
        """
        计算教育经历的持续年数
        
        Args:
            time_label: 时间标签
            education_label: 学历标签
            
        Returns:
            float: 持续年数
        """
        parsed = self.parse_education_time_label(time_label, education_label)
        if not parsed:
            return 0.0
        
        start_time, end_time = parsed
        
        try:
            start_year, start_month = map(int, start_time.split('.'))
            end_year, end_month = map(int, end_time.split('.'))
            
            start_months = start_year * 12 + start_month
            end_months = end_year * 12 + end_month
            
            duration_months = end_months - start_months
            duration_years = duration_months / 12.0
            
            return max(0.0, duration_years)
            
        except Exception as e:
            print(f"计算教育持续时间时出错: {e}")
            return 0.0

# 使用示例
if __name__ == "__main__":
    # 创建处理器实例
    processor = EducationExperienceProcessor()
    
    # 示例数据
    sample_education_experiences = [
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
    
    print("=== 开始处理教育经历 ===")
    
    # 处理教育经历
    processed_experiences = processor.process_education_experiences(sample_education_experiences)
    
    print("\n=== 处理结果 ===")
    for i, exp in enumerate(processed_experiences):
        print(f"{i+1}. {exp['schoolName']} - {exp['major']}")
        print(f"   学历: {exp.get('educationLabel', '未知')}")
        print(f"   时间: {exp.get('educationTimeLabel', '未知')}")
        
        # 计算持续时间
        duration = processor.get_education_duration_years(
            exp.get('educationTimeLabel', ''), 
            exp.get('educationLabel', '')
        )
        print(f"   持续时间: {duration:.1f}年")
        print()