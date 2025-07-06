#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简历处理主执行脚本

这个脚本提供了一个用户友好的界面来执行智联招聘简历数据的cityLabel处理。
它会提示用户确认操作，配置处理参数，并执行多线程数据处理。
"""

import os
import sys
import time
import signal
from datetime import datetime

# 导入公共数据库连接模块
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db_connection import get_db_connection, close_db_connection
from multithread_resume_processor import ResumeProcessor, ResumeProcessorConfig


class ResumeProcessingRunner:
    """简历处理运行器"""
    
    def __init__(self):
        self.processor = None
        self.start_time = None
        self.interrupted = False
        
        # 注册信号处理器
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        print("\n\n收到中断信号，正在安全停止...")
        self.interrupted = True
        if self.processor:
            print("等待当前批次处理完成...")
    
    def _print_banner(self):
        """打印横幅"""
        print("=" * 70)
        print("           智联招聘简历cityLabel处理程序")
        print("=" * 70)
        print(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("功能: 处理简历数据中的cityLabel字段，去除'现居'前缀")
        print("=" * 70)
    
    def _get_user_confirmation(self):
        """获取用户确认"""
        print("\n⚠️  重要提示:")
        print("   此操作将修改数据库中的简历数据")
        print("   建议在执行前备份相关数据")
        print("   处理过程中请勿强制终止程序")
        
        while True:
            confirm = input("\n是否继续执行? (y/N): ").strip().lower()
            if confirm in ['y', 'yes']:
                return True
            elif confirm in ['n', 'no', '']:
                return False
            else:
                print("请输入 y 或 n")
    
    def _configure_processing(self):
        """配置处理参数"""
        print("\n" + "-" * 50)
        print("配置处理参数")
        print("-" * 50)
        
        config = ResumeProcessorConfig()
        
        # 配置线程数
        while True:
            try:
                threads = input(f"线程数 (默认: {config.max_workers}): ").strip()
                if threads:
                    config.max_workers = int(threads)
                    if config.max_workers < 1 or config.max_workers > 32:
                        print("线程数应在1-32之间")
                        continue
                break
            except ValueError:
                print("请输入有效的数字")
        
        # 配置批次大小
        while True:
            try:
                batch = input(f"批次大小 (默认: {config.batch_size}): ").strip()
                if batch:
                    config.batch_size = int(batch)
                    if config.batch_size < 1 or config.batch_size > 1000:
                        print("批次大小应在1-1000之间")
                        continue
                break
            except ValueError:
                print("请输入有效的数字")
        
        # 配置训练类型
        train_type = input(f"训练类型 (默认: {config.train_type or '全部'}): ").strip()
        if train_type:
            config.train_type = train_type
        
        # 配置表名
        table_name = input(f"表名 (默认: {config.table_name}): ").strip()
        if table_name:
            config.table_name = table_name
        
        # 配置日志文件
        log_file = input(f"日志文件 (默认: {config.log_file}): ").strip()
        if log_file:
            config.log_file = log_file
        
        return config
    
    def _preview_data(self, processor):
        """预览待处理数据"""
        print("\n" + "-" * 50)
        print("数据预览")
        print("-" * 50)
        
        try:
            stats = processor.get_processing_stats()
            
            print(f"数据库表: {processor.config.table_name}")
            print(f"训练类型: {processor.config.train_type or '全部'}")
            print(f"总记录数: {stats['total_count']}")
            print(f"已处理: {stats['processed_count']}")
            print(f"待处理: {stats['total_count'] - stats['processed_count']}")
            
            if stats['total_count'] == 0:
                print("\n❌ 没有找到符合条件的记录")
                return False
            
            if stats['total_count'] == stats['processed_count']:
                print("\n✅ 所有记录都已处理完成")
                return False
            
            # 获取样本数据
            sample_data = processor.get_sample_data(limit=5)
            if sample_data:
                print(f"\n样本数据 (前{len(sample_data)}条):")
                for i, (record_id, processed_info) in enumerate(sample_data, 1):
                    try:
                        import json
                        data = json.loads(processed_info)
                        city_label = data.get('cityLabel', '无')
                        name = data.get('name', f'记录{record_id}')
                        print(f"  {i}. ID:{record_id}, 姓名:{name}, cityLabel:'{city_label}'")
                    except:
                        print(f"  {i}. ID:{record_id}, 数据解析失败")
            
            return True
            
        except Exception as e:
            print(f"获取数据预览失败: {e}")
            return False
    
    def _estimate_processing_time(self, processor):
        """估算处理时间"""
        print("\n" + "-" * 50)
        print("处理时间估算")
        print("-" * 50)
        
        try:
            stats = processor.get_processing_stats()
            remaining_count = stats['total_count'] - stats['processed_count']
            
            if remaining_count == 0:
                print("没有待处理的记录")
                return
            
            # 基于配置估算处理时间
            # 假设每条记录处理时间约0.01-0.05秒
            avg_time_per_record = 0.02
            
            # 考虑多线程加速
            thread_efficiency = min(processor.config.max_workers * 0.8, 8)  # 线程效率
            estimated_time = (remaining_count * avg_time_per_record) / thread_efficiency
            
            print(f"待处理记录: {remaining_count:,}")
            print(f"线程数: {processor.config.max_workers}")
            print(f"批次大小: {processor.config.batch_size}")
            print(f"预计批次数: {(remaining_count + processor.config.batch_size - 1) // processor.config.batch_size}")
            
            if estimated_time < 60:
                print(f"预计耗时: {estimated_time:.1f} 秒")
            elif estimated_time < 3600:
                print(f"预计耗时: {estimated_time/60:.1f} 分钟")
            else:
                print(f"预计耗时: {estimated_time/3600:.1f} 小时")
            
            print(f"预计处理速度: {remaining_count/estimated_time:.1f} 记录/秒")
            
        except Exception as e:
            print(f"时间估算失败: {e}")
    
    def _monitor_progress(self, processor):
        """监控处理进度"""
        print("\n" + "-" * 50)
        print("开始处理 (按 Ctrl+C 安全停止)")
        print("-" * 50)
        
        self.start_time = time.time()
        last_processed = 0
        last_time = self.start_time
        
        try:
            while not self.interrupted:
                time.sleep(5)  # 每5秒检查一次
                
                current_processed = processor.processed_count
                current_failed = processor.failed_count
                current_time = time.time()
                
                # 计算速度
                time_diff = current_time - last_time
                processed_diff = current_processed - last_processed
                
                if time_diff > 0:
                    current_speed = processed_diff / time_diff
                else:
                    current_speed = 0
                
                # 计算总体进度
                total_elapsed = current_time - self.start_time
                total_processed = current_processed + current_failed
                
                if total_elapsed > 0:
                    avg_speed = total_processed / total_elapsed
                else:
                    avg_speed = 0
                
                # 显示进度
                print(f"\r进度: 成功={current_processed}, 失败={current_failed}, "
                      f"当前速度={current_speed:.1f}/秒, 平均速度={avg_speed:.1f}/秒, "
                      f"耗时={total_elapsed:.0f}秒", end="", flush=True)
                
                last_processed = current_processed
                last_time = current_time
                
                # 检查是否完成
                if hasattr(processor, '_processing_complete') and processor._processing_complete:
                    break
        
        except KeyboardInterrupt:
            self.interrupted = True
        
        print()  # 换行
    
    def _show_final_results(self, processor):
        """显示最终结果"""
        print("\n" + "-" * 50)
        print("处理完成")
        print("-" * 50)
        
        end_time = time.time()
        total_time = end_time - self.start_time if self.start_time else 0
        
        print(f"总耗时: {total_time:.2f} 秒")
        print(f"成功处理: {processor.processed_count} 条")
        print(f"处理失败: {processor.failed_count} 条")
        
        total_processed = processor.processed_count + processor.failed_count
        if total_processed > 0:
            success_rate = (processor.processed_count / total_processed) * 100
            print(f"成功率: {success_rate:.2f}%")
            
            if total_time > 0:
                avg_speed = total_processed / total_time
                print(f"平均速度: {avg_speed:.2f} 记录/秒")
        
        # 显示日志文件位置
        if processor.config.log_file and os.path.exists(processor.config.log_file):
            log_size = os.path.getsize(processor.config.log_file)
            print(f"\n日志文件: {processor.config.log_file} ({log_size} 字节)")
        
        # 显示最终统计
        try:
            final_stats = processor.get_processing_stats()
            print(f"\n最终统计:")
            print(f"  数据库总记录: {final_stats['total_count']}")
            print(f"  已处理记录: {final_stats['processed_count']}")
            print(f"  处理成功率: {final_stats['success_rate']:.2f}%")
        except Exception as e:
            print(f"获取最终统计失败: {e}")
    
    def _cleanup(self):
        """清理资源"""
        if self.processor:
            try:
                # 关闭数据库连接等
                if hasattr(self.processor, 'cleanup'):
                    self.processor.cleanup()
            except Exception as e:
                print(f"清理资源时出错: {e}")
    
    def _show_recommendations(self, processor):
        """显示建议"""
        print("\n" + "-" * 50)
        print("建议")
        print("-" * 50)
        
        total_processed = processor.processed_count + processor.failed_count
        
        if processor.failed_count > 0:
            failure_rate = (processor.failed_count / total_processed) * 100
            if failure_rate > 5:
                print(f"⚠️  失败率较高 ({failure_rate:.1f}%)，建议检查:")
                print("   - 数据库连接是否稳定")
                print("   - 数据格式是否正确")
                print("   - 系统资源是否充足")
        
        if self.start_time:
            total_time = time.time() - self.start_time
            if total_time > 0 and total_processed > 0:
                speed = total_processed / total_time
                
                if speed < 10:
                    print(f"💡 处理速度较慢 ({speed:.1f}记录/秒)，建议:")
                    print("   - 增加线程数")
                    print("   - 增大批次大小")
                    print("   - 检查数据库性能")
                elif speed > 100:
                    print(f"✅ 处理速度良好 ({speed:.1f}记录/秒)")
        
        print("\n📋 后续操作建议:")
        print("   - 检查处理日志确认无误")
        print("   - 验证数据库中的更新结果")
        print("   - 备份处理后的数据")
        if processor.failed_count > 0:
            print("   - 分析失败记录并考虑重新处理")
    
    def run(self):
        """运行主程序"""
        try:
            # 打印横幅
            self._print_banner()
            
            # 获取用户确认
            if not self._get_user_confirmation():
                print("\n操作已取消")
                return
            
            # 配置处理参数
            config = self._configure_processing()
            
            # 创建处理器
            print("\n正在初始化处理器...")
            self.processor = ResumeProcessor(config)
            
            # 预览数据
            if not self._preview_data(self.processor):
                print("\n没有需要处理的数据，程序退出")
                return
            
            # 估算处理时间
            self._estimate_processing_time(self.processor)
            
            # 最后确认
            if not input("\n确认开始处理? (y/N): ").strip().lower() in ['y', 'yes']:
                print("\n操作已取消")
                return
            
            # 开始处理
            print("\n正在启动多线程处理...")
            
            # 在单独线程中启动处理
            import threading
            processing_thread = threading.Thread(
                target=self.processor.start_processing,
                daemon=True
            )
            processing_thread.start()
            
            # 监控进度
            self._monitor_progress(self.processor)
            
            # 等待处理完成
            processing_thread.join(timeout=1)
            
            # 显示最终结果
            self._show_final_results(self.processor)
            
            # 显示建议
            self._show_recommendations(self.processor)
            
        except KeyboardInterrupt:
            print("\n\n用户中断操作")
        except Exception as e:
            print(f"\n程序执行出错: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # 清理资源
            self._cleanup()
            print("\n程序结束")


def main():
    """主函数"""
    # 检查Python版本
    if sys.version_info < (3, 6):
        print("错误: 需要Python 3.6或更高版本")
        sys.exit(1)
    
    # 检查依赖
    try:
        import psycopg2
    except ImportError:
        print("错误: 缺少psycopg2依赖，请运行: pip install psycopg2-binary")
        sys.exit(1)
    
    # 运行程序
    runner = ResumeProcessingRunner()
    runner.run()


if __name__ == "__main__":
    main()