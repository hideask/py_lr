#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智联招聘jobSummary处理器性能对比测试

本脚本用于对比单线程和多线程处理的性能差异，
帮助用户选择最优的配置参数。

注意: 此脚本仅用于性能测试，不会实际修改数据库数据
"""

import time
import json
import logging
from typing import Dict, List, Tuple
from company.job.multithread_jobsummary_processor import JobSummaryProcessor, ProcessConfig
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('performance_comparison.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PerformanceTester:
    """性能测试器"""
    
    def __init__(self):
        self.processor = JobSummaryProcessor()
        self.test_results = []
    
    def simulate_processing(self, data: List[Tuple], config: ProcessConfig, use_multithread: bool = True) -> Dict:
        """模拟处理过程（不实际更新数据库）"""
        start_time = time.time()
        
        processed_count = 0
        error_count = 0
        
        if use_multithread:
            # 模拟多线程处理
            from concurrent.futures import ThreadPoolExecutor, as_completed
            
            batch_size = config.batch_size
            max_workers = config.max_workers
            
            for i in range(0, len(data), batch_size):
                batch_data = data[i:i + batch_size]
                
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = [executor.submit(self._simulate_single_record, record) for record in batch_data]
                    
                    for future in as_completed(futures):
                        try:
                            result = future.result()
                            if result:
                                processed_count += 1
                            else:
                                error_count += 1
                        except Exception:
                            error_count += 1
        else:
            # 模拟单线程处理
            for record in data:
                try:
                    result = self._simulate_single_record(record)
                    if result:
                        processed_count += 1
                    else:
                        error_count += 1
                except Exception:
                    error_count += 1
        
        end_time = time.time()
        duration = end_time - start_time
        
        return {
            'total': len(data),
            'processed': processed_count,
            'errors': error_count,
            'duration_seconds': duration,
            'throughput': len(data) / duration if duration > 0 else 0
        }
    
    def _simulate_single_record(self, record_data: Tuple) -> bool:
        """模拟单条记录处理"""
        try:
            record_id, processed_info, processed_jobsummary = record_data
            
            # 模拟JSON解析和处理
            if isinstance(processed_info, str):
                info_data = json.loads(processed_info)
            else:
                info_data = processed_info
            
            # 模拟更新操作
            info_data['jobSummary'] = processed_jobsummary
            updated_info = json.dumps(info_data, ensure_ascii=False)
            
            # 模拟一些处理时间
            time.sleep(0.001)  # 1ms的模拟处理时间
            
            return True
        except Exception:
            return False
    
    def test_batch_sizes(self, data: List[Tuple], thread_count: int = 6) -> List[Dict]:
        """测试不同批次大小的性能"""
        logger.info(f"测试不同批次大小的性能（线程数: {thread_count}）")
        
        batch_sizes = [10, 20, 50, 100, 200]
        results = []
        
        for batch_size in batch_sizes:
            logger.info(f"测试批次大小: {batch_size}")
            
            config = ProcessConfig(
                batch_size=batch_size,
                max_workers=thread_count,
                train_type='3'
            )
            
            # 多线程测试
            multi_stats = self.simulate_processing(data, config, use_multithread=True)
            
            result = {
                'batch_size': batch_size,
                'thread_count': thread_count,
                'duration': multi_stats['duration_seconds'],
                'throughput': multi_stats['throughput'],
                'processed': multi_stats['processed'],
                'errors': multi_stats['errors']
            }
            
            results.append(result)
            logger.info(f"批次大小 {batch_size}: 耗时 {multi_stats['duration_seconds']:.2f}s, 吞吐量 {multi_stats['throughput']:.2f} 记录/秒")
        
        return results
    
    def test_thread_counts(self, data: List[Tuple], batch_size: int = 50) -> List[Dict]:
        """测试不同线程数量的性能"""
        logger.info(f"测试不同线程数量的性能（批次大小: {batch_size}）")
        
        thread_counts = [1, 2, 4, 6, 8, 10, 12]
        results = []
        
        for thread_count in thread_counts:
            logger.info(f"测试线程数量: {thread_count}")
            
            config = ProcessConfig(
                batch_size=batch_size,
                max_workers=thread_count,
                train_type='3'
            )
            
            if thread_count == 1:
                # 单线程测试
                stats = self.simulate_processing(data, config, use_multithread=False)
            else:
                # 多线程测试
                stats = self.simulate_processing(data, config, use_multithread=True)
            
            result = {
                'thread_count': thread_count,
                'batch_size': batch_size,
                'duration': stats['duration_seconds'],
                'throughput': stats['throughput'],
                'processed': stats['processed'],
                'errors': stats['errors'],
                'speedup': 0  # 将在后面计算
            }
            
            results.append(result)
            logger.info(f"线程数 {thread_count}: 耗时 {stats['duration_seconds']:.2f}s, 吞吐量 {stats['throughput']:.2f} 记录/秒")
        
        # 计算加速比
        single_thread_duration = results[0]['duration']
        for result in results:
            if single_thread_duration > 0:
                result['speedup'] = single_thread_duration / result['duration']
        
        return results
    
    def generate_test_data(self, count: int = 1000) -> List[Tuple]:
        """生成测试数据"""
        logger.info(f"生成 {count} 条测试数据")
        
        test_data = []
        for i in range(count):
            processed_info = json.dumps({
                "jobTitle": f"软件工程师{i}",
                "company": f"测试公司{i}",
                "jobSummary": f"原始工作描述{i}",
                "salary": f"{10 + i % 20}k-{15 + i % 25}k",
                "location": f"城市{i % 10}"
            }, ensure_ascii=False)
            
            processed_jobsummary = f"这是第{i}个职位的详细工作描述，包含了具体的工作内容和要求。" * (i % 3 + 1)
            
            test_data.append((i + 1, processed_info, processed_jobsummary))
        
        return test_data
    
    def save_results_to_csv(self, results: List[Dict], filename: str):
        """保存结果到CSV文件"""
        df = pd.DataFrame(results)
        df.to_csv(filename, index=False, encoding='utf-8')
        logger.info(f"结果已保存到 {filename}")
    
    def plot_performance_charts(self, batch_results: List[Dict], thread_results: List[Dict]):
        """绘制性能图表"""
        try:
            # 设置中文字体
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False
            
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
            
            # 1. 批次大小 vs 吞吐量
            batch_sizes = [r['batch_size'] for r in batch_results]
            batch_throughputs = [r['throughput'] for r in batch_results]
            
            ax1.plot(batch_sizes, batch_throughputs, 'b-o', linewidth=2, markersize=6)
            ax1.set_xlabel('批次大小')
            ax1.set_ylabel('吞吐量 (记录/秒)')
            ax1.set_title('批次大小 vs 处理吞吐量')
            ax1.grid(True, alpha=0.3)
            
            # 2. 线程数 vs 吞吐量
            thread_counts = [r['thread_count'] for r in thread_results]
            thread_throughputs = [r['throughput'] for r in thread_results]
            
            ax2.plot(thread_counts, thread_throughputs, 'r-s', linewidth=2, markersize=6)
            ax2.set_xlabel('线程数量')
            ax2.set_ylabel('吞吐量 (记录/秒)')
            ax2.set_title('线程数量 vs 处理吞吐量')
            ax2.grid(True, alpha=0.3)
            
            # 3. 线程数 vs 加速比
            speedups = [r['speedup'] for r in thread_results]
            
            ax3.plot(thread_counts, speedups, 'g-^', linewidth=2, markersize=6)
            ax3.plot(thread_counts, thread_counts, 'k--', alpha=0.5, label='理想加速比')
            ax3.set_xlabel('线程数量')
            ax3.set_ylabel('加速比')
            ax3.set_title('线程数量 vs 加速比')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
            
            # 4. 批次大小 vs 处理时间
            batch_durations = [r['duration'] for r in batch_results]
            
            ax4.bar(range(len(batch_sizes)), batch_durations, color='orange', alpha=0.7)
            ax4.set_xlabel('批次大小')
            ax4.set_ylabel('处理时间 (秒)')
            ax4.set_title('批次大小 vs 处理时间')
            ax4.set_xticks(range(len(batch_sizes)))
            ax4.set_xticklabels(batch_sizes)
            ax4.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig('performance_comparison.png', dpi=300, bbox_inches='tight')
            logger.info("性能图表已保存到 performance_comparison.png")
            
            # 显示图表（如果在支持的环境中）
            try:
                plt.show()
            except:
                logger.info("无法显示图表，但已保存到文件")
                
        except ImportError:
            logger.warning("matplotlib 未安装，跳过图表生成")
        except Exception as e:
            logger.error(f"生成图表时出错: {str(e)}")


def main():
    """主函数"""
    logger.info("智联招聘jobSummary处理器性能对比测试")
    logger.info("=" * 50)
    
    tester = PerformanceTester()
    
    try:
        # 1. 生成测试数据
        test_data = tester.generate_test_data(1000)  # 生成1000条测试数据
        
        # 2. 测试不同批次大小
        logger.info("\n开始批次大小性能测试...")
        batch_results = tester.test_batch_sizes(test_data, thread_count=6)
        
        # 3. 测试不同线程数量
        logger.info("\n开始线程数量性能测试...")
        thread_results = tester.test_thread_counts(test_data, batch_size=50)
        
        # 4. 保存结果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        tester.save_results_to_csv(batch_results, f'batch_size_results_{timestamp}.csv')
        tester.save_results_to_csv(thread_results, f'thread_count_results_{timestamp}.csv')
        
        # 5. 生成图表
        logger.info("\n生成性能图表...")
        tester.plot_performance_charts(batch_results, thread_results)
        
        # 6. 输出最优配置建议
        logger.info("\n" + "=" * 50)
        logger.info("性能测试结果分析")
        logger.info("=" * 50)
        
        # 找出最优批次大小
        best_batch = max(batch_results, key=lambda x: x['throughput'])
        logger.info(f"最优批次大小: {best_batch['batch_size']} (吞吐量: {best_batch['throughput']:.2f} 记录/秒)")
        
        # 找出最优线程数
        best_thread = max(thread_results, key=lambda x: x['throughput'])
        logger.info(f"最优线程数: {best_thread['thread_count']} (吞吐量: {best_thread['throughput']:.2f} 记录/秒)")
        
        # 计算多线程优势
        single_thread = thread_results[0]
        best_multithread = best_thread
        improvement = (best_multithread['throughput'] / single_thread['throughput'] - 1) * 100
        logger.info(f"多线程性能提升: {improvement:.1f}%")
        
        # 推荐配置
        logger.info("\n推荐配置:")
        logger.info(f"  批次大小: {best_batch['batch_size']}")
        logger.info(f"  线程数量: {best_thread['thread_count']}")
        logger.info(f"  预期吞吐量: {max(best_batch['throughput'], best_thread['throughput']):.2f} 记录/秒")
        
        logger.info("\n性能测试完成！")
        
    except Exception as e:
        logger.error(f"性能测试失败: {str(e)}")
        raise


if __name__ == "__main__":
    main()