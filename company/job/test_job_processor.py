#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智联招聘岗位处理器测试脚本

本脚本用于测试多线程岗位处理器的各项功能，
包括单元测试和集成测试。
"""

import json
import time
import unittest
from unittest.mock import Mock, patch

from company.job.multithread_job_processor import JobProcessor, JobProcessorConfig


class TestJobProcessor(unittest.TestCase):
    """岗位处理器单元测试"""
    
    def setUp(self):
        """测试前准备"""
        self.config = JobProcessorConfig()
        self.config.max_workers = 2  # 测试时使用较少线程
        self.config.batch_size = 5
        self.processor = JobProcessor(self.config)
    
    def test_config_initialization(self):
        """测试配置初始化"""
        self.assertEqual(len(self.config.bot_ids), 6)
        self.assertIn('7522851405448265762', self.config.bot_ids)
        self.assertEqual(self.config.train_type, '3')
        self.assertEqual(self.config.table_name, 'zhilian_job')
    
    def test_bot_id_rotation(self):
        """测试Bot ID轮询"""
        # 获取所有Bot ID，验证轮询
        bot_ids = []
        for i in range(len(self.config.bot_ids) * 2):  # 测试两轮
            bot_id = self.processor.get_next_bot_id()
            bot_ids.append(bot_id)
        
        # 验证前6个和后6个Bot ID相同（轮询效果）
        self.assertEqual(bot_ids[:6], bot_ids[6:12])
        
        # 验证包含所有配置的Bot ID
        unique_bot_ids = list(set(bot_ids[:6]))
        self.assertEqual(len(unique_bot_ids), 6)
        for bot_id in self.config.bot_ids:
            self.assertIn(bot_id, unique_bot_ids)
    
    def test_random_id_generation(self):
        """测试随机ID生成"""
        thread_name = "TestThread"
        user_id1, conversation_id1 = self.processor.generate_random_ids(thread_name)
        user_id2, conversation_id2 = self.processor.generate_random_ids(thread_name)
        
        # 验证ID格式
        self.assertTrue(user_id1.startswith(thread_name))
        self.assertTrue(user_id2.startswith(thread_name))
        
        # 验证ID唯一性
        self.assertNotEqual(user_id1, user_id2)
        self.assertNotEqual(conversation_id1, conversation_id2)
        
        # 验证conversation_id长度
        self.assertEqual(len(conversation_id1), 11)
        self.assertEqual(len(conversation_id2), 11)
    
    def test_timestamp_formatting(self):
        """测试时间戳格式化"""
        timestamp = 1640995200.123  # 2022-01-01 00:00:00.123
        formatted = self.processor.format_timestamp(timestamp)
        
        # 验证格式
        self.assertRegex(formatted, r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}')
        self.assertIn('2022-01-01', formatted)
    
    @patch('multithread_job_processor.requests.post')
    def test_coze_api_success(self, mock_post):
        """测试Coze API成功调用"""
        # 模拟成功响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'messages': [
                {
                    'type': 'answer',
                    'content': '这是一个测试响应内容'
                }
            ]
        }
        mock_post.return_value = mock_response
        
        # 调用API
        result, success = self.processor.call_coze_api(
            "测试输入", "test_bot_id", "test_user", "test_conversation"
        )
        
        # 验证结果
        self.assertTrue(success)
        self.assertEqual(result, '这是一个测试响应内容')
        
        # 验证API调用参数
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]['json']['bot_id'], 'test_bot_id')
        self.assertEqual(call_args[1]['json']['query'], '测试输入')
    
    @patch('multithread_job_processor.requests.post')
    def test_coze_api_failure(self, mock_post):
        """测试Coze API失败情况"""
        # 模拟失败响应
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = 'Internal Server Error'
        mock_post.return_value = mock_response
        
        # 调用API
        result, success = self.processor.call_coze_api(
            "测试输入", "test_bot_id", "test_user", "test_conversation"
        )
        
        # 验证结果
        self.assertFalse(success)
        self.assertIn('API调用失败', result)
    
    @patch('multithread_job_processor.requests.post')
    def test_coze_api_timeout(self, mock_post):
        """测试Coze API超时"""
        # 模拟超时
        mock_post.side_effect = requests.exceptions.Timeout()
        
        # 调用API
        result, success = self.processor.call_coze_api(
            "测试输入", "test_bot_id", "test_user", "test_conversation"
        )
        
        # 验证结果
        self.assertFalse(success)
        self.assertEqual(result, 'API调用超时')
    
    @patch('multithread_job_processor.get_db_connection')
    def test_fetch_unprocessed_data(self, mock_get_connection):
        """测试获取未处理数据"""
        # 模拟数据库连接和游标
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        # 模拟查询结果
        mock_cursor.fetchall.return_value = [
            (1, '{"jobTitle": "软件工程师", "company": "测试公司"}'),
            (2, '{"jobTitle": "产品经理", "company": "另一家公司"}')
        ]
        
        # 调用方法
        result = self.processor.fetch_unprocessed_data(5)
        
        # 验证结果
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][0], 1)
        self.assertIn('软件工程师', result[0][1])
        
        # 验证数据库调用
        mock_cursor.execute.assert_called()
        mock_connection.commit.assert_called()
    
    @patch('multithread_job_processor.get_db_connection')
    def test_update_result_to_db_success(self, mock_get_connection):
        """测试成功更新结果到数据库"""
        # 模拟数据库连接
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        # 调用方法
        result = self.processor.update_result_to_db(
            record_id=1,
            job_description_detail="处理结果",
            bot_id="test_bot",
            start_time="2024-01-01 10:00:00.000",
            end_time="2024-01-01 10:00:05.000",
            elapsed_time=5.0,
            success=True
        )
        
        # 验证结果
        self.assertTrue(result)
        
        # 验证数据库调用
        mock_cursor.execute.assert_called()
        mock_connection.commit.assert_called()
        
        # 验证更新参数
        call_args = mock_cursor.execute.call_args[0]
        self.assertIn('UPDATE zhilian_job', call_args[0])
        self.assertEqual(call_args[1][1], '2')  # process_type = '2' for success
    
    @patch('multithread_job_processor.get_db_connection')
    def test_update_result_to_db_failure(self, mock_get_connection):
        """测试更新失败结果到数据库"""
        # 模拟数据库连接
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        # 调用方法
        result = self.processor.update_result_to_db(
            record_id=1,
            job_description_detail="处理失败",
            bot_id="test_bot",
            start_time="2024-01-01 10:00:00.000",
            end_time="2024-01-01 10:00:05.000",
            elapsed_time=5.0,
            success=False
        )
        
        # 验证结果
        self.assertTrue(result)
        
        # 验证更新参数
        call_args = mock_cursor.execute.call_args[0]
        self.assertEqual(call_args[1][1], '3')  # process_type = '3' for failure
    
    @patch('multithread_job_processor.get_db_connection')
    def test_get_processing_stats(self, mock_get_connection):
        """测试获取处理统计信息"""
        # 模拟数据库连接
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        # 模拟查询结果
        mock_cursor.fetchone.side_effect = [
            (1000,),  # total_count
            (200,),   # pending_count
            (750,),   # processed_count
            (50,)     # failed_count
        ]
        
        # 调用方法
        stats = self.processor.get_processing_stats()
        
        # 验证结果
        self.assertEqual(stats['total_count'], 1000)
        self.assertEqual(stats['pending_count'], 200)
        self.assertEqual(stats['processed_count'], 750)
        self.assertEqual(stats['failed_count'], 50)
        self.assertEqual(stats['success_rate'], 75.0)


class TestJobProcessorIntegration:
    """集成测试类（需要真实数据库连接）"""
    
    def __init__(self):
        self.config = JobProcessorConfig()
        self.config.max_workers = 2
        self.config.batch_size = 3
        self.processor = JobProcessor(self.config)
    
    def test_real_database_connection(self):
        """测试真实数据库连接"""
        print("\n=== 测试真实数据库连接 ===")
        
        try:
            # 获取处理统计信息
            stats = self.processor.get_processing_stats()
            
            if stats:
                print(f"数据库连接成功！")
                print(f"总记录数: {stats['total_count']}")
                print(f"待处理记录数: {stats['pending_count']}")
                print(f"已处理记录数: {stats['processed_count']}")
                print(f"失败记录数: {stats['failed_count']}")
                print(f"成功率: {stats['success_rate']:.2f}%")
            else:
                print("无法获取统计信息")
                
        except Exception as e:
            print(f"数据库连接测试失败: {str(e)}")
    
    def test_fetch_sample_data(self):
        """测试获取样本数据"""
        print("\n=== 测试获取样本数据 ===")
        
        try:
            # 获取少量数据进行测试
            rows = self.processor.fetch_unprocessed_data(3)
            
            if rows:
                print(f"成功获取 {len(rows)} 条样本数据:")
                for i, (record_id, processed_info) in enumerate(rows[:2], 1):
                    print(f"  {i}. ID: {record_id}")
                    # 只显示前100个字符
                    info_preview = processed_info[:100] + "..." if len(processed_info) > 100 else processed_info
                    print(f"     内容: {info_preview}")
            else:
                print("没有找到待处理的数据")
                
        except Exception as e:
            print(f"获取样本数据失败: {str(e)}")
    
    def test_single_record_processing(self):
        """测试单条记录处理（模拟模式）"""
        print("\n=== 测试单条记录处理（模拟模式）===")
        
        # 使用模拟数据
        test_record_id = 99999
        test_processed_info = json.dumps({
            "jobTitle": "高级Python开发工程师",
            "company": "测试科技有限公司",
            "requirements": "3年以上Python开发经验，熟悉Django/Flask框架",
            "salary": "15k-25k",
            "location": "北京"
        }, ensure_ascii=False)
        
        print(f"测试记录ID: {test_record_id}")
        print(f"测试内容: {test_processed_info}")
        
        # 测试Bot ID轮询
        bot_id = self.processor.get_next_bot_id()
        print(f"分配的Bot ID: {bot_id}")
        
        # 测试随机ID生成
        user_id, conversation_id = self.processor.generate_random_ids("TestThread")
        print(f"用户ID: {user_id}")
        print(f"对话ID: {conversation_id}")
        
        print("注意: 这是模拟测试，不会实际调用API或更新数据库")


def run_unit_tests():
    """运行单元测试"""
    print("运行单元测试...")
    unittest.main(argv=[''], exit=False, verbosity=2)


def run_integration_tests():
    """运行集成测试"""
    print("\n" + "=" * 50)
    print("运行集成测试...")
    print("=" * 50)
    
    integration_tester = TestJobProcessorIntegration()
    
    # 运行各项集成测试
    integration_tester.test_real_database_connection()
    integration_tester.test_fetch_sample_data()
    integration_tester.test_single_record_processing()


def performance_test():
    """性能测试"""
    print("\n" + "=" * 50)
    print("性能测试")
    print("=" * 50)
    
    config = JobProcessorConfig()
    config.max_workers = 1  # 单线程测试
    config.batch_size = 5
    
    processor = JobProcessor(config)
    
    # 测试Bot ID轮询性能
    print("\n测试Bot ID轮询性能...")
    start_time = time.time()
    for _ in range(10000):
        processor.get_next_bot_id()
    end_time = time.time()
    print(f"10000次Bot ID轮询耗时: {end_time - start_time:.4f} 秒")
    
    # 测试随机ID生成性能
    print("\n测试随机ID生成性能...")
    start_time = time.time()
    for i in range(1000):
        processor.generate_random_ids(f"Thread-{i}")
    end_time = time.time()
    print(f"1000次随机ID生成耗时: {end_time - start_time:.4f} 秒")


if __name__ == "__main__":
    print("智联招聘岗位处理器测试")
    print("=" * 50)
    
    # 运行单元测试
    # run_unit_tests()
    
    # 运行集成测试
    run_integration_tests()
    
    # 运行性能测试
    performance_test()
    
    print("\n所有测试完成！")