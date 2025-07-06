# -*- coding: utf-8 -*-
"""
工作经历处理器类
用于处理workExperiences的timeLabel数据，包括格式转换、去除时间段交叉和计算总年月
"""

import re
from datetime import datetime
from typing import List, Tuple, Optional

class WorkExperienceProcessor:
    """
    工作经历处理器类
    """
    
    def __init__(self):
        """
        初始化处理器
        """
        pass
    
    def parse_time_label(self, time_label: str) -> Optional[Tuple[str, str]]:
        """
        解析timeLabel，提取开始时间和结束时间
        支持多种格式：
        - "xxxx.xx - xxxx.xx (xx年 xx个月)"
        - "xxxx.xx - 至今 (xx年 xx个月)"
        - "xxxx.xx - xxxx.xx"
        
        Args:
            time_label: 时间标签字符串
            
        Returns:
            tuple: (开始时间, 结束时间) 或 None
        """
        if not time_label:
            return None
        
        # 匹配各种时间格式
        patterns = [
            # 格式1: "xxxx.xx - xxxx.xx (xx年 xx个月)"
            r'(\d{4}\.\d{2})\s*-\s*(\d{4}\.\d{2})\s*\([^)]+\)',
            # 格式2: "xxxx.xx - 至今 (xx年 xx个月)"
            r'(\d{4}\.\d{2})\s*-\s*至今\s*\([^)]+\)',
            # 格式3: "xxxx.xx - xxxx.xx"
            r'(\d{4}\.\d{2})\s*-\s*(\d{4}\.\d{2})',
            # 格式4: "xxxx.xx - 至今"
            r'(\d{4}\.\d{2})\s*-\s*至今'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, time_label)
            if match:
                start_time = match.group(1)
                if '至今' in time_label:
                    end_time = '2025.05'  # 将"至今"转换为2025.05
                else:
                    end_time = match.group(2) if len(match.groups()) > 1 else '2025.05'
                return start_time, end_time
        
        return None
    
    def convert_to_standard_format(self, time_label: str) -> str:
        """
        将timeLabel转换为标准格式 xxxx.xx - xxxx.xx
        
        Args:
            time_label: 原始时间标签
            
        Returns:
            str: 标准格式的时间标签
        """
        parsed = self.parse_time_label(time_label)
        if not parsed:
            return time_label
        
        start_time, end_time = parsed
        return f"{start_time} - {end_time}"
    
    def get_work_experience_periods(self, work_experiences: List[dict]) -> List[Tuple[str, str]]:
        """
        获取workExperiences下每一条timeLabel的数据，转换成标准格式
        
        Args:
            work_experiences: 工作经历列表
            
        Returns:
            list: 标准格式的时间段列表 [(start, end), ...]
        """
        periods = []
        
        if not work_experiences or not isinstance(work_experiences, list):
            return periods
        
        for exp in work_experiences:
            if isinstance(exp, dict) and 'timeLabel' in exp:
                time_label = exp['timeLabel']
                parsed = self.parse_time_label(time_label)
                if parsed:
                    start_time, end_time = parsed
                    periods.append((start_time, end_time))
                    print(f"解析时间段: {time_label} -> {start_time} - {end_time}")
        
        return periods
    
    def time_to_months(self, time_str: str) -> int:
        """
        将时间字符串转换为月数
        
        Args:
            time_str: 时间字符串，格式为 "yyyy.mm"
            
        Returns:
            int: 总月数
        """
        try:
            year, month = map(int, time_str.split('.'))
            return year * 12 + month
        except:
            return 0
    
    def months_to_time(self, months: int) -> str:
        """
        将月数转换为时间字符串
        
        Args:
            months: 总月数
            
        Returns:
            str: 时间字符串，格式为 "yyyy.mm"
        """
        year = months // 12
        month = months % 12
        if month == 0:
            year -= 1
            month = 12
        return f"{year:04d}.{month:02d}"
    
    def merge_overlapping_periods(self, periods: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        """
        去除交叉的时间段，重新组合成不交叉的时间段
        
        Args:
            periods: 时间段列表 [(start, end), ...]
            
        Returns:
            list: 合并后的不交叉时间段列表
        """
        if not periods:
            return []
        
        # 转换为月数进行处理
        month_periods = []
        for start, end in periods:
            start_months = self.time_to_months(start)
            end_months = self.time_to_months(end)
            if start_months <= end_months:  # 确保开始时间不晚于结束时间
                month_periods.append((start_months, end_months))
        
        if not month_periods:
            return []
        
        # 按开始时间排序
        month_periods.sort(key=lambda x: x[0])
        
        # 合并重叠的时间段
        merged = [month_periods[0]]
        
        for current_start, current_end in month_periods[1:]:
            last_start, last_end = merged[-1]
            
            # 如果当前时间段与上一个时间段重叠
            if current_start <= last_end:  # 只合并重叠的时间段，不合并相邻的月份
                # 合并时间段
                merged[-1] = (last_start, max(last_end, current_end))
                print(f"合并时间段: ({self.months_to_time(last_start)}, {self.months_to_time(last_end)}) + ({self.months_to_time(current_start)}, {self.months_to_time(current_end)}) -> ({self.months_to_time(last_start)}, {self.months_to_time(max(last_end, current_end))})")
            else:
                # 不重叠，添加新的时间段
                merged.append((current_start, current_end))
        
        # 转换回时间字符串格式
        result = []
        for start_months, end_months in merged:
            start_time = self.months_to_time(start_months)
            end_time = self.months_to_time(end_months)
            result.append((start_time, end_time))
        
        return result
    
    def calculate_total_duration(self, periods: List[Tuple[str, str]]) -> str:
        """
        计算总的年月，格式为xx年xx月
        
        Args:
            periods: 时间段列表 [(start, end), ...]
            
        Returns:
            str: 总时长，格式为"xx年xx月"
        """
        if not periods:
            return "0个月"
        
        total_months = 0
        
        for start, end in periods:
            start_months = self.time_to_months(start)
            end_months = self.time_to_months(end)
            duration = end_months - start_months
            
            # 如果开始时间和结束时间相同，算作1个月
            if duration == 0:
                duration = 1
            
            if duration > 0:
                total_months += duration
                print(f"时间段 {start} - {end}: {duration} 个月")
        
        years = total_months // 12
        months = total_months % 12
        
        if years > 0 and months > 0:
            return f"{years}年{months}个月"
        elif years > 0:
            return f"{years}年"
        elif months > 0:
            return f"{months}个月"
        else:
            return "0个月"
    
    def process_work_experiences(self, work_experiences: List[dict]) -> dict:
        """
        处理工作经历的完整流程
        
        Args:
            work_experiences: 工作经历列表
            
        Returns:
            dict: 处理结果，包含原始时间段、合并后时间段和总时长
        """
        print("=== 开始处理工作经历 ===")
        
        # 1. 获取并转换时间段格式
        print("\n1. 提取时间段:")
        periods = self.get_work_experience_periods(work_experiences)
        
        if not periods:
            print("未找到有效的时间段")
            return {
                'original_periods': [],
                'merged_periods': [],
                'total_duration': '0年0个月'
            }
        
        print(f"提取到 {len(periods)} 个时间段")
        
        # 2. 去除交叉的时间段
        print("\n2. 合并重叠时间段:")
        merged_periods = self.merge_overlapping_periods(periods)
        print(f"合并后剩余 {len(merged_periods)} 个时间段")
        
        for start, end in merged_periods:
            print(f"  {start} - {end}")
        
        # 3. 计算总的年月
        print("\n3. 计算总时长:")
        total_duration = self.calculate_total_duration(merged_periods)
        print(f"总工作时长: {total_duration}")
        
        return {
            'original_periods': periods,
            'merged_periods': merged_periods,
            'total_duration': total_duration
        }

# 使用示例
if __name__ == "__main__":
    # 创建处理器实例
    processor = WorkExperienceProcessor()
    
    # 示例数据
    sample_work_experiences = [
        # {'timeLabel': '2020.01 - 2022.06 (2年5个月)'},
        # {'timeLabel': '2022.03 - 2023.08 (2年5个月)'},
        # {'timeLabel': '2023.08 - 2024.06 (2年5个月)'},
        # {'timeLabel': '2021.03 - 2023.08 (2年5个月)'},
        # {'timeLabel': '2024.08 - 至今 (2年4个月)'},
        # {'timeLabel': '2019.06 - 2020.12 (1年6个月)'}

       { "timeLabel": "2015.03 - 2017.04 (2年 1个月)"},
        {"timeLabel": "2017.07 - 2018.02 (7个月)"},
        {"timeLabel": "2018.03 - 2025.05 (7年 2个月)"}
    ]
    
    # 处理工作经历
    result = processor.process_work_experiences(sample_work_experiences)
    
    print("\n=== 处理结果 ===")
    print(f"原始时间段数: {len(result['original_periods'])}")
    print(f"合并后时间段数: {len(result['merged_periods'])}")
    print(f"总工作时长: {result['total_duration']}")