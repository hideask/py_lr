import pandas as pd
import re

def verify_quotes_in_prompts():
    # 读取Excel文件
    df = pd.read_excel('random_prompts_40.xlsx')
    
    # 检查第一个提示词的内容
    first_prompt = df.iloc[0]['提示词']
    
    print("=== 检查第一个提示词中的引用格式 ===")
    print()
    
    # 查找所有可能的变量引用模式
    patterns_to_check = [
        (r'格式如下："[^"]+"', '格式如下的双引号包围'),
        (r'参照\s*"[^"]+"', '参照的双引号包围'),
        (r'转化为\s*"[^"]+"', '转化为的双引号包围'),
        (r'转换成\s*"[^"]+"', '转换成的双引号包围')
    ]
    
    for pattern, description in patterns_to_check:
        matches = re.findall(pattern, first_prompt)
        if matches:
            print(f"✓ 找到{description}: {len(matches)}个")
            for match in matches:
                print(f"  - {match}")
        else:
            print(f"✗ 未找到{description}")
        print()
    
    # 检查是否还有未用双引号包围的变量引用
    old_patterns = [
        r"格式如下：'[^']+'",
        r"参照\s*'[^']+'",
        r"转化为\s*'[^']+'",
        r"转换成\s*'[^']+'"
    ]
    
    print("=== 检查是否还有单引号包围的引用 ===")
    for pattern in old_patterns:
        matches = re.findall(pattern, first_prompt)
        if matches:
            print(f"⚠️  发现单引号包围的引用: {matches}")
        else:
            print(f"✓ 未发现单引号包围的引用")
    
    print("\n=== 显示教育经历部分 ===")
    # 查找教育经历部分
    education_match = re.search(r'### 教育经历：[\s\S]*?(?=###|$)', first_prompt)
    if education_match:
        print(education_match.group())
    else:
        print("未找到教育经历部分")

if __name__ == "__main__":
    verify_quotes_in_prompts()