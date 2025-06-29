# -*- coding: utf-8 -*-
import json
import re
import psycopg2
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod

prompt_resume = """
# 角色
你是一个专业且高效的简历精灵，能运用丰富的行业经验和专业知识，精准对求职者口述的简历内容进行识别，并将结果以格式化的形式准确返回。
## 技能：简历生成及格式化返回
1. 当用户需要生成简历信息时，以用户的求职意向返回格式化简历信息，包括以下内容：
（1）个人信息;
（2）求职意向（多条）;
（3）技能标签（多条）;
（4）工作经历（多条）;
（5）项目经历（多条）;
（6）教育经历（多条）;
（7）语言能力（多条）；
（8）证书信息（多条）。
2、具体json格式如下
{
    "用户": {
        "姓名": "",
        "性别": "",
        "年龄": "",
        "年龄标签": "",
        "最高学历": "",
        "工作年限": "",
        "工作年限标签": "",
        "居住城市": "",
        "手机号": "",
        "电子邮箱": ""
    },
    "简历": {
        "技能标签": [],
        "教育经历": [{
            "学校名称": "",
            "教育时间段": "",
            "专业": "",
            "学历层次": ""
        }],
        "工作经历": [{
            "工作单位": "",
            "职位名称": "",
            "工作内容": "",
            "工作时间段": ""
        }],
        "项目经历": [{
            "项目名称": "",
            "项目时间段": "",
            "项目描述": ""
        }],
        "语言能力": [{
            "语言种类": "",
            "读写能力": "",
            "听说能力": ""
        }],
        "证书信息": [{
            "证书名称": ""
        }],
        "求职意向": [{
            "期望行业": "",
            "期望职位": "",
            "工作性质": "",
            "期望地点": "",
            "期望薪资": ""
        }]
    }
}
3. 对识别出的信息进行科学整理，去除其中的网址、段落符号等无关内容，按照清晰、规范且符合行业标准的格式重新组织,如果用户没有提及的内容则在格式化内容中返回此项为空字符串""。
4. 将格式化后的简历信息以json格式返回,要求json内容完整、准确无误，格式正确。

## 限制。
- 输出内容需严格遵循格式化要求，不得随意更改格式框架，确保json格式的规范性和准确性。
"""

context_resume = """
请根据求职者简历生成描述，生成简历并格式化返回，要求简历内容亮眼，不要有错别字，列出想找的岗位所需要掌握的必须技能作为专业技能。
"""

prompt_job = """
# 角色
你是一个专业且高效的岗位精灵，能运用丰富的行业经验和专业知识，精准对岗位数据信息进行提取，并将结果以格式化的形式准确返回。
## 技能
1、	当用户需要生成岗位的格式化信息时，按照指定的 JSON 结构生成标准化招聘数据，确保字段对应准确、信息完整。
2、	需严格匹配以下字段要求，无对应内容留空或填 “不限”：
{
"公司名称": "",
"岗位名称": "",
"福利待遇": "",
"工作区域": "",
"岗位描述": "",
"招聘人数": "",
"工作性质": "",
"工作年限": "",
"薪资范围": "",
"学历要求": "",
"详细地址": ""
}

"""

context_job = """
请根据岗位生成描述，生成岗位并格式化返回，要求岗位内容亮眼，不要有错别字。
"""

platform = "zhilian_resume"

if platform == "zhilian_resume":
   prompt = prompt_resume
   context = context_resume
elif platform == "zhilian_job":
   prompt = prompt_job
   context = context_job
elif platform == "sc_resume":
   prompt = prompt_resume
   context = context_resume
elif platform == "sc_job":
   prompt = prompt_job
   context = context_job




@dataclass
class TableConfig:
    """表配置类"""
    table_name: str
    id_field: str = "id"

    if platform == "zhilian_resume":
        json_source_field: str = "resume_processed_info"
        description_field: str = "resume_description_detail"
        json_target_field: str = "resume_processed_info_ch"
    elif platform == "zhilian_job":
        json_source_field: str = "processed_info"
        description_field: str = "job_description_detail"
        json_target_field: str = "job_processed_info_ch"
    elif platform == "sc_resume":
        json_source_field: str = "resume_info"
        description_field: str = "resume_description_detail"
        json_target_field: str = "resume_processed_info_ch"
    elif platform == "sc_job":
        json_source_field: str = "processed_info"
        description_field: str = "job_description_detail"
        json_target_field: str = "job_processed_info_ch"

    train_data_field: str = "train_data_ch"
    system_field: str = "system_ch"
    context_field: str = "context_ch"
    target_field: str = "target_ch"
    batch_size: int = 1000


class JSONTranslator:
    """JSON键值翻译器"""
    
    def __init__(self):

        if platform == "zhilian_resume" or platform == "sc_resume":
        #简历
            self.key_mapping = {
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
            "ethnicity": "民族",
            "idCard": "证件号码",
            
            # 简历信息
            "resume": "简历",
            "skillTags": "技能标签",
            
            # 教育经历
            "educationExperiences": "教育经历",
            "schoolName": "学校名称",
            # "beginTime": "入学时间",
            # "endTime": "毕业时间",
            "educationTimeLabel": "教育时间段",
            "major": "专业",
            "educationLabel": "学历层次",
            
            # 工作经历
            "workExperiences": "工作经历",
            "orgName": "工作单位",
            "jobTitle": "职位名称",
            "description": "工作内容",
            "timeLabel": "工作时间段",
            # "workSkillTags": "工作技能标签",
            
            # 项目经历
            "projectExperiences": "项目经历",
            # "beginTime": "项目开始时间",
            # "endTime": "项目结束时间",
            "timeLabel": "项目时间段",
            "description": "项目描述",
            # "responsibility": "项目职责",
        
            # 语言技能
            "languageSkills": "语言能力",
            "readWriteSkill": "读写能力",
            "hearSpeakSkill": "听说能力",
            
            # 证书
            "certificates": "证书信息",
            
            # 求职意向
            "purposes": "求职意向",
            "industryLabel": "期望行业",
            "jobTypeLabel": "期望职位",
            "jobNatureLabel": "工作性质",
            "location": "期望地点",
            "salaryLabel": "期望薪资"
        }
        elif platform == "zhilian_job" or platform == "sc_job":
        #岗位
            self.key_mapping = {
                "companyName" : "公司名称",
                "name" : "岗位名称",
                # "job_name" : "岗位全称",
                "welfareTagList" : "福利待遇",
                "cityDistrict" : "工作区域",
                "jobSummary" : "岗位描述",
                "recruitNumber" : "招聘人数",
                "workType" : "工作性质",
                "salaryReal" : "薪资范围",
                "workingExp" : "工作年限",
                "education" : "学历要求",
                # "needMajor" : "专业要求",
                # "staffName" : "联系人",
                "address" : "详细地址",   
            }
    
    
    def translate_json_keys(self, data: Any) -> Any:
        """将JSON中的英文key转换为中文key"""
        return self._translate_recursive(data)
    
    def _translate_recursive(self, obj: Any, parent_key: Optional[str] = None) -> Any:
        """递归翻译JSON对象的key，只保留在key_mapping中定义的字段"""
        if isinstance(obj, dict):
            translated = {}
            for key, value in obj.items():
                # 只处理在key_mapping中定义的字段
                if key in self.key_mapping:
                    chinese_key = self.key_mapping[key]
                    
                    # 特殊处理name字段的上下文翻译
                    if platform == "zhilian_resume" or platform == "sc_resume":
                        if key == "name":
                            if parent_key == "workSkillTags":
                                chinese_key = "技能名称"
                            elif parent_key == "certificates":
                                chinese_key = "证书名称"
                            elif parent_key == "projectExperiences":
                                chinese_key = "项目名称"
                            elif parent_key == "languageSkills":
                                chinese_key = "语言种类"
                            elif parent_key == "user":
                                chinese_key = "姓名"
                            else:
                                chinese_key = "名称"

                        # 特殊处理时间字段的上下文翻译
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

                        if key == 'description':
                            if parent_key == 'workExperiences':
                                chinese_key = '工作内容'
                            elif parent_key == 'projectExperiences':
                                chinese_key = '项目描述'
                            elif parent_key == 'educationExperiences':
                                chinese_key = '教育描述'
                            else:
                                chinese_key = '描述'
                        
                        if key == 'timeLabel':
                            if parent_key == 'workExperiences':
                                chinese_key = '工作时间段'
                            elif parent_key == 'projectExperiences':
                                chinese_key = '项目时间段'
                            elif parent_key == 'educationExperiences':
                                chinese_key = '教育时间段'
                            else:
                                chinese_key = '时间段'
                    
                    # 递归处理值，传递当前key作为父级上下文
                    translated[chinese_key] = self._translate_recursive(value, key)
                # 不在key_mapping中的字段将被过滤掉，不包含在结果中
            return translated
        elif isinstance(obj, list):
            return [self._translate_recursive(item, parent_key) for item in obj]
        else:
            return obj


class TrainingDataBuilder:
    """训练数据构建器"""
    
    def __init__(self, system_template: str = "", context_template: str = ""):
        self.system_template = system_template
        self.context_template = context_template
    
    def build_training_data(self, system_content: str, context_content: str, target_content: str) -> Dict[str, Any]:
        """构建训练数据格式"""
        return {
            "system": [system_content] if system_content else [""],
            "context": [context_content] if context_content else [""],
            "target": target_content if target_content else ""
        }


class DatabaseProcessor:
    """数据库处理器基类"""
    
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.translator = JSONTranslator()
        self.training_builder = TrainingDataBuilder()
        self._lock = threading.Lock()
    
    def get_connection(self) -> psycopg2.extensions.connection:
        """获取数据库连接"""
        return psycopg2.connect(**self.db_config)
    
    def _process_single_record(self, record_data: tuple, config: TableConfig) -> Optional[tuple]:
        """处理单条记录"""
        try:
            record_id, json_data, description = record_data
            
            # 解析JSON数据
            if isinstance(json_data, str):
                parsed_data = json.loads(json_data)
            else:
                parsed_data = json_data
            
            # 1. 转换JSON键为中文
            translated_json = self.translator.translate_json_keys(parsed_data)
            translated_json_str = json.dumps(translated_json, ensure_ascii=False, indent=2)
            
            # 2. 构建训练数据
            system_content = prompt
            context_content = description + "       " + context
            target_content = translated_json_str
            
            training_data = self.training_builder.build_training_data(
                system_content, context_content, target_content
            )
            training_data_str = json.dumps(training_data, ensure_ascii=False, indent=2)
            
            return (record_id, translated_json_str, training_data_str)
            
        except Exception as e:
            print(f"处理记录 {record_data[0] if record_data else 'unknown'} 时出错: {str(e)}")
            return None
    
    def _batch_update_database(self, results: List[tuple], config: TableConfig) -> int:
        """批量更新数据库"""
        if not results:
            return 0
            
        connection = None
        cursor = None
        updated_count = 0
        
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            update_sql = f"""
                UPDATE {config.table_name} 
                SET {config.json_target_field} = %s,
                    {config.train_data_field} = %s
                WHERE {config.id_field} = %s
            """
            
            with self._lock:
                for record_id, translated_json_str, training_data_str in results:
                    cursor.execute(update_sql, (
                        translated_json_str,
                        training_data_str,
                        record_id
                    ))
                    updated_count += 1
                
                connection.commit()
                
        except Exception as e:
            print(f"批量更新数据库时出错: {str(e)}")
            if connection:
                connection.rollback()
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
                
        return updated_count
    
    def process_table(self, config: TableConfig, 
                     max_workers: int = 4,
                     system_generator: Optional[Callable[[Dict], str]] = None,
                     context_generator: Optional[Callable[[Dict], str]] = None,
                     target_generator: Optional[Callable[[Dict], str]] = None) -> None:
        """多线程处理指定表的数据"""
        
        connection = None
        cursor = None
        
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            # 获取需要处理的数据
            select_sql = f"""
                SELECT {config.id_field}, {config.json_source_field}, {config.description_field}
                FROM {config.table_name}
                WHERE {config.json_source_field} IS NOT NULL
                AND {config.json_target_field} IS NULL
                LIMIT {config.batch_size}
            """
            
            # select_sql = f"""
            #     SELECT {config.id_field}, {config.json_source_field}, {config.description_field}
            #     FROM {config.table_name}
            #     WHERE train_data_ch like '%null%'
            #     LIMIT {config.batch_size}
            # """

            cursor.execute(select_sql)
            rows = cursor.fetchall()
            
            print(f"开始多线程处理表 {config.table_name}，共 {len(rows)} 条数据，使用 {max_workers} 个线程")
            
            if not rows:
                print("没有需要处理的数据")
                return
            
            # 使用线程池处理数据
            results_queue = Queue()
            processed_count = 0
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # 提交所有任务
                futures = [executor.submit(self._process_single_record, row, config) for row in rows]
                
                # 收集结果
                batch_results = []
                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        batch_results.append(result)
                        processed_count += 1
                        
                        # 每处理一定数量就批量更新数据库
                        if len(batch_results) >= 10:
                            updated = self._batch_update_database(batch_results, config)
                            print(f"已处理 {processed_count} 条记录，更新 {updated} 条")
                            batch_results = []
                
                # 处理剩余的结果
                if batch_results:
                    updated = self._batch_update_database(batch_results, config)
                    print(f"最终处理完成，共处理 {processed_count} 条记录")
            
            print(f"表 {config.table_name} 多线程处理完成，共处理 {processed_count} 条记录")
            
        except Exception as e:
            print(f"多线程处理表 {config.table_name} 时出错: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def process_table_single_thread(self, config: TableConfig, 
                                   system_generator: Optional[Callable[[Dict], str]] = None,
                                   context_generator: Optional[Callable[[Dict], str]] = None,
                                   target_generator: Optional[Callable[[Dict], str]] = None) -> None:
        """单线程处理指定表的数据（原始方法）"""
        
        connection = None
        cursor = None
        
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            # 获取需要处理的数据
            select_sql = f"""
                SELECT {config.id_field}, {config.json_source_field}, {config.description_field}
                FROM {config.table_name}
                WHERE {config.json_source_field} IS NOT NULL
                AND {config.json_target_field} IS NULL
                LIMIT {config.batch_size}
            """
            
            cursor.execute(select_sql)
            rows = cursor.fetchall()
            
            print(f"开始处理表 {config.table_name}，共 {len(rows)} 条数据")
            
            processed_count = 0
            
            for row in rows:
                try:
                    record_id, json_data, description = row
                    
                    # 解析JSON数据
                    if isinstance(json_data, str):
                        parsed_data = json.loads(json_data)
                    else:
                        parsed_data = json_data
                    
                    # 1. 转换JSON键为中文
                    translated_json = self.translator.translate_json_keys(parsed_data)
                    translated_json_str = json.dumps(translated_json, ensure_ascii=False, indent=2)
                    
                    # 2. 构建训练数据
                    system_content = prompt
                    context_content = description + "       " + context
                    target_content = translated_json_str
                    
                    training_data = self.training_builder.build_training_data(
                        system_content, context_content, target_content
                    )
                    training_data_str = json.dumps(training_data, ensure_ascii=False, indent=2)
                    
                    # 3. 更新数据库
                    update_sql = f"""
                        UPDATE {config.table_name} 
                        SET {config.json_target_field} = %s,
                            {config.train_data_field} = %s
                        WHERE {config.id_field} = %s
                    """
                    
                    cursor.execute(update_sql, (
                        translated_json_str,
                        training_data_str,
                        record_id
                    ))
                    
                    processed_count += 1
                    
                    if processed_count % 100 == 0:
                        connection.commit()
                        print(f"已处理 {processed_count} 条记录")
                        
                except Exception as e:
                    print(f"处理记录 {record_id} 时出错: {str(e)}")
                    continue
            
            # 最终提交
            connection.commit()
            print(f"表 {config.table_name} 处理完成，共处理 {processed_count} 条记录")
            
        except Exception as e:
            print(f"处理表 {config.table_name} 时出错: {str(e)}")
            if connection:
                connection.rollback()
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()


class ResumeProcessor(DatabaseProcessor):
    """简历处理器"""
    
    def __init__(self):
        db_config = {
            "dbname": "yhaimg",
            "user": "yhaimg",
            "password": "Zq*6^pD6g2%JJ!z8",
            "host": "172.31.255.227",
            "port": "5588"
        }
        super().__init__(db_config)
    
    def process_zhilian_resume(self, batch_size: int = 5, max_workers: int = 4, use_multithread: bool = True):
        """处理智联招聘简历表"""
        if platform == "zhilian_resume":
            config = TableConfig(
                table_name="zhilian_resume",
                json_source_field="resume_processed_info",
                description_field="resume_description_detail",
                batch_size=batch_size
            )
        elif platform == "sc_resume":
            config = TableConfig(
                table_name="sc_pub_recruitmentnet_resume",
                json_source_field="resume_info",
                description_field="resume_description_detail",
                batch_size=batch_size
            )
        elif platform == "zhilian_job":
            #智联岗位
            config = TableConfig(
                table_name="zhilian_job",
                json_source_field="processed_info",
                description_field="job_description_detail",
                batch_size=batch_size
            )
        elif platform == "sc_job":
            #智联岗位
            config = TableConfig(
                table_name="sc_pub_recruitmentnet_job",
                json_source_field="processed_info",
                description_field="job_description_detail",
                batch_size=batch_size
            )

        if use_multithread:
            self.process_table(config, max_workers=max_workers)
        else:
            self.process_table_single_thread(config)


def main():
    """主函数示例"""
    processor = ResumeProcessor()
    
    # 多线程处理智联招聘简历表（默认模式）
    print("=== 多线程处理模式 ===")
    processor.process_zhilian_resume(
        batch_size=40000,      # 批次大小
        max_workers=10,      # 线程数
        use_multithread=True # 使用多线程
    )
    
    # 单线程处理（如果需要的话）
    # print("\n=== 单线程处理模式 ===")
    # processor.process_zhilian_resume(
    #     batch_size=10,
    #     use_multithread=False
    # )
    
    # 如果需要处理其他表，可以创建新的配置
    # 例如处理其他简历表：
    # other_config = TableConfig(
    #     table_name="other_resume_table",
    #     json_source_field="other_json_field",
    #     description_field="other_description_field",
    #     batch_size=20
    # )
    # 
    # # 多线程处理其他表
    # processor.process_table(other_config, max_workers=6)
    # 
    # # 单线程处理其他表
    # processor.process_table_single_thread(other_config)


if __name__ == "__main__":
    main()