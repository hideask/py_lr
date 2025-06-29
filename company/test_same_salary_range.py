#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试相同数值薪资范围的处理
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from job_compare import compare_json_with_text

def test_same_salary_range_matching():
    """测试相同数值薪资范围的匹配"""
    print("=== 测试相同数值薪资范围的处理 ===")
    
    # 测试用例1：JSON中有 "5000-5000"，文本中有 "5000"
    test_json_1 = {
        "薪资范围": "5000-5000",
        "职位名称": "前端开发"
    }
    
    test_text_1 = """
    职位：前端开发
    薪资：5000元
    工作地点：上海
    """
    
    print("\n测试用例1：JSON中薪资范围为 '5000-5000'，文本中为 '5000元'")
    print(f"JSON: {test_json_1}")
    print(f"文本: {test_text_1.strip()}")
    
    result_1 = compare_json_with_text(test_json_1, test_text_1)
    print(f"比较结果: {result_1}")
    
    # 测试用例2：JSON中有 "8000-8000"，文本中有 "月薪8000"
    test_json_2 = {
        "薪资范围": "8000-8000",
        "职位名称": "后端开发"
    }
    
    test_text_2 = """
    职位：后端开发
    月薪8000
    工作地点：深圳
    """
    
    print("\n测试用例2：JSON中薪资范围为 '8000-8000'，文本中为 '月薪8000'")
    print(f"JSON: {test_json_2}")
    print(f"文本: {test_text_2.strip()}")
    
    result_2 = compare_json_with_text(test_json_2, test_text_2)
    print(f"比较结果: {result_2}")
    
    # 测试用例3：JSON中有 "50000-50000"，文本中有 "5万"（应该匹配）
    test_json_3 = {
        "薪资范围": "50000-50000",
        "职位名称": "架构师"
    }
    
    test_text_3 = """
    职位：架构师
    薪资：5万元
    工作地点：北京
    """
    
    print("\n测试用例3：JSON中薪资范围为 '50000-50000'，文本中为 '5万元'")
    print(f"JSON: {test_json_3}")
    print(f"文本: {test_text_3.strip()}")
    
    result_3 = compare_json_with_text(test_json_3, test_text_3)
    print(f"比较结果: {result_3}")
    
    # 测试用例4：JSON中有 "6000-6000"，文本中有不同薪资（应该不匹配）
    test_json_4 = {
        "薪资范围": "6000-6000",
        "职位名称": "测试工程师"
    }
    
    test_text_4 = """
    职位：测试工程师
    薪资：7000-8000元
    工作地点：广州
    """
    
    print("\n测试用例4：JSON中薪资范围为 '6000-6000'，文本中为不同薪资（应该不匹配）")
    print(f"JSON: {test_json_4}")
    print(f"文本: {test_text_4.strip()}")
    
    result_4 = compare_json_with_text(test_json_4, test_text_4)
    print(f"比较结果: {result_4}")
    
    # 测试用例5：JSON中有 "120000-120000"，文本中有 "12万"（应该匹配）
    test_json_5 = {
        "薪资范围": "120000-120000",
        "职位名称": "产品经理"
    }
    
    test_text_5 = """
    职位：产品经理
    年薪：12万
    工作地点：杭州
    """
    
    print("\n测试用例5：JSON中薪资范围为 '120000-120000'，文本中为 '12万'")
    print(f"JSON: {test_json_5}")
    print(f"文本: {test_text_5.strip()}")
    
    result_5 = compare_json_with_text(test_json_5, test_text_5)
    print(f"比较结果: {result_5}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_same_salary_range_matching()