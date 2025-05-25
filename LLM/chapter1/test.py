import subprocess
import logging
import json

# 配置日志记录
logging.basicConfig(level=logging.INFO)


def call_curl(url, method='GET', headers=None, data=None, options=None):
    try:
        # 构建curl命令
        command = ['curl', url]

        # 添加方法
        command.extend(['-X', method])

        # 添加头部信息
        if headers:
            for key, value in headers.items():
                command.extend(['--header', f"{key}: {value}"])

        # 添加数据
        if data:
            command.extend(['--data-raw', json.dumps(data)])

        # 添加其他选项
        if options:
            command.extend(options)

        # 使用subprocess.run来执行curl命令
        result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=10)
        logging.info(f"Successfully fetched data from {url}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        logging.error(f"Error fetching data from {url}: {e.stderr}")
        return f"Error: {e.stderr}"
    except subprocess.TimeoutExpired:
        logging.error(f"Timeout expired while fetching data from {url}")
        return "Error: Timeout expired"


# 示例调用
url = "http://172.31.253.251:8109/v1/chat-messages"
headers = {
    'Authorization': 'Bearer app-C3kVhOjgJfMax6S1r5YN',
    'Content-Type': 'application/json',
    'Platform-Token': '5500d7c34dd34600b80898ff9471f1bc'
}
data = {
    "inputs": {},
    "query": "hello",
    "response_mode": "blocking",
    "conversation_id": "",
    "user": "username",
    "files": [
        {
            "type": "image",
            "transfer_method": "remote_url",
            "url": "http://172.31.253.251:8109/v1/logo/logo.svg"
        }
    ]
}

response = call_curl(url, method='POST', headers=headers, data=data)
print(response)
