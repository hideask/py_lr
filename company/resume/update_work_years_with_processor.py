#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用WorkExperienceProcessor处理工作年限的脚本
从数据库查询数据，使用WorkExperienceProcessor计算总工作年限，并更新相关字段
"""

import json
import logging
from typing import Dict, Any, Optional, Tuple
from work_experience_processor import WorkExperienceProcessor
from db_connection import DatabaseConnection

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('update_work_years.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WorkYearsUpdater:
    """工作年限更新器"""
    
    def __init__(self):
        self.processor = WorkExperienceProcessor()
        self.db_connection = DatabaseConnection()
    
    def get_database_connection(self):
        """获取数据库连接"""
        try:
            connection = self.db_connection.get_connection()
            return connection
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    def parse_work_years(self, work_years_str) -> Tuple[int, int]:
        """解析工作年限字符串，返回年和月"""
        if not work_years_str:
            return 0, 0
        
        try:
            # 如果输入是数字类型，转换为字符串
            if isinstance(work_years_str, (int, float)):
                work_years_str = str(work_years_str)
            
            # 处理格式如 "5年3个月"
            years = 0
            months = 0
            
            if '年' in work_years_str:
                year_part = work_years_str.split('年')[0]
                years = int(year_part)
            
            if '个月' in work_years_str:
                month_part = work_years_str.split('年')[-1].replace('个月', '')
                if month_part:
                    months = int(month_part)
            
            # 如果没有年月标识，尝试直接解析为年数
            if '年' not in work_years_str and '个月' not in work_years_str:
                try:
                    years = int(float(work_years_str))
                except ValueError:
                    pass
            
            return years, months
        except Exception as e:
            logger.warning(f"解析工作年限失败: {work_years_str}, 错误: {e}")
            return 0, 0
    
    def calculate_year_difference(self, old_years: str, new_years: str) -> float:
        """计算工作年限差异（以年为单位）"""
        old_y, old_m = self.parse_work_years(old_years)
        new_y, new_m = self.parse_work_years(new_years)
        
        old_total = old_y + old_m / 12.0
        new_total = new_y + new_m / 12.0
        
        return abs(new_total - old_total)
    
    def process_resume_data(self):
        """处理简历数据"""
        connection = None
        try:
            connection = self.get_database_connection()
            cursor = connection.cursor()
            
            # 查询数据
            query = """
            SELECT id, resume_processed_info 
            FROM zhilian_resume 
              where  train_type = '3'
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            logger.info(f"查询到 {len(results)} 条记录")
            
            processed_count = 0
            updated_count = 0
            check_type_11_count = 0
            
            for record_id, resume_processed_info in results:
                try:
                    # 解析JSON数据
                    if not resume_processed_info:
                        continue
                    
                    resume_data = json.loads(resume_processed_info)
                    
                    
                    # 获取workExperiences数据 - 从resume节点下获取
                    resume_info = resume_data.get('resume', {})
                    work_experiences = resume_info.get('workExperiences', [])
                    if not work_experiences:
                        logger.debug(f"简历ID {record_id}: 没有workExperiences数据")
                        continue
                    
                    logger.debug(f"简历ID {record_id}: 找到 {len(work_experiences)} 个工作经历")
                    
                    # 使用WorkExperienceProcessor计算总工作年限
                    result = self.processor.process_work_experiences(work_experiences)
                    total_work_years = result['total_duration']
                    
                    # 获取原有的工作年限
                    user_data = resume_data.get('user', {})
                    old_work_years = user_data.get('workYears', '')
                    
                    # 更新user节点下的workYears字段
                    if 'user' not in resume_data:
                        resume_data['user'] = {}
                    resume_data['user']['workYears'] = total_work_years
                    
                    # 计算年限差异
                    year_diff = self.calculate_year_difference(old_work_years, total_work_years)
                    
                    # 准备更新字段
                    work_years_field = f"{old_work_years}|{total_work_years}" if old_work_years else total_work_years
                    check_type_value = '11' if year_diff >= 1.0 else None
                    
                    # 更新数据库
                    update_query = """
                    UPDATE zhilian_resume 
                    SET resume_processed_info = %s, work_years = %s
                    """
                    update_params = [json.dumps(resume_data, ensure_ascii=False), work_years_field]
                    
                    if check_type_value is not None:
                        update_query += ", check_type = %s"
                        update_params.append(check_type_value)
                        check_type_11_count += 1
                    
                    update_query += " WHERE id = %s"
                    update_params.append(record_id)
                    
                    cursor.execute(update_query, update_params)
                    updated_count += 1
                    
                    if year_diff >= 1.0:
                        logger.info(f"简历ID {record_id}: 工作年限差异 {year_diff:.1f}年, 原:{old_work_years} -> 新:{total_work_years}")
                    
                    processed_count += 1
                    
                    if processed_count % 100 == 0:
                        logger.info(f"已处理 {processed_count} 条记录")
                        connection.commit()
                
                except Exception as e:
                    logger.error(f"处理简历ID {record_id} 时出错: {e}")
                    continue
            
            # 提交所有更改
            connection.commit()
            
            logger.info(f"处理完成:")
            logger.info(f"- 总查询记录数: {len(results)}")
            logger.info(f"- 成功处理记录数: {processed_count}")
            logger.info(f"- 数据库更新记录数: {updated_count}")
            logger.info(f"- check_type设为11的记录数: {check_type_11_count}")
            
            # 验证更新结果
            self.verify_updates(cursor)
            
        except Exception as e:
            logger.error(f"处理过程中出错: {e}")
            if connection:
                connection.rollback()
        finally:
            if connection:
                connection.close()
    
    def verify_updates(self, cursor):
        """验证更新结果"""
        try:
            # 检查work_years字段包含"|"的记录数
            cursor.execute("""
                SELECT COUNT(*) FROM zhilian_resume 
                WHERE work_years LIKE '%|%' 
                AND LENGTH(resume_description_detail_bk) >= 1000 
                AND LENGTH(resume_description_detail_bk) <= 10000 
                AND train_type = '3'
            """)
            pipe_count = cursor.fetchone()[0]
            logger.info(f"包含'|'的work_years记录数: {pipe_count}")
            
            # 检查check_type=11的记录数
            cursor.execute("""
                SELECT COUNT(*) FROM zhilian_resume 
                WHERE check_type = '11' 
                AND LENGTH(resume_description_detail_bk) >= 1000 
                AND LENGTH(resume_description_detail_bk) <= 10000 
                AND train_type = '3'
            """)
            check_type_11_count = cursor.fetchone()[0]
            logger.info(f"check_type=11的记录数: {check_type_11_count}")
            
            # 显示一些样本数据
            cursor.execute("""
                SELECT id, work_years FROM zhilian_resume 
                WHERE work_years LIKE '%|%' 
                AND LENGTH(resume_description_detail_bk) >= 1000 
                AND LENGTH(resume_description_detail_bk) <= 10000 
                AND train_type = '3'
                LIMIT 5
            """)
            samples = cursor.fetchall()
            logger.info("样本数据:")
            for sample_id, work_years in samples:
                logger.info(f"  简历ID {sample_id}: {work_years}")
                
        except Exception as e:
            logger.error(f"验证过程中出错: {e}")

def main():
    """主函数"""
    updater = WorkYearsUpdater()
    updater.process_resume_data()

if __name__ == "__main__":
    main()