import json
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from company.job.job_compare import compare_json_with_text

def test_welfare_matching():
    """测试福利待遇匹配功能"""
    
    # 测试数据 - 包含福利待遇的JSON
    test_json = {
        "福利待遇": [
            "五险一金",
            "有餐补", 
            "绩效奖金",
            "带薪假期",
            "节日慰问",
            "定期团建",
            "弹性工作",
            "体检福利"
        ],
        "公司名称": "测试公司",
        "薪资范围": "8000-12000"
    }
    
    # 测试文本 - 模拟职位描述，只包含部分福利
    test_text = """
    我们公司提供完善的福利待遇：
    - 五险一金，保障员工基本权益
    - 绩效奖金，根据工作表现发放
    - 带薪假期，包括年假、病假等
    - 定期团建活动，增进团队感情
    - 弹性工作时间，提高工作效率
    
    公司名称：测试公司
    薪资范围：8000-12000元
    
    我们致力于为员工创造良好的工作环境。
    """
    
    print("=" * 60)
    print("福利待遇匹配测试")
    print("=" * 60)
    
    print("\n测试JSON数据:")
    print(json.dumps(test_json, ensure_ascii=False, indent=2))
    
    print("\n测试文本内容:")
    print(test_text)
    
    print("\n开始比对...")
    print("-" * 40)
    
    # 执行比对
    missing_data = compare_json_with_text(test_json, test_text)
    
    print("\n比对结果:")
    if missing_data:
        print("发现以下不匹配的数据:")
        for key, value in missing_data.items():
            print(f"  {key}: {value}")
            
            # 特别关注福利待遇
            if "福利待遇" in key:
                print(f"    -> 这些福利项在文本中未找到: {value}")
    else:
        print("所有数据都在文本中找到了匹配！")
    
    print("\n" + "=" * 60)

def test_welfare_with_variations():
    """测试福利待遇的变体匹配"""
    
    print("\n测试福利待遇变体匹配")
    print("=" * 60)
    
    # 测试数据
    test_json = {
        "福利待遇": [
            "有餐补",
            "提供住房补贴",
            "享受年终奖",
            "交通补助"
        ]
    }
    
    # 测试文本 - 使用不同的表达方式
    test_text = """
    公司福利包括：
    - 餐补每月500元
    - 住房补贴根据级别发放
    - 年终奖根据业绩确定
    - 不提供交通补助
    """
    
    print("\n测试JSON数据:")
    print(json.dumps(test_json, ensure_ascii=False, indent=2))
    
    print("\n测试文本内容:")
    print(test_text)
    
    print("\n开始比对...")
    print("-" * 40)
    
    # 执行比对
    missing_data = compare_json_with_text(test_json, test_text)
    
    print("\n比对结果:")
    if missing_data:
        print("发现以下不匹配的数据:")
        for key, value in missing_data.items():
            print(f"  {key}: {value}")
    else:
        print("所有数据都在文本中找到了匹配！")

if __name__ == "__main__":
    # 运行测试
    test_welfare_matching()
    test_welfare_with_variations()
    
    print("\n测试完成！")