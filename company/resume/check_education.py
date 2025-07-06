import pandas as pd

df = pd.read_excel('random_prompts_40.xlsx')

# 检查所有40个提示词，找到包含教育经历模块的
found_education = False
for idx in range(len(df)):
    prompt = df.iloc[idx]['提示词']
    if '### 教育经历' in prompt:
        print(f'在第{idx+1}个提示词中找到教育经历模块:')
        lines = prompt.split('\n')
        
        for i, line in enumerate(lines):
            if '### 教育经历' in line:
                print(f'第{i}行: {line}')
                if i+1 < len(lines):
                    print(f'第{i+1}行: {lines[i+1]}')
                if i+2 < len(lines):
                    print(f'第{i+2}行: {lines[i+2]}')
                break
        
        # 检查是否包含<>括号
        if '<{education_reference}>' in prompt:
            print('\n✓ 教育经历部分包含<{education_reference}>格式')
        else:
            print('\n✗ 教育经历部分不包含<{education_reference}>格式')
        
        found_education = True
        break

if not found_education:
    print('在所有40个提示词中都没有找到教育经历模块')
    print('\n检查模块顺序:')
    for idx in range(min(5, len(df))):
        print(f'提示词{idx+1}的模块顺序: {df.iloc[idx]["模块顺序"]}')