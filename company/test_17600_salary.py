#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 17600-17600 薪资范围的处理
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from job_compare import compare_json_with_text

def test_17600_salary_matching():
    """测试 17600-17600 薪资范围的匹配"""
    print("=== 测试 17600-17600 薪资范围的处理 ===")
    
    # 测试用例1：JSON中有 "17600-17600"，文本中有 "17600"
    test_json_1 = {
        "薪资范围": "17600-17600",
        "职位名称": "高级开发工程师"
    }
    
    test_text_1 = """
    职位：高级开发工程师
    薪资：17600元/月
    工作地点：北京
    """
    
    print("\n测试用例1：JSON中薪资范围为 '17600-17600'，文本中为 '17600元/月'")
    print(f"JSON: {test_json_1}")
    print(f"文本: {test_text_1.strip()}")
    
    result_1 = compare_json_with_text(test_json_1, test_text_1)
    print(f"比较结果: {result_1}")
    
    # 测试用例2：JSON中有 "17600-17600"，文本中有 "月薪17600"
    test_text_2 = """
    职位：高级开发工程师
    月薪17600
    工作地点：上海
    """
    
    print("\n测试用例2：JSON中薪资范围为 '17600-17600'，文本中为 '月薪17600'")
    print(f"JSON: {test_json_1}")
    print(f"文本: {test_text_2.strip()}")
    
    result_2 = compare_json_with_text(test_json_1, test_text_2)
    print(f"比较结果: {result_2}")
    
    # 测试用例3：JSON中有 "17600-17600"，文本中有不同薪资（应该不匹配）
    test_text_3 = """
    职位：高级开发工程师
    薪资：15000-18000元
    工作地点：深圳
    """
    
    print("\n测试用例3：JSON中薪资范围为 '17600-17600'，文本中为不同薪资（应该不匹配）")
    print(f"JSON: {test_json_1}")
    print(f"文本: {test_text_3.strip()}")
    
    result_3 = compare_json_with_text(test_json_1, test_text_3)
    print(f"比较结果: {result_3}")
    
    # 测试用例4：JSON中有 "17600-17600"，文本中有 "薪资17600元"
    test_text_4 = """
    职位：高级开发工程师
    薪资17600元
    福利：五险一金
    """
    
    print("\n测试用例4：JSON中薪资范围为 '17600-17600'，文本中为 '薪资17600元'")
    print(f"JSON: {test_json_1}")
    print(f"文本: {test_text_4.strip()}")
    
    result_4 = compare_json_with_text(test_json_1, test_text_4)
    print(f"比较结果: {result_4}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_17600_salary_matching()