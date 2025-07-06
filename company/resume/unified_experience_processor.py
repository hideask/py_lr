# -*- coding: utf-8 -*-
"""
统一经历处理器
集成工作经历和教育经历的"至今"数据处理功能
将process_remaining_zhijin_records.py的功能整合到类架构中
"""

import json
import re
from typing import List, Dict, Tuple, Optional
from db_connection import DatabaseConnection
from work_experience_processor import WorkExperienceProcessor
from company.resume.education_experience_processor import EducationExperienceProcessor
import logging

class UnifiedExperienceProcessor:
    """
    统一经历处理器
    集成工作经历和教育经历的"至今"数据处理功能
    """
    
    def __init__(self):
        """
        初始化处理器
        """
        self.work_processor = WorkExperienceProcessor()
        self.education_processor = EducationExperienceProcessor()
        self.logger = logging.getLogger(__name__)
    
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
            return None, None, None
        
        start_time = match.group(1)
        duration_text = match.group(2)
        
        return start_time, '至今', duration_text
    
    def calculate_duration(self, start_time: str, end_time: str = '2025.05') -> str:
        """
        计算两个时间点之间的持续时间
        
        Args:
            start_time: 开始时间 (格式: YYYY.MM)
            end_time: 结束时间 (格式: YYYY.MM)
            
        Returns:
            str: 持续时间描述
        """
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
        更新timeLabel，将'至今'替换为'2025.05'并重新计算持续时间
        
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
        new_duration = self.calculate_duration(start_time, '2025.05')
        
        # 构建新的时间标签
        new_time_label = f"{start_time} - 2025.05 ({new_duration})"
        
        self.logger.info(f"    更新: {time_label} -> {new_time_label}")
        return new_time_label, True
    
    def process_work_experiences(self, experiences: List[Dict]) -> bool:
        """
        处理工作经历列表中的"至今"数据
        
        Args:
            experiences: 工作经历列表
            
        Returns:
            bool: 是否有更新
        """
        updated = False
        
        if not experiences or not isinstance(experiences, list):
            return updated
        
        for i, exp in enumerate(experiences):
            if isinstance(exp, dict) and 'timeLabel' in exp:
                original_time_label = exp['timeLabel']
                new_time_label, was_updated = self.update_time_label(original_time_label)
                
                if was_updated:
                    exp['timeLabel'] = new_time_label
                    updated = True
                    self.logger.info(f"    工作经历 {i+1}: {original_time_label} -> {new_time_label}")
        
        return updated
    
    def process_project_experiences(self, experiences: List[Dict]) -> bool:
        """
        处理项目经历列表中的"至今"数据
        
        Args:
            experiences: 项目经历列表
            
        Returns:
            bool: 是否有更新
        """
        updated = False
        
        if not experiences or not isinstance(experiences, list):
            return updated
        
        for i, exp in enumerate(experiences):
            if isinstance(exp, dict) and 'timeLabel' in exp:
                original_time_label = exp['timeLabel']
                new_time_label, was_updated = self.update_time_label(original_time_label)
                
                if was_updated:
                    exp['timeLabel'] = new_time_label
                    updated = True
                    self.logger.info(f"    项目经历 {i+1}: {original_time_label} -> {new_time_label}")
        
        return updated
    
    def process_education_experiences_zhijin(self, experiences: List[Dict]) -> bool:
        """
        处理教育经历列表中的"至今"数据（智联格式）
        
        Args:
            experiences: 教育经历列表
            
        Returns:
            bool: 是否有更新
        """
        updated = False
        
        if not experiences or not isinstance(experiences, list):
            return updated
        
        for i, exp in enumerate(experiences):
            if isinstance(exp, dict) and 'educationTimeLabel' in exp:
                original_time_label = exp['educationTimeLabel']
                
                # 使用教育经历处理器的逻辑
                processed_exp = self.education_processor.process_education_experiences([exp])
                if processed_exp and len(processed_exp) > 0:
                    new_time_label = processed_exp[0].get('educationTimeLabel', original_time_label)
                    
                    if new_time_label != original_time_label:
                        exp['educationTimeLabel'] = new_time_label
                        updated = True
                        self.logger.info(f"    教育经历 {i+1}: {original_time_label} -> {new_time_label}")
        
        return updated
    
    def process_single_resume(self, resume_data: Dict) -> bool:
        """
        处理单个简历的所有经历数据
        
        Args:
            resume_data: 简历数据字典
            
        Returns:
            bool: 是否有更新
        """
        if 'resume' not in resume_data:
            return False
        
        resume = resume_data['resume']
        has_updates = False
        
        # 处理工作经历
        if 'workExperiences' in resume:
            work_updated = self.process_work_experiences(resume['workExperiences'])
            if work_updated:
                has_updates = True
        
        # 处理项目经历
        if 'projectExperiences' in resume:
            project_updated = self.process_project_experiences(resume['projectExperiences'])
            if project_updated:
                has_updates = True
        
        # 处理教育经历
        if 'educationExperiences' in resume:
            education_updated = self.process_education_experiences_zhijin(resume['educationExperiences'])
            if education_updated:
                has_updates = True
        
        return has_updates
    
    def process_resume_data_batch(self, train_type: str = '3') -> Dict[str, int]:
        """
        批量处理包含'至今'的简历数据
        
        Args:
            train_type: 训练类型，默认为'3'
            
        Returns:
            dict: 处理结果统计
        """
        db = DatabaseConnection()
        conn = None
        cursor = None
        
        stats = {
            'total_found': 0,
            'total_updated': 0,
            'work_updated': 0,
            'project_updated': 0,
            'education_updated': 0,
            'errors': 0
        }
        
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # 查询剩余需要处理的记录
            query = """
                SELECT id, resume_processed_info 
                FROM zhilian_resume 
                WHERE train_type = %s 
                AND resume_processed_info LIKE %s
            """
            
            cursor.execute(query, (train_type, '%至今%'))
            records = cursor.fetchall()
            
            stats['total_found'] = len(records)
            self.logger.info(f"找到 {len(records)} 条需要处理的记录")
            
            for record_id, resume_info in records:
                try:
                    # 解析JSON数据
                    resume_data = json.loads(resume_info)
                    
                    self.logger.info(f"\n处理简历ID {record_id}:")
                    
                    # 处理简历数据
                    has_updates = self.process_single_resume(resume_data)
                    
                    # 如果有更新，保存到数据库
                    if has_updates:
                        # 更新resume_processed_info
                        updated_resume_info = json.dumps(resume_data, ensure_ascii=False)
                        
                        # 更新数据库
                        update_query = """
                            UPDATE zhilian_resume 
                            SET resume_processed_info = %s, work_years = %s
                            WHERE id = %s
                        """
                        
                        cursor.execute(update_query, (updated_resume_info, '1', record_id))
                        stats['total_updated'] += 1
                        
                        self.logger.info(f"  已更新简历ID {record_id}，work_years设置为1")
                
                except json.JSONDecodeError as e:
                    self.logger.error(f"简历ID {record_id} JSON解析错误: {e}")
                    stats['errors'] += 1
                    continue
                except Exception as e:
                    self.logger.error(f"处理简历ID {record_id} 时出错: {e}")
                    stats['errors'] += 1
                    continue
            
            # 提交事务
            conn.commit()
            self.logger.info(f"\n处理完成，共更新 {stats['total_updated']} 条记录")
            
            # 验证处理结果
            self._verify_processing_results(cursor, train_type)
            
        except Exception as e:
            self.logger.error(f"处理过程中出错: {e}")
            if conn:
                conn.rollback()
            stats['errors'] += 1
        
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
            self.logger.info("\n数据库连接已关闭")
        
        return stats
    
    def _verify_processing_results(self, cursor, train_type: str):
        """
        验证处理结果
        
        Args:
            cursor: 数据库游标
            train_type: 训练类型
        """
        self.logger.info("\n=== 验证处理结果 ===")
        
        # 检查剩余的'至今'记录
        cursor.execute("""
            SELECT COUNT(*) FROM zhilian_resume 
            WHERE train_type = %s 
            AND resume_processed_info LIKE %s
        """, (train_type, '%至今%'))
        
        result = cursor.fetchone()
        remaining_count = result[0] if result else 0
        self.logger.info(f"剩余包含'至今'的记录数: {remaining_count}")
        
        # 检查work_years='1'的记录数
        cursor.execute("""
            SELECT COUNT(*) FROM zhilian_resume 
            WHERE work_years = '1'
            AND train_type = %s 
        """, (train_type,))
        
        result = cursor.fetchone()
        work_years_1_count = result[0] if result else 0
        self.logger.info(f"work_years='1'的记录数: {work_years_1_count}")
        
        # 显示一些样本
        cursor.execute("""
            SELECT id FROM zhilian_resume 
            WHERE work_years = '1'
            AND train_type = %s 
            ORDER BY id
            LIMIT 10
        """, (train_type,))
        
        samples = cursor.fetchall()
        self.logger.info("\nwork_years='1'的样本记录:")
        for (sample_id,) in samples:
            self.logger.info(f"  简历ID {sample_id}")


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('unified_experience_processor.log'),
            logging.StreamHandler()
        ]
    )
    
    # 创建处理器并运行
    processor = UnifiedExperienceProcessor()
    results = processor.process_resume_data_batch()
    
    print("\n=== 处理结果统计 ===")
    print(f"找到记录数: {results['total_found']}")
    print(f"更新记录数: {results['total_updated']}")
    print(f"错误记录数: {results['errors']}")