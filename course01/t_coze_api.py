# -*- coding: utf-8 -*-

import requests
import json
from typing import Dict, List, Optional
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
        "bot_id": "7522356641783136294",
        "user": "29032201862555",
        "query": json.dumps({"user": {"name": "敬先生", "genderLabel": "男", "email": "", "age": 55, "maxEducationLabel": "高中", "workYears": 34, "cityLabel": "现居成都 成华区", "phone": "189****9949"}, "resume": {"educationExperiences": [{"schoolName": "四川省绵阳市盐亭县中学", "educationTimeLabel": "1970.01 - 至今", "major": "", "educationLabel": "高中"}], "workExperiences": [{"orgName": "《老街包子》锦江区", "description": "早餐店，白案糸列   包子馒头花卷饺子面条中餐等等", "jobTitle": "白案面点师傅", "timeLabel": "2020.12 - 2023.12 (3年)"}, {"orgName": "宣伟（上海）涂料有限公司", "description": "调色工程师售我技术服务", "jobTitle": "喷涂技术员", "timeLabel": "2003.07 - 2008.11 (5年 4个月)"}, {"orgName": "上海嘉定RD", "description": "优秀的调漆打板技术，曾经参与富士康公司，微软公司，苹果公司，联想公司，惠普公司等众多企业工厂的产品颜色开发以及售后技术服务\n\n17年的实验室工作经历,使我熟悉工业涂料检测工艺,通过改变添加剂、溶剂,调整配方等等来达到一定的性能要求,使我养成了良好的实验室工作习惯,懂得RD工作对公司的重要性,对客户的重要性,体会到管理工作的复杂性,必要性\n\n负责对接销售部门工作申请安排,RD日常管理工作/配方系统/配方转移/TDS制定等工作", "jobTitle": "运营主管", "timeLabel": "2002.11 - 2019.12 (17年 1个月)"}, {"orgName": "深圳大迪涂料公司", "description": "中期任公司主管,负责公司RD颜色开发,技术服务,质量控制管理工作", "jobTitle": "油漆/化工涂料研发", "timeLabel": "1998.04 - 2003.07 (5年 3个月)"}, {"orgName": "海口海外酒店有限公司", "description": "负责中厨具体工作，开发新的菜品，协助厨师长", "jobTitle": "中餐厨师", "timeLabel": "1991.07 - 1998.04 (6年 9个月)"}, {"orgName": "", "description": "", "jobTitle": "面点师", "timeLabel": "工作6年11个月"}], "projectExperiences": [], "languageSkills": [], "certificates": [{"name": "C1驾驶证"}], "purposes": [{"industryLabel": "不限行业", "jobTypeLabel": "面点师", "jobNatureLabel": "全职", "location": "成都", "salaryLabel": "5千-8千/月"}, {"industryLabel": "不限行业", "jobTypeLabel": "调色/配色技术员", "jobNatureLabel": "全职", "location": "成都-成华区", "salaryLabel": "6千-9千/月"}]}}),
        "stream": False,
        "custom_variables": {}
    }

    response = requests.post(url, headers=headers, json=data, stream=True)
    # print("请求响应内容:", response.text)
    result = ""
    if response.status_code == 200:
        print("请求成功，响应内容:", response.text)
        result = getanswers(response)
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
    return result

def getanswers(response):
    """从coze响应中提取答案内容"""
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

def extract_content_from_coze_response(response) -> Dict[str, any]:
    """从coze API响应中提取所有content内容
    
    Args:
        response: requests响应对象
        
    Returns:
        Dict包含提取的内容和元数据
    """
    extracted_data = {
        'contents': [],
        'full_content': '',
        'message_count': 0,
        'status': 'success',
        'error': None
    }
    
    try:
        if response.status_code != 200:
            extracted_data['status'] = 'error'
            extracted_data['error'] = f"HTTP {response.status_code}: {response.text}"
            return extracted_data
        
        # 尝试解析JSON响应
        try:
            response_json = response.json()
            print(f"解析到JSON响应: {type(response_json)}")
            
            # 检查是否有messages字段
            if 'messages' in response_json:
                messages = response_json['messages']
                print(f"找到 {len(messages)} 条消息")
                
                for i, message in enumerate(messages):
                    if message.get('type') == 'answer' and 'content' in message:
                        content = message['content']
                        if content:
                            extracted_data['contents'].append({
                                'content': content,
                                'message_id': message.get('id', f'msg_{i}'),
                                'role': message.get('role', ''),
                                'type': message.get('type', '')
                            })
                            extracted_data['full_content'] += content
                            extracted_data['message_count'] += 1
                            print(f"提取到第 {i+1} 条消息内容，长度: {len(content)}")
            else:
                print("响应中没有找到messages字段")
                print(f"响应结构: {list(response_json.keys()) if isinstance(response_json, dict) else 'Not a dict'}")
                
        except json.JSONDecodeError:
            print("不是JSON格式，尝试解析流式数据")
            # 如果不是JSON，尝试原来的流式数据解析方法
            for line in response.content.split(b'\n'):
                line = line.decode('utf-8').strip()
                if line.startswith('data:{'):
                    try:
                        json_data = json.loads(line[5:])
                        if json_data.get('event') == 'message':
                            message = json_data.get('message', {})
                            if message.get('type') == 'answer':
                                content = message.get('content', '')
                                if content:
                                    extracted_data['contents'].append({
                                        'content': content,
                                        'message_id': message.get('id', ''),
                                        'timestamp': json_data.get('created_at', '')
                                    })
                                    extracted_data['full_content'] += content
                                    extracted_data['message_count'] += 1
                    except json.JSONDecodeError as e:
                        print(f"JSON解析错误: {e}")
                        continue
                    except Exception as e:
                        print(f"处理消息时出错: {e}")
                        continue
                    
    except Exception as e:
        extracted_data['status'] = 'error'
        extracted_data['error'] = str(e)
        print(f"提取过程中出错: {e}")
        
    return extracted_data

def save_content_to_file(content: str, filename: str = 'coze_content.txt') -> bool:
    """将提取的内容保存到文件
    
    Args:
        content: 要保存的内容
        filename: 文件名
        
    Returns:
        bool: 保存是否成功
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"内容已保存到: {filename}")
        return True
    except Exception as e:
        print(f"保存文件时出错: {e}")
        return False

def main():
    """主函数：调用coze API并提取content内容"""
    print("正在调用Coze API...")
    
    # 调用API
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
        "bot_id": "7522356641783136294",
        "user": "29032201862555",
        "query": json.dumps({"user": {"name": "敬先生", "genderLabel": "男", "email": "", "age": 55, "maxEducationLabel": "高中", "workYears": 34, "cityLabel": "现居成都 成华区", "phone": "189****9949"}, "resume": {"educationExperiences": [{"schoolName": "四川省绵阳市盐亭县中学", "educationTimeLabel": "1970.01 - 至今", "major": "", "educationLabel": "高中"}], "workExperiences": [{"orgName": "《老街包子》锦江区", "description": "早餐店，白案糸列   包子馒头花卷饺子面条中餐等等", "jobTitle": "白案面点师傅", "timeLabel": "2020.12 - 2023.12 (3年)"}, {"orgName": "宣伟（上海）涂料有限公司", "description": "调色工程师售我技术服务", "jobTitle": "喷涂技术员", "timeLabel": "2003.07 - 2008.11 (5年 4个月)"}, {"orgName": "上海嘉定RD", "description": "优秀的调漆打板技术，曾经参与富士康公司，微软公司，苹果公司，联想公司，惠普公司等众多企业工厂的产品颜色开发以及售后技术服务\n\n17年的实验室工作经历,使我熟悉工业涂料检测工艺,通过改变添加剂、溶剂,调整配方等等来达到一定的性能要求,使我养成了良好的实验室工作习惯,懂得RD工作对公司的重要性,对客户的重要性,体会到管理工作的复杂性,必要性\n\n负责对接销售部门工作申请安排,RD日常管理工作/配方系统/配方转移/TDS制定等工作", "jobTitle": "运营主管", "timeLabel": "2002.11 - 2019.12 (17年 1个月)"}, {"orgName": "深圳大迪涂料公司", "description": "中期任公司主管,负责公司RD颜色开发,技术服务,质量控制管理工作", "jobTitle": "油漆/化工涂料研发", "timeLabel": "1998.04 - 2003.07 (5年 3个月)"}, {"orgName": "海口海外酒店有限公司", "description": "负责中厨具体工作，开发新的菜品，协助厨师长", "jobTitle": "中餐厨师", "timeLabel": "1991.07 - 1998.04 (6年 9个月)"}, {"orgName": "", "description": "", "jobTitle": "面点师", "timeLabel": "工作6年11个月"}], "projectExperiences": [], "languageSkills": [], "certificates": [{"name": "C1驾驶证"}], "purposes": [{"industryLabel": "不限行业", "jobTypeLabel": "面点师", "jobNatureLabel": "全职", "location": "成都", "salaryLabel": "5千-8千/月"}, {"industryLabel": "不限行业", "jobTypeLabel": "调色/配色技术员", "jobNatureLabel": "全职", "location": "成都-成华区", "salaryLabel": "6千-9千/月"}]}}),
        "stream": False,
        "custom_variables": {}
    }

    try:
        response = requests.post(url, headers=headers, json=data, stream=True)
        
        # 显示响应状态和部分内容用于调试
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应内容前500字符: {response.text[:500]}")
        
        # 提取content内容
        extracted_data = extract_content_from_coze_response(response)
        
        if extracted_data['status'] == 'success':
            print(f"\n成功提取到 {extracted_data['message_count']} 条消息")
            print("\n=== 完整内容 ===")
            print(extracted_data['full_content'])
            
            # 保存到文件
            if extracted_data['full_content']:
                save_content_to_file(extracted_data['full_content'], 'extracted_coze_content.txt')
                
                # 保存详细信息到JSON文件
                with open('coze_response_details.json', 'w', encoding='utf-8') as f:
                    json.dump(extracted_data, f, ensure_ascii=False, indent=2)
                print("详细信息已保存到: coze_response_details.json")
            
            return extracted_data['full_content']
        else:
            print(f"提取失败: {extracted_data['error']}")
            return None
            
    except Exception as e:
        print(f"调用API时出错: {e}")
        return None

if __name__ == '__main__':
    # 使用新的main函数
    result = main()
    if result:
        print("\n=== 内容提取完成 ===")
    else:
        print("\n=== 内容提取失败 ===")