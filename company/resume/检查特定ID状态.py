# -*- coding: utf-8 -*-
"""
检查特定ID的处理状态脚本
"""

import json
from db_connection import get_db_connection, close_db_connection

def check_specific_ids():
    """检查特定ID的状态"""
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        # 查询这三个ID的状态
        cursor.execute("""
            SELECT id, train_type, check_type, 
                   CASE 
                       WHEN resume_processed_info IS NULL THEN 'NULL'
                       WHEN resume_processed_info = '' THEN 'EMPTY'
                       ELSE 'HAS_DATA'
                   END as data_status,
                   LENGTH(resume_processed_info) as data_length
            FROM zhilian_resume 
            WHERE id IN ('301', '25582', '50')
            ORDER BY id
        """)
        
        rows = cursor.fetchall()
        
        print("ID状态检查结果:")
        print("-" * 80)
        print(f"{'ID':<10} {'train_type':<12} {'check_type':<15} {'data_status':<12} {'data_length':<12}")
        print("-" * 80)
        
        for row in rows:
            print(f"{row[0]:<10} {row[1]:<12} {str(row[2]):<15} {row[3]:<12} {str(row[4]):<12}")
        
        if not rows:
            print("未找到这些ID的记录")
        
        # 检查是否有JSON解析问题
        print("\n检查JSON数据格式:")
        print("-" * 50)
        
        cursor.execute("""
            SELECT id, resume_processed_info
            FROM zhilian_resume 
            WHERE id IN ('301', '25582', '50')
            AND resume_processed_info IS NOT NULL
            AND resume_processed_info != ''
        """)
        
        data_rows = cursor.fetchall()
        
        for row in data_rows:
            resume_id = row[0]
            resume_data = row[1]
            
            try:
                if isinstance(resume_data, str):
                    parsed_data = json.loads(resume_data)
                else:
                    parsed_data = resume_data
                
                # 检查关键字段
                resume_info = parsed_data.get('resume', {})
                education_count = len(resume_info.get('educationExperiences', []))
                work_count = len(resume_info.get('workExperiences', []))
                project_count = len(resume_info.get('projectExperiences', []))
                cert_count = len(resume_info.get('certificates', []))
                
                print(f"ID {resume_id}: JSON格式正常")
                print(f"  - 教育经历: {education_count} 条")
                print(f"  - 工作经历: {work_count} 条")
                print(f"  - 项目经历: {project_count} 条")
                print(f"  - 证书: {cert_count} 条")
                
            except json.JSONDecodeError as e:
                print(f"ID {resume_id}: JSON解析失败 - {e}")
            except Exception as e:
                print(f"ID {resume_id}: 数据处理失败 - {e}")
    
    except Exception as e:
        print(f"查询失败: {e}")
    
    finally:
        close_db_connection(cursor, connection)

def reset_specific_ids():
    """重置特定ID的处理状态"""
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        # 重置这三个ID的check_type
        cursor.execute("""
            UPDATE zhilian_resume 
            SET check_type = NULL
            WHERE id IN ('301', '25582', '50')
            AND train_type = '3'
        """)
        
        affected_rows = cursor.rowcount
        connection.commit()
        
        print(f"已重置 {affected_rows} 条记录的处理状态")
        
    except Exception as e:
        print(f"重置失败: {e}")
        connection.rollback()
    
    finally:
        close_db_connection(cursor, connection)

if __name__ == "__main__":
    print("=== 检查特定ID状态 ===")
    check_specific_ids()
    
    print("\n=== 重置处理状态 ===")
    reset_specific_ids()
    
    print("\n=== 重置后再次检查 ===")
    check_specific_ids()