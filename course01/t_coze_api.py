import requests
import json

from twisted.python.util import println


def chat_query():
    url = 'https://api.coze.cn/open_api/v2/chat'
    headers = {
        "Content-Type": "application/json",
        "Connection": "keep-alive",
        "Accept": "*/*",
        "Authorization" : "Bearer pat_Gg8YY6O4kYqiZiFOU20ZwvTLlIh8c6IdtDW2F2n20rfPexIXdgcBVnVTk4hOQCP0",
        "Host": "api.coze.cn",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    data = {
        "conversation_id": "123",
        "bot_id": "7519044359497760768",
        "user": "29032201862555",
        "query": "工伤认定",
        "stream": False,
        "custom_variables": {}
    }

    response = requests.post(url, headers=headers, json=data, stream=True)
    # print("请求响应内容:", response.text)
    result = ""
    if response.status_code == 200:
        print("请求成功，响应内容:", response.text)
        # result = getanswers(response)
    else:
        print(f"请求失败，状态码: {response.status_code}, 响应内容: {response.text}")

    # if response.status_code == 200:
    #     for line in response.iter_lines():  # decode_unicode=True 将字节解码为字符串
    #         if line:  # 忽略空行
    #             # 处理每一行数据
    #             line = line.decode('utf-8').strip()
    #             if line.startswith('data:{'):
    #                 json_data = json.loads(line[5:])
    #                 if json_data['event'] == 'message' and json_data['message']['type'] == 'answer':
    #                     println(json_data['message']['content'])
    #             # 或者进行其他处理
    #             # process(line)
    # return result

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