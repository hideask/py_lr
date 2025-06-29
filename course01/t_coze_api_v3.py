# -*- coding: utf-8-sig -*-

import requests
import json

from twisted.python.util import println

query = {"user": {"name": "曾先生", "genderLabel": "男", "email": "", "age": 21, "ageLabel": "21岁", "maxEducationLabel": "大专", "workYears": 0, "workYearsLabel": "无经验", "cityLabel": "现居北京 东城区", "phone": "156****2612"}, "resume": {"skillTags": [], "educationExperiences": [{"schoolName": "成都航空职业技术学院", "beginTime": 1661961600000, "endTime": 1751299200000, "educationTimeLabel": "2022.09 - 2025.07", "major": "电气自动化技术", "educationLabel": "大专"}], "workExperiences": [], "projectExperiences": [], "languageSkills": [], "certificates": [], "purposes": [{"industryLabel": "不限行业", "jobTypeLabel": "商品销售", "jobNatureLabel": "全职", "location": "成都", "salaryLabel": "6千-1.1万/月"}, {"industryLabel": "电子商务、人工智能、新媒体", "jobTypeLabel": "人力资源专员/助理", "jobNatureLabel": "兼职、全职、实习", "location": "成都", "salaryLabel": "5千-8千/月"}, {"industryLabel": "快速消费品", "jobTypeLabel": "行政专员/助理", "jobNatureLabel": "兼职、全职、实习", "location": "成都", "salaryLabel": "8千-1万/月"}]}}
def chat_query():
    url = 'https://api.coze.cn/v3/chat'
    headers = {
        "Content-Type": "application/json",
        "Authorization" : "Bearer pat_wkSk1NRVFOl7CMVxGTht2QBQiDWOnGGWPObkg56nQnMoPTnUEuYrmmkEgKfsZf6r",
    }
    data = {
        "bot_id": "7512823884287475712",
        "user_id": "788899678976",
        # "query": json.dumps(query),
        "stream": True,
        "auto_save_history": False,
        "additional_messages" : [
            {
                "role": "user",
                "content": json.dumps(query),
                "content_type": "text"
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data, stream=True)
    # print("请求响应内容:", response.text)
    result = ""

    if response.status_code == 200:
        for line in response.iter_lines():  # decode_unicode=True 将字节解码为字符串
            if line:  # 忽略空行
                # 处理每一行数据
                line = line.decode('utf-8').strip()
                print(line)
                # 或者进行其他处理
                # process(line)
    return result

def getanswers(response):
    result = ""
    for line in response.content.split(b'\n'):
        # print(line)
        line = line.decode('utf-8').strip()
        if line.startswith('data:{'):
            # print(line)
            try:
                json_data = json.loads(line[5:])
                if json_data['event'] == 'message' and json_data['message']['type'] == 'answer':
                    result += json_data['message']['content']
            except Exception as e:
                print(str(e))
                continue
    return result

if __name__ == '__main__':
    print(chat_query())