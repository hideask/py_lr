# -*- coding: utf-8 -*-
"""
智联招聘简历数据处理器
统一的工具类，集成了简历数据去重、格式清洗、"至今"数据处理等功能
支持不同的配置选项，可以根据需要启用或禁用特定功能
"""

import json
import threading
import logging
import time
import re
import copy
import html
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, date
from concurrent.futures import ThreadPoolExecutor
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_connection import get_db_connection, close_db_connection, DatabaseConnection
from education_experience_processor import EducationExperienceProcessor
from work_experience_processor import WorkExperienceProcessor

class ZhilianResumeProcessorConfig:
    """
    智联招聘简历处理器配置类
    """
    
    def __init__(self):
        # 基础配置
        self.num_threads = 5  # 线程数量
        self.batch_size = 50  # 每批处理的数据量
        
        # 功能开关
        self.enable_deduplication = True  # 启用去重功能
        self.enable_zhijin_processing = True  # 启用"至今"数据处理
        self.enable_certificate_splitting = True  # 启用证书分割功能
        self.enable_format_cleaning = True  # 启用格式清洗功能
        self.enable_data_filtering = True  # 启用数据过滤功能
        self.enable_html_cleaning = True  # 启用HTML清洗功能
        self.enable_excel_export = False  # 启用Excel导出功能
        
        # 去重配置
        self.deduplicate_education = True  # 去重教育经历
        self.deduplicate_work = True  # 去重工作经历
        self.deduplicate_project = True  # 去重项目经历
        
        # "至今"处理配置
        self.zhijin_end_date = '2025.05'  # "至今"替换的结束日期
        self.process_work_zhijin = True  # 处理工作经历的"至今"
        self.process_project_zhijin = True  # 处理项目经历的"至今"
        self.process_education_zhijin = True  # 处理教育经历的"至今"
        
        # 数据过滤配置
        self.retain_fields = {
            "user": {
                "name": True,
                "genderLabel": True,
                "age": True,
                "maxEducationLabel": True,
                "workYears": True,
                "cityLabel": True,
                "unlockedPhone": True,
                "email": True
            },
            "resume": {
                "educationExperiences": {
                    "schoolName": True,
                    "educationTimeLabel": True,
                    "major": True,
                    "educationLabel": True
                },
                "workExperiences": {
                    "orgName": True,
                    "jobTitle": True,
                    "description": True,
                    "timeLabel": True
                },
                "projectExperiences": {
                    "name": True,
                    "timeLabel": True,
                    "description": True
                },
                "languageSkills": {
                    "name": True,
                    "readWriteSkill": True,
                    "hearSpeakSkill": True
                },
                "certificates": {
                    "name": True
                },
                "purposes": {
                    "industryLabel": "",
                    "jobTypeLabel": "",
                    "jobNatureLabel": "",
                    "location": "",
                    "salaryLabel": ""
                }
            }
        }
        
        # Excel导出配置
        self.excel_platform = ""  # 'wy', 'sc', 或空字符串
        self.excel_start_id = 5000
        self.excel_end_id = 15000
        self.excel_output_dir = "./"
        
        # 数据库配置
        self.train_type = '3'  # 训练类型过滤
        self.update_work_years = True  # 是否更新work_years字段
        
        # 日志配置
        self.log_level = logging.INFO
        self.log_file = 'zhilian_resume_processor.log'
        self.enable_console_log = True

class ZhilianResumeProcessor:
    """
    智联招聘简历数据处理器
    统一的工具类，集成多种处理功能
    """
    
    def __init__(self, config: ZhilianResumeProcessorConfig = None):
        """
        初始化处理器
        
        Args:
            config: 配置对象，如果为None则使用默认配置
        """
        self.config = config or ZhilianResumeProcessorConfig()
        self.lock = threading.Lock()
        
        # 初始化子处理器
        self.education_processor = EducationExperienceProcessor()
        self.work_processor = WorkExperienceProcessor()
        
        # 配置日志
        self._setup_logging()
        
        # 统计信息
        self.stats = {
            'total_processed': 0,
            'total_updated': 0,
            'education_updated': 0,
            'work_updated': 0,
            'project_updated': 0,
            'certificate_updated': 0,
            'errors': 0
        }
    
    def _setup_logging(self):
        """
        配置日志系统
        """
        self.logger = logging.getLogger(f'{__name__}_{id(self)}')
        self.logger.setLevel(self.config.log_level)
        
        # 清除已有的处理器
        self.logger.handlers.clear()
        
        # 文件处理器
        if self.config.log_file:
            file_handler = logging.FileHandler(self.config.log_file, encoding='utf-8')
            file_handler.setLevel(self.config.log_level)
            file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
        
        # 控制台处理器
        if self.config.enable_console_log:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(self.config.log_level)
            console_formatter = logging.Formatter('%(levelname)s - %(message)s')
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
    
    def parse_time_period(self, time_str: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        解析时间段字符串，返回开始时间、结束时间和持续时间
        
        Args:
            time_str: 时间字符串
            
        Returns:
            tuple: (开始时间, 结束时间, 持续时间文本)
        """
        if not time_str or '至今' not in time_str:
            return None, None, None
        
        # 匹配格式: "xxxx.xx - 至今 (xx年 xx个月)"
        pattern = r'(\d{4}\.\d{2})\s*-\s*至今\s*\(([^)]+)\)'
        match = re.search(pattern, time_str)
        
        if not match:
            # 匹配简单格式: "xxxx.xx - 至今"
            simple_pattern = r'(\d{4}\.\d{2})\s*-\s*至今'
            simple_match = re.search(simple_pattern, time_str)
            if simple_match:
                start_time = simple_match.group(1)
                return start_time, '至今', None
            return None, None, None
        
        start_time = match.group(1)
        duration_text = match.group(2)
        
        return start_time, '至今', duration_text
    
    def calculate_duration(self, start_time: str, end_time: str = None) -> str:
        """
        计算两个时间点之间的持续时间
        
        Args:
            start_time: 开始时间 (格式: YYYY.MM)
            end_time: 结束时间 (格式: YYYY.MM)
            
        Returns:
            str: 持续时间描述
        """
        if not end_time:
            end_time = self.config.zhijin_end_date
        
        try:
            start_year, start_month = map(int, start_time.split('.'))
            end_year, end_month = map(int, end_time.split('.'))
            
            # 计算总月数
            total_months = (end_year - start_year) * 12 + (end_month - start_month)
            
            if total_months < 0:
                return "0个月"
            
            years = total_months // 12
            months = total_months % 12
            
            if years > 0 and months > 0:
                return f"{years}年 {months}个月"
            elif years > 0:
                return f"{years}年"
            else:
                return f"{months}个月"
        
        except Exception as e:
            self.logger.error(f"计算持续时间出错: {e}")
            return "0个月"
    
    def update_time_label(self, time_label: str) -> Tuple[str, bool]:
        """
        更新timeLabel，将'至今'替换为指定日期并重新计算持续时间
        
        Args:
            time_label: 原始时间标签
            
        Returns:
            tuple: (更新后的时间标签, 是否有更新)
        """
        if not time_label or '至今' not in time_label:
            return time_label, False
        
        start_time, _, _ = self.parse_time_period(time_label)
        if not start_time:
            return time_label, False
        
        # 计算新的持续时间
        new_duration = self.calculate_duration(start_time, self.config.zhijin_end_date)
        
        # 构建新的时间标签
        new_time_label = f"{start_time} - {self.config.zhijin_end_date} ({new_duration})"
        
        self.logger.debug(f"更新时间标签: {time_label} -> {new_time_label}")
        return new_time_label, True
    
    def deduplicate_education_experiences(self, education_experiences: List[Dict]) -> List[Dict]:
        """
        根据schoolName和major去重教育经历，并处理"至今"类型的educationTimeLabel
        
        Args:
            education_experiences: 教育经历列表
            
        Returns:
            去重后的教育经历列表
        """
        if not education_experiences or not self.config.deduplicate_education:
            return education_experiences
        
        # 首先处理"至今"类型的数据
        if self.config.enable_zhijin_processing and self.config.process_education_zhijin:
            processed_experiences = self.education_processor.process_education_experiences(education_experiences)
        else:
            processed_experiences = education_experiences
        
        if not self.config.enable_deduplication:
            return processed_experiences
        
        seen = set()
        unique_experiences = []
        
        for exp in processed_experiences:
            if not isinstance(exp, dict):
                continue
                
            school_name = exp.get('schoolName', '').strip()
            major = exp.get('major', '').strip()
            
            # 创建唯一标识
            key = (school_name.lower(), major.lower())
            
            if key not in seen and (school_name or major):
                seen.add(key)
                unique_experiences.append(exp)
                self.logger.debug(f"保留教育经历: {school_name} - {major}")
            else:
                self.logger.debug(f"删除重复教育经历: {school_name} - {major}")
        
        return unique_experiences
    
    def deduplicate_work_experiences(self, work_experiences: List[Dict]) -> List[Dict]:
        """
        根据orgName、jobTitle和timeLabel去重工作经历，并处理"至今"类型的timeLabel
        
        Args:
            work_experiences: 工作经历列表
            
        Returns:
            去重后的工作经历列表
        """
        if not work_experiences or not self.config.deduplicate_work:
            return work_experiences
        
        # 首先处理"至今"类型的数据
        if self.config.enable_zhijin_processing and self.config.process_work_zhijin:
            self.process_work_experiences_zhijin(work_experiences)
        
        if not self.config.enable_deduplication:
            return work_experiences
        
        seen = set()
        unique_experiences = []
        
        for exp in work_experiences:
            if not isinstance(exp, dict):
                continue
                
            org_name = exp.get('orgName', '').strip()
            job_title = exp.get('jobTitle', '').strip()
            time_label = exp.get('timeLabel', '').strip()
            
            # 创建唯一标识
            key = (org_name.lower(), job_title.lower(), time_label.lower())
            
            if key not in seen and (org_name or job_title or time_label):
                seen.add(key)
                unique_experiences.append(exp)
                self.logger.debug(f"保留工作经历: {org_name} - {job_title} - {time_label}")
            else:
                self.logger.debug(f"删除重复工作经历: {org_name} - {job_title} - {time_label}")
        
        return unique_experiences
    
    def deduplicate_project_experiences(self, project_experiences: List[Dict]) -> List[Dict]:
        """
        根据name和timeLabel去重项目经历，并处理"至今"类型的timeLabel
        支持模糊匹配
        
        Args:
            project_experiences: 项目经历列表
            
        Returns:
            去重后的项目经历列表
        """
        if not project_experiences or not self.config.deduplicate_project:
            return project_experiences
        
        # 首先处理"至今"类型的数据
        if self.config.enable_zhijin_processing and self.config.process_project_zhijin:
            self.process_project_experiences_zhijin(project_experiences)
        
        if not self.config.enable_deduplication:
            return project_experiences
        
        unique_experiences = []
        
        for i, exp in enumerate(project_experiences):
            if not isinstance(exp, dict):
                continue
                
            name = exp.get('name', '').strip()
            time_label = exp.get('timeLabel', '').strip()
            
            if not name and not time_label:
                continue
            
            # 检查是否与已有项目重复
            is_duplicate = False
            for existing_exp in unique_experiences:
                existing_name = existing_exp.get('name', '').strip()
                existing_time_label = existing_exp.get('timeLabel', '').strip()
                
                # 检查时间标签是否相同
                time_match = time_label.lower() == existing_time_label.lower()
                
                # 检查项目名称是否相似（包含关系或完全匹配）
                name_match = False
                if name and existing_name:
                    # 完全匹配
                    if name.lower() == existing_name.lower():
                        name_match = True
                    # 包含关系匹配
                    elif name.lower() in existing_name.lower() or existing_name.lower() in name.lower():
                        name_match = True
                
                if time_match and name_match:
                    is_duplicate = True
                    self.logger.debug(f"删除重复项目经历: {name} - {time_label}")
                    break
            
            if not is_duplicate:
                unique_experiences.append(exp)
                self.logger.debug(f"保留项目经历: {name} - {time_label}")
        
        return unique_experiences
    
    def process_certificates(self, certificates: List[Dict]) -> List[Dict]:
        """
        处理证书数据，将包含多个证书的字符串分割成单独的证书
        
        Args:
            certificates: 证书列表
            
        Returns:
            处理后的证书列表
        """
        if not certificates or not self.config.enable_certificate_splitting:
            return certificates
        
        processed_certificates = []
        
        for cert in certificates:
            if not isinstance(cert, dict):
                continue
                
            name = cert.get('name', '').strip()
            if not name:
                continue
            
            # 定义分隔符模式
            separators = r'[，,、；;]'
            
            # 分割证书名称
            cert_names = re.split(separators, name)
            
            for cert_name in cert_names:
                cert_name = cert_name.strip()
                if cert_name:
                    # 创建新的证书对象，保留原有的其他字段
                    new_cert = cert.copy()
                    new_cert['name'] = cert_name
                    processed_certificates.append(new_cert)
                    self.logger.debug(f"处理证书: {cert_name}")
        
        return processed_certificates
    
    def process_work_experiences_zhijin(self, work_experiences: List[Dict]) -> bool:
        """
        处理工作经历列表中的"至今"数据
        
        Args:
            work_experiences: 工作经历列表
            
        Returns:
            bool: 是否有更新
        """
        updated = False
        
        if not work_experiences or not isinstance(work_experiences, list):
            return updated
        
        for i, exp in enumerate(work_experiences):
            if isinstance(exp, dict) and 'timeLabel' in exp:
                original_time_label = exp['timeLabel']
                new_time_label, was_updated = self.update_time_label(original_time_label)
                
                if was_updated:
                    exp['timeLabel'] = new_time_label
                    updated = True
                    self.logger.debug(f"工作经历 {i+1}: {original_time_label} -> {new_time_label}")
        
        return updated
    
    def process_project_experiences_zhijin(self, project_experiences: List[Dict]) -> bool:
        """
        处理项目经历列表中的"至今"数据
        
        Args:
            project_experiences: 项目经历列表
            
        Returns:
            bool: 是否有更新
        """
        updated = False
        
        if not project_experiences or not isinstance(project_experiences, list):
            return updated
        
        for i, exp in enumerate(project_experiences):
            if isinstance(exp, dict) and 'timeLabel' in exp:
                original_time_label = exp['timeLabel']
                new_time_label, was_updated = self.update_time_label(original_time_label)
                
                if was_updated:
                    exp['timeLabel'] = new_time_label
                    updated = True
                    self.logger.debug(f"项目经历 {i+1}: {original_time_label} -> {new_time_label}")
        
        return updated
    
    def process_resume_data(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理单条简历数据
        
        Args:
            resume_data: 简历数据字典
            
        Returns:
            处理后的简历数据
        """
        processed_data = resume_data.copy()
        
        # 检查是否有resume节点
        if 'resume' not in processed_data:
            self.logger.warning("数据中没有找到resume节点")
            return processed_data
        
        resume_data = processed_data['resume']
        
        # 处理教育经历
        if 'educationExperiences' in resume_data:
            original_count = len(resume_data['educationExperiences'])
            resume_data['educationExperiences'] = self.deduplicate_education_experiences(
                resume_data['educationExperiences']
            )
            new_count = len(resume_data['educationExperiences'])
            if new_count != original_count:
                self.stats['education_updated'] += 1
                self.logger.debug(f"教育经历: {original_count} -> {new_count}")
        
        # 处理工作经历
        if 'workExperiences' in resume_data:
            original_count = len(resume_data['workExperiences'])
            resume_data['workExperiences'] = self.deduplicate_work_experiences(
                resume_data['workExperiences']
            )
            new_count = len(resume_data['workExperiences'])
            if new_count != original_count:
                self.stats['work_updated'] += 1
                self.logger.debug(f"工作经历: {original_count} -> {new_count}")
        
        # 处理项目经历
        if 'projectExperiences' in resume_data:
            original_count = len(resume_data['projectExperiences'])
            resume_data['projectExperiences'] = self.deduplicate_project_experiences(
                resume_data['projectExperiences']
            )
            new_count = len(resume_data['projectExperiences'])
            if new_count != original_count:
                self.stats['project_updated'] += 1
                self.logger.debug(f"项目经历: {original_count} -> {new_count}")
        
        # 处理证书
        if 'certificates' in resume_data:
            original_count = len(resume_data['certificates'])
            resume_data['certificates'] = self.process_certificates(
                resume_data['certificates']
            )
            new_count = len(resume_data['certificates'])
            if new_count != original_count:
                self.stats['certificate_updated'] += 1
                self.logger.debug(f"证书: {original_count} -> {new_count}")
        
        # 更新processed_data中的resume数据
        processed_data['resume'] = resume_data
        
        # 应用数据过滤
        if self.config.enable_data_filtering:
            processed_data = self.filter_resume_data(processed_data, self.config.retain_fields)
        
        # 应用HTML清理
        if self.config.enable_html_cleaning:
            processed_data = self._apply_html_cleaning(processed_data)
        
        # 应用格式清洗
        if self.config.enable_format_cleaning:
            processed_data = self._apply_format_cleaning(processed_data)
        
        return processed_data
    
    def fetch_resume_data_from_db(self, batch_size: int = None) -> List[Tuple[int, str]]:
        """
        从数据库获取简历数据
        
        Args:
            batch_size: 批次大小
            
        Returns:
            简历数据列表 [(id, resume_processed_info), ...]
        """
        if batch_size is None:
            batch_size = self.config.batch_size
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        try:
            # 查询未处理的简历数据并标记为正在处理
            cursor.execute("""
                SELECT id, resume_processed_info 
                FROM zhilian_resume 
                WHERE train_type = %s 
                AND (check_type IS NULL OR (check_type != '12' AND check_type != '13'))
                ORDER BY id 
                LIMIT %s 
                FOR UPDATE SKIP LOCKED
            """, (self.config.train_type, batch_size))
            
            rows = cursor.fetchall()
            
            if rows:
                ids = [row[0] for row in rows]
                # 标记这些数据为正在处理
                cursor.execute("""
                    UPDATE zhilian_resume 
                    SET check_type = 'processing' 
                    WHERE id = ANY(%s)
                """, (ids,))
                connection.commit()
            
            return rows
            
        except Exception as e:
            self.logger.error(f"从数据库获取数据失败: {e}")
            connection.rollback()
            return []
        finally:
            close_db_connection(cursor, connection)
    
    def has_data_changed(self, original_data: Dict[str, Any], processed_data: Dict[str, Any]) -> bool:
        """
        检查数据是否发生变化
        
        Args:
            original_data: 原始数据
            processed_data: 处理后的数据
            
        Returns:
            bool: 数据是否发生变化
        """
        try:
            # 获取resume节点
            original_resume = original_data.get('resume', {})
            processed_resume = processed_data.get('resume', {})
            
            # 检查关键字段是否有变化
            fields_to_check = ['educationExperiences', 'workExperiences', 'projectExperiences', 'certificates']
            
            for field in fields_to_check:
                original_field = original_resume.get(field, [])
                processed_field = processed_resume.get(field, [])
                
                # 比较字段内容
                if self.normalize_for_comparison(original_field) != self.normalize_for_comparison(processed_field):
                    self.logger.debug(f"字段 {field} 发生变化")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"比较数据变化时出错: {e}")
            # 出错时默认认为数据有变化，确保数据被更新
            return True
    
    def normalize_for_comparison(self, data: Any) -> str:
        """
        标准化数据用于比较
        
        Args:
            data: 要标准化的数据
            
        Returns:
            str: 标准化后的字符串
        """
        try:
            # 将数据转换为JSON字符串进行比较，确保格式一致
            return json.dumps(data, ensure_ascii=False, sort_keys=True)
        except Exception:
            # 如果转换失败，返回字符串表示
            return str(data)
    
    def deep_clean(self, data: Any) -> Any:
        """深度清理数据，去除特殊字符"""
        if isinstance(data, str):
            # 去除零宽字符和其他特殊字符
            data = re.sub(r'[\u200b-\u200f\u202c-\u202e\ufeff]', '', data)
            return data
        elif isinstance(data, dict):
            return {k: self.deep_clean(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.deep_clean(i) for i in data]
        else:
            return data
    
    def clean_html(self, text: str) -> str:
        """清理HTML标签和实体"""
        if not text:
            return ""
        
        # 解码HTML实体
        text = html.unescape(html.unescape(text))
        
        # 去除HTML标签
        text = re.sub(r"<[^>]+>", "", text)
        
        # 处理特殊HTML实体
        text = re.sub(r"&\s*lt\s*;?", "<", text)
        text = re.sub(r"&\s*gt\s*;?", ">", text)
        text = re.sub(r"&\s*#xa\s*;?", "\n", text)
        text = re.sub(r"&\s*#xd\s*;?", "\r", text)
        text = re.sub(r"&\s*#x9\s*;?", " ", text)
        
        # 替换特殊空白字符
        text = re.sub(r"[\xa0\u200b\u200c\u200d\u200e\u200f]", " ", text)
        
        # 合并连续空白
        text = re.sub(r"\s+", " ", text).strip()
        
        return text
    
    def filter_resume_data(self, input_data: Dict, required_fields: Dict) -> Dict:
        """根据配置过滤简历数据"""
        def filter_dict(data, fields):
            if not isinstance(data, dict):
                return data
            
            result = {}
            for key, value in data.items():
                if key in fields:
                    value = self.deep_clean(value)
                    current_key = 'phone' if key == 'unlockedPhone' else key
                    
                    if isinstance(value, dict):
                        result[current_key] = filter_dict(value, fields.get(key, {}))
                    elif isinstance(value, list):
                        result[current_key] = [
                            filter_dict(item, fields.get(key, {}))
                            if isinstance(item, dict) else item
                            for item in value
                        ]
                    else:
                        result[current_key] = value
            return result
        
        return filter_dict(input_data, required_fields)
    
    def replace_none_with_empty(self, data: Any) -> Any:
        """递归地将None替换为空字符串"""
        if isinstance(data, dict):
            return {k: self.replace_none_with_empty(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.replace_none_with_empty(item) for item in data]
        elif data is None:
            return ""
        elif isinstance(data, str) and str(data) == "null":
            return ""
        else:
            return data
    
    def remove_empty_fields(self, data: Any) -> Any:
        """递归删除空值字段"""
        if isinstance(data, dict):
            return {
                k: self.remove_empty_fields(v)
                for k, v in data.items()
                if v not in (None, "", [], {}) and not (isinstance(v, str) and v.strip() == "")
            }
        elif isinstance(data, list):
            return [self.remove_empty_fields(item) for item in data if item not in (None, "", [], {})]
        else:
            return data
    
    def _apply_html_cleaning(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """应用HTML清理"""
        def clean_html_recursive(obj):
            if isinstance(obj, str):
                return self.clean_html(obj)
            elif isinstance(obj, dict):
                return {k: clean_html_recursive(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_html_recursive(item) for item in obj]
            else:
                return obj
        
        return clean_html_recursive(data)
    
    def _apply_format_cleaning(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """应用格式清洗"""
        # 深度清理数据
        cleaned_data = self.deep_clean(data)
        
        # 替换None值为空字符串
        cleaned_data = self.replace_none_with_empty(cleaned_data)
        
        # 删除空字段
        cleaned_data = self.remove_empty_fields(cleaned_data)
        
        return cleaned_data
    
    class DateEncoder(json.JSONEncoder):
        """自定义JSON编码器处理日期类型"""
        def default(self, obj):
            if isinstance(obj, date):
                return obj.strftime('%Y-%m-%d')
            return super().default(obj)
    
    def export_to_excel(self, data_list: List[Tuple], platform: str = "") -> str:
        """导出数据到Excel文件"""
        excel_data = []
        
        # 系统设置和提示词（从原始代码移植）
        system_setting = "你是一个专业且高效的简历精灵，请根据提供的 JSON 格式简历数据，以第一人称视角撰写专业、真实且有说服力的简历自述。撰写时需模拟求职者自然表达的语气，避免模板化、机械化表述。\n\n"
        
        prompt = "## 具体要求如下：\n" + \
                "###.结构与顺序：严格按照「个人概述→求职意向→教育经历→工作经历→项目经历→技能→证书→语言能力」的顺序撰写，各部分过渡自然，避免生硬分段。\n" + \
                "### 个人概述：开篇说明姓名、年龄、性别、工作年限、学历、专业、手机号码、 电子邮箱及现居地，结合求职意向，简要提炼1-2项核心竞争优势，如专业背景或实践能力。\n" + \
                "### 求职意向：清晰列出所有期望行业、目标岗位、工作地点及薪资范围，可简要阐述职业发展方向，体现职业规划。\n" + \
                "### 教育经历：教育经历需明确学校名称、专业、学历及具体起止时间段。\n" + \
                "### 工作经历：工作经历描述时，按照时间倒叙描述所有经历。明确每段经历的起止时间段，及所有相关字段信息，工作经历描述保留字段中的原样内容，一字不差！！格式为：工作经历描述 + 原数据内容。不要出现近两年、近期等模糊字段。\n" + \
                "### 项目经历：项目经验描述时，按照时间倒叙描述所有经历。明确每段经历的起止时间段，项目名称及所有相关字段信息，避免简单罗列任务，项目经历描述保留字段中的原样内容，一字不差！！格式为：项目经历描述 + 原数据内容。不要出现近两年、近期等模糊字段。\n" + \
                "### 技能：技能部分分类清晰，按原有数据输出，中间用逗号隔开。\n" + \
                "### 语言：证书需注明名称，语言能力区分读写、听说水平，未明确说明则表述为基础水平。\n" + \
                "### 内容真实性：所有信息必须严格基于原始JSON数据，禁止添加任何未提及的内容，包括但不限于获奖经历、项目成果、技能优势等；数据缺失时，不用列出，不得虚构。\n" + \
                "### 自然叙事：摒弃模块化、分标题式的表述方式，以流畅连贯的段落自然过渡各部分内容，像讲述个人经历故事一样，用生活化的逻辑串联信息，例如通过时间线、因果关系衔接（例：这段留学经历让我接触到前沿理念，也让我后来在工作中尝试用数字化工具解决问题）。\n"
        
        prompt_sc = "## 具体要求如下：\n" + \
                   "###.结构与顺序：严格按照「个人概述→求职意向→教育经历→工作经历」的顺序撰写，各部分过渡自然，避免生硬分段，如果没有相关信息就不生成，不补充，例如没有教育经历，就不生成教育经历相关内容，没有工作经历就不生成工作经历相关内容。\n" + \
                   "### 个人概述：开篇说明姓名、年龄、性别、工作年限、学历、专业、手机号码、 及现居地，结合求职意向，简要提炼1-2项核心竞争优势，如专业背景或实践能力。\n" + \
                   "### 求职意向：清晰列出所有期望行业、目标岗位、工作地点及薪资范围。\n" + \
                   "### 教育经历：教育经历需明确学校名称、专业、学历及具体起止时间段。\n" + \
                   "### 工作经历：工作经历描述时，按照时间倒叙描述所有经历。明确每段经历的起止时间段，及所有相关字段信息，工作经历描述保留字段中的原样内容，一字不差！！格式为：工作经历描述 + 原数据内容。不要出现近两年、近期等模糊字段。\n" + \
                   "### 语言：证书需注明名称，语言能力区分读写、听说水平，未明确说明则表述为基础水平。\n" + \
                   "### 内容真实性：所有信息必须严格基于原始JSON数据，禁止添加任何未提及的内容，包括但不限于获奖经历、项目成果、技能优势等；数据缺失时，不用生成，不得虚构。\n" + \
                   "### 自然叙事：摒弃模块化、分标题式的表述方式，以流畅连贯的段落自然过渡各部分内容，像讲述个人经历故事一样，用生活化的逻辑串联信息，例如通过时间线、因果关系衔接。\n"
        
        input_r = "输入：```json\n "
        input_l = "```\n"
        output = "输出："
        
        # 遍历数据并组装
        for resume_id, info in data_list:
            info_dict = json.loads(info) if isinstance(info, str) else info
            info_dict['id'] = resume_id
            
            if platform == 'wy':
                row_data = {
                    'input': '##' + system_setting + prompt + input_r + json.dumps(info_dict, ensure_ascii=False, cls=self.DateEncoder) + input_l + output,
                    'expectedAnswer': '',
                    'systemSetting': system_setting,
                    'modelAnswer': ''
                }
            elif platform == 'sc':
                row_data = {
                    'input': '##' + system_setting + prompt_sc + input_r + json.dumps(info_dict, ensure_ascii=False, cls=self.DateEncoder) + input_l + output,
                    'expectedAnswer': '',
                    'systemSetting': system_setting,
                    'modelAnswer': ''
                }
            else:
                row_data = {
                    'id': resume_id,
                    'info': json.dumps(info_dict, ensure_ascii=False, cls=self.DateEncoder)
                }
            excel_data.append(row_data)
        
        # 创建DataFrame并导出
        df = pd.DataFrame(excel_data)
        
        if platform == 'wy':
            output_file = f'{self.config.excel_output_dir}resume_data_wy_{self.config.excel_start_id}_{self.config.excel_end_id}.xlsx'
        elif platform == 'sc':
            output_file = f'{self.config.excel_output_dir}resume_data_sc_{self.config.excel_start_id}_{self.config.excel_end_id}.xlsx'
        else:
            output_file = f'{self.config.excel_output_dir}resume_data_json_{self.config.excel_start_id}_{self.config.excel_end_id}.xlsx'
        
        df.to_excel(output_file, index=False)
        self.logger.info(f"数据已导出到 {output_file}")
        return output_file
    
    def process_single_resume_job_info(self, resume_data: Tuple) -> bool:
        """处理单个简历的工作信息提取"""
        resume_id, resume_info = resume_data
        connection = None
        cursor = None
        
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            job_list = set()
            job_name_list = set()
            
            resume_json = json.loads(resume_info)
            resume_part = resume_json.get('resume', {})
            work_experiences = resume_part.get('workExperiences', [])
            
            for work_exp in work_experiences:
                job_subtype = work_exp.get('jobSubtype')
                job_subtype_highlight = work_exp.get('jobSubtypeHighlight')
                
                if job_subtype:
                    job_list.add(job_subtype)
                if job_subtype_highlight and job_subtype_highlight.get('name'):
                    job_name_list.add(job_subtype_highlight.get('name'))
            
            # 转换为逗号分隔的字符串
            job_list_str = ','.join(job_list) if job_list else ''
            job_name_list_str = ','.join(job_name_list) if job_name_list else ''
            
            cursor.execute(
                "UPDATE zhilian_resume SET job_sub_type = %s, job_sub_type_name = %s WHERE id = %s",
                (job_list_str, job_name_list_str, resume_id)
            )
            connection.commit()
            self.logger.info(f"成功处理简历工作信息，ID: {resume_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"处理简历工作信息失败，ID: {resume_id}, 错误: {e}")
            return False
        finally:
            close_db_connection(cursor, connection)
    
    def update_resume_data_in_db(self, resume_id: int, processed_data: Dict[str, Any], original_data: Dict[str, Any]):
        """
        更新处理后的简历数据到数据库
        
        Args:
            resume_id: 简历ID
            processed_data: 处理后的数据
            original_data: 原始数据
        """
        connection = get_db_connection()
        cursor = connection.cursor()
        
        try:
            # 将处理后的数据转换为JSON字符串
            processed_json = json.dumps(processed_data, ensure_ascii=False)
            
            # 检查数据是否发生变化
            data_changed = self.has_data_changed(original_data, processed_data)
            
            if data_changed:
                # 数据有变化，更新数据和check_type
                if self.config.update_work_years:
                    cursor.execute("""
                        UPDATE zhilian_resume 
                        SET resume_processed_info = %s, check_type = '12', work_years = '1'
                        WHERE id = %s
                    """, (processed_json, resume_id))
                else:
                    cursor.execute("""
                        UPDATE zhilian_resume 
                        SET resume_processed_info = %s, check_type = '12'
                        WHERE id = %s
                    """, (processed_json, resume_id))
                
                self.stats['total_updated'] += 1
                self.logger.info(f"线程:{threading.current_thread().name} 已更新简历ID：{resume_id}（数据有变化）")
            else:
                # 数据无变化，只更新check_type为已处理但无变化的状态
                cursor.execute("""
                    UPDATE zhilian_resume 
                    SET check_type = '13'
                    WHERE id = %s
                """, (resume_id,))
                self.logger.info(f"线程:{threading.current_thread().name} 简历ID：{resume_id} 数据无变化，标记为已处理")
            
            connection.commit()
            
        except Exception as e:
            self.logger.error(f"更新数据库失败，简历ID {resume_id}: {e}")
            connection.rollback()
            self.stats['errors'] += 1
            
            # 如果更新失败，重置check_type
            try:
                cursor.execute("""
                    UPDATE zhilian_resume 
                    SET check_type = NULL 
                    WHERE id = %s
                """, (resume_id,))
                connection.commit()
            except Exception as reset_error:
                self.logger.error(f"重置check_type失败: {reset_error}")
                
        finally:
            close_db_connection(cursor, connection)
    
    def worker_thread(self, batch_size: int = None):
        """
        工作线程函数
        
        Args:
            batch_size: 每批处理的数据量
        """
        if batch_size is None:
            batch_size = self.config.batch_size
        
        thread_name = threading.current_thread().name
        
        while True:
            with self.lock:
                rows = self.fetch_resume_data_from_db(batch_size)
            
            if not rows:
                self.logger.info(f"线程 {thread_name} 没有更多数据，退出")
                break
            
            self.logger.info(f"线程 {thread_name} 正在处理 {len(rows)} 条简历数据...")
            
            for row in rows:
                resume_id = row[0]
                resume_processed_info = row[1]
                
                try:
                    # 解析JSON数据
                    if isinstance(resume_processed_info, str):
                        resume_data = json.loads(resume_processed_info)
                    else:
                        resume_data = resume_processed_info
                    
                    if not isinstance(resume_data, dict):
                        self.logger.warning(f"简历ID {resume_id} 的数据格式不正确，跳过处理")
                        continue
                    
                    # 保存原始数据的副本用于比较
                    original_data = copy.deepcopy(resume_data)
                    
                    # 处理简历数据
                    processed_data = self.process_resume_data(resume_data)
                    
                    # 更新数据库，传入原始数据用于比较
                    self.update_resume_data_in_db(resume_id, processed_data, original_data)
                    
                    self.stats['total_processed'] += 1
                    
                except json.JSONDecodeError as e:
                    self.logger.error(f"简历ID {resume_id} JSON解析失败: {e}")
                    self.stats['errors'] += 1
                    # 标记为处理失败
                    try:
                        connection = get_db_connection()
                        cursor = connection.cursor()
                        cursor.execute("""
                            UPDATE zhilian_resume 
                            SET check_type = 'json_error' 
                            WHERE id = %s
                        """, (resume_id,))
                        connection.commit()
                        close_db_connection(cursor, connection)
                    except Exception as db_error:
                        self.logger.error(f"更新错误状态失败: {db_error}")
                        
                except Exception as e:
                    self.logger.error(f"处理简历ID {resume_id} 时出错: {e}")
                    self.stats['errors'] += 1
                    # 重置check_type以便重新处理
                    try:
                        connection = get_db_connection()
                        cursor = connection.cursor()
                        cursor.execute("""
                            UPDATE zhilian_resume 
                            SET check_type = NULL 
                            WHERE id = %s
                        """, (resume_id,))
                        connection.commit()
                        close_db_connection(cursor, connection)
                    except Exception as db_error:
                        self.logger.error(f"重置check_type失败: {db_error}")
    
    def start_processing(self, num_threads: int = None, batch_size: int = None):
        """
        启动多线程处理简历数据
        
        Args:
            num_threads: 线程数量
            batch_size: 每批处理的数据量
        """
        if num_threads is None:
            num_threads = self.config.num_threads
        if batch_size is None:
            batch_size = self.config.batch_size
        
        threads = []
        
        self.logger.info(f"启动 {num_threads} 个线程处理简历数据，每批处理 {batch_size} 条")
        self.logger.info(f"配置信息: 去重={self.config.enable_deduplication}, 至今处理={self.config.enable_zhijin_processing}, 证书分割={self.config.enable_certificate_splitting}")
        
        start_time = time.time()
        
        for i in range(num_threads):
            thread = threading.Thread(
                target=self.worker_thread,
                args=(batch_size,),
                name=f"ZhilianWorker-{i+1}"
            )
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        self.logger.info("所有简历数据处理完成")
        self.logger.info(f"总处理时间: {end_time - start_time:.2f} 秒")
        self.print_stats()
    
    def print_stats(self):
        """
        打印处理统计信息
        """
        self.logger.info("=== 处理统计信息 ===")
        self.logger.info(f"总处理记录数: {self.stats['total_processed']}")
        self.logger.info(f"总更新记录数: {self.stats['total_updated']}")
        self.logger.info(f"教育经历更新数: {self.stats['education_updated']}")
        self.logger.info(f"工作经历更新数: {self.stats['work_updated']}")
        self.logger.info(f"项目经历更新数: {self.stats['project_updated']}")
        self.logger.info(f"证书更新数: {self.stats['certificate_updated']}")
        self.logger.info(f"错误记录数: {self.stats['errors']}")
    
    def process_single_resume_by_id(self, resume_id: int) -> Dict[str, Any]:
        """
        处理单个简历（根据ID）
        
        Args:
            resume_id: 简历ID
            
        Returns:
            dict: 处理结果
        """
        connection = get_db_connection()
        cursor = connection.cursor()
        
        try:
            cursor.execute("""
                SELECT id, resume_processed_info 
                FROM zhilian_resume 
                WHERE id = %s
            """, (resume_id,))
            
            row = cursor.fetchone()
            if not row:
                return {'success': False, 'message': f'未找到简历ID {resume_id}'}
            
            resume_processed_info = row[1]
            
            # 解析JSON数据
            if isinstance(resume_processed_info, str):
                resume_data = json.loads(resume_processed_info)
            else:
                resume_data = resume_processed_info
            
            # 保存原始数据的副本用于比较
            original_data = copy.deepcopy(resume_data)
            
            # 处理简历数据
            processed_data = self.process_resume_data(resume_data)
            
            # 更新数据库
            self.update_resume_data_in_db(resume_id, processed_data, original_data)
            
            return {
                'success': True, 
                'message': f'简历ID {resume_id} 处理完成',
                'data_changed': self.has_data_changed(original_data, processed_data)
            }
            
        except Exception as e:
            self.logger.error(f"处理简历ID {resume_id} 时出错: {e}")
            return {'success': False, 'message': f'处理失败: {str(e)}'}
        
        finally:
            close_db_connection(cursor, connection)
    
    def export_resumes_to_excel(self, platform: str = "", limit: Optional[int] = None) -> str:
        """导出简历数据到Excel文件"""
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            # 构建查询语句
            if platform == 'wy':
                sql = f"SELECT id, resume_processed_info as info FROM zhilian_resume WHERE resume_processed_info IS NOT NULL and id > {self.config.excel_start_id} and id <= {self.config.excel_end_id} ORDER BY id"
            elif platform == 'sc':
                sql = f"SELECT id, resume_info as info FROM sc_pub_recruitmentnet_resume WHERE resume_info IS NOT NULL and id > {self.config.excel_start_id} and id <= {self.config.excel_end_id} ORDER BY id"
            else:
                sql = f"SELECT id, resume_processed_info as info FROM zhilian_resume WHERE resume_processed_info IS NOT NULL and id > {self.config.excel_start_id} and id <= {self.config.excel_end_id} and length(resume_processed_info) <= 5000 ORDER BY id"
            
            if limit:
                sql += f" LIMIT {limit}"
            
            cursor.execute(sql)
            resume_data = cursor.fetchall()
            
            self.logger.info(f"获取到 {len(resume_data)} 条简历数据用于导出")
            
            # 导出到Excel
            output_file = self.export_to_excel(resume_data, platform)
            
            return output_file
            
        except Exception as e:
            self.logger.error(f"导出Excel失败: {e}")
            raise
        finally:
            close_db_connection(cursor, connection)
    
    def process_job_info_extraction(self, max_workers: int = 10) -> Dict[str, Any]:
        """多线程处理简历工作信息提取"""
        start_time = time.time()
        self.logger.info(f"开始提取简历工作信息，线程数: {max_workers}")
        
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT id, resume_info FROM zhilian_resume WHERE resume_info IS NOT NULL")
            resume_data = cursor.fetchall()
            close_db_connection(cursor, connection)
            
            self.logger.info(f"获取到 {len(resume_data)} 条简历数据")
            
            success_count = 0
            failed_count = 0
            
            # 使用线程池处理
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(self.process_single_resume_job_info, resume) for resume in resume_data]
                
                for future in futures:
                    try:
                        if future.result():
                            success_count += 1
                        else:
                            failed_count += 1
                    except Exception as e:
                        self.logger.error(f"线程执行异常: {e}")
                        failed_count += 1
            
            end_time = time.time()
            total_time = end_time - start_time
            
            self.logger.info(f"工作信息提取完成！成功: {success_count}, 失败: {failed_count}, 耗时: {total_time:.2f}秒")
            
            return {
                'success': True,
                'processed_count': success_count,
                'failed_count': failed_count,
                'total_time': total_time,
                'message': f'工作信息提取完成，成功: {success_count}, 失败: {failed_count}'
            }
            
        except Exception as e:
            self.logger.error(f"工作信息提取过程中发生错误: {e}")
            return {
                'success': False,
                'processed_count': 0,
                'failed_count': 0,
                'total_time': 0,
                'message': f'工作信息提取失败: {str(e)}'
            }
    
    def process_data_filtering_only(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """仅执行数据过滤处理"""
        start_time = time.time()
        self.logger.info("开始执行数据过滤处理")
        
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            # 获取原始数据
            sql = "SELECT id, resume_info FROM zhilian_resume WHERE resume_processed_info IS NULL"
            if limit:
                sql += f" LIMIT {limit}"
            
            cursor.execute(sql)
            resume_data = cursor.fetchall()
            
            self.logger.info(f"获取到 {len(resume_data)} 条待处理简历")
            
            processed_count = 0
            failed_count = 0
            
            for resume_id, resume_info in resume_data:
                try:
                    resume_json = json.loads(resume_info)
                    filtered_data = self.filter_resume_data(resume_json, self.config.retain_fields)
                    processed_info = json.dumps(filtered_data, ensure_ascii=False)
                    
                    cursor.execute(
                        "UPDATE zhilian_resume SET resume_processed_info = %s WHERE id = %s",
                        (processed_info, resume_id)
                    )
                    connection.commit()
                    processed_count += 1
                    self.logger.debug(f"已过滤简历 {resume_id}")
                    
                except Exception as e:
                    connection.rollback()
                    self.logger.error(f"过滤简历 {resume_id} 失败: {e}")
                    failed_count += 1
                    continue
            
            end_time = time.time()
            total_time = end_time - start_time
            
            self.logger.info(f"数据过滤完成！成功: {processed_count}, 失败: {failed_count}, 耗时: {total_time:.2f}秒")
            
            return {
                'success': True,
                'processed_count': processed_count,
                'failed_count': failed_count,
                'total_time': total_time,
                'message': f'数据过滤完成，成功: {processed_count}, 失败: {failed_count}'
            }
            
        except Exception as e:
            self.logger.error(f"数据过滤过程中发生错误: {e}")
            return {
                'success': False,
                'processed_count': 0,
                'failed_count': 0,
                'total_time': 0,
                'message': f'数据过滤失败: {str(e)}'
            }
        finally:
            close_db_connection(cursor, connection)
    
    def process_sc_platform_resumes(self) -> Dict[str, Any]:
        """处理SC平台简历数据"""
        start_time = time.time()
        self.logger.info("开始处理SC平台简历数据")
        
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            # 获取SC平台简历数据
            cursor.execute("""
                SELECT id, resume_info 
                FROM sc_pub_recruitmentnet_resume 
                WHERE resume_info IS NOT NULL
            """)
            resume_data = cursor.fetchall()
            
            self.logger.info(f"获取到 {len(resume_data)} 条SC平台简历数据")
            
            processed_count = 0
            failed_count = 0
            
            for resume_id, resume_info in resume_data:
                try:
                    # 解析JSON数据
                    resume_json = json.loads(resume_info)
                    
                    # 转换为统一格式
                    unified_data = self._convert_sc_to_unified_format(resume_json)
                    
                    # 应用清理和过滤
                    if self.config.enable_html_cleaning:
                        unified_data = self._apply_html_cleaning(unified_data)
                    
                    if self.config.enable_data_filtering:
                        unified_data = self.filter_resume_data(unified_data, self.config.retain_fields)
                    
                    # 更新数据库
                    processed_info = json.dumps(unified_data, ensure_ascii=False, cls=self.DateEncoder)
                    cursor.execute(
                        "UPDATE sc_pub_recruitmentnet_resume SET resume_processed_info = %s WHERE id = %s",
                        (processed_info, resume_id)
                    )
                    connection.commit()
                    processed_count += 1
                    self.logger.debug(f"已处理SC简历 {resume_id}")
                    
                except Exception as e:
                    connection.rollback()
                    self.logger.error(f"处理SC简历 {resume_id} 失败: {e}")
                    failed_count += 1
                    continue
            
            end_time = time.time()
            total_time = end_time - start_time
            
            self.logger.info(f"SC平台简历处理完成！成功: {processed_count}, 失败: {failed_count}, 耗时: {total_time:.2f}秒")
            
            return {
                'success': True,
                'processed_count': processed_count,
                'failed_count': failed_count,
                'total_time': total_time,
                'message': f'SC平台简历处理完成，成功: {processed_count}, 失败: {failed_count}'
            }
            
        except Exception as e:
            self.logger.error(f"SC平台简历处理过程中发生错误: {e}")
            return {
                'success': False,
                'processed_count': 0,
                'failed_count': 0,
                'total_time': 0,
                'message': f'SC平台简历处理失败: {str(e)}'
            }
        finally:
            close_db_connection(cursor, connection)
    
    def _convert_sc_to_unified_format(self, sc_data: Dict[str, Any]) -> Dict[str, Any]:
        """将SC平台数据转换为统一格式"""
        # 这里实现SC平台数据到统一格式的转换逻辑
        # 根据实际的SC数据结构进行调整
        unified_data = {
            'resume': sc_data.copy()
        }
        return unified_data

# 使用示例
if __name__ == "__main__":
    # 创建配置
    config = ZhilianResumeProcessorConfig()
    
    # 自定义配置
    config.num_threads = 10
    config.batch_size = 30
    config.enable_deduplication = True
    config.enable_zhijin_processing = True
    config.enable_certificate_splitting = True
    
    # 创建处理器
    processor = ZhilianResumeProcessor(config)
    
    # 开始处理
    processor.start_processing()