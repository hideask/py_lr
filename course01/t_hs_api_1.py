import hashlib
import time

import requests
import json

app_id = 'bd2740a6-b9bc-487a-8695-cd6754d45da6'
def get_md5code(params, timestamp):
    # 将业务参数转换为JSON字符串，并拼接上时间戳
    combined_string = json.dumps(params) + timestamp
    # print(combined_string)

    # 计算MD5
    md5_hash = hashlib.md5(combined_string.encode('utf-8'))

    # 取32位小写值
    md5_32lower = md5_hash.hexdigest().lower()

    # print(md5_32lower)
    return md5_32lower

#获取数字人登录信息
def get_login_info():
    # 获取当前时间戳
    # timestamp = str(int(datetime.utcnow().timestamp()))
    timestamp = str(int(time.time()))
    # timestamp = '1718606532'
    # 定义请求体中的数据
    data = {
        "appId": app_id,
        "accessKey": "dQXqGokL4WwP9luWi39jqQ==",
        "secretKey": "it5CK_BkikwL9TW9Y9vXP1qHrmzlx9vhYknD1c0cfMQ="
    }

    # print(timestamp)

    md5_32lower = get_md5code(data, timestamp)

    # 定义请求的URL
    url = 'https://virtulahuman-api.openvirtualhuman.cn/openapi/v2/oauth/token'

    # 构建请求头
    headers = {
        'timestamp': str(timestamp),  # 生成当前时间的Unix时间戳（秒级）
        'sign': md5_32lower,  # 假定的签名值，实际中需要根据API要求计算
        'Content-Type': 'application/json'
    }

    # 发送POST请求
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # 检查响应状态码
    if response.status_code == 200:
        print("请求成功，响应内容:", response.text)
    else:
        print(f"请求失败，状态码: {response.status_code}, 响应内容: {response.text}")
    return response.json()

#获取数字人url地址
def get_url(enterpriseId,accessToken):
    url = 'https://api-mp.x-era.com/v1/instance'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': accessToken,
        'Enterprise-Id': enterpriseId,
        'appId': app_id
    }
    data = {
        "video": {
            "height": 1920,
            "width": 1080,
            "bitrate": 2000
        },
        "position": {
            "auto": True
        },
        "sceneId": "fae07be4e85f40b5991490519699ea3e",
        "timbreId": "7522ca7273ea43d7b8d92c541dd11be2",
        "mode": "interact",
        "background": {
            "type": "color",
            "color": "#FF0000",
            # "color": "transparent"
            "background-color": "rgba(255, 0, 0, 0.5)"
        },
        "stopAfter": 300
    }

    # 创建请求对象
    # req = requests.Request('POST', url, headers=headers, data=json.dumps(data))

    # 准备请求（这一步会构造出一个可以发送的请求对象，但不实际发送）
    # prepared_req = req.prepare()

    # 打印请求报文
    # print("请求方法:", prepared_req.method)
    # print("请求URL:", prepared_req.url)
    # print("请求头:\n", prepared_req.headers)
    # print("请求体:\n", prepared_req.body)

    # 发送POST请求
    response = requests.post(url, headers=headers, json=data)

    # 检查响应状态码
    if response.status_code == 200:
        print("请求成功，响应内容:", response.text)
    else:
        print(f"请求失败，状态码: {response.status_code}, 响应内容: {response.text}")

    return response.json()

def getAgentToken():
    url = 'http://llmops.volcenginepaas.com:3000/api/proxy/api/v1/create_conversation'
    # url = 'http://10.56.63.23:32300/api/proxy/api/v1/create_conversation'
    headers = {
        "Content-Type": "application/json",
        "Apikey": "cpqenlrfdo77284d714g"
    }
    data = {
        "Apikey": "cpqenlrfdo77284d714g",
        "UserID": "cpoer93fdo77284d22ng"
    }

    # req = requests.Request('POST', url, headers=headers, json=data)

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("请求成功，响应内容:", response.text)
    else:
        print(f"请求失败，状态码: {response.status_code}, 响应内容: {response.text}")
    return response.json()


def getChatId(api_key, user_id):
    url = 'http://llmops.volcenginepaas.com:3000/api/proxy/api/v1/create_conversation'
    # url = 'http://10.56.63.23:32300/api/proxy/api/v1/create_conversation'
    headers = {
        "Content-Type": "application/json",
        "Apikey": api_key
    }
    data = {
        "Appkey": api_key,
        "Inputs": {
            "var": "variable"
        },
        "UserID": user_id
    }

    # req = requests.Request('POST', url, headers=headers, json=data)

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("请求成功，响应内容:", response.text)
    else:
        print(f"请求失败，状态码: {response.status_code}, 响应内容: {response.text}")
    return response.json()

def chat_query(api_key, user_id, chat_id, query):
    url = 'http://llmops.volcenginepaas.com:3000/api/proxy/api/v1/chat_query'
    # url = 'http://10.56.63.23:32300/api/proxy/api/v1/create_conversation'
    responseMode = "streaming"
    # responseMode = "blocking"
    headers = {
        "Content-Type": "application/json",
        "Apikey": api_key
    }
    data = {
        "Query": query,
        "AppConversationID": chat_id,
        "AppKey": api_key,
        "ResponseMode": responseMode,
        "UserID": user_id
    }


    response = requests.post(url, headers=headers, json=data)
    # print("请求响应内容:", response.text)
    result = ""
    if response.status_code == 200:
        # print("请求成功，响应内容:", response.text)
        result = getanswers(response, responseMode)
    else:
        print(f"请求失败，状态码: {response.status_code}, 响应内容: {response.text}")
    return result

def getanswers(response, responseMode):
    result = ""
    for line in response.content.split(b'\n'):
        # print(line)
        line = line.decode('utf-8').strip()
        if line.startswith('data:data:'):
            try:
                json_data = json.loads(line[10:])
                if (responseMode == "streaming" and json_data['event'] == "message")\
                        or (responseMode == "blocking" and json_data['event'] == "message_end"):
                    result += json_data['answer']
            except Exception as e:
                print(str(e))
                continue
    return result

if __name__ == '__main__':
    # 通过调用get_login_info函数来获取登录信息
    # 这里获取的登录信息可能包括企业ID和访问令牌等关键数据
    res = get_login_info()

    # 使用获取到的企业ID和访问令牌来进一步获取流媒体相关的信息
    # 这里假设get_url函数需要这两个参数来构造请求，以获取特定企业的流媒体URL和UUID
    res1 = get_url(res['data']['enterpriseId'], res['data']['accessToken'])

    # 输出访问令牌，用于后续的身份验证或授权过程
    # print(res['data']['accessToken'])

    # 输出流媒体URL，这是获取到的关键流媒体资源的地址
    # print(res1['data']['pullStreamUrl'])
    #
    # # 输出UUID，这可能是用于唯一标识流媒体资源的标识符
    # print(res1['data']['uuid'])
    api_key = 'cpqenlrfdo77284d714g'
    # api_key = 'cpsee1kr5s4jj70mmbqg'
    user_id = '123'
    # user_id = '123456'
    # res_chat_id = getChatId(api_key, user_id)
    # print(res_chat_id)
    #
    # chat_id = res_chat_id['Conversation']['AppConversationID']
    # print(chat_id)
    # print("结果输出")
    # print(chat_query(api_key, user_id, 'cpsclp3fdo77284d9a6g', '你好，我要找份工作'))
    # print(chat_query(api_key, user_id, 'cpsclp3fdo77284d9a6g', '公司欠我工资不发怎么办'))
    # query = input("请输入您的咨询内容（输入'退出'以结束）: ")
    # while query != '退出':
    #     print(chat_query(api_key, user_id, "cq72ot3fdo77284dq650", query))
    #     query = input("请输入您的咨询内容（输入'退出'以结束）: ")




    



