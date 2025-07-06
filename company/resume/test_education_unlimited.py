#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def check_value_in_text(key, value, text):
    """检查值是否在文本中"""
    if key == "岗位描述" or key == "详细地址":  # 跳过岗位描述字段
        return True
    
    # 将文本转换为小写并去除所有空格，用于比对
    text_normalized = text.replace(' ', '').lower()
    
    if isinstance(value, str) and value.strip():
        # 特殊处理：学历不限不做匹配，直接返回True
        if value.strip() == "学历不限":
            return True
            
        value_normalized = value.replace(' ', '').lower()
        
        # 首先尝试普通比较
        if value_normalized in text_normalized:
            return True
        
        return False
    elif isinstance(value, (int, float)):
        value_normalized = str(value).replace(' ', '').lower()
        return value_normalized in text_normalized
    elif isinstance(value, list):
        # 对于列表，检查每个元素，返回不匹配的元素列表
        missing_items = []
        for item in value:
            if isinstance(item, str) and item.strip():
                item_normalized = item.replace(' ', '').lower()
                if item_normalized not in text_normalized:
                    missing_items.append(item)
        return missing_items if missing_items else True
    else:
        return True

def test_education_unlimited():
    """测试学历不限的特殊处理"""
    print("=== 学历不限测试 ===")
    
    # 测试用例1：学历要求为 '学历不限'，文本中没有相关信息（应该匹配）
    print("\n测试用例1：学历要求为 '学历不限'，文本中没有相关信息（应该匹配）")
    text1 = """职位：软件工程师
    薪资：8000-12000元
    工作地点：北京
    """
    print(f"值: '学历不限'")
    print(f"文本: {text1.strip()}")
    result1 = check_value_in_text('学历要求', '学历不限', text1)
    print(f"匹配结果: {result1}")
    
    # 测试用例2：学历要求为 '学历不限'，文本中有不同学历要求（应该匹配）
    print("\n测试用例2：学历要求为 '学历不限'，文本中有不同学历要求（应该匹配）")
    text2 = """职位：前端开发
    学历要求：本科及以上
    薪资：10000-15000元
    工作地点：上海
    """
    print(f"值: '学历不限'")
    print(f"文本: {text2.strip()}")
    result2 = check_value_in_text('学历要求', '学历不限', text2)
    print(f"匹配结果: {result2}")
    
    # 测试用例3：学历要求为 '本科'，文本中为 '学历不限'（应该不匹配）
    print("\n测试用例3：学历要求为 '本科'，文本中为 '学历不限'（应该不匹配）")
    text3 = """职位：后端开发
    学历要求：学历不限
    薪资：12000-18000元
    工作地点：深圳
    """
    print(f"值: '本科'")
    print(f"文本: {text3.strip()}")
    result3 = check_value_in_text('学历要求', '本科', text3)
    print(f"匹配结果: {result3}")
    
    # 测试用例4：学历要求为 '学历不限'，文本中也为 '学历不限'（应该匹配）
    print("\n测试用例4：学历要求为 '学历不限'，文本中也为 '学历不限'（应该匹配）")
    text4 = """职位：测试工程师
    学历要求：学历不限
    薪资：9000-14000元
    工作地点：广州
    """
    print(f"值: '学历不限'")
    print(f"文本: {text4.strip()}")
    result4 = check_value_in_text('学历要求', '学历不限', text4)
    print(f"匹配结果: {result4}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_education_unlimited()