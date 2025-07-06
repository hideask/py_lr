#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试薪资转换函数
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import re

def convert_salary_to_wan_format(salary_str):
    """将薪资范围转换为万元格式，如240000-250000转换为24-25万，0-0转换为面议，5000-5000转换为5000"""
    import re
    # 匹配薪资范围格式：数字-数字
    pattern = r'(\d+)-(\d+)'
    match = re.match(pattern, salary_str.strip())
    
    if match:
        min_salary = int(match.group(1))
        max_salary = int(match.group(2))
        
        # 特殊处理：0-0 转换为面议
        if min_salary == 0 and max_salary == 0:
            return "面议"
        
        # 特殊处理：相同数值的范围，如5000-5000转换为5000，17600-17600转换为17600
        if min_salary == max_salary:
            return str(min_salary)
        
        # 如果薪资大于等于10000，转换为万元格式
        if min_salary >= 10000 and max_salary >= 10000:
            min_wan = min_salary / 10000
            max_wan = max_salary / 10000
            
            # 格式化为合适的显示格式
            if min_wan == int(min_wan):
                min_str = str(int(min_wan))
            else:
                min_str = f"{min_wan:.1f}"
            
            if max_wan == int(max_wan):
                max_str = str(int(max_wan))
            else:
                max_str = f"{max_wan:.1f}"
            
            return f"{min_str}-{max_str}万"
    
    return None

def test_salary_conversions():
    """测试各种薪资转换"""
    test_cases = [
        "0-0",
        "5000-5000",
        "8000-8000",
        "17600-17600",
        "50000-50000",
        "120000-120000",
        "5000-8000",
        "15000-20000"
    ]
    
    print("=== 薪资转换测试 ===")
    for salary in test_cases:
        result = convert_salary_to_wan_format(salary)
        print(f"{salary} -> {result}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_salary_conversions()