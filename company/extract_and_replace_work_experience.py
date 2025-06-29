import json
import psycopg2
import re
from db_connection import get_db_connection, close_db_connection

def extract_work_experience_data():
    """从zhilian_job表中提取包含特定工作年限的数据"""
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        # 查询包含"工作年限": "3-5年"的数据
        sql = """
        SELECT id, job_description_detail, compare_result 
        FROM zhilian_job 
        WHERE compare_result IS NOT NULL 
        AND compare_result::text LIKE '%"工作年限": "3-5年"%'
        """
        
        cursor.execute(sql)
        results = cursor.fetchall()
        
        print(f"找到 {len(results)} 条包含'工作年限: 3-5年'的记录")
        
        # 处理每条记录
        updated_count = 0
        for record in results:
            job_id, job_description_detail, compare_result = record
            
            if job_description_detail:
                # 检查是否包含目标字段
                target_patterns = [
                    "三年以上",
                    "至少拥有三年", 
                    "3年以上",
                    " 3 年以上",
                    "3 年及以上",
                    "2 年以上",
                    "3 至 5 年",
                    " 3 年",
                    "2年以上",
                    "三年或以上",
                    "三年及以上",
                    "三至五年以上",
                    "至少三年",
                    "至少 3 年",
                    "两年以上",
                    " 4 年以上",
                    "三到五年",
                    "三至五年",
                    "3至5年",
                    " 5 年以上",
                    " 1 年以上",
                ]
                
                # 检查是否包含任何目标模式
                contains_target = any(pattern in job_description_detail for pattern in target_patterns)
                
                if contains_target:
                    print(f"\n处理记录 ID: {job_id}")
                    print(f"原始描述: {job_description_detail[:200]}...")
                    
                    # 执行替换
                    updated_description = replace_work_experience_terms(job_description_detail)
                    
                    if updated_description != job_description_detail:
                        # 更新数据库
                        update_sql = "UPDATE zhilian_job SET job_description_detail = %s WHERE id = %s"
                        cursor.execute(update_sql, (updated_description, job_id))
                        connection.commit()
                        
                        updated_count += 1
                        print(f"已更新记录 ID: {job_id}")
                        print(f"更新后描述: {updated_description[:200]}...")
                    else:
                        print(f"记录 ID: {job_id} 无需更新")
        
        print(f"\n总共更新了 {updated_count} 条记录")
        
    except Exception as e:
        print(f"执行过程中出现错误: {str(e)}")
        connection.rollback()
    finally:
        close_db_connection(cursor, connection)

def replace_work_experience_terms(text):
    """替换工作年限相关的术语"""
    if not text:
        return text
    
    # 定义替换规则
    replacements = {
        "三年以上": "3 - 5年",
        "至少拥有三年": "3 - 5年",
        "3年以上": "3 - 5年",
        " 3 年以上": "3 - 5年",
        "3 年及以上": "3 - 5年",
        "2 年以上": "3 - 5年",
        "3 至 5 年": "3 - 5年",
        " 3 年": "3 - 5年",
        "2年以上": "3 - 5年",
        "三年或以上": "3 - 5年",
        "三年及以上": "3 - 5年",
        "三至五年以上": "3 - 5年",
        "至少三年": "3 - 5年",
        "至少 3 年": "3 - 5年",
        "两年以上": "3 - 5年",
        " 4 年以上": "3 - 5年",
        "三到五年": "3 - 5年",
        "三至五年": "3 - 5年",
        "3至5年": "3 - 5年",
        " 5 年以上": "3 - 5年",
        " 1 年以上": "3 - 5年",
    }
    
    updated_text = text
    
    # 执行替换
    for old_term, new_term in replacements.items():
        if old_term in updated_text:
            updated_text = updated_text.replace(old_term, new_term)
            print(f"  替换: '{old_term}' -> '{new_term}'")
    
    return updated_text

def preview_data():
    """预览符合条件的数据"""
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        # 查询包含"工作年限": "3-5年"的数据
        sql = """
        SELECT id, job_description_detail, compare_result 
        FROM zhilian_job 
        WHERE compare_result IS NOT NULL 
        AND compare_result::text LIKE '%"工作年限": "3-5年"%'
        LIMIT 10
        """
        
        cursor.execute(sql)
        results = cursor.fetchall()
        
        print(f"预览前10条包含'工作年限: 3-5年'的记录:\n")
        
        for i, (job_id, job_description_detail, compare_result) in enumerate(results, 1):
            print(f"记录 {i}:")
            print(f"  ID: {job_id}")
            print(f"  描述: {job_description_detail[:150] if job_description_detail else 'None'}...")
            
            # 解析compare_result
            try:
                compare_data = json.loads(compare_result) if compare_result else {}
                print(f"  比较结果: {compare_data}")
            except:
                print(f"  比较结果: {compare_result}")
            
            # 检查是否包含目标字段
            if job_description_detail:
                target_patterns = ["三年以上", "至少拥有三年", "3年以上", " 3 年以上", "3 年及以上", "2 年以上"]
                found_patterns = [pattern for pattern in target_patterns if pattern in job_description_detail]
                if found_patterns:
                    print(f"  包含目标模式: {found_patterns}")
            
            print("-" * 80)
        
    except Exception as e:
        print(f"预览数据时出现错误: {str(e)}")
    finally:
        close_db_connection(cursor, connection)

if __name__ == "__main__":
    print("工作年限数据提取和替换工具")
    print("=" * 50)
    
    # 首先预览数据
    print("1. 预览符合条件的数据...")
    preview_data()
    

    print("\n2. 开始执行替换操作...")
    extract_work_experience_data()
   