import sys
sys.path.append('/company')

from company.resume.merged_prompt_generator import generate_random_prompt

def test_certificate_randomization():
    """测试certificate_prompt是否参与随机排序"""
    
    print("=== 测试certificate_prompt随机排序 ===")
    
    # 生成5个随机提示词，查看模块顺序
    for i in range(5):
        prompt, order, references = generate_random_prompt()
        print(f"\n示例{i+1}的模块顺序:")
        print(' -> '.join(order))
        
        # 检查certificate_prompt的位置
        if 'certificate_prompt' in order:
            cert_position = order.index('certificate_prompt')
            print(f"certificate_prompt位置: {cert_position + 1}/{len(order)}")
        else:
            print("❌ certificate_prompt未找到！")
    
    print("\n=== 验证完成 ===")

if __name__ == "__main__":
    test_certificate_randomization()