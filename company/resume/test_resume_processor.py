#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简历处理器测试脚本

本脚本用于测试简历处理器的各项功能，包括：
1. 单元测试
2. 集成测试
3. 性能测试
"""

import json
import unittest
import tempfile
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# 导入公共数据库连接模块
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db_connection import get_db_connection, close_db_connection
from multithread_resume_processor import ResumeProcessor, ResumeProcessorConfig


class TestResumeProcessorConfig(unittest.TestCase):
    """测试配置类"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = ResumeProcessorConfig()
        
        self.assertEqual(config.max_workers, 4)
        self.assertEqual(config.batch_size, 100)
        self.assertEqual(config.train_type, '3')
        self.assertEqual(config.table_name, 'zhilian_resume')
        self.assertIsNotNone(config.db_config)
    
    def test_custom_config(self):
        """测试自定义配置"""
        config = ResumeProcessorConfig()
        config.max_workers = 8
        config.batch_size = 50
        config.train_type = None
        
        self.assertEqual(config.max_workers, 8)
        self.assertEqual(config.batch_size, 50)
        self.assertIsNone(config.train_type)


class TestResumeProcessor(unittest.TestCase):
    """测试简历处理器"""
    
    def setUp(self):
        """测试前准备"""
        self.config = ResumeProcessorConfig()
        # 使用临时日志文件
        self.temp_log = tempfile.NamedTemporaryFile(delete=False, suffix='.log')
        self.config.log_file = self.temp_log.name
        
        self.processor = ResumeProcessor(self.config)
    
    def tearDown(self):
        """测试后清理"""
        # 清理临时文件
        if os.path.exists(self.temp_log.name):
            os.unlink(self.temp_log.name)
    
    def test_process_city_label_with_prefix(self):
        """测试处理带有'现居'前缀的cityLabel"""
        processed_info = json.dumps({
            "name": "张三",
            "user": {
                "cityLabel": "现居成都 崇州市",
                "age": 25
            }
        }, ensure_ascii=False)
        
        success, result, error = self.processor.process_city_label(processed_info)
        
        self.assertTrue(success)
        self.assertIsNone(error)
        
        result_data = json.loads(result)
        self.assertEqual(result_data['user']['cityLabel'], "成都 崇州市")
        self.assertEqual(result_data['name'], "张三")
        self.assertEqual(result_data['user']['age'], 25)
    
    def test_process_city_label_without_prefix(self):
        """测试处理不带'现居'前缀的cityLabel"""
        processed_info = json.dumps({
            "name": "李四",
            "user": {
                "cityLabel": "北京 朝阳区",
                "age": 30
            }
        }, ensure_ascii=False)
        
        success, result, error = self.processor.process_city_label(processed_info)
        
        self.assertTrue(success)
        self.assertEqual(result, processed_info)  # 应该没有变化
        self.assertEqual(error, "无需处理")
    
    def test_process_city_label_no_field(self):
        """测试处理没有cityLabel字段的数据"""
        processed_info = json.dumps({
            "name": "王五",
            "user": {
                "age": 28
            }
        }, ensure_ascii=False)
        
        success, result, error = self.processor.process_city_label(processed_info)
        
        self.assertTrue(success)
        self.assertEqual(result, processed_info)
        self.assertEqual(error, "user节点中无cityLabel字段")
    
    def test_process_city_label_invalid_json(self):
        """测试处理无效JSON"""
        invalid_json = "{'name': '张三', 'cityLabel': '现居成都'}"  # 无效JSON
        
        success, result, error = self.processor.process_city_label(invalid_json)
        
        self.assertFalse(success)
        self.assertEqual(result, invalid_json)
        self.assertIn("JSON解析失败", error)
    
    def test_process_city_label_non_string(self):
        """测试cityLabel不是字符串的情况"""
        processed_info = json.dumps({
            "name": "赵六",
            "user": {
                "cityLabel": 123,  # 不是字符串
                "age": 35
            }
        }, ensure_ascii=False)
        
        success, result, error = self.processor.process_city_label(processed_info)
        
        self.assertTrue(success)
        self.assertEqual(result, processed_info)
        self.assertEqual(error, "cityLabel不是字符串类型")
    
    def test_process_city_label_no_user_node(self):
        """测试处理没有user节点的数据"""
        processed_info = json.dumps({
            "name": "测试用户",
            "age": 28
        }, ensure_ascii=False)
        
        success, result, error = self.processor.process_city_label(processed_info)
        
        self.assertTrue(success)
        self.assertEqual(result, processed_info)
        self.assertEqual(error, "无user节点")
    
    def test_process_city_label_user_not_dict(self):
        """测试user节点不是字典的情况"""
        processed_info = json.dumps({
            "name": "测试用户",
            "user": "not a dict",  # user不是字典
            "age": 28
        }, ensure_ascii=False)
        
        success, result, error = self.processor.process_city_label(processed_info)
        
        self.assertTrue(success)
        self.assertEqual(result, processed_info)
        self.assertEqual(error, "user节点不是字典类型")
    
    @patch('db_connection.get_db_connection')
    def test_get_connection(self, mock_get_connection):
        """测试数据库连接"""
        mock_conn = Mock()
        mock_get_connection.return_value = mock_conn
        
        conn = self.processor.get_connection()
        
        self.assertEqual(conn, mock_conn)
        mock_get_connection.assert_called_once()
    
    @patch('db_connection.get_db_connection')
    def test_fetch_resume_data_with_train_type(self, mock_get_connection):
        """测试获取指定训练类型的简历数据"""
        # 模拟数据库连接和查询
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (1, '{"name": "张三", "cityLabel": "现居成都"}'),
            (2, '{"name": "李四", "cityLabel": "现居北京"}')
        ]
        mock_get_connection.return_value = mock_conn
        
        result = self.processor.fetch_resume_data()
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][0], 1)
        self.assertIn("张三", result[0][1])
        
        # 验证SQL查询
        expected_sql = "SELECT id, processed_info FROM zhilian_resume WHERE train_type = %s"
        mock_cursor.execute.assert_called_with(expected_sql, ('3',))
    
    @patch('db_connection.get_db_connection')
    def test_fetch_resume_data_without_train_type(self, mock_get_connection):
        """测试获取所有简历数据"""
        # 设置为不过滤训练类型
        self.processor.config.train_type = None
        
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(1, '{"name": "张三"}')]
        mock_get_connection.return_value = mock_conn
        
        result = self.processor.fetch_resume_data()
        
        # 验证SQL查询
        expected_sql = "SELECT id, processed_info FROM zhilian_resume"
        mock_cursor.execute.assert_called_with(expected_sql, ())
    
    @patch('db_connection.get_db_connection')
    def test_update_resume_data(self, mock_get_connection):
        """测试更新简历数据"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.rowcount = 1
        mock_conn.cursor.return_value = mock_cursor
        mock_get_connection.return_value = mock_conn
        
        new_data = '{"name": "张三", "cityLabel": "成都"}'
        result = self.processor.update_resume_data(1, new_data)
        
        self.assertTrue(result)
        
        # 验证SQL更新
        expected_sql = "UPDATE zhilian_resume SET processed_info = %s WHERE id = %s"
        mock_cursor.execute.assert_called_with(expected_sql, (new_data, 1))
        mock_conn.commit.assert_called_once()
    
    @patch.object(ResumeProcessor, 'update_resume_data')
    def test_process_single_record_success(self, mock_update):
        """测试成功处理单条记录"""
        mock_update.return_value = True
        
        processed_info = json.dumps({
            "name": "张三",
            "user": {
                "cityLabel": "现居成都 崇州市"
            }
        }, ensure_ascii=False)
        
        success, error = self.processor.process_single_record(1, processed_info)
        
        self.assertTrue(success)
        self.assertIsNone(error)
        self.assertEqual(self.processor.processed_count, 1)
        
        # 验证调用了更新方法
        mock_update.assert_called_once()
    
    def test_process_single_record_no_change(self):
        """测试处理无需更改的记录"""
        processed_info = json.dumps({
            "name": "张三",
            "user": {
                "cityLabel": "成都 崇州市"  # 没有'现居'前缀
            }
        }, ensure_ascii=False)
        
        success, error = self.processor.process_single_record(1, processed_info)
        
        self.assertTrue(success)
        self.assertEqual(error, "无需更新")
        self.assertEqual(self.processor.processed_count, 1)
    
    @patch.object(ResumeProcessor, 'process_single_record')
    def test_process_batch(self, mock_process):
        """测试批次处理"""
        # 模拟处理结果
        mock_process.side_effect = [
            (True, None),
            (False, "处理失败"),
            (True, "无需更新")
        ]
        
        batch_data = [
            (1, '{"name": "张三", "user": {"cityLabel": "现居成都"}}'),
            (2, '{"name": "李四", "user": {"cityLabel": "现居北京"}}'),
            (3, '{"name": "王五", "user": {"cityLabel": "上海"}}')
        ]
        
        results = self.processor.process_batch(batch_data)
        
        self.assertEqual(len(results), 3)
        self.assertTrue(results[0][1])  # 第一条成功
        self.assertFalse(results[1][1])  # 第二条失败
        self.assertTrue(results[2][1])  # 第三条成功
        
        self.assertEqual(self.processor.failed_count, 1)
    
    @patch.object(ResumeProcessor, 'get_connection')
    def test_get_processing_stats(self, mock_get_conn):
        """测试获取处理统计信息"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (1000,)  # 总记录数
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        # 设置一些处理计数
        self.processor.processed_count = 800
        self.processor.failed_count = 50
        
        stats = self.processor.get_processing_stats()
        
        self.assertEqual(stats['total_count'], 1000)
        self.assertEqual(stats['processed_count'], 800)
        self.assertEqual(stats['failed_count'], 50)
        self.assertEqual(stats['success_rate'], 80.0)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.config = ResumeProcessorConfig()
        # 使用临时日志文件
        self.temp_log = tempfile.NamedTemporaryFile(delete=False, suffix='.log')
        self.config.log_file = self.temp_log.name
    
    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.temp_log.name):
            os.unlink(self.temp_log.name)
    
    @patch('db_connection.get_db_connection')
    def test_end_to_end_processing(self, mock_get_connection):
        """端到端处理测试"""
        # 模拟数据库连接
        mock_conn = Mock()
        mock_cursor = Mock()
        
        # 模拟查询结果
        test_data = [
            (1, '{"name": "张三", "user": {"cityLabel": "现居成都 崇州市", "age": 25}}'),
            (2, '{"name": "李四", "user": {"cityLabel": "现居北京 朝阳区", "age": 30}}'),
            (3, '{"name": "王五", "user": {"cityLabel": "上海 浦东区", "age": 28}}')
        ]
        
        # 设置查询返回
        mock_cursor.fetchall.return_value = test_data
        mock_cursor.fetchone.return_value = (len(test_data),)  # 总数查询
        mock_cursor.rowcount = 1  # 更新影响行数
        
        mock_conn.cursor.return_value = mock_cursor
        mock_get_connection.return_value = mock_conn
        
        # 创建处理器并执行
        processor = ResumeProcessor(self.config)
        processor.start_processing(limit=3)
        
        # 验证处理结果
        self.assertEqual(processor.processed_count, 3)
        self.assertEqual(processor.failed_count, 0)
        
        # 验证数据库更新调用
        # 应该有2次更新调用（前两条有'现居'前缀）
        update_calls = [call for call in mock_cursor.execute.call_args_list 
                       if 'UPDATE' in str(call)]
        self.assertEqual(len(update_calls), 2)


class TestPerformance(unittest.TestCase):
    """性能测试"""
    
    def test_city_label_processing_performance(self):
        """测试cityLabel处理性能"""
        config = ResumeProcessorConfig()
        temp_log = tempfile.NamedTemporaryFile(delete=False, suffix='.log')
        config.log_file = temp_log.name
        
        processor = ResumeProcessor(config)
        
        # 生成测试数据
        test_data = json.dumps({
            "name": "测试用户",
            "user": {
                "cityLabel": "现居成都 崇州市",
                "age": 25,
                "education": "本科",
                "experience": "3年工作经验"
            }
        }, ensure_ascii=False)
        
        import time
        
        # 测试处理1000次的时间
        start_time = time.time()
        for _ in range(1000):
            processor.process_city_label(test_data)
        end_time = time.time()
        
        processing_time = end_time - start_time
        rate = 1000 / processing_time
        
        print(f"\n性能测试结果:")
        print(f"  处理1000条记录耗时: {processing_time:.3f}秒")
        print(f"  处理速度: {rate:.2f}记录/秒")
        
        # 清理
        os.unlink(temp_log.name)
        
        # 性能要求：至少每秒处理1000条记录
        self.assertGreater(rate, 1000, "处理速度应该大于1000记录/秒")


def run_real_data_test():
    """真实数据测试（需要真实数据库连接）"""
    print("\n=== 真实数据测试 ===")
    print("注意：此测试需要真实的数据库连接")
    
    try:
        config = ResumeProcessorConfig()
        processor = ResumeProcessor(config)
        
        # 获取统计信息
        stats = processor.get_processing_stats()
        print(f"数据库连接成功")
        print(f"总记录数: {stats['total_count']}")
        
        # 获取样本数据
        sample_data = processor.fetch_resume_data(limit=3)
        print(f"\n样本数据 (前3条):")
        for i, (record_id, processed_info) in enumerate(sample_data, 1):
            print(f"  记录 {i}: ID={record_id}")
            try:
                data = json.loads(processed_info)
                city_label = data.get('cityLabel', '无')
                print(f"    cityLabel: {city_label}")
            except:
                print(f"    JSON解析失败")
        
        print("\n真实数据测试完成")
        
    except Exception as e:
        print(f"真实数据测试失败: {e}")
        print("请检查数据库连接配置")


def run_sample_processing():
    """样本处理测试"""
    print("\n=== 样本处理测试 ===")
    
    # 测试数据
    test_cases = [
        '{"name": "张三", "cityLabel": "现居成都 崇州市", "age": 25}',
        '{"name": "李四", "cityLabel": "现居北京 朝阳区", "age": 30}',
        '{"name": "王五", "cityLabel": "上海 浦东区", "age": 28}',
        '{"name": "赵六", "cityLabel": "现居深圳", "age": 32}',
        '{"name": "钱七", "age": 29}',  # 没有cityLabel
    ]
    
    config = ResumeProcessorConfig()
    temp_log = tempfile.NamedTemporaryFile(delete=False, suffix='.log')
    config.log_file = temp_log.name
    
    processor = ResumeProcessor(config)
    
    print("处理结果:")
    for i, test_data in enumerate(test_cases, 1):
        print(f"\n测试 {i}:")
        print(f"  原始数据: {test_data}")
        
        success, result, error = processor.process_city_label(test_data)
        
        if success:
            if result != test_data:
                result_data = json.loads(result)
                print(f"  处理后: cityLabel = '{result_data.get('cityLabel', '无')}'")
            else:
                print(f"  结果: {error or '无变化'}")
        else:
            print(f"  失败: {error}")
    
    # 清理
    os.unlink(temp_log.name)
    print("\n样本处理测试完成")


if __name__ == '__main__':
    print("简历处理器测试套件")
    print("=" * 40)
    
    # 运行单元测试
    print("\n1. 运行单元测试...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # 运行样本处理测试
    run_sample_processing()
    
    # 运行真实数据测试（可选）
    test_real_data = input("\n是否运行真实数据测试? (需要数据库连接) (y/n): ").strip().lower()
    if test_real_data in ['y', 'yes', '是']:
        run_real_data_test()
    
    print("\n所有测试完成!")