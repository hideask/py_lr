#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智联招聘岗位处理性能对比脚本

本脚本用于测试不同线程数和批次大小配置下的处理性能，
通过模拟处理过程（不实际调用API和修改数据库）来评估最优配置。
"""

import time
import threading
import random
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from multithread_job_processor import JobProcessor, JobProcessorConfig
import matplotlib.pyplot as plt
import pandas as pd


class PerformanceTestConfig:
    """性能测试配置"""
    
    def __init__(self):
        # 测试参数
        self.test_record_count = 1000  # 测试记录数量
        self.thread_counts = [1, 2, 4, 8, 16, 32]  # 测试的线程数
        self.batch_sizes = [10, 20, 50, 100]  # 测试的批次大小
        
        # 模拟参数
        self.simulate_api_delay = True  # 是否模拟API延迟
        self.min_api_delay = 1.0  # 最小API延迟(秒)
        self.max_api_delay = 3.0  # 最大API延迟(秒)
        self.api_success_rate = 0.95  # API成功率
        
        self.simulate_db_delay = True  # 是否模拟数据库延迟
        self.min_db_delay = 0.01  # 最小数据库延迟(秒)
        self.max_db_delay = 0.05  # 最大数据库延迟(秒)
        
        # 输出配置
        self.save_results = True  # 是否保存结果
        self.generate_charts = True  # 是否生成图表
        self.results_file = 'job_performance_results.json'
        self.charts_dir = 'performance_charts'


class MockJobProcessor:
    """模拟岗位处理器"""
    
    def __init__(self, config: JobProcessorConfig, test_config: PerformanceTestConfig):
        self.config = config
        self.test_config = test_config
        self.processed_count = 0
        self.failed_count = 0
        self.lock = threading.Lock()
        
        # 生成测试数据
        self.test_data = self._generate_test_data()
    
    def _generate_test_data(self):
        """生成测试数据"""
        test_data = []
        for i in range(self.test_config.test_record_count):
            processed_info = {
                "jobTitle": f"测试岗位 {i+1}",
                "company": f"测试公司 {i+1}",
                "salary": f"{random.randint(5, 50)}K-{random.randint(51, 100)}K",
                "location": random.choice(["北京", "上海", "深圳", "杭州", "广州"]),
                "requirements": f"岗位要求 {i+1}" * random.randint(10, 50)
            }
            test_data.append((i+1, json.dumps(processed_info, ensure_ascii=False)))
        return test_data
    
    def _simulate_api_call(self, processed_info):
        """模拟API调用"""
        if self.test_config.simulate_api_delay:
            delay = random.uniform(
                self.test_config.min_api_delay,
                self.test_config.max_api_delay
            )
            time.sleep(delay)
        
        # 模拟成功/失败
        if random.random() < self.test_config.api_success_rate:
            return f"处理结果: {processed_info[:100]}..."
        else:
            raise Exception("模拟API调用失败")
    
    def _simulate_db_update(self, record_id, result):
        """模拟数据库更新"""
        if self.test_config.simulate_db_delay:
            delay = random.uniform(
                self.test_config.min_db_delay,
                self.test_config.max_db_delay
            )
            time.sleep(delay)
        
        # 模拟数据库操作
        return True
    
    def process_single_record(self, record_id, processed_info):
        """处理单条记录"""
        try:
            # 模拟API调用
            result = self._simulate_api_call(processed_info)
            
            # 模拟数据库更新
            self._simulate_db_update(record_id, result)
            
            with self.lock:
                self.processed_count += 1
            
            return True, None
            
        except Exception as e:
            with self.lock:
                self.failed_count += 1
            return False, str(e)
    
    def process_batch(self, batch_data):
        """处理批次数据"""
        results = []
        for record_id, processed_info in batch_data:
            success, error = self.process_single_record(record_id, processed_info)
            results.append((record_id, success, error))
        return results
    
    def start_processing(self):
        """开始处理"""
        # 重置计数器
        self.processed_count = 0
        self.failed_count = 0
        
        # 分批处理
        batches = []
        for i in range(0, len(self.test_data), self.config.batch_size):
            batch = self.test_data[i:i + self.config.batch_size]
            batches.append(batch)
        
        # 多线程处理
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            futures = [executor.submit(self.process_batch, batch) for batch in batches]
            
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"批次处理失败: {e}")
    
    def get_stats(self):
        """获取统计信息"""
        total = self.processed_count + self.failed_count
        success_rate = (self.processed_count / total * 100) if total > 0 else 0
        
        return {
            'total_count': len(self.test_data),
            'processed_count': self.processed_count,
            'failed_count': self.failed_count,
            'success_rate': success_rate
        }


class PerformanceTester:
    """性能测试器"""
    
    def __init__(self, test_config: PerformanceTestConfig):
        self.test_config = test_config
        self.results = []
    
    def run_single_test(self, thread_count, batch_size):
        """运行单个测试"""
        print(f"\n测试配置: {thread_count}线程, {batch_size}批次大小")
        
        # 创建配置
        config = JobProcessorConfig()
        config.max_workers = thread_count
        config.batch_size = batch_size
        
        # 创建模拟处理器
        processor = MockJobProcessor(config, self.test_config)
        
        # 记录开始时间
        start_time = time.time()
        
        # 开始处理
        processor.start_processing()
        
        # 记录结束时间
        end_time = time.time()
        total_time = end_time - start_time
        
        # 获取统计信息
        stats = processor.get_stats()
        
        # 计算性能指标
        throughput = stats['processed_count'] / total_time if total_time > 0 else 0
        avg_time_per_record = total_time / stats['total_count'] if stats['total_count'] > 0 else 0
        
        result = {
            'thread_count': thread_count,
            'batch_size': batch_size,
            'total_time': total_time,
            'throughput': throughput,
            'avg_time_per_record': avg_time_per_record,
            'processed_count': stats['processed_count'],
            'failed_count': stats['failed_count'],
            'success_rate': stats['success_rate'],
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"  处理时间: {total_time:.2f}秒")
        print(f"  吞吐量: {throughput:.2f}记录/秒")
        print(f"  成功率: {stats['success_rate']:.2f}%")
        
        return result
    
    def run_all_tests(self):
        """运行所有测试"""
        print("开始性能测试...")
        print(f"测试记录数: {self.test_config.test_record_count}")
        print(f"线程数配置: {self.test_config.thread_counts}")
        print(f"批次大小配置: {self.test_config.batch_sizes}")
        
        total_tests = len(self.test_config.thread_counts) * len(self.test_config.batch_sizes)
        current_test = 0
        
        for thread_count in self.test_config.thread_counts:
            for batch_size in self.test_config.batch_sizes:
                current_test += 1
                print(f"\n进度: {current_test}/{total_tests}")
                
                result = self.run_single_test(thread_count, batch_size)
                self.results.append(result)
                
                # 短暂休息
                time.sleep(1)
        
        print("\n所有测试完成!")
    
    def analyze_results(self):
        """分析结果"""
        if not self.results:
            print("没有测试结果可分析")
            return
        
        print("\n" + "=" * 60)
        print("性能分析结果")
        print("=" * 60)
        
        # 转换为DataFrame
        df = pd.DataFrame(self.results)
        
        # 找到最佳配置
        best_throughput = df.loc[df['throughput'].idxmax()]
        best_time = df.loc[df['total_time'].idxmin()]
        best_success_rate = df.loc[df['success_rate'].idxmax()]
        
        print(f"\n最佳吞吐量配置:")
        print(f"  线程数: {best_throughput['thread_count']}, 批次大小: {best_throughput['batch_size']}")
        print(f"  吞吐量: {best_throughput['throughput']:.2f} 记录/秒")
        print(f"  处理时间: {best_throughput['total_time']:.2f} 秒")
        
        print(f"\n最快处理时间配置:")
        print(f"  线程数: {best_time['thread_count']}, 批次大小: {best_time['batch_size']}")
        print(f"  处理时间: {best_time['total_time']:.2f} 秒")
        print(f"  吞吐量: {best_time['throughput']:.2f} 记录/秒")
        
        print(f"\n最佳成功率配置:")
        print(f"  线程数: {best_success_rate['thread_count']}, 批次大小: {best_success_rate['batch_size']}")
        print(f"  成功率: {best_success_rate['success_rate']:.2f}%")
        print(f"  吞吐量: {best_success_rate['throughput']:.2f} 记录/秒")
        
        # 线程数影响分析
        print(f"\n线程数影响分析:")
        thread_analysis = df.groupby('thread_count').agg({
            'throughput': 'mean',
            'total_time': 'mean',
            'success_rate': 'mean'
        }).round(2)
        
        for thread_count, row in thread_analysis.iterrows():
            print(f"  {thread_count}线程: 平均吞吐量 {row['throughput']:.2f}, 平均时间 {row['total_time']:.2f}s, 平均成功率 {row['success_rate']:.2f}%")
        
        # 批次大小影响分析
        print(f"\n批次大小影响分析:")
        batch_analysis = df.groupby('batch_size').agg({
            'throughput': 'mean',
            'total_time': 'mean',
            'success_rate': 'mean'
        }).round(2)
        
        for batch_size, row in batch_analysis.iterrows():
            print(f"  批次{batch_size}: 平均吞吐量 {row['throughput']:.2f}, 平均时间 {row['total_time']:.2f}s, 平均成功率 {row['success_rate']:.2f}%")
        
        return df
    
    def generate_charts(self, df):
        """生成性能图表"""
        if not self.test_config.generate_charts:
            return
        
        import os
        os.makedirs(self.test_config.charts_dir, exist_ok=True)
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 1. 吞吐量热力图
        plt.figure(figsize=(12, 8))
        pivot_throughput = df.pivot(index='thread_count', columns='batch_size', values='throughput')
        plt.subplot(2, 2, 1)
        plt.imshow(pivot_throughput.values, cmap='YlOrRd', aspect='auto')
        plt.colorbar(label='吞吐量 (记录/秒)')
        plt.title('吞吐量热力图')
        plt.xlabel('批次大小')
        plt.ylabel('线程数')
        plt.xticks(range(len(pivot_throughput.columns)), pivot_throughput.columns)
        plt.yticks(range(len(pivot_throughput.index)), pivot_throughput.index)
        
        # 2. 处理时间对比
        plt.subplot(2, 2, 2)
        for batch_size in self.test_config.batch_sizes:
            subset = df[df['batch_size'] == batch_size]
            plt.plot(subset['thread_count'], subset['total_time'], marker='o', label=f'批次{batch_size}')
        plt.title('处理时间 vs 线程数')
        plt.xlabel('线程数')
        plt.ylabel('处理时间 (秒)')
        plt.legend()
        plt.grid(True)
        
        # 3. 吞吐量对比
        plt.subplot(2, 2, 3)
        for batch_size in self.test_config.batch_sizes:
            subset = df[df['batch_size'] == batch_size]
            plt.plot(subset['thread_count'], subset['throughput'], marker='s', label=f'批次{batch_size}')
        plt.title('吞吐量 vs 线程数')
        plt.xlabel('线程数')
        plt.ylabel('吞吐量 (记录/秒)')
        plt.legend()
        plt.grid(True)
        
        # 4. 成功率对比
        plt.subplot(2, 2, 4)
        for batch_size in self.test_config.batch_sizes:
            subset = df[df['batch_size'] == batch_size]
            plt.plot(subset['thread_count'], subset['success_rate'], marker='^', label=f'批次{batch_size}')
        plt.title('成功率 vs 线程数')
        plt.xlabel('线程数')
        plt.ylabel('成功率 (%)')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        chart_file = f"{self.test_config.charts_dir}/performance_comparison.png"
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"\n图表已保存到: {chart_file}")
    
    def save_results(self):
        """保存结果"""
        if not self.test_config.save_results or not self.results:
            return
        
        result_data = {
            'test_config': {
                'test_record_count': self.test_config.test_record_count,
                'thread_counts': self.test_config.thread_counts,
                'batch_sizes': self.test_config.batch_sizes,
                'simulate_api_delay': self.test_config.simulate_api_delay,
                'api_success_rate': self.test_config.api_success_rate
            },
            'results': self.results,
            'test_time': datetime.now().isoformat()
        }
        
        with open(self.test_config.results_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n结果已保存到: {self.test_config.results_file}")
    
    def get_recommendations(self, df):
        """获取配置建议"""
        print("\n" + "=" * 60)
        print("配置建议")
        print("=" * 60)
        
        # 基于不同目标的建议
        best_throughput = df.loc[df['throughput'].idxmax()]
        best_balance = df.loc[(df['throughput'] * df['success_rate'] / 100).idxmax()]
        
        print(f"\n1. 追求最大吞吐量:")
        print(f"   推荐配置: {best_throughput['thread_count']}线程, {best_throughput['batch_size']}批次")
        print(f"   预期性能: {best_throughput['throughput']:.2f}记录/秒")
        
        print(f"\n2. 平衡性能和稳定性:")
        print(f"   推荐配置: {best_balance['thread_count']}线程, {best_balance['batch_size']}批次")
        print(f"   预期性能: {best_balance['throughput']:.2f}记录/秒, {best_balance['success_rate']:.2f}%成功率")
        
        # 资源使用建议
        print(f"\n3. 资源使用建议:")
        if best_throughput['thread_count'] <= 8:
            print(f"   当前最优配置对系统资源要求适中")
        else:
            print(f"   当前最优配置需要较多系统资源，请确保服务器配置充足")
        
        print(f"\n4. 生产环境建议:")
        print(f"   - 建议从较小的线程数开始，逐步增加")
        print(f"   - 监控系统资源使用情况")
        print(f"   - 考虑API限流和数据库连接池大小")
        print(f"   - 设置合适的超时和重试机制")


def main():
    """主函数"""
    print("智联招聘岗位处理性能测试")
    print("=" * 40)
    
    # 创建测试配置
    test_config = PerformanceTestConfig()
    
    # 显示测试配置
    print(f"\n测试配置:")
    print(f"  测试记录数: {test_config.test_record_count}")
    print(f"  线程数范围: {test_config.thread_counts}")
    print(f"  批次大小范围: {test_config.batch_sizes}")
    print(f"  模拟API延迟: {test_config.simulate_api_delay}")
    print(f"  API成功率: {test_config.api_success_rate * 100}%")
    
    # 确认开始测试
    confirm = input("\n是否开始性能测试? (y/n): ").strip().lower()
    if confirm not in ['y', 'yes', '是']:
        print("测试取消")
        return
    
    try:
        # 创建测试器
        tester = PerformanceTester(test_config)
        
        # 运行测试
        start_time = time.time()
        tester.run_all_tests()
        total_test_time = time.time() - start_time
        
        print(f"\n总测试时间: {total_test_time:.2f}秒")
        
        # 分析结果
        df = tester.analyze_results()
        
        # 生成图表
        if df is not None:
            try:
                tester.generate_charts(df)
            except ImportError:
                print("\n注意: 无法生成图表，请安装 matplotlib")
            except Exception as e:
                print(f"\n生成图表失败: {e}")
        
        # 保存结果
        tester.save_results()
        
        # 获取建议
        if df is not None:
            tester.get_recommendations(df)
        
        print("\n性能测试完成!")
        
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n测试过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()