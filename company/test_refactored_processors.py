# -*- coding: utf-8 -*-
"""
重构后处理器的测试文件
验证新架构的功能正确性
"""

import unittest
import json
import logging
from unittest.mock import Mock, patch, MagicMock
from common_db_processor import (
    BaseQueryProcessor, 
    JSONProcessor, 
    HTMLCleanProcessor, 
    CommonQueryBuilder
)
from refactored_processors import (
    JobProcessor, 
    ResumeProcessor, 
    DataSyncProcessor, 
    CompareProcessor
)
from db_connection import DatabaseConnection

# 配置测试日志
logging.basicConfig(level=logging.DEBUG)


class TestDatabaseConnection(unittest.TestCase):
    """测试数据库连接类"""
    
    def test_database_connection_init(self):
        """测试数据库连接初始化"""
        db = DatabaseConnection(
            dbname="test_db",
            user="test_user",
            password="test_password",
            host="localhost",
            port="5432"
        )
        
        self.assertEqual(db.dbname, "test_db")
        self.assertEqual(db.user, "test_user")
        self.assertEqual(db.password, "test_password")
        self.assertEqual(db.host, "localhost")
        self.assertEqual(db.port, "5432")
    
    @patch('psycopg2.connect')
    def test_get_connection(self, mock_connect):
        """测试获取数据库连接"""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        db = DatabaseConnection()
        connection = db.get_connection()
        
        self.assertEqual(connection, mock_connection)
        mock_connect.assert_called_once()
    
    def test_close_connection(self):
        """测试关闭数据库连接"""
        mock_cursor = Mock()
        mock_connection = Mock()
        
        DatabaseConnection.close_connection(mock_cursor, mock_connection)
        
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()


class TestCommonQueryBuilder(unittest.TestCase):
    """测试通用查询构建器"""
    
    def test_build_select_with_condition(self):
        """测试构建SELECT语句"""
        sql = CommonQueryBuilder.build_select_with_condition(
            table_name="test_table",
            fields=["id", "name", "email"],
            where_condition="status = 'active'",
            limit=100
        )
        
        expected = "SELECT id, name, email FROM test_table WHERE status = 'active' LIMIT 100"
        self.assertEqual(sql, expected)
    
    def test_build_select_without_condition(self):
        """测试构建无条件SELECT语句"""
        sql = CommonQueryBuilder.build_select_with_condition(
            table_name="test_table",
            fields=["id", "name"]
        )
        
        expected = "SELECT id, name FROM test_table"
        self.assertEqual(sql, expected)
    
    def test_build_update_by_id(self):
        """测试构建UPDATE语句"""
        sql = CommonQueryBuilder.build_update_by_id(
            table_name="test_table",
            update_fields=["name", "email", "status"]
        )
        
        expected = "UPDATE test_table SET name = %s, email = %s, status = %s WHERE id = %s"
        self.assertEqual(sql, expected)
    
    def test_build_insert(self):
        """测试构建INSERT语句"""
        sql = CommonQueryBuilder.build_insert(
            table_name="test_table",
            fields=["name", "email", "status"]
        )
        
        expected = "INSERT INTO test_table (name, email, status) VALUES (%s, %s, %s)"
        self.assertEqual(sql, expected)


class TestHTMLCleanProcessor(unittest.TestCase):
    """测试HTML清理处理器"""
    
    def setUp(self):
        self.processor = HTMLCleanProcessor()
    
    def test_clean_html_basic(self):
        """测试基本HTML清理"""
        html_text = "<p>Hello <b>World</b></p>"
        cleaned = self.processor.clean_html(html_text)
        self.assertEqual(cleaned, "Hello World")
    
    def test_clean_html_entities(self):
        """测试HTML实体清理"""
        html_text = "&lt;div&gt;Hello &amp; World&lt;/div&gt;"
        cleaned = self.processor.clean_html(html_text)
        self.assertEqual(cleaned, "<div>Hello & World</div>")
    
    def test_clean_html_special_chars(self):
        """测试特殊字符清理"""
        html_text = "Hello&#xa;World&#xd;Test"
        cleaned = self.processor.clean_html(html_text)
        self.assertEqual(cleaned, "Hello\nWorld\rTest")
    
    def test_clean_html_whitespace(self):
        """测试空白字符处理"""
        html_text = "  Hello    World  \n\n  Test  "
        cleaned = self.processor.clean_html(html_text)
        self.assertEqual(cleaned, "Hello World Test")
    
    def test_process_record(self):
        """测试记录处理"""
        record = (1, "<p>Hello <b>World</b></p>")
        result = self.processor.process_record(record)
        
        self.assertEqual(result, (1, "Hello World"))
    
    def test_process_record_empty(self):
        """测试空记录处理"""
        record = (1, None)
        result = self.processor.process_record(record)
        
        self.assertIsNone(result)


class TestJSONProcessor(unittest.TestCase):
    """测试JSON处理器"""
    
    def setUp(self):
        self.processor = JSONProcessor()
    
    def test_process_record_with_json_string(self):
        """测试处理JSON字符串记录"""
        json_data = '{"name": "test", "value": 123}'
        record = (1, json_data)
        
        result = self.processor.process_record(record)
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 1)
        # 验证JSON格式正确
        parsed_result = json.loads(result[1])
        self.assertEqual(parsed_result["name"], "test")
        self.assertEqual(parsed_result["value"], 123)
    
    def test_process_record_with_dict(self):
        """测试处理字典记录"""
        json_data = {"name": "test", "value": 123}
        record = (1, json_data)
        
        result = self.processor.process_record(record)
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 1)
        # 验证JSON格式正确
        parsed_result = json.loads(result[1])
        self.assertEqual(parsed_result["name"], "test")
        self.assertEqual(parsed_result["value"], 123)
    
    def test_process_record_invalid_json(self):
        """测试处理无效JSON"""
        record = (1, "invalid json")
        result = self.processor.process_record(record)
        
        self.assertIsNone(result)
    
    def test_process_json_data_default(self):
        """测试默认JSON数据处理"""
        data = {"key1": "value1", "key2": "value2"}
        result = self.processor.process_json_data(data)
        
        # 默认实现应该返回原数据
        self.assertEqual(result, data)


class TestJobProcessor(unittest.TestCase):
    """测试岗位处理器"""
    
    def setUp(self):
        self.processor = JobProcessor()
    
    def test_filter_fields(self):
        """测试字段过滤"""
        data = {
            "companyName": "Test Company",
            "salary60": "10000-15000",
            "unwanted_field": "should be removed",
            "staffCard": {
                "staffName": "John Doe",
                "unwanted_nested": "remove this"
            }
        }
        
        result = self.processor._filter_fields(data, self.processor.retain_fields)
        
        # 验证保留的字段
        self.assertEqual(result["companyName"], "Test Company")
        self.assertEqual(result["salary60"], "10000-15000")
        self.assertEqual(result["staffCard"]["staffName"], "John Doe")
        
        # 验证不需要的字段被过滤
        self.assertNotIn("unwanted_field", result)
        self.assertNotIn("unwanted_nested", result["staffCard"])
    
    def test_process_json_data(self):
        """测试JSON数据处理"""
        data = {
            "companyName": "Test Company",
            "salary60": "10000-15000",
            "unwanted_field": "should be removed"
        }
        
        result = self.processor.process_json_data(data)
        
        self.assertIn("companyName", result)
        self.assertIn("salary60", result)
        self.assertNotIn("unwanted_field", result)


class TestResumeProcessor(unittest.TestCase):
    """测试简历处理器"""
    
    def setUp(self):
        self.processor = ResumeProcessor()
    
    def test_filter_fields_by_template(self):
        """测试模板字段过滤"""
        data = {
            "user": {
                "name": "John Doe",
                "age": 30,
                "unwanted": "remove this"
            },
            "resume": {
                "skillTags": ["Python", "SQL"],
                "unwanted_section": "remove this"
            }
        }
        
        template = {
            "user": {
                "name": True,
                "age": True
            },
            "resume": {
                "skillTags": True
            }
        }
        
        result = self.processor._filter_fields_by_template(data, template)
        
        # 验证保留的字段
        self.assertEqual(result["user"]["name"], "John Doe")
        self.assertEqual(result["user"]["age"], 30)
        self.assertEqual(result["resume"]["skillTags"], ["Python", "SQL"])
        
        # 验证不需要的字段被过滤
        self.assertNotIn("unwanted", result["user"])
        self.assertNotIn("unwanted_section", result["resume"])
    
    def test_filter_array_fields(self):
        """测试数组字段过滤"""
        data = {
            "workExperiences": [
                {
                    "orgName": "Company A",
                    "jobTitle": "Developer",
                    "unwanted": "remove this"
                },
                {
                    "orgName": "Company B",
                    "jobTitle": "Senior Developer",
                    "unwanted": "remove this too"
                }
            ]
        }
        
        template = {
            "workExperiences": {
                "orgName": True,
                "jobTitle": True
            }
        }
        
        result = self.processor._filter_fields_by_template(data, template)
        
        # 验证数组处理正确
        self.assertEqual(len(result["workExperiences"]), 2)
        self.assertEqual(result["workExperiences"][0]["orgName"], "Company A")
        self.assertEqual(result["workExperiences"][1]["jobTitle"], "Senior Developer")
        
        # 验证不需要的字段被过滤
        self.assertNotIn("unwanted", result["workExperiences"][0])
        self.assertNotIn("unwanted", result["workExperiences"][1])


class TestBaseQueryProcessor(unittest.TestCase):
    """测试基础查询处理器"""
    
    def setUp(self):
        # 创建一个具体的实现类用于测试
        class TestProcessor(BaseQueryProcessor):
            def process_record(self, record):
                # 简单的测试处理逻辑
                return (record[0], f"processed_{record[1]}")
        
        self.processor = TestProcessor()
    
    @patch('psycopg2.connect')
    def test_simple_query(self, mock_connect):
        """测试简单查询"""
        # 模拟数据库连接和游标
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(1, 'test'), (2, 'data')]
        
        # 执行查询
        results = self.processor.simple_query("SELECT * FROM test_table")
        
        # 验证结果
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], (1, 'test'))
        self.assertEqual(results[1], (2, 'data'))
        
        # 验证调用
        mock_cursor.execute.assert_called_once_with("SELECT * FROM test_table")
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()
    
    @patch('psycopg2.connect')
    def test_simple_update(self, mock_connect):
        """测试简单更新"""
        # 模拟数据库连接和游标
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 5
        
        # 执行更新
        affected_rows = self.processor.simple_update(
            "UPDATE test_table SET status = %s", 
            ('active',)
        )
        
        # 验证结果
        self.assertEqual(affected_rows, 5)
        
        # 验证调用
        mock_cursor.execute.assert_called_once_with(
            "UPDATE test_table SET status = %s", 
            ('active',)
        )
        mock_connection.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_end_to_end_workflow(self):
        """测试端到端工作流程"""
        # 这里可以添加更复杂的集成测试
        # 例如测试完整的数据处理流程
        pass


def run_performance_test():
    """性能测试（可选）"""
    import time
    
    print("\n=== 性能测试 ===")
    
    # 测试HTML清理性能
    html_processor = HTMLCleanProcessor()
    test_html = "<p>Hello <b>World</b></p>" * 1000
    
    start_time = time.time()
    for _ in range(1000):
        html_processor.clean_html(test_html)
    end_time = time.time()
    
    print(f"HTML清理性能: {end_time - start_time:.4f}秒 (1000次操作)")
    
    # 测试JSON处理性能
    json_processor = JSONProcessor()
    test_data = {"key" + str(i): "value" + str(i) for i in range(100)}
    
    start_time = time.time()
    for _ in range(1000):
        json_processor.process_json_data(test_data)
    end_time = time.time()
    
    print(f"JSON处理性能: {end_time - start_time:.4f}秒 (1000次操作)")


if __name__ == '__main__':
    # 运行单元测试
    print("运行单元测试...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # 运行性能测试
    run_performance_test()
    
    print("\n所有测试完成！")