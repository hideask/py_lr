# -*- coding: utf-8 -*-
"""
简历数据去重处理脚本
多线程处理简历数据，去除重复的教育经历、工作经历、项目经历，并处理证书数据
"""

import json
import threading
import logging
import time
import re
import copy
from typing import List, Dict, Any, Tuple
from db_connection import get_db_connection, close_db_connection
from datetime import datetime
from education_experience_processor import EducationExperienceProcessor
from unified_experience_processor import UnifiedExperienceProcessor

# 创建 logger 对象
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 创建一个用于写入文件的 handler
file_handler = logging.FileHandler('resume_deduplication.log')
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# 创建一个用于输出到控制台的 handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

# 将两个 handler 添加到 logger 中
logger.addHandler(file_handler)
logger.addHandler(console_handler)

class ResumeDataProcessor:
    """简历数据处理器"""
    
    def __init__(self):
        self.lock = threading.Lock()
        self.education_processor = EducationExperienceProcessor()
        self.unified_processor = UnifiedExperienceProcessor()
    
    def deduplicate_education_experiences(self, education_experiences: List[Dict]) -> List[Dict]:
        """
        根据schoolName和major去重教育经历，并处理"至今"类型的educationTimeLabel
        
        Args:
            education_experiences: 教育经历列表
            
        Returns:
            去重后的教育经历列表
        """
        if not education_experiences:
            return []
        
        # 首先处理"至今"类型的数据
        processed_experiences = self.education_processor.process_education_experiences(education_experiences)
        
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
                logger.debug(f"保留教育经历: {school_name} - {major}")
            else:
                logger.debug(f"删除重复教育经历: {school_name} - {major}")
        
        return unique_experiences
    
    def deduplicate_work_experiences(self, work_experiences: List[Dict]) -> List[Dict]:
        """
        根据orgName、jobTitle和timeLabel去重工作经历，并处理"至今"类型的timeLabel
        
        Args:
            work_experiences: 工作经历列表
            
        Returns:
            去重后的工作经历列表
        """
        if not work_experiences:
            return []
        
        # 首先处理"至今"类型的数据
        self.unified_processor.process_work_experiences(work_experiences)
        
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
                logger.debug(f"保留工作经历: {org_name} - {job_title} - {time_label}")
            else:
                logger.debug(f"删除重复工作经历: {org_name} - {job_title} - {time_label}")
        
        return unique_experiences
    
    def deduplicate_project_experiences(self, project_experiences: List[Dict]) -> List[Dict]:
        """
        根据name和timeLabel去重项目经历，并处理"至今"类型的timeLabel
        支持模糊匹配（如"移动网络工程，A网一5G"和"移动网络工程"视为重复）
        
        Args:
            project_experiences: 项目经历列表
            
        Returns:
            去重后的项目经历列表
        """
        if not project_experiences:
            return []
        
        # 首先处理"至今"类型的数据
        self.unified_processor.process_project_experiences(project_experiences)
        
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
                    logger.debug(f"删除重复项目经历: {name} - {time_label}")
                    break
            
            if not is_duplicate:
                unique_experiences.append(exp)
                logger.debug(f"保留项目经历: {name} - {time_label}")
        
        return unique_experiences
    
    def process_certificates(self, certificates: List[Dict]) -> List[Dict]:
        """
        处理证书数据，将包含多个证书的字符串分割成单独的证书
        
        Args:
            certificates: 证书列表
            
        Returns:
            处理后的证书列表
        """
        if not certificates:
            return []
        
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
                    logger.debug(f"处理证书: {cert_name}")
        
        return processed_certificates
    
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
            logger.warning("数据中没有找到resume节点")
            return processed_data
        
        resume_data = processed_data['resume']
        
        # 处理教育经历
        if 'educationExperiences' in resume_data:
            resume_data['educationExperiences'] = self.deduplicate_education_experiences(
                resume_data['educationExperiences']
            )
        
        # 处理工作经历
        if 'workExperiences' in resume_data:
            resume_data['workExperiences'] = self.deduplicate_work_experiences(
                resume_data['workExperiences']
            )
        
        # 处理项目经历
        if 'projectExperiences' in resume_data:
            resume_data['projectExperiences'] = self.deduplicate_project_experiences(
                resume_data['projectExperiences']
            )
        
        # 处理证书
        if 'certificates' in resume_data:
            resume_data['certificates'] = self.process_certificates(
                resume_data['certificates']
            )
        
        # 更新processed_data中的resume数据
        processed_data['resume'] = resume_data
        
        return processed_data
    
    def fetch_resume_data_from_db(self, batch_size: int = 100) -> List[Tuple[int, str]]:
        """
        从数据库获取简历数据
        
        Args:
            batch_size: 批次大小
            
        Returns:
            简历数据列表 [(id, resume_processed_info), ...]
        """
        connection = get_db_connection()
        cursor = connection.cursor()
        
        try:
            # 查询未处理的简历数据并标记为正在处理
            cursor.execute("""
                SELECT id, resume_processed_info 
                FROM zhilian_resume 
                WHERE train_type = '3' 
                AND (check_type IS NULL OR (check_type != '12' AND check_type != '13'))
                ORDER BY id 
                LIMIT %s 
                FOR UPDATE SKIP LOCKED
            """, (batch_size,))
            # cursor.execute("""
            #     SELECT id, resume_processed_info 
            #     FROM zhilian_resume 
            #     WHERE id in ('301','25582','50')
            #     LIMIT %s 
            #     FOR UPDATE SKIP LOCKED
            # """, (batch_size,))
            
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
            logger.error(f"从数据库获取数据失败: {e}")
            connection.rollback()
            return []
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
                cursor.execute("""
                    UPDATE zhilian_resume 
                    SET resume_processed_info = %s, check_type = '12'
                    WHERE id = %s
                """, (processed_json, resume_id))
                logger.info(f"线程:{threading.current_thread().name} 已更新简历ID：{resume_id}（数据有变化）")
            else:
                # 数据无变化，只更新check_type为已处理但无变化的状态
                cursor.execute("""
                    UPDATE zhilian_resume 
                    SET check_type = '13'
                    WHERE id = %s
                """, (resume_id,))
                logger.info(f"线程:{threading.current_thread().name} 简历ID：{resume_id} 数据无变化，标记为已处理")
            
            connection.commit()
            
        except Exception as e:
            logger.error(f"更新数据库失败，简历ID {resume_id}: {e}")
            connection.rollback()
            
            # 如果更新失败，重置check_type
            try:
                cursor.execute("""
                    UPDATE zhilian_resume 
                    SET check_type = NULL 
                    WHERE id = %s
                """, (resume_id,))
                connection.commit()
            except Exception as reset_error:
                logger.error(f"重置check_type失败: {reset_error}")
                
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
            original_resume = original_data.get('', {})
            processed_resume = processed_data.get('', {})
            
            # 检查关键字段是否有变化
            fields_to_check = ['educationExperiences', 'workExperiences', 'projectExperiences', 'certificates']
            
            for field in fields_to_check:
                original_field = original_resume.get(field, [])
                processed_field = processed_resume.get(field, [])
                
                # 比较字段内容
                if self.normalize_for_comparison(original_field) != self.normalize_for_comparison(processed_field):
                    logger.debug(f"字段 {field} 发生变化")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"比较数据变化时出错: {e}")
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
    
    def worker_thread(self, batch_size: int = 50):
        """
        工作线程函数
        
        Args:
            batch_size: 每批处理的数据量
        """
        thread_name = threading.current_thread().name
        
        while True:
            with self.lock:
                rows = self.fetch_resume_data_from_db(batch_size)
            
            if not rows:
                logger.info(f"线程 {thread_name} 没有更多数据，退出")
                break
            
            logger.info(f"线程 {thread_name} 正在处理 {len(rows)} 条简历数据...")
            
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
                        logger.warning(f"简历ID {resume_id} 的数据格式不正确，跳过处理")
                        continue
                    
                    # 保存原始数据的副本用于比较
                    original_data = copy.deepcopy(resume_data)
                    
                    # 处理简历数据
                    processed_data = self.process_resume_data(resume_data)
                    
                    # 更新数据库，传入原始数据用于比较
                    self.update_resume_data_in_db(resume_id, processed_data, original_data)
                    
                except json.JSONDecodeError as e:
                    logger.error(f"简历ID {resume_id} JSON解析失败: {e}")
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
                        logger.error(f"更新错误状态失败: {db_error}")
                        
                except Exception as e:
                    logger.error(f"处理简历ID {resume_id} 时出错: {e}")
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
                        logger.error(f"重置check_type失败: {db_error}")
    
    def start_processing(self, num_threads: int = 5, batch_size: int = 50):
        """
        启动多线程处理简历数据
        
        Args:
            num_threads: 线程数量
            batch_size: 每批处理的数据量
        """
        threads = []
        
        logger.info(f"启动 {num_threads} 个线程处理简历数据，每批处理 {batch_size} 条")
        
        for i in range(num_threads):
            thread = threading.Thread(
                target=self.worker_thread,
                args=(batch_size,),
                name=f"ResumeWorker-{i+1}"
            )
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        logger.info("所有简历数据处理完成")

def main():
    """主函数"""
    # 配置参数
    num_threads = 20  # 线程数量
    batch_size = 20  # 每批处理的数据量
    
    # 创建处理器实例
    processor = ResumeDataProcessor()
    
    # 开始处理
    start_time = time.time()
    processor.start_processing(num_threads=num_threads, batch_size=batch_size)
    end_time = time.time()
    
    logger.info(f"总处理时间: {end_time - start_time:.2f} 秒")

if __name__ == "__main__":
    main()