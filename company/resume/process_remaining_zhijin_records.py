# -*- coding: utf-8 -*-
"""
处理剩余的包含'至今'的记录
将工作和项目经历中的'至今'替换为'2025.05'并重新计算时间
同时更新work_years字段为1
"""

import json
import re
from datetime import datetime
from db_connection import DatabaseConnection

def parse_time_period(time_str):
    """
    解析时间段字符串，返回开始时间、结束时间和持续时间
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

def calculate_duration(start_time, end_time='2025.05'):
    """
    计算两个时间点之间的持续时间
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
        print(f"计算持续时间出错: {e}")
        return "0个月"

def update_time_label(time_label):
    """
    更新timeLabel，将'至今'替换为'2025.05'并重新计算持续时间
    """
    if not time_label or '至今' not in time_label:
        return time_label, False
    
    start_time, _, _ = parse_time_period(time_label)
    if not start_time:
        return time_label, False
    
    # 计算新的持续时间
    new_duration = calculate_duration(start_time, '2025.05')
    
    # 构建新的时间标签
    new_time_label = f"{start_time} - 2025.05 ({new_duration})"
    
    print(f"    更新: {time_label} -> {new_time_label}")
    return new_time_label, True

def process_experiences(experiences, experience_type):
    """
    处理工作或项目经历列表
    """
    updated = False
    
    if not experiences or not isinstance(experiences, list):
        return updated
    
    for i, exp in enumerate(experiences):
        if isinstance(exp, dict) and 'timeLabel' in exp:
            original_time_label = exp['timeLabel']
            new_time_label, was_updated = update_time_label(original_time_label)
            
            if was_updated:
                exp['timeLabel'] = new_time_label
                updated = True
                print(f"    {experience_type} {i+1}: {original_time_label} -> {new_time_label}")
    
    return updated

def process_resume_data():
    """
    处理剩余的包含'至今'的简历数据
    """
    db = DatabaseConnection()
    conn = None
    cursor = None
    
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # 查询剩余需要处理的记录
        query = """
            SELECT id, resume_processed_info 
            FROM zhilian_resume 
            where train_type = '3' 
            AND resume_processed_info LIKE %s
        """
        
        cursor.execute(query, ('%至今%',))
        records = cursor.fetchall()
        
        print(f"找到 {len(records)} 条需要处理的记录")
        
        updated_count = 0
        
        for record_id, resume_info in records:
            try:
                # 解析JSON数据
                resume_data = json.loads(resume_info)
                
                if 'resume' not in resume_data:
                    continue
                
                resume = resume_data['resume']
                has_updates = False
                
                print(f"\n处理简历ID {record_id}:")
                
                # 处理工作经历
                if 'workExperiences' in resume:
                    work_updated = process_experiences(resume['workExperiences'], '工作经历')
                    if work_updated:
                        has_updates = True
                
                # 处理项目经历
                if 'projectExperiences' in resume:
                    project_updated = process_experiences(resume['projectExperiences'], '项目经历')
                    if project_updated:
                        has_updates = True
                
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
                    updated_count += 1
                    
                    print(f"  已更新简历ID {record_id}，work_years设置为1")
                
            except json.JSONDecodeError as e:
                print(f"简历ID {record_id} JSON解析错误: {e}")
                continue
            except Exception as e:
                print(f"处理简历ID {record_id} 时出错: {e}")
                continue
        
        # 提交事务
        conn.commit()
        print(f"\n处理完成，共更新 {updated_count} 条记录")
        
        # 验证处理结果
        print("\n=== 验证处理结果 ===")
        
        # 检查剩余的'至今'记录
        cursor.execute("""
            SELECT COUNT(*) FROM zhilian_resume 
            WHERE train_type = '3' 
            AND resume_processed_info LIKE %s
        """, ('%至今%',))
        
        result = cursor.fetchone()
        remaining_count = result[0] if result else 0
        print(f"剩余包含'至今'的记录数: {remaining_count}")
        
        # 检查work_years='1'的记录数
        cursor.execute("""
            SELECT COUNT(*) FROM zhilian_resume 
            WHERE work_years = '1'
            and train_type = '3' 
        """, )
        
        result = cursor.fetchone()
        work_years_1_count = result[0] if result else 0
        print(f"work_years='1'的记录数: {work_years_1_count}")
        
        # 显示一些样本
        cursor.execute("""
            SELECT id FROM zhilian_resume 
            WHERE work_years = '1'
            and train_type = '3' 
            ORDER BY id
            LIMIT 10
        """)
        
        samples = cursor.fetchall()
        print("\nwork_years='1'的样本记录:")
        for (sample_id,) in samples:
            print(f"  简历ID {sample_id}")
        
    except Exception as e:
        print(f"处理过程中出错: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("\n数据库连接已关闭")

if __name__ == "__main__":
    process_resume_data()