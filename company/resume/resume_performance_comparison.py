#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简历处理性能对比脚本

这个脚本用于测试简历处理程序在不同线程数和批次大小配置下的性能。
通过模拟API调用和数据库操作来评估最优配置。
"""

import json
import time
import threading
import statistics
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# 导入公共数据库连接模块
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db_connection import get_db_connection, close_db_connection
from multithread_resume_processor import ResumeProcessor, ResumeProcessorConfig


class ResumePerformanceTester:
    """简历处理性能测试器"""
    
    def __init__(self):
        self.test_results = []
        self.lock = threading.Lock()
    
    def generate_test_data(self, count=1000):
        """生成测试数据"""
        test_data = []
        
        city_templates = [
            "现居北京 朝阳区",
            "现居上海 浦东新区",
            "现居深圳 南山区",
            "现居广州 天河区",
            "现居杭州 西湖区",
            "现居成都 高新区",
            "现居武汉 洪山区",
            "现居南京 鼓楼区",
            "现居西安 雁塔区",
            "现居重庆 渝北区",
            "苏州 工业园区",  # 无'现居'前缀
            "天津 和平区",
            "青岛 市南区"
        ]
        
        for i in range(count):
            city_label = city_templates[i % len(city_templates)]
            
            data = {
                "id": i + 1,
                "name": f"测试用户{i+1}",
                "cityLabel": city_label,
                "age": 20 + (i % 40),
                "education": ["高中", "大专", "本科", "硕士", "博士"][i % 5],
                "experience": f"{i % 15}年",
                "industry": ["IT", "金融", "教育", "医疗", "制造"][i % 5]
            }
            
            test_data.append((i + 1, json.dumps(data, ensure_ascii=False)))
        
        return test_data
    
    def simulate_city_label_processing(self, processed_info):
        """模拟cityLabel处理"""
        try:
            # 模拟处理时间
            time.sleep(0.001 + (hash(processed_info) % 10) * 0.0001)  # 1-2ms
            
            data = json.loads(processed_info)
            
            if 'cityLabel' in data and isinstance(data['cityLabel'], str):
                city_label = data['cityLabel']
                if city_label.startswith('现居'):
                    data['cityLabel'] = city_label[2:].strip()
                    return True, json.dumps(data, ensure_ascii=False), None
                else:
                    return True, processed_info, "cityLabel不包含'现居'前缀"
            else:
                return True, processed_info, "未找到cityLabel字段或字段类型错误"
                
        except json.JSONDecodeError:
            return False, None, "JSON解析失败"
        except Exception as e:
            return False, None, str(e)
    
    def simulate_database_update(self, record_id, processed_info):
        """模拟数据库更新"""
        # 模拟数据库更新时间
        time.sleep(0.002 + (record_id % 5) * 0.0001)  # 2-2.5ms
        return True
    
    def process_single_record_simulation(self, record_id, processed_info):
        """模拟单条记录处理"""
        try:
            # 处理cityLabel
            success, result, error = self.simulate_city_label_processing(processed_info)
            
            if not success:
                return False, error
            
            # 如果数据有变化，模拟更新数据库
            if result != processed_info:
                update_success = self.simulate_database_update(record_id, result)
                if not update_success:
                    return False, "数据库更新失败"
            
            return True, error
            
        except Exception as e:
            return False, str(e)
    
    def test_single_thread_performance(self, test_data):
        """测试单线程性能"""
        print("\n测试单线程性能...")
        
        start_time = time.time()
        success_count = 0
        failed_count = 0
        
        for record_id, processed_info in test_data:
            success, error = self.process_single_record_simulation(record_id, processed_info)
            if success:
                success_count += 1
            else:
                failed_count += 1
        
        end_time = time.time()
        total_time = end_time - start_time
        
        result = {
            'type': '单线程',
            'threads': 1,
            'batch_size': len(test_data),
            'total_records': len(test_data),
            'success_count': success_count,
            'failed_count': failed_count,
            'total_time': total_time,
            'records_per_second': len(test_data) / total_time if total_time > 0 else 0,
            'success_rate': (success_count / len(test_data)) * 100 if test_data else 0
        }
        
        return result
    
    def test_multithread_performance(self, test_data, max_workers, batch_size):
        """测试多线程性能"""
        print(f"\n测试多线程性能 (线程数: {max_workers}, 批次大小: {batch_size})...")
        
        start_time = time.time()
        success_count = 0
        failed_count = 0
        
        # 分批处理
        batches = []
        for i in range(0, len(test_data), batch_size):
            batch = test_data[i:i + batch_size]
            batches.append(batch)
        
        def process_batch(batch):
            batch_success = 0
            batch_failed = 0
            
            for record_id, processed_info in batch:
                success, error = self.process_single_record_simulation(record_id, processed_info)
                if success:
                    batch_success += 1
                else:
                    batch_failed += 1
            
            return batch_success, batch_failed
        
        # 使用线程池处理
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_batch = {executor.submit(process_batch, batch): batch for batch in batches}
            
            for future in as_completed(future_to_batch):
                try:
                    batch_success, batch_failed = future.result()
                    success_count += batch_success
                    failed_count += batch_failed
                except Exception as e:
                    print(f"批次处理失败: {e}")
                    failed_count += len(future_to_batch[future])
        
        end_time = time.time()
        total_time = end_time - start_time
        
        result = {
            'type': '多线程',
            'threads': max_workers,
            'batch_size': batch_size,
            'total_records': len(test_data),
            'success_count': success_count,
            'failed_count': failed_count,
            'total_time': total_time,
            'records_per_second': len(test_data) / total_time if total_time > 0 else 0,
            'success_rate': (success_count / len(test_data)) * 100 if test_data else 0,
            'batches_count': len(batches)
        }
        
        return result
    
    def run_comprehensive_test(self, data_sizes=[100, 500, 1000], thread_counts=[1, 2, 4, 8, 16], batch_sizes=[10, 50, 100, 200]):
        """运行综合性能测试"""
        print("=" * 70)
        print("简历处理性能综合测试")
        print("=" * 70)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        all_results = []
        
        for data_size in data_sizes:
            print(f"\n{'='*50}")
            print(f"测试数据量: {data_size} 条记录")
            print(f"{'='*50}")
            
            # 生成测试数据
            test_data = self.generate_test_data(data_size)
            
            # 测试单线程性能（基准）
            single_thread_result = self.test_single_thread_performance(test_data)
            all_results.append(single_thread_result)
            
            print(f"单线程基准: {single_thread_result['records_per_second']:.2f} 记录/秒")
            
            # 测试不同线程数和批次大小的组合
            for threads in thread_counts:
                if threads == 1:  # 跳过单线程，已经测试过
                    continue
                
                for batch_size in batch_sizes:
                    if batch_size > data_size:  # 跳过过大的批次
                        continue
                    
                    try:
                        result = self.test_multithread_performance(test_data, threads, batch_size)
                        result['data_size'] = data_size
                        result['speedup'] = result['records_per_second'] / single_thread_result['records_per_second']
                        all_results.append(result)
                        
                        print(f"  {threads}线程, 批次{batch_size}: {result['records_per_second']:.2f} 记录/秒, "
                              f"加速比: {result['speedup']:.2f}x")
                        
                    except Exception as e:
                        print(f"  {threads}线程, 批次{batch_size}: 测试失败 - {e}")
        
        self.test_results = all_results
        return all_results
    
    def analyze_results(self):
        """分析测试结果"""
        if not self.test_results:
            print("没有测试结果可分析")
            return
        
        print("\n" + "=" * 70)
        print("性能分析报告")
        print("=" * 70)
        
        # 按数据量分组分析
        data_sizes = list(set(r.get('data_size', r['total_records']) for r in self.test_results))
        data_sizes.sort()
        
        for data_size in data_sizes:
            print(f"\n数据量: {data_size} 条记录")
            print("-" * 40)
            
            size_results = [r for r in self.test_results if r.get('data_size', r['total_records']) == data_size]
            
            # 找出最佳配置
            best_result = max(size_results, key=lambda x: x['records_per_second'])
            
            print(f"最佳配置:")
            print(f"  线程数: {best_result['threads']}")
            print(f"  批次大小: {best_result['batch_size']}")
            print(f"  处理速度: {best_result['records_per_second']:.2f} 记录/秒")
            print(f"  总耗时: {best_result['total_time']:.2f} 秒")
            print(f"  成功率: {best_result['success_rate']:.2f}%")
            
            if 'speedup' in best_result:
                print(f"  加速比: {best_result['speedup']:.2f}x")
        
        # 整体最佳配置
        print(f"\n整体最佳配置:")
        print("-" * 40)
        
        # 按处理速度排序
        sorted_results = sorted(self.test_results, key=lambda x: x['records_per_second'], reverse=True)
        top_5 = sorted_results[:5]
        
        for i, result in enumerate(top_5, 1):
            data_size = result.get('data_size', result['total_records'])
            speedup = result.get('speedup', 1.0)
            print(f"  {i}. {result['threads']}线程, 批次{result['batch_size']}, "
                  f"数据量{data_size}, 速度{result['records_per_second']:.2f}记录/秒, "
                  f"加速比{speedup:.2f}x")
    
    def generate_recommendations(self):
        """生成配置建议"""
        if not self.test_results:
            print("没有测试结果，无法生成建议")
            return
        
        print("\n" + "=" * 70)
        print("配置建议")
        print("=" * 70)
        
        # 分析线程数效果
        thread_performance = {}
        for result in self.test_results:
            threads = result['threads']
            if threads not in thread_performance:
                thread_performance[threads] = []
            thread_performance[threads].append(result['records_per_second'])
        
        print("\n线程数性能分析:")
        for threads in sorted(thread_performance.keys()):
            speeds = thread_performance[threads]
            avg_speed = statistics.mean(speeds)
            max_speed = max(speeds)
            print(f"  {threads}线程: 平均{avg_speed:.2f}记录/秒, 最高{max_speed:.2f}记录/秒")
        
        # 分析批次大小效果
        batch_performance = {}
        for result in self.test_results:
            if result['threads'] > 1:  # 只分析多线程结果
                batch_size = result['batch_size']
                if batch_size not in batch_performance:
                    batch_performance[batch_size] = []
                batch_performance[batch_size].append(result['records_per_second'])
        
        if batch_performance:
            print("\n批次大小性能分析:")
            for batch_size in sorted(batch_performance.keys()):
                speeds = batch_performance[batch_size]
                avg_speed = statistics.mean(speeds)
                max_speed = max(speeds)
                print(f"  批次{batch_size}: 平均{avg_speed:.2f}记录/秒, 最高{max_speed:.2f}记录/秒")
        
        # 生成具体建议
        print("\n具体建议:")
        
        # 找出最佳线程数
        best_thread_count = max(thread_performance.keys(), 
                               key=lambda x: statistics.mean(thread_performance[x]))
        
        print(f"1. 推荐线程数: {best_thread_count}")
        print(f"   理由: 在测试中表现最佳，平均处理速度最高")
        
        # 找出最佳批次大小
        if batch_performance:
            best_batch_size = max(batch_performance.keys(), 
                                 key=lambda x: statistics.mean(batch_performance[x]))
            print(f"\n2. 推荐批次大小: {best_batch_size}")
            print(f"   理由: 在多线程环境下表现最佳")
        
        # 资源使用建议
        print(f"\n3. 资源使用建议:")
        if best_thread_count <= 4:
            print(f"   - 适合中小型服务器或开发环境")
        elif best_thread_count <= 8:
            print(f"   - 适合中等配置的生产服务器")
        else:
            print(f"   - 适合高配置的生产服务器")
        
        print(f"   - 建议监控CPU和内存使用率")
        print(f"   - 建议监控数据库连接数")
        
        # 扩展性建议
        print(f"\n4. 扩展性建议:")
        print(f"   - 对于大数据量处理，考虑分批执行")
        print(f"   - 监控处理过程中的系统资源")
        print(f"   - 根据实际硬件配置调整参数")
    
    def save_results_to_file(self, filename=None):
        """保存结果到文件"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'resume_performance_test_{timestamp}.json'
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'test_time': datetime.now().isoformat(),
                    'results': self.test_results
                }, f, ensure_ascii=False, indent=2)
            
            print(f"\n测试结果已保存到: {filename}")
            
        except Exception as e:
            print(f"保存结果失败: {e}")


def main():
    """主函数"""
    print("简历处理性能测试工具")
    print("=" * 50)
    
    tester = ResumePerformanceTester()
    
    try:
        # 运行测试
        print("\n选择测试模式:")
        print("1. 快速测试 (小数据量)")
        print("2. 标准测试 (中等数据量)")
        print("3. 完整测试 (大数据量)")
        print("4. 自定义测试")
        
        choice = input("\n请选择 (1-4): ").strip()
        
        if choice == '1':
            # 快速测试
            results = tester.run_comprehensive_test(
                data_sizes=[100, 200],
                thread_counts=[1, 2, 4],
                batch_sizes=[10, 50]
            )
        
        elif choice == '2':
            # 标准测试
            results = tester.run_comprehensive_test(
                data_sizes=[500, 1000],
                thread_counts=[1, 2, 4, 8],
                batch_sizes=[50, 100, 200]
            )
        
        elif choice == '3':
            # 完整测试
            results = tester.run_comprehensive_test(
                data_sizes=[1000, 2000, 5000],
                thread_counts=[1, 2, 4, 8, 16],
                batch_sizes=[100, 200, 500]
            )
        
        elif choice == '4':
            # 自定义测试
            try:
                data_size = int(input("数据量: "))
                max_threads = int(input("最大线程数: "))
                max_batch = int(input("最大批次大小: "))
                
                thread_counts = list(range(1, max_threads + 1))
                batch_sizes = [10, 50, 100, 200, 500]
                batch_sizes = [b for b in batch_sizes if b <= max_batch]
                
                results = tester.run_comprehensive_test(
                    data_sizes=[data_size],
                    thread_counts=thread_counts,
                    batch_sizes=batch_sizes
                )
            except ValueError:
                print("输入无效，使用默认配置")
                results = tester.run_comprehensive_test()
        
        else:
            print("无效选择，使用默认配置")
            results = tester.run_comprehensive_test()
        
        # 分析结果
        tester.analyze_results()
        
        # 生成建议
        tester.generate_recommendations()
        
        # 保存结果
        save_choice = input("\n是否保存测试结果到文件? (y/N): ").strip().lower()
        if save_choice in ['y', 'yes']:
            tester.save_results_to_file()
        
        print("\n测试完成!")
        
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n测试过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()