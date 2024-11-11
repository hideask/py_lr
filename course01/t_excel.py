import pandas as pd

# 指定Excel文件路径
excel_file_path = 'path/to/your/excel/file.xlsx'

# 使用pandas读取Excel文件
df = pd.read_excel(excel_file_path)

# 打印数据框的前几行
print(df.head())