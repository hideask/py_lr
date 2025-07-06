# -*- coding: utf-8 -*-
import json

def translate_json_keys(data):
    """
    将JSON中的英文key转换为中文key
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
        "cityLabel": "城市",
        "unlockedPhone": "手机号",
        "email": "邮箱",
        
        # 简历信息
        "resume": "简历",
        "skillTags": "技能标签",
        
        # 教育经历
        "educationExperiences": "教育经历",
        "schoolName": "学校名称",
        "beginTime": "开始时间",
        "endTime": "结束时间",
        "educationTimeLabel": "教育时间",
        "major": "专业",
        "educationLabel": "学历",
        
        # 工作经历
        "workExperiences": "工作经历",
        "orgName": "公司名称",
        "jobTitle": "职位",
        "description": "描述",
        "timeLabel": "时间",
        "workSkillTags": "工作技能标签",
        
        # 项目经历
        "projectExperiences": "项目经历",
        "responsibility": "职责",
        
        # 语言技能
        "languageSkills": "语言技能",
        "readWriteSkill": "读写能力",
        "hearSpeakSkill": "听说能力",
        
        # 证书
        "certificates": "证书",
        
        # 求职意向
        "purposes": "求职意向",
        "industryLabel": "行业",
        "jobTypeLabel": "职位类型",
        "jobNatureLabel": "工作性质",
        "location": "地点",
        "salaryLabel": "薪资"
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
                
                # 递归处理值，传递当前key作为父级上下文
                translated[chinese_key] = translate_recursive(value, key)
            return translated
        elif isinstance(obj, list):
            return [translate_recursive(item, parent_key) for item in obj]
        else:
            return obj
    
    return translate_recursive(data)

def main():
    # 示例JSON数据
    sample_json = {
        "user": {
            "name": "张女士",
            "genderLabel": "女",
            "age": 29,
            "ageLabel": "29岁",
            "maxEducationLabel": "硕士",
            "workYears": 4,
            "workYearsLabel": "4年",
            "cityLabel": "现居上海 浦东新区"
        },
        "resume": {
            "skillTags": [
                "医疗器械注册",
                "FDA法规",
                "质量管理体系",
                "临床评估",
                "技术文档编制"
            ],
            "educationExperiences": [
                {
                    "schoolName": "上海交通大学",
                    "educationTimeLabel": "2015.09 - 2019.06",
                    "major": "生物医学工程",
                    "educationLabel": "本科"
                },
                {
                    "schoolName": "复旦大学",
                    "educationTimeLabel": "2019.09 - 2021.06",
                    "major": "药学",
                    "educationLabel": "硕士"
                }
            ],
            "workExperiences": [
                {
                    "orgName": "迈瑞医疗国际有限公司",
                    "description": "主导3个二类医疗器械产品注册，完成20+份技术文档编制，协调研发、质量部门完成体系核查，平均缩短注册周期30%",
                    "jobTitle": "医疗器械注册专员",
                    "timeLabel": "2021.07 - 至今 (2年11个月)",
                    "workSkillTags": [
                        {
                            "name": "注册申报"
                        },
                        {
                            "name": "GMP认证"
                        },
                        {
                            "name": "CE认证"
                        }
                    ]
                }
            ],
            "projectExperiences": [
                {
                    "name": "可穿戴心电监测设备注册项目",
                    "timeLabel": "2022.03 - 2023.02 (11个月)",
                    "description": "带领3人团队完成注册检验、临床评价和体系核查，创新采用真实世界数据替代部分临床试验，节省成本120万元"
                }
            ],
            "certificates": [
                {
                    "name": "医疗器械注册专员（RAC）认证"
                }
            ],
            "purposes": [
                {
                    "industryLabel": "医疗器械",
                    "jobTypeLabel": "注册经理",
                    "jobNatureLabel": "全职",
                    "location": "上海",
                    "salaryLabel": "1.5万-2.5万/月"
                }
            ]
        }
    }
    
    # 转换JSON
    translated_json = translate_json_keys(sample_json)
    
    # 打印原始JSON
    print("原始JSON:")
    print(json.dumps(sample_json, ensure_ascii=False, indent=2))
    
    print("\n" + "="*50 + "\n")
    
    # 打印转换后的JSON
    print("转换后的JSON:")
    print(json.dumps(translated_json, ensure_ascii=False, indent=2))
    
    # 保存到文件
    with open('translated_json.json', 'w', encoding='utf-8') as f:
        json.dump(translated_json, f, ensure_ascii=False, indent=2)
    
    print("\n转换完成！结果已保存到 translated_json.json 文件中。")

if __name__ == "__main__":
    main()