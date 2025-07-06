import pandas as pd
import re

def verify_single_quotes():
    """验证生成的提示词中所有引用都使用单引号"""
    
    # 读取Excel文件
    file_path = '/company/random_prompts_40.xlsx'
    
    try:
        df = pd.read_excel(file_path)
        print(f"成功读取文件: {file_path}")
        print(f"文件包含 {len(df)} 行数据")
        print(f"列名: {list(df.columns)}")
        
        # 获取提示词列
        if '提示词' in df.columns:
            prompts = df['提示词'].tolist()
            
            print("\n=== 验证单引号格式 ===")
            
            # 检查单引号引用模式
            single_quote_patterns = [
                r"格式如下：'[^']*'",  # 格式如下：'...'
                r"参照\s*'[^']*'",     # 参照 '...'
                r"转化为\s*'[^']*'",   # 转化为 '...'
                r"转换成\s*'[^']*'"    # 转换成 '...'
            ]
            
            # 检查双引号引用模式（应该没有）
            double_quote_patterns = [
                r'格式如下："[^"]*"',  # 格式如下："..."
                r'参照\s*"[^"]*"',     # 参照 "..."
                r'转化为\s*"[^"]*"',   # 转化为 "..."
                r'转换成\s*"[^"]*"'    # 转换成 "..."
            ]
            
            single_quote_found = 0
            double_quote_found = 0
            
            # 检查第一个提示词的详细内容
            first_prompt = prompts[0]
            print("\n=== 第一个提示词中的引用示例 ===")
            
            for pattern in single_quote_patterns:
                matches = re.findall(pattern, first_prompt)
                if matches:
                    print(f"单引号模式 '{pattern}' 找到: {len(matches)} 个匹配")
                    for match in matches[:3]:  # 只显示前3个
                        print(f"  - {match}")
                    single_quote_found += len(matches)
            
            for pattern in double_quote_patterns:
                matches = re.findall(pattern, first_prompt)
                if matches:
                    print(f"双引号模式 '{pattern}' 找到: {len(matches)} 个匹配")
                    for match in matches[:3]:  # 只显示前3个
                        print(f"  - {match}")
                    double_quote_found += len(matches)
            
            # 统计所有提示词
            print("\n=== 所有提示词统计 ===")
            total_single = 0
            total_double = 0
            
            for i, prompt in enumerate(prompts):
                for pattern in single_quote_patterns:
                    matches = re.findall(pattern, prompt)
                    total_single += len(matches)
                
                for pattern in double_quote_patterns:
                    matches = re.findall(pattern, prompt)
                    total_double += len(matches)
            
            print(f"总共找到单引号引用: {total_single} 个")
            print(f"总共找到双引号引用: {total_double} 个")
            
            if total_double == 0:
                print("\n✅ 验证通过：所有引用都使用单引号格式")
            else:
                print(f"\n❌ 验证失败：发现 {total_double} 个双引号引用")
            
            # 显示教育经历部分（包含<>格式）
            print("\n=== 教育经历部分示例 ===")
            education_pattern = r'### 教育经历：[^#]*'
            education_match = re.search(education_pattern, first_prompt, re.DOTALL)
            if education_match:
                education_section = education_match.group(0)
                print(education_section[:300] + "..." if len(education_section) > 300 else education_section)
            
        else:
            print("错误：未找到'提示词'列")
            
    except Exception as e:
        print(f"读取文件时出错: {e}")

if __name__ == "__main__":
    verify_single_quotes()