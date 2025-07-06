import psycopg2
import json
from concurrent.futures import ThreadPoolExecutor
from db_connection import get_db_connection, close_db_connection

def compare_json_with_text(json_data, text_data):
    """比对JSON数据和文本内容，返回不在文本中的key-value对"""
    missing_data = {}
    
    def check_value_in_text(key, value, text):
        """检查值是否在文本中"""
        if key == "岗位描述" or key == "详细地址":  # 跳过岗位描述字段
            return True
        
        # 将文本转换为小写并去除所有空格，用于比对
        text_normalized = text.replace(' ', '').lower()
        
        def convert_salary_to_wan_format(salary_str):
            """将薪资范围转换为万元格式，如240000-250000转换为24-25万，0-0转换为面议，5000-5000转换为5000"""
            import re
            # 匹配薪资范围格式：数字-数字
            pattern = r'(\d+)-(\d+)'
            match = re.match(pattern, salary_str.strip())
            
            if match:
                min_salary = int(match.group(1))
                max_salary = int(match.group(2))
                
                # 特殊处理：0-0 转换为面议
                if min_salary == 0 and max_salary == 0:
                    return "面议"
                
                # 特殊处理：相同数值的范围，如5000-5000转换为5000，17600-17600转换为17600
                if min_salary == max_salary:
                    return str(min_salary)
                
                # 如果薪资大于等于10000，转换为万元格式
                if min_salary >= 10000 and max_salary >= 10000:
                    min_wan = min_salary / 10000
                    max_wan = max_salary / 10000
                    
                    # 格式化为合适的显示格式
                    if min_wan == int(min_wan):
                        min_str = str(int(min_wan))
                    else:
                        min_str = f"{min_wan:.1f}"
                    
                    if max_wan == int(max_wan):
                        max_str = str(int(max_wan))
                    else:
                        max_str = f"{max_wan:.1f}"
                    
                    return f"{min_str}-{max_str}万"
            
            return None
        
        if isinstance(value, str) and value.strip():
            # 特殊处理：学历不限不做匹配，直接返回True
            if value.strip() == "学历不限":
                return True
                
            value_normalized = value.replace(' ', '').lower()
            
            # 首先尝试普通比较
            if value_normalized in text_normalized:
                return True
            
            # 如果普通比较失败，且值看起来像薪资范围，尝试转换为万元格式
            wan_format = convert_salary_to_wan_format(value)
            if wan_format:
                wan_normalized = wan_format.replace(' ', '').lower()
                if wan_normalized in text_normalized:
                    return True
            
            # 如果是公司名称相关字段，尝试英文括号转中文括号后再比较
            if key in ["公司名称", "企业名称", "单位名称", "招聘单位"]:
                # 将英文括号转换为中文括号
                value_with_chinese_brackets = value.replace('(', '（').replace(')', '）')
                value_chinese_normalized = value_with_chinese_brackets.replace(' ', '').lower()
                if value_chinese_normalized in text_normalized:
                    return True
                
                # 同时尝试将文本中的英文括号转换为中文括号后比较
                text_with_chinese_brackets = text.replace('(', '（').replace(')', '）')
                text_chinese_normalized = text_with_chinese_brackets.replace(' ', '').lower()
                if value_normalized in text_chinese_normalized:
                    return True
            
            return False
        elif isinstance(value, (int, float)):
            value_normalized = str(value).replace(' ', '').lower()
            return value_normalized in text_normalized
        elif isinstance(value, list):
            # 对于列表，检查每个元素，返回不匹配的元素列表
            missing_items = []
            for item in value:
                if isinstance(item, str) and item.strip():
                    item_normalized = item.replace(' ', '').lower()
                    item_found = False
                    
                    # 首先尝试普通比较
                    if item_normalized in text_normalized:
                        item_found = True
                    else:
                        # 如果普通比较失败，尝试薪资格式转换
                        wan_format = convert_salary_to_wan_format(item)
                        if wan_format:
                            wan_normalized = wan_format.replace(' ', '').lower()
                            if wan_normalized in text_normalized:
                                item_found = True
                        
                        # 如果是福利待遇相关字段，尝试更灵活的匹配
                        if not item_found and key in ["福利待遇", "福利", "待遇", "员工福利"]:
                            # 尝试部分匹配，去掉常见的修饰词
                            item_core = item.replace('有', '').replace('提供', '').replace('享受', '')
                            item_core_normalized = item_core.replace(' ', '').lower()
                            if item_core_normalized in text_normalized:
                                item_found = True
                    
                    if not item_found:
                        missing_items.append(item)
            
            # 如果有不匹配的项，返回这些项；否则返回True表示全部匹配
            return missing_items if missing_items else True
        return True
    
    def traverse_json(data, prefix=""):
        """递归遍历JSON数据"""
        if isinstance(data, dict):
            for key, value in data.items():
                current_key = f"{prefix}.{key}" if prefix else key
                
                if isinstance(value, (dict, list)) and value:
                    # 对于列表类型，需要特殊处理check_value_in_text的返回值
                    if isinstance(value, list):
                        result = check_value_in_text(key, value, text_data)
                        if result is not True:  # 如果返回的不是True，说明有不匹配的项
                            if isinstance(result, list) and result:  # 返回的是不匹配项的列表
                                missing_data[current_key] = result
                            elif not result:  # 返回False表示完全不匹配
                                missing_data[current_key] = value
                    else:
                        traverse_json(value, current_key)
                else:
                    result = check_value_in_text(key, value, text_data)
                    if result is not True:
                        if isinstance(result, list) and result:  # 返回的是不匹配项的列表
                            missing_data[current_key] = result
                        elif not result:  # 返回False表示不匹配
                            missing_data[current_key] = value
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    traverse_json(item, f"{prefix}[{i}]")
                else:
                    if not check_value_in_text(f"item_{i}", item, text_data):
                        missing_data[f"{prefix}[{i}]"] = item
    
    traverse_json(json_data)
    return missing_data

def process_single_job(job_data):
    """处理单个工作记录"""
    job_id, job_processed_info_ch, job_description_detail = job_data
    connection = None
    cursor = None
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 解析JSON数据
        if job_processed_info_ch:
            try:
                json_data = json.loads(job_processed_info_ch)
            except json.JSONDecodeError as e:
                print(f"JSON解析失败 (id:{job_id}): {str(e)}")
                return
        else:
            print(f"job_processed_info_ch为空 (id:{job_id})")
            return
        
        # 确保job_description_detail不为空
        if not job_description_detail:
            print(f"job_description_detail为空 (id:{job_id})")
            return
        
        # 比对数据
        missing_data = compare_json_with_text(json_data, job_description_detail)
        
        # 更新compare_result字段
        if missing_data:
            compare_result = json.dumps(missing_data, ensure_ascii=False)
            cursor.execute(
                "UPDATE zhilian_job SET compare_result = %s WHERE id = %s", 
                (compare_result, job_id)
            )
            connection.commit()
            print(f"更新compare_result成功 (id:{job_id}): 发现{len(missing_data)}个不匹配项")
        else:
            # 如果没有不匹配的数据，清空compare_result字段
            cursor.execute(
                "UPDATE zhilian_job SET compare_result = NULL WHERE id = %s", 
                (job_id,)
            )
            connection.commit()
            print(f"数据完全匹配 (id:{job_id})")
            
    except Exception as ex:
        print(f"处理失败 (id:{job_id}): {str(ex)}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def compare_job_data(limit=None, max_workers=4):
    """比对zhilian_job表中的JSON数据和文本数据"""
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # 构建查询SQL
    sql = "SELECT id, job_processed_info_ch, job_description_detail FROM zhilian_job WHERE job_processed_info_ch IS NOT NULL and compare_result is not null"
    if limit:
        sql += f" LIMIT {limit}"
    
    cursor.execute(sql)
    jobs = cursor.fetchall()
    close_db_connection(cursor, connection)
    
    print(f"获取成功{len(jobs)}条数据，开始多线程处理...")
    
    # 使用线程池执行器进行多线程处理
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        futures = [executor.submit(process_single_job, job_data) for job_data in jobs]
        
        # 等待所有任务完成
        for future in futures:
            try:
                future.result()  # 获取结果，如果有异常会抛出
            except Exception as ex:
                print(f"线程执行异常: {str(ex)}")
    
    print("所有工作记录处理完成！")

def compare_job_data_single_thread(limit=None):
    """单线程版本的比对函数"""
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # 构建查询SQL
    sql = "SELECT id, job_processed_info_ch, job_description_detail FROM zhilian_job WHERE job_processed_info_ch IS NOT NULL AND job_description_detail IS NOT NULL"
    if limit:
        sql += f" LIMIT {limit}"
    
    cursor.execute(sql)
    jobs = cursor.fetchall()
    print(f"获取成功{len(jobs)}条数据")
    
    try:
        for job_id, job_processed_info_ch, job_description_detail in jobs:
            # 解析JSON数据
            if job_processed_info_ch:
                try:
                    json_data = json.loads(job_processed_info_ch)
                except json.JSONDecodeError as e:
                    print(f"JSON解析失败 (id:{job_id}): {str(e)}")
                    continue
            else:
                print(f"job_processed_info_ch为空 (id:{job_id})")
                continue
            
            # 确保job_description_detail不为空
            if not job_description_detail:
                print(f"job_description_detail为空 (id:{job_id})")
                continue
            
            # 比对数据
            missing_data = compare_json_with_text(json_data, job_description_detail)
            
            # 更新compare_result字段
            if missing_data:
                compare_result = json.dumps(missing_data, ensure_ascii=False)
                cursor.execute(
                    "UPDATE zhilian_job SET compare_result = %s WHERE id = %s", 
                    (compare_result, job_id)
                )
                connection.commit()
                print(f"更新compare_result成功 (id:{job_id}): 发现{len(missing_data)}个不匹配项")
            else:
                # 如果没有不匹配的数据，清空compare_result字段
                cursor.execute(
                    "UPDATE zhilian_job SET compare_result = NULL WHERE id = %s", 
                    (job_id,)
                )
                connection.commit()
                print(f"数据完全匹配 (id:{job_id})")
                
    except Exception as ex:
        print(f"处理异常: {str(ex)}")
    finally:
        close_db_connection(cursor, connection)

if __name__ == "__main__":
    # 使用示例
    
    # 多线程版本（推荐）
    print("开始多线程比对...")
    compare_job_data(limit=10000, max_workers=10)  # 限制处理10条记录，使用4个线程
    
    # 单线程版本
    # print("开始单线程比对...")
    # compare_job_data_single_thread(limit=10)  # 限制处理10条记录
    
    # 处理所有数据（谨慎使用）
    # compare_job_data()  # 处理所有符合条件的记录