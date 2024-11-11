import hashlib
import time

import requests
import json
from datetime import datetime



# 获取当前时间戳
# timestamp = str(int(datetime.utcnow().timestamp()))
timestamp = str(int(time.time()))
# timestamp = '1718606532'
# 定义请求体中的数据
data = {
    "appId": "bd2740a6-b9bc-487a-8695-cd6754d45da6",
    "accessKey": "dQXqGokL4WwP9luWi39jqQ==",
    "secretKey": "it5CK_BkikwL9TW9Y9vXP1qHrmzlx9vhYknD1c0cfMQ="
    # "timestamp": timestamp
}


print(timestamp)

# 将业务参数转换为JSON字符串，并拼接上时间戳
combined_string = json.dumps(data) + timestamp
print(combined_string)

# 计算MD5
md5_hash = hashlib.md5(combined_string.encode('utf-8'))

# 取32位小写值
md5_32lower = md5_hash.hexdigest().lower()

print(md5_32lower)


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
