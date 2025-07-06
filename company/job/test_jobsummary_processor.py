#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试智联招聘jobSummary多线程处理器

测试功能:
1. 测试数据库连接
2. 测试单条记录处理
3. 测试多线程处理性能
4. 测试错误处理
"""

import json
import unittest
from unittest.mock import Mock, patch
from company.job.multithread_jobsummary_processor import JobSummaryProcessor, ProcessConfig
import logging

# 配置测试日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestJobSummaryProcessor(unittest.TestCase):
    """测试JobSummaryProcessor类"""
    
    def setUp(self):
        """测试前准备"""
        self.processor = JobSummaryProcessor()
        self.config = ProcessConfig(
            batch_size=10,
            max_workers=2,
            train_type='3',
            table_name='zhilian_job'
        )
    
    def test_process_single_record_success(self):
        """测试单条记录处理成功"""
        # 准备测试数据
        processed_info = json.dumps({
            "jobTitle": "软件工程师",
            "company": "测试公司",
            "jobSummary": "原始工作描述"
        }, ensure_ascii=False)
        
        processed_jobsummary = "这是新的工作描述内容"
        
        record_data = (1, processed_info, processed_jobsummary)
        
        # 执行处理
        result = self.processor.process_single_record(record_data)
        
        # 验证结果
        self.assertIsNotNone(result)
        record_id, updated_info = result
        self.assertEqual(record_id, 1)
        
        # 验证JSON内容
        updated_data = json.loads(updated_info)
        self.assertEqual(updated_data['jobSummary'], processed_jobsummary)
        self.assertEqual(updated_data['jobTitle'], "软件工程师")
        self.assertEqual(updated_data['company'], "测试公司")
    
    def test_process_single_record_invalid_json(self):
        """测试处理无效JSON"""
        # 准备无效JSON数据
        record_data = (1, "invalid json", "新的工作描述")
        
        # 执行处理
        result = self.processor.process_single_record(record_data)
        
        # 验证结果为None（处理失败）
        self.assertIsNone(result)
        self.assertEqual(self.processor.error_count, 1)
    
    def test_process_single_record_empty_data(self):
        """测试处理空数据"""
        # 准备空数据
        record_data = (1, None, "新的工作描述")
        
        # 执行处理
        result = self.processor.process_single_record(record_data)
        
        # 验证结果为None（处理失败）
        self.assertIsNone(result)
    
    @patch('multithread_jobsummary_processor.JobSummaryProcessor.get_connection')
    def test_fetch_data_to_process(self, mock_get_connection):
        """测试获取待处理数据"""
        # 模拟数据库连接和查询结果
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_get_connection.return_value = mock_connection
        
        # 模拟查询结果
        mock_cursor.fetchall.return_value = [
            (1, '{"jobTitle": "工程师1"}', "描述1"),
            (2, '{"jobTitle": "工程师2"}', "描述2")
        ]
        
        # 执行查询
        data = self.processor.fetch_data_to_process(self.config)
        
        # 验证结果
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0][0], 1)
        self.assertEqual(data[1][0], 2)
        
        # 验证SQL查询被正确调用
        mock_cursor.execute.assert_called_once()
        call_args = mock_cursor.execute.call_args
        self.assertIn('train_type = %s', call_args[0][0])
        self.assertEqual(call_args[0][1], ('3',))
    
    @patch('multithread_jobsummary_processor.JobSummaryProcessor.get_connection')
    def test_batch_update_database(self, mock_get_connection):
        """测试批量更新数据库"""
        # 模拟数据库连接
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_get_connection.return_value = mock_connection
        
        # 准备测试数据
        results = [
            (1, '{"jobSummary": "更新后的描述1"}'),
            (2, '{"jobSummary": "更新后的描述2"}')
        ]
        
        # 执行批量更新
        updated_count = self.processor.batch_update_database(results, self.config)
        
        # 验证结果
        self.assertEqual(updated_count, 2)
        self.assertEqual(mock_cursor.execute.call_count, 2)
        mock_connection.commit.assert_called_once()
    
    def test_config_validation(self):
        """测试配置验证"""
        # 测试默认配置
        config = ProcessConfig()
        self.assertEqual(config.batch_size, 100)
        self.assertEqual(config.max_workers, 8)
        self.assertEqual(config.train_type, '3')
        self.assertEqual(config.table_name, 'zhilian_job')
        
        # 测试自定义配置
        custom_config = ProcessConfig(
            batch_size=50,
            max_workers=4,
            train_type='2',
            table_name='custom_table'
        )
        self.assertEqual(custom_config.batch_size, 50)
        self.assertEqual(custom_config.max_workers, 4)
        self.assertEqual(custom_config.train_type, '2')
        self.assertEqual(custom_config.table_name, 'custom_table')


def test_real_data_processing():
    """测试真实数据处理（需要数据库连接）"""
    logger.info("开始真实数据处理测试")
    
    try:
        # 创建处理器
        processor = JobSummaryProcessor()
        
        # 测试配置（小批量）
        test_config = ProcessConfig(
            batch_size=5,
            max_workers=2,
            train_type='3',
            table_name='zhilian_job'
        )
        
        # 先测试获取数据
        logger.info("测试获取待处理数据...")
        data = processor.fetch_data_to_process(test_config)
        logger.info(f"获取到 {len(data)} 条待处理数据")
        
        if len(data) > 0:
            # 测试处理单条记录
            logger.info("测试处理单条记录...")
            first_record = data[0]
            result = processor.process_single_record(first_record)
            
            if result:
                logger.info(f"单条记录处理成功: ID={result[0]}")
                # 验证JSON格式
                try:
                    updated_data = json.loads(result[1])
                    logger.info(f"更新后的jobSummary长度: {len(updated_data.get('jobSummary', ''))}")
                except json.JSONDecodeError as e:
                    logger.error(f"JSON解析失败: {e}")
            else:
                logger.warning("单条记录处理失败")
        
        logger.info("真实数据处理测试完成")
        
    except Exception as e:
        logger.error(f"真实数据处理测试失败: {str(e)}")


def test_performance_comparison():
    """测试性能对比（单线程 vs 多线程）"""
    logger.info("开始性能对比测试")
    
    try:
        processor = JobSummaryProcessor()
        
        # 小批量配置用于测试
        config = ProcessConfig(
            batch_size=10,
            max_workers=4,
            train_type='3',
            table_name='zhilian_job'
        )
        
        # 注意：这里只是演示，实际运行时请谨慎，避免重复更新数据
        logger.info("配置信息:")
        logger.info(f"  批次大小: {config.batch_size}")
        logger.info(f"  最大线程数: {config.max_workers}")
        logger.info(f"  训练类型: {config.train_type}")
        logger.info(f"  表名: {config.table_name}")
        
        # 获取待处理数据数量
        data = processor.fetch_data_to_process(config)
        logger.info(f"待处理数据量: {len(data)} 条")
        
        if len(data) == 0:
            logger.info("没有待处理数据，性能测试跳过")
            return
        
        # 提示用户
        logger.warning("注意：性能测试将实际修改数据库数据")
        logger.warning("如需执行，请取消注释下面的代码")
        
        # 取消注释下面的代码来执行实际的性能测试
        # logger.info("开始多线程处理测试...")
        # multi_stats = processor.process_data_multithread(config)
        # logger.info(f"多线程处理结果: {multi_stats}")
        
    except Exception as e:
        logger.error(f"性能对比测试失败: {str(e)}")


def main():
    """主测试函数"""
    logger.info("开始JobSummary处理器测试")
    logger.info("=" * 50)
    
    # 运行单元测试
    logger.info("1. 运行单元测试")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    logger.info("\n" + "=" * 50)
    
    # 运行真实数据测试
    logger.info("2. 运行真实数据测试")
    test_real_data_processing()
    
    logger.info("\n" + "=" * 50)
    
    # 运行性能对比测试
    logger.info("3. 运行性能对比测试")
    test_performance_comparison()
    
    logger.info("\n" + "=" * 50)
    logger.info("所有测试完成！")


if __name__ == "__main__":
    main()