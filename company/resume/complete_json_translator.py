# -*- coding: utf-8 -*-
import json

def translate_json_keys(data):
    """
    将JSON中的英文key转换为中文key
    支持完整的简历数据结构转换
    """
    # 定义英文到中文的映射字典
    key_mapping = {
        # 用户信息
        "user": "用户",
        "name": "姓名",
        "genderLabel": "性别",
        "age": "年龄",
        "ageLabel": "年龄标签",
        "maxEducationLabel": "最高学历",
        "workYears": "工作年限",
        "workYearsLabel": "工作年限标签",
        "cityLabel": "居住城市",
        "phone": "手机号",
        "email": "电子邮箱",
        
        # 简历信息
        "resume": "简历",
        "skillTags": "技能标签",
        
        # 教育经历
        "educationExperiences": "教育经历",
        "schoolName": "学校名称",
        "beginTime": "入学时间",
        "endTime": "毕业时间",
        "educationTimeLabel": "教育时间段",
        "major": "专业",
        "educationLabel": "学历层次",
        
        # 工作经历
        "workExperiences": "工作经历",
        "orgName": "公司名称",
        "jobTitle": "职位名称",
        "description": "工作内容",
        "timeLabel": "工作时间段",
        "workSkillTags": "工作技能标签",
        
        # 项目经历
        "projectExperiences": "项目经历",
        "beginTime": "项目开始时间",
        "endTime": "项目结束时间",
        "timeLabel": "项目时间段",
        "description": "项目描述",
        "responsibility": "项目职责",
        
        # 语言技能
        "languageSkills": "语言技能",
        "readWriteSkill": "读写能力",
        "hearSpeakSkill": "听说能力",
        
        # 证书
        "certificates": "证书",
        
        # 求职意向
        "purposes": "求职意向",
        "industryLabel": "期望行业",
        "jobTypeLabel": "期望职位",
        "jobNatureLabel": "工作性质",
        "location": "期望地点",
        "salaryLabel": "期望薪资"
    }
    
    def translate_recursive(obj, parent_key=None):
        """
        递归翻译JSON对象的key
        """
        if isinstance(obj, dict):
            translated = {}
            for key, value in obj.items():
                # 翻译key，如果映射中没有则保持原样
                chinese_key = key_mapping.get(key, key)
                
                # 特殊处理name字段，根据父级上下文决定翻译
                if key == "name":
                    if parent_key == "workSkillTags":
                        chinese_key = "技能名称"
                    elif parent_key == "certificates":
                        chinese_key = "证书名称"
                    elif parent_key == "projectExperiences":
                        chinese_key = "项目名称"
                    elif parent_key == "languageSkills":
                        chinese_key = "语言名称"
                    else:
                        chinese_key = "姓名"

                if key == 'beginTime':
                    if parent_key == 'workExperiences':
                        chinese_key = '工作开始时间'
                    elif parent_key == 'projectExperiences':
                        chinese_key = '项目开始时间'
                    elif parent_key == 'educationExperiences':
                        chinese_key = '教育开始时间'
                    else:
                        chinese_key = '开始时间'
                
                if key == 'endTime':
                    if parent_key == 'workExperiences':
                        chinese_key = '工作结束时间'
                    elif parent_key == 'projectExperiences':
                        chinese_key = '项目结束时间'
                    elif parent_key == 'educationExperiences':
                        chinese_key = '教育结束时间'
                    else:
                        chinese_key = '结束时间'
                
                # 递归处理值，传递当前key作为父级上下文
                translated[chinese_key] = translate_recursive(value, key)
            return translated
        elif isinstance(obj, list):
            return [translate_recursive(item, parent_key) for item in obj]
        else:
            return obj
    
    return translate_recursive(data)

def translate_from_file(input_file, output_file=None):
    """
    从文件读取JSON并转换key，保存到输出文件
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        translated_data = translate_json_keys(data)
        
        if output_file is None:
            output_file = input_file.replace('.json', '_translated.json')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(translated_data, f, ensure_ascii=False, indent=2)
        
        print(f"转换完成！结果已保存到 {output_file}")
        return translated_data
    
    except FileNotFoundError:
        print(f"错误：找不到文件 {input_file}")
        return None
    except json.JSONDecodeError:
        print(f"错误：{input_file} 不是有效的JSON文件")
        return None

def main():
    # 完整的示例JSON数据（用户提供的数据）
    complete_json = {
    "user": {
        "name": "万女士",
        "genderLabel": "女",
        "email": "",
        "age": 28,
        "ageLabel": "28岁",
        "maxEducationLabel": "硕士",
        "workYears": 3,
        "workYearsLabel": "3年",
        "cityLabel": "现居成都 青羊区",
        "phone": "158****3514"
    },
    "resume": {
        "skillTags": [
            "gan",
            "纂刻"
        ],
        "educationExperiences": [
            {
                "schoolName": "桂林电子科技大学",
                "beginTime": 1567267200000,
                "endTime": 1656604800000,
                "educationTimeLabel": "2019.09 - 2022.07",
                "major": "材料工程技术",
                "educationLabel": "硕士"
            },
            {
                "schoolName": "攀枝花学院",
                "beginTime": 1441036800000,
                "endTime": 1559318400000,
                "educationTimeLabel": "2015.09 - 2019.06",
                "major": "材料成型及控制工程",
                "educationLabel": "本科"
            }
        ],
        "workExperiences": [
            {
                "orgName": "成都海威华芯科技有限公司",
                "description": "负责GaN/Si与GaN/SiC HEMT 器件的开发、电性调试及其代工流片工作，主要包括：\n1、常开型GaN/Si HEMT器件的工艺开发，包括P-GaN刻蚀，OHM退火，钝化层工艺等，其中刻蚀与钝化层工艺的改良极大促进器件Vth，Ig等电性改善。\n2、负责完成GaN/SiC HEMT产品全流程流片。日常监控制程中的工艺量测数据及对inline issue解析，解决光刻显影不良、刻蚀形貌缺陷、金属黑边等工艺问题，改善器件形貌与提升电性，并顺利完成产品交付。\n3、监控流片工艺参数，负责提升芯片良率。根据异常SPC/MES/WAT数据反馈，找出问题制程并提出改善方案。芯片良率提高约20%。\n4、负责器件可靠性提升，根据调研，设计实验，通过改变相关工艺制程提升器件可靠性，目前已取得较大成效。E-mode器件HTRB项目通过500H验证无样品失效，HTGB项目通过1000H验证无样品失效。",
                "jobTitle": "工艺整合工程师（PIE）",
                "timeLabel": "2022.07 - 至今 (2年 9个月)",
                "workSkillTags": [
                    {
                        "name": "半导体"
                    },
                    {
                        "name": "芯片"
                    }
                ]
            }
        ],
        "projectExperiences": [
            {
                "name": "IPD 无源器件开发",
                "beginTime": 1701360000000,
                "endTime": 0,
                "timeLabel": "2023.12 - 至今 (1年 4个月)",
                "description": "协助部门无源产品开发设计，已制版且在产线流片验证并出货。主要工艺调试包括工艺开发以及电性调试，包括TFR电阻性能调试，金属连线调试，器件稳定性烘焙调试等。\n1、工艺开发：根据版图设计确定最佳的工艺流程数据，满足产品性能要求和生产效率。通过小批量试制，验证各步骤的可行性和效果，收集数据并进行分析，优化工艺流程。\n2、电性调试：测量和调试TFR电阻值，考虑温度对其影响，同时优化电阻材料。\n3、稳定性烘焙：设计对照实验，通过不同温度环境下烘焙不同时间，确定在250℃下烘焙一定时长可有效提升器件稳定性。",
                "responsibility": ""
            },
            {
                "name": "GaN/Si 功率器件开发",
                "beginTime": 1656604800000,
                "endTime": 1701360000000,
                "timeLabel": "2022.07 - 2023.12 (1年 5个月)",
                "description": "该项目主要是开发常开型GaN/Si HEMT器件（E-MODE）\n工艺调试\n1、P-GaN 刻蚀：此工艺为E-MODE关键工艺，刻蚀效果好坏直接影响器件阈值电压和栅漏电等关键电性参数。通过精细控制刻蚀条件与参数，成功优化了刻蚀界面的质量，减少了表面损耗和缺陷，提升器件电性。有效将Vth正偏，同时减少GATE 漏电，Ig约为nA量级。\n2、OHM 退火：调整退火温度、时间与气氛等条件，改善金属与半导体的接触质量，降低接触电阻。\n3、PE刻蚀后钝化层保护：有效防止器件表面污染和后续工艺对表面的损伤。增强其绝缘性与稳定性。\n4、可靠性攻关：针对器件可靠性，设计实验方案，通过调整钝化层厚度与工艺顺序，减少后续工艺对器件的侵蚀和损伤，提高器件可靠性。E-MODE器件在HTRB项目中通过500H验证，HTGB项目中通过1000H验证。",
                "responsibility": ""
            },
            {
                "name": "铁基非晶纳米晶软磁合金的制备与研究",
                "beginTime": 1567267200000,
                "endTime": 1654012800000,
                "timeLabel": "2019.09 - 2022.06 (2年 9个月)",
                "description": "独立完成文献调研，实验设计、制备、测试分析，论文撰写。采用电弧熔炼法制备FeSiBPCCu合金，利用单辊悬淬法制备铁基非晶合金带材，研究不同元素掺杂对其非晶形成能力，软磁性能，热力学性能等影响。",
                "responsibility": ""
            }
        ],
        "languageSkills": [
            {
                "name": "英语",
                "readWriteSkill": "良好",
                "hearSpeakSkill": "良好"
            },
            {
                "name": "日语",
                "readWriteSkill": "一般",
                "hearSpeakSkill": "良好"
            }
        ],
        "certificates": [
            {
                "name": "GET-4"
            },
            {
                "name": "获得2021年度校二等奖学金"
            },
            {
                "name": "获得2020年度校三等奖学金"
            },
            {
                "name": "获得2019年度校二等奖学金"
            },
            {
                "name": "2021创客中国广西中小企业比赛创客组一等奖"
            },
            {
                "name": "获2021移动互联网大赛（广西赛区）铜奖"
            }
        ],
        "purposes": [
            {
                "industryLabel": "不限行业",
                "jobTypeLabel": "材料工程师",
                "jobNatureLabel": "全职",
                "location": "成都",
                "salaryLabel": "8千-1.6万/月"
            },
            {
                "industryLabel": "船舶/航空/航天/火车制造、钢铁/有色金属冶炼及加工、军工制造",
                "jobTypeLabel": "工艺整合工程师（PIE）",
                "jobNatureLabel": "全职",
                "location": "成都-青羊区",
                "salaryLabel": "9千-1.4万/月"
            },
            {
                "industryLabel": "光电子行业、消费电子产品、电子/半导体/集成电路",
                "jobTypeLabel": "工艺整合工程师（PIE）",
                "jobNatureLabel": "全职",
                "location": "成都-青羊区",
                "salaryLabel": "8千-1.5万/月"
            }
        ]
    }
}
    
    print("JSON Key转换程序")
    print("=" * 50)
    
    # 转换JSON
    translated_json = translate_json_keys(complete_json)
    
    # 打印转换后的JSON（部分）
    print("转换后的JSON结构（部分展示）:")
    print(json.dumps(translated_json, ensure_ascii=False, indent=2)[:1000] + "...")
    
    # 保存完整结果到文件
    with open('complete_translated_json.json', 'w', encoding='utf-8') as f:
        json.dump(translated_json, f, ensure_ascii=False, indent=2)
    
    print("\n完整转换结果已保存到 complete_translated_json.json 文件中。")
    
    # 使用说明
    print("\n使用说明:")
    print("1. 直接运行此程序：转换内置的示例JSON")
    print("2. 使用translate_json_keys(data)函数：传入JSON数据进行转换")
    print("3. 使用translate_from_file(input_file)函数：从文件读取并转换JSON")
    
if __name__ == "__main__":
    main()