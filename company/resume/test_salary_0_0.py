#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试薪资范围 "0-0" 的处理
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from company.job.job_compare import compare_json_with_text

def test_salary_0_0_matching():
    """测试薪资范围 0-0 的匹配"""
    print("=== 测试薪资范围 0-0 的处理 ===")
    
    # 测试用例1：JSON中有 "0-0"，文本中有 "面议"
    test_json_1 = {
        "薪资范围": "0-0",
        "职位名称": "软件工程师"
    }
    
    test_text_1 = """
    职位：软件工程师
    薪资：面议
    工作地点：北京
    """
    
    print("\n测试用例1：JSON中薪资范围为 '0-0'，文本中为 '面议'")
    print(f"JSON: {test_json_1}")
    print(f"文本: {test_text_1.strip()}")
    
    result_1 = compare_json_with_text(test_json_1, test_text_1)
    print(f"比较结果: {result_1}")
    
    # 测试用例2：JSON中有 "0-0"，文本中有 "薪资面议"
    test_text_2 = """
    职位：软件工程师
    薪资面议
    工作地点：北京
    """
    
    print("\n测试用例2：JSON中薪资范围为 '0-0'，文本中为 '薪资面议'")
    print(f"JSON: {test_json_1}")
    print(f"文本: {test_text_2.strip()}")
    
    result_2 = compare_json_with_text(test_json_1, test_text_2)
    print(f"比较结果: {result_2}")
    
    # 测试用例3：JSON中有 "0-0"，文本中有 "待遇面议"
    test_text_3 = """
    职位：软件工程师
    待遇面议
    工作地点：北京
    """
    
    print("\n测试用例3：JSON中薪资范围为 '0-0'，文本中为 '待遇面议'")
    print(f"JSON: {test_json_1}")
    print(f"文本: {test_text_3.strip()}")
    
    result_3 = compare_json_with_text(test_json_1, test_text_3)
    print(f"比较结果: {result_3}")
    
    # 测试用例4：JSON中有 "0-0"，文本中没有相关信息（应该不匹配）
    test_text_4 = """
    职位：软件工程师
    薪资：8000-12000元
    工作地点：北京
    """
    
    print("\n测试用例4：JSON中薪资范围为 '0-0'，文本中为具体薪资（应该不匹配）")
    print(f"JSON: {test_json_1}")
    print(f"文本: {test_text_4.strip()}")
    
    result_4 = compare_json_with_text(test_json_1, test_text_4)
    print(f"比较结果: {result_4}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_salary_0_0_matching()