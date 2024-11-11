import requests
import json

from twisted.python.util import println


def chat_query():
    url = 'https://api.coze.cn/v3/chat'
    headers = {
        "Content-Type": "application/json",
        "Authorization" : "Bearer pat_M6dOiyngbNi4JSkctY4PUlgkWoz2961UIL4tq2FttNULLiod3xhqvTz9oqPl1Zap",
    }
    data = {

        "bot_id": "7399609039661056038",
        "user_id": "29032201862555",
        "query": "工伤认定",
        "stream": True,
        "auto_save_history": True,
        "additional_messages" : [
            {
                "role": "user",
                "content": "工伤认定",
                "content_type": "text"
            }
        ]
        #{"additional_messages":[{"role":"user","content_type":"text","content":"1加上8等于多少呢"}],"user_id":"29032201862555","stream":true,"bot_id":"7399609039661056038","auto_save_history":true}
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