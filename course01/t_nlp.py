import jieba.analyse
import jieba
import re

# text = "我想找一个【销售（岗位名称aca112）】的工作，希望的工作地点是【成都（工作地点acb215）】，每月的薪资为【8k（薪资范围salary）】"

# 使用 TF-IDF 提取关键词
# keywords = jieba.analyse.extract_tags(text, topK=5, withWeight=False)
# print(keywords)
#
# keywords = jieba.cut(text)
#
# text = "我想找一个【销售（岗位名称aca112）】的工作，希望的工作地点是【成都（工作地点acb215）】，每月的薪资为【8k（薪资范围salary）】"
#
# # 使用 jieba.tokenize 显示每个词的位置
# tokens = jieba.tokenize(text)
#
# # 打印每个词及其位置
# for token in tokens:
#     start, end, word = token
#     print(f"词: {word}, 起始位置: {start}, 结束位置: {end}")

# 使用正则表达式提取找工作
sentence = "我想找一个***的工作，希望的工作地点是***，每月的薪资为***"
pattern_job = r"我想找一个(.*)的工作，"  # 使用.*来匹配任意字符，直到遇到“的工作”
pattern_address = r"希望的工作地点是(.*)，"
pattern_salary = r"每月的薪资为(.*)"

result_job = re.search(pattern_job, sentence)
result_address = re.search(pattern_address, sentence)
result_salary = re.search(pattern_salary, sentence)


result_job_text = result_job.group(1) if result_job else '无' # group(1) 获取第一个括号内的匹配内容，没有就是无
result_address_text = result_address.group(1) if result_address else '无'
result_salary_text = result_salary.group(1) if result_salary else '无'
# result_salary_text = re.sub(r'[^\w\s]]', '', result_salary_text)
result_salary_text = re.sub(r'[.。,，;；！!？?、]', '', result_salary_text)
print(result_job_text)
print(result_address_text)
print(result_salary_text)

# 使用正则表达式提取找人才
sentence = "请为我推荐学历为【本科（学历要求aac011）】、薪资不超过【5k（薪资范围salary）】、年龄在【35岁以上（年龄age）】的【工程师（岗位名称aca112）】!"
pattern_edu = r"学历为(.*)、薪资不超过"
pattern_salary = r"薪资不超过(.*)、"
pattern_age_job = r"年龄在(.*)的(.*)"
result_edu = re.search(pattern_edu, sentence)
result_salary = re.search(pattern_salary, sentence)
result_age_job = re.search(pattern_age_job, sentence)

result_edu_text = result_edu.group(1) if result_edu else '无' # group(1) 获取第一个括号内的匹配内容，没有就是无print(result_edu.group(1))
result_salary_text = result_salary.group(1) if result_salary else '无'
result_age_text = result_age_job.group(1) if (result_age_job and len(result_age_job.groups()) >= 1) else '无'
result_job_text = result_age_job.group(2) if (result_age_job and len(result_age_job.groups()) >= 2) else '无'
result_job_text = re.sub(r'[.。,，;；！!？?、]', '', result_job_text)
print(result_edu_text)
print(result_salary_text)
print(result_age_text)
print(result_job_text)

# 使用正则表达式提取招聘会信息
sentence = "我要查询【明天（招聘会时间acb333_ti）】在【成都（招聘会地点aab301）】的【网络（招聘会类型acb481）】招聘会"
pattern_date_address_type = r"我要查询(.*)在(.*)的(.*)招聘会"
result_date_address_type = re.search(pattern_date_address_type, sentence)

result_date_text = result_date_address_type.group(1) if (result_date_address_type and len(result_date_address_type.groups()) >= 1) else '无'
result_address_text = result_date_address_type.group(2) if (result_date_address_type and len(result_date_address_type.groups()) >= 2) else '无'
result_type_text = result_date_address_type.group(3) if (result_date_address_type and len(result_date_address_type.groups()) >= 3) else '无'
print(result_date_text)
print(result_address_text)
print(result_type_text)


