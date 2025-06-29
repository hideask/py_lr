# -*- coding: utf-8 -*-
"""
通用数据库处理器
提供统一的查询和更新方法，减少重复代码
"""

import psycopg2
import json
import logging
from typing import List, Dict, Any, Optional, Callable, Tuple
from abc import ABC, abstractmethod
from db_connection import DatabaseConnection, get_db_connection, close_db_connection


class BaseQueryProcessor(ABC):
    """
    基础查询处理器抽象类
    定义通用的查询和更新接口
    """
    
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        """
        初始化处理器
        
        Args:
            db_connection: 数据库连接实例，如果为None则使用默认连接
        """
        self.db_connection = db_connection or DatabaseConnection()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def get_connection(self):
        """获取数据库连接"""
        return self.db_connection.get_connection()
    
    def close_connection(self, cursor=None, connection=None):
        """关闭数据库连接"""
        self.db_connection.close_connection(cursor, connection)
    
    @abstractmethod
    def process_record(self, record: tuple) -> Optional[tuple]:
        """
        处理单条记录的抽象方法
        
        Args:
            record: 数据库记录元组
            
        Returns:
            处理后的结果元组，如果处理失败返回None
        """
        pass
    
    def batch_query_and_update(self, 
                              query_sql: str, 
                              update_sql: str,
                              query_params: tuple = None,
                              batch_size: int = 1000,
                              process_func: Optional[Callable] = None) -> int:
        """
        批量查询和更新数据
        
        Args:
            query_sql: 查询SQL语句
            update_sql: 更新SQL语句
            query_params: 查询参数
            batch_size: 批处理大小
            process_func: 自定义处理函数
            
        Returns:
            更新的记录数量
        """
        connection = None
        cursor = None
        updated_count = 0
        
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            # 执行查询
            if query_params:
                cursor.execute(query_sql, query_params)
            else:
                cursor.execute(query_sql)
            
            records = cursor.fetchall()
            self.logger.info(f"查询到 {len(records)} 条记录")
            
            # 批量处理记录
            batch_updates = []
            for record in records:
                try:
                    # 使用自定义处理函数或默认处理方法
                    if process_func:
                        result = process_func(record)
                    else:
                        result = self.process_record(record)
                    
                    if result:
                        batch_updates.append(result)
                        
                        # 达到批处理大小时执行更新
                        if len(batch_updates) >= batch_size:
                            updated_count += self._execute_batch_update(
                                cursor, update_sql, batch_updates
                            )
                            batch_updates.clear()
                            connection.commit()
                            
                except Exception as e:
                    self.logger.error(f"处理记录失败: {record[0] if record else 'unknown'}, 错误: {str(e)}")
                    continue
            
            # 处理剩余的记录
            if batch_updates:
                updated_count += self._execute_batch_update(
                    cursor, update_sql, batch_updates
                )
                connection.commit()
            
            self.logger.info(f"成功更新 {updated_count} 条记录")
            
        except Exception as e:
            self.logger.error(f"批量处理失败: {str(e)}")
            if connection:
                connection.rollback()
        finally:
            self.close_connection(cursor, connection)
            
        return updated_count
    
    def _execute_batch_update(self, cursor, update_sql: str, batch_data: List[tuple]) -> int:
        """
        执行批量更新
        
        Args:
            cursor: 数据库游标
            update_sql: 更新SQL语句
            batch_data: 批量数据
            
        Returns:
            更新的记录数量
        """
        updated_count = 0
        for data in batch_data:
            cursor.execute(update_sql, data)
            updated_count += 1
        return updated_count
    
    def simple_query(self, sql: str, params: tuple = None) -> List[tuple]:
        """
        简单查询方法
        
        Args:
            sql: SQL语句
            params: 查询参数
            
        Returns:
            查询结果列表
        """
        connection = None
        cursor = None
        results = []
        
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            
            results = cursor.fetchall()
            
        except Exception as e:
            self.logger.error(f"查询失败: {str(e)}")
        finally:
            self.close_connection(cursor, connection)
            
        return results
    
    def simple_update(self, sql: str, params: tuple = None) -> int:
        """
        简单更新方法
        
        Args:
            sql: SQL语句
            params: 更新参数
            
        Returns:
            影响的行数
        """
        connection = None
        cursor = None
        affected_rows = 0
        
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            
            affected_rows = cursor.rowcount
            connection.commit()
            
        except Exception as e:
            self.logger.error(f"更新失败: {str(e)}")
            if connection:
                connection.rollback()
        finally:
            self.close_connection(cursor, connection)
            
        return affected_rows


class JSONProcessor(BaseQueryProcessor):
    """
    JSON数据处理器
    专门处理包含JSON字段的数据库记录
    """
    
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        super().__init__(db_connection)
    
    def process_record(self, record: tuple) -> Optional[tuple]:
        """
        处理包含JSON数据的记录
        默认实现，子类可以重写
        
        Args:
            record: 数据库记录元组
            
        Returns:
            处理后的结果元组
        """
        try:
            record_id = record[0]
            json_data = record[1] if len(record) > 1 else None
            
            if json_data:
                # 如果是字符串，尝试解析为JSON
                if isinstance(json_data, str):
                    parsed_data = json.loads(json_data)
                else:
                    parsed_data = json_data
                
                # 处理JSON数据（子类可以重写此逻辑）
                processed_data = self.process_json_data(parsed_data)
                processed_json_str = json.dumps(processed_data, ensure_ascii=False)
                
                return (record_id, processed_json_str)
            
        except Exception as e:
            self.logger.error(f"处理JSON记录失败: {record[0] if record else 'unknown'}, 错误: {str(e)}")
        
        return None
    
    def process_json_data(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理JSON数据的方法，子类可以重写
        
        Args:
            json_data: 原始JSON数据
            
        Returns:
            处理后的JSON数据
        """
        # 默认返回原数据，子类可以重写实现具体的处理逻辑
        return json_data


class HTMLCleanProcessor(BaseQueryProcessor):
    """
    HTML清理处理器
    专门处理包含HTML标签的文本字段
    """
    
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        super().__init__(db_connection)
    
    def process_record(self, record: tuple) -> Optional[tuple]:
        """
        处理包含HTML的记录
        
        Args:
            record: 数据库记录元组 (id, html_content)
            
        Returns:
            处理后的结果元组 (id, cleaned_content)
        """
        try:
            record_id = record[0]
            html_content = record[1] if len(record) > 1 else None
            
            if html_content:
                cleaned_content = self.clean_html(html_content)
                return (record_id, cleaned_content)
            
        except Exception as e:
            self.logger.error(f"处理HTML记录失败: {record[0] if record else 'unknown'}, 错误: {str(e)}")
        
        return None
    
    def clean_html(self, text: str) -> str:
        """
        清理HTML标签和特殊字符
        
        Args:
            text: 包含HTML的文本
            
        Returns:
            清理后的纯文本
        """
        import html
        import re
        
        if not text:
            return ""
        
        # 解码HTML实体
        text = html.unescape(text)
        
        # 去除HTML标签
        text = re.sub(r"<[^>]+>", "", text)
        
        # 处理特殊字符
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


class CommonQueryBuilder:
    """
    通用查询构建器
    提供常用的SQL查询模板
    """
    
    @staticmethod
    def build_select_with_condition(table_name: str, 
                                   fields: List[str], 
                                   where_condition: str = None,
                                   limit: int = None) -> str:
        """
        构建带条件的SELECT语句
        
        Args:
            table_name: 表名
            fields: 字段列表
            where_condition: WHERE条件
            limit: 限制条数
            
        Returns:
            SQL语句
        """
        fields_str = ", ".join(fields)
        sql = f"SELECT {fields_str} FROM {table_name}"
        
        if where_condition:
            sql += f" WHERE {where_condition}"
        
        if limit:
            sql += f" LIMIT {limit}"
        
        return sql
    
    @staticmethod
    def build_update_by_id(table_name: str, 
                          update_fields: List[str], 
                          id_field: str = "id") -> str:
        """
        构建按ID更新的UPDATE语句
        
        Args:
            table_name: 表名
            update_fields: 要更新的字段列表
            id_field: ID字段名
            
        Returns:
            SQL语句
        """
        set_clause = ", ".join([f"{field} = %s" for field in update_fields])
        return f"UPDATE {table_name} SET {set_clause} WHERE {id_field} = %s"
    
    @staticmethod
    def build_insert(table_name: str, fields: List[str]) -> str:
        """
        构建INSERT语句
        
        Args:
            table_name: 表名
            fields: 字段列表
            
        Returns:
            SQL语句
        """
        fields_str = ", ".join(fields)
        placeholders = ", ".join(["%s"] * len(fields))
        return f"INSERT INTO {table_name} ({fields_str}) VALUES ({placeholders})"