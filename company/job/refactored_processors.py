# -*- coding: utf-8 -*-
"""
重构后的处理器实现
使用通用数据库处理器重构现有的查询和更新逻辑
"""

import json
import re
from typing import Dict, Any, Optional, List
from common_db_processor import BaseQueryProcessor, JSONProcessor, HTMLCleanProcessor, CommonQueryBuilder
from db_connection import DatabaseConnection


class JobProcessor(JSONProcessor):
    """
    岗位数据处理器
    重构job_process.py中的处理逻辑
    """
    
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        super().__init__(db_connection)
        self.retain_fields = {
            "companyName": "",
            "companySize": "",
            "displayPhoneNumber": False,
            "education": "",
            "industryName": "",
            "cardCustomJson": "",
            "jobSummary": "",
            "name": "",
            "needMajor": [],
            "staffCard": {
                "staffName": ""
            },
            "recruitNumber": True,
            "salary60": "",
            "salaryCount": "",
            "salaryReal": "",
            "subJobTypeLevelName": "",
            "welfareTagList": [],
            "workCity": "",
            "cityDistrict": "",
            "streetName": "",
            "workType": "",
            "workingExp": ""
        }
    
    def process_json_data(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理岗位JSON数据，保留指定字段
        
        Args:
            json_data: 原始岗位JSON数据
            
        Returns:
            处理后的岗位JSON数据
        """
        return self._filter_fields(json_data, self.retain_fields)
    
    def _filter_fields(self, data: Dict[str, Any], template: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据模板过滤字段
        
        Args:
            data: 原始数据
            template: 字段模板
            
        Returns:
            过滤后的数据
        """
        result = {}
        for key, value in template.items():
            if key in data:
                if isinstance(value, dict) and isinstance(data[key], dict):
                    result[key] = self._filter_fields(data[key], value)
                elif isinstance(value, list) and isinstance(data[key], list):
                    result[key] = data[key]
                else:
                    result[key] = data[key]
            else:
                result[key] = value
        return result
    
    def clean_job_descriptions(self, table_name: str = "sc_pub_recruitmentnet_job"):
        """
        清理岗位描述中的HTML标签
        
        Args:
            table_name: 表名
        """
        html_processor = HTMLCleanProcessor(self.db_connection)
        
        query_sql = CommonQueryBuilder.build_select_with_condition(
            table_name=table_name,
            fields=["id", "job_description"],
            where_condition="job_description LIKE '%<%' OR job_description LIKE '%&%'"
        )
        
        update_sql = CommonQueryBuilder.build_update_by_id(
            table_name=table_name,
            update_fields=["job_description"]
        )
        
        updated_count = html_processor.batch_query_and_update(
            query_sql=query_sql,
            update_sql=update_sql
        )
        
        self.logger.info(f"清理了 {updated_count} 条岗位描述")
        return updated_count
    
    def process_job_info(self, table_name: str = "zhilian_job", limit: int = 1000):
        """
        处理岗位信息
        
        Args:
            table_name: 表名
            limit: 处理数量限制
        """
        query_sql = CommonQueryBuilder.build_select_with_condition(
            table_name=table_name,
            fields=["id", "job_info", "category_name", "job_name"],
            limit=limit
        )
        
        update_sql = CommonQueryBuilder.build_update_by_id(
            table_name=table_name,
            update_fields=["processed_info"]
        )
        
        def process_func(record):
            """自定义处理函数"""
            try:
                record_id, job_info, category_name, job_name = record
                if job_info:
                    processed_info = self.process_json_data(json.loads(job_info))
                    return (record_id, json.dumps(processed_info, ensure_ascii=False))
            except Exception as e:
                self.logger.error(f"处理岗位信息失败: {record[0]}, 错误: {str(e)}")
            return None
        
        updated_count = self.batch_query_and_update(
            query_sql=query_sql,
            update_sql=update_sql,
            process_func=process_func
        )
        
        self.logger.info(f"处理了 {updated_count} 条岗位信息")
        return updated_count


class ResumeProcessor(JSONProcessor):
    """
    简历数据处理器
    重构resume_process.py中的处理逻辑
    """
    
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        super().__init__(db_connection)
        self.retain_fields = {
            "user": {
                "name": True,
                "genderLabel": True,
                "age": True,
                "ageLabel": True,
                "maxEducationLabel": True,
                "workYears": True,
                "workYearsLabel": True,
                "cityLabel": True,
                "unlockedPhone": True,
                "email": True
            },
            "resume": {
                "skillTags": True,
                "educationExperiences": {
                    "schoolName": True,
                    "beginTime": True,
                    "endTime": True,
                    "educationTimeLabel": True,
                    "major": True,
                    "educationLabel": True
                },
                "workExperiences": {
                    "orgName": True,
                    "jobTitle": True,
                    "description": True,
                    "timeLabel": True,
                    "workSkillTags": {
                        "name": True
                    }
                },
                "projectExperiences": {
                    "name": True,
                    "beginTime": True,
                    "endTime": True,
                    "timeLabel": True,
                    "description": True,
                    "responsibility": True,
                },
                "languageSkills": {
                    "name": True,
                    "readWriteSkill": True,
                    "hearSpeakSkill": True
                },
                "certificates": {
                    "name": True,
                },
                "purposes": {
                    "industryLabel": "",
                    "jobTypeLabel": "",
                    "jobNatureLabel": "",
                    "location": "",
                    "salaryLabel": "",
                }
            }
        }
    
    def process_json_data(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理简历JSON数据，保留指定字段
        
        Args:
            json_data: 原始简历JSON数据
            
        Returns:
            处理后的简历JSON数据
        """
        return self._filter_fields_by_template(json_data, self.retain_fields)
    
    def _filter_fields_by_template(self, data: Any, template: Any) -> Any:
        """
        根据模板递归过滤字段
        
        Args:
            data: 原始数据
            template: 字段模板
            
        Returns:
            过滤后的数据
        """
        if isinstance(template, dict):
            if not isinstance(data, dict):
                return {}
            
            result = {}
            for key, value in template.items():
                if key in data:
                    if isinstance(value, bool) and value:
                        result[key] = data[key]
                    elif isinstance(value, dict):
                        if isinstance(data[key], list):
                            result[key] = [
                                self._filter_fields_by_template(item, value)
                                for item in data[key]
                            ]
                        else:
                            result[key] = self._filter_fields_by_template(data[key], value)
                    else:
                        result[key] = value
            return result
        else:
            return data
    
    def process_resume_info(self, table_name: str = "zhilian_resume", limit: int = 1000):
        """
        处理简历信息
        
        Args:
            table_name: 表名
            limit: 处理数量限制
        """
        query_sql = CommonQueryBuilder.build_select_with_condition(
            table_name=table_name,
            fields=["id", "resume_info"],
            where_condition="resume_processed_info IS NULL",
            limit=limit
        )
        
        update_sql = CommonQueryBuilder.build_update_by_id(
            table_name=table_name,
            update_fields=["resume_processed_info"]
        )
        
        def process_func(record):
            """自定义处理函数"""
            try:
                record_id, resume_info = record
                if resume_info:
                    processed_info = self.process_json_data(json.loads(resume_info))
                    return (record_id, json.dumps(processed_info, ensure_ascii=False))
            except Exception as e:
                self.logger.error(f"处理简历信息失败: {record[0]}, 错误: {str(e)}")
            return None
        
        updated_count = self.batch_query_and_update(
            query_sql=query_sql,
            update_sql=update_sql,
            process_func=process_func
        )
        
        self.logger.info(f"处理了 {updated_count} 条简历信息")
        return updated_count


class DataSyncProcessor(BaseQueryProcessor):
    """
    数据同步处理器
    重构data_syn.py中的同步逻辑
    """
    
    def __init__(self, source_db: DatabaseConnection, target_db: DatabaseConnection):
        super().__init__(source_db)
        self.source_db = source_db
        self.target_db = target_db
    
    def process_record(self, record: tuple) -> Optional[tuple]:
        """
        数据同步不需要单独处理记录
        """
        return record
    
    def sync_table(self, table_name: str, source_columns: List[str], target_columns: List[str]):
        """
        同步表数据
        
        Args:
            table_name: 表名
            source_columns: 源表列名
            target_columns: 目标表列名
        """
        source_conn = None
        target_conn = None
        source_cursor = None
        target_cursor = None
        
        try:
            # 连接源数据库和目标数据库
            source_conn = self.source_db.get_connection()
            target_conn = self.target_db.get_connection()
            source_cursor = source_conn.cursor()
            target_cursor = target_conn.cursor()
            
            # 查询源表数据
            source_cursor.execute(f"SELECT * FROM {table_name}")
            rows = source_cursor.fetchall()
            
            # 清空目标表
            target_cursor.execute(f"DELETE FROM {table_name}")
            
            # 插入数据到目标表
            for row in rows:
                self._insert_into_table(target_cursor, table_name, target_columns, row)
            
            target_conn.commit()
            self.logger.info(f"成功同步表 {table_name}，共 {len(rows)} 条记录")
            
        except Exception as e:
            self.logger.error(f"同步表 {table_name} 失败: {str(e)}")
            if target_conn:
                target_conn.rollback()
        finally:
            if source_cursor:
                source_cursor.close()
            if target_cursor:
                target_cursor.close()
            if source_conn:
                source_conn.close()
            if target_conn:
                target_conn.close()
    
    def _insert_into_table(self, cursor, table_name: str, columns: List[str], row: tuple):
        """
        插入数据到表中
        
        Args:
            cursor: 数据库游标
            table_name: 表名
            columns: 列名列表
            row: 数据行
        """
        try:
            columns_str = ", ".join(columns)
            placeholders = ", ".join(["%s"] * len(columns))
            sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            
            # 确保数据长度匹配
            data = row[:len(columns)]
            cursor.execute(sql, data)
            
        except Exception as e:
            self.logger.error(f"插入数据到表 {table_name} 失败: {str(e)}")


class CompareProcessor(BaseQueryProcessor):
    """
    比较处理器
    重构job_compare.py中的比较逻辑
    """
    
    def process_record(self, record: tuple) -> Optional[tuple]:
        """
        处理比较记录
        
        Args:
            record: (id, job_processed_info_ch, job_description_detail)
            
        Returns:
            (id, compare_result)
        """
        try:
            record_id, job_info, job_description = record
            
            if job_info and job_description:
                # 执行比较逻辑（这里可以调用具体的比较算法）
                compare_result = self._compare_job_data(job_info, job_description)
                return (record_id, compare_result)
            
        except Exception as e:
            self.logger.error(f"比较记录失败: {record[0] if record else 'unknown'}, 错误: {str(e)}")
        
        return None
    
    def _compare_job_data(self, job_info: str, job_description: str) -> str:
        """
        比较岗位数据
        
        Args:
            job_info: 岗位信息JSON
            job_description: 岗位描述
            
        Returns:
            比较结果
        """
        # 这里实现具体的比较逻辑
        # 示例：简单的相似度计算
        try:
            job_data = json.loads(job_info)
            # 实现具体的比较算法
            similarity_score = self._calculate_similarity(job_data, job_description)
            return json.dumps({"similarity": similarity_score}, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"比较数据失败: {str(e)}")
            return json.dumps({"error": str(e)}, ensure_ascii=False)
    
    def _calculate_similarity(self, job_data: Dict[str, Any], description: str) -> float:
        """
        计算相似度
        
        Args:
            job_data: 岗位数据
            description: 描述文本
            
        Returns:
            相似度分数
        """
        # 简单的相似度计算示例
        # 实际应用中可以使用更复杂的算法
        return 0.8  # 示例返回值
    
    def process_job_comparison(self, table_name: str = "zhilian_job"):
        """
        处理岗位比较
        
        Args:
            table_name: 表名
        """
        query_sql = CommonQueryBuilder.build_select_with_condition(
            table_name=table_name,
            fields=["id", "job_processed_info_ch", "job_description_detail"],
            where_condition="job_processed_info_ch IS NOT NULL AND job_description_detail IS NOT NULL"
        )
        
        update_sql = CommonQueryBuilder.build_update_by_id(
            table_name=table_name,
            update_fields=["compare_result"]
        )
        
        updated_count = self.batch_query_and_update(
            query_sql=query_sql,
            update_sql=update_sql
        )
        
        self.logger.info(f"处理了 {updated_count} 条岗位比较")
        return updated_count