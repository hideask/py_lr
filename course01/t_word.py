# from docx import Document
#
#
# def read_word_file(file_path):
#     # 打开Word文档
#     doc = Document(file_path)
#
#     # 初始化一个空字符串来保存所有段落的文本
#     text = ''
#
#     # 遍历文档中的每个段落
#     for paragraph in doc.paragraphs:
#         # 将段落文本添加到text变量中
#         text += paragraph.text + '\n'
#
#     return text
#
#
# # 指定Word文件路径
# file_path = 'example.docx'
# # 调用函数并打印内容
# content = read_word_file(file_path)
# print(content)



import json
# 原始数据
data = {
  "intention": "求职找工作",
  "acb215": "广安",
  "aca112": "销售",
  "salary": {
    "max_salary": 8000,
    "min_salary": 3000,
    "type": "月薪"
  }
}

# 转换 salary 中的数值为字符串
data['salary']['max_salary'] = str(data['salary']['max_salary'])
data['salary']['min_salary'] = str(data['salary']['min_salary'])

# 将整个对象转换为字符串
biz_content_str = json.dumps(data, ensure_ascii=False)

# 最终的结果
final_data = {
  "biz_content": biz_content_str
}

print(final_data)