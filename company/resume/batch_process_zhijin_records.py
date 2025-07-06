# -*- coding: utf-8 -*-
"""
批量处理智联简历记录
使用统一经历处理器替代process_remaining_zhijin_records.py
同时处理工作经历、项目经历和教育经历的"至今"数据
"""

import logging
from unified_experience_processor import UnifiedExperienceProcessor

def setup_logging():
    """
    配置日志
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('batch_process_zhijin_records.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def main():
    """
    主函数 - 批量处理智联简历记录
    """
    logger = setup_logging()
    
    logger.info("开始批量处理智联简历记录")
    logger.info("使用统一经历处理器处理工作经历、项目经历和教育经历的'至今'数据")
    
    try:
        # 创建统一处理器
        processor = UnifiedExperienceProcessor()
        
        # 处理train_type='3'的记录
        logger.info("处理train_type='3'的记录...")
        results = processor.process_resume_data_batch(train_type='3')
        
        # 输出处理结果
        logger.info("\n=== 处理结果统计 ===")
        logger.info(f"找到记录数: {results['total_found']}")
        logger.info(f"更新记录数: {results['total_updated']}")
        logger.info(f"错误记录数: {results['errors']}")
        
        if results['total_updated'] > 0:
            logger.info(f"成功更新了 {results['total_updated']} 条记录")
            logger.info("所有包含'至今'的工作经历、项目经历和教育经历已处理完成")
            logger.info("work_years字段已设置为'1'")
        else:
            logger.info("没有找到需要更新的记录")
        
        if results['errors'] > 0:
            logger.warning(f"处理过程中出现 {results['errors']} 个错误，请检查日志")
        
        logger.info("批量处理完成")
        
    except Exception as e:
        logger.error(f"批量处理过程中出现错误: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    
    return True

def process_other_train_types():
    """
    处理其他train_type的记录
    """
    logger = logging.getLogger(__name__)
    processor = UnifiedExperienceProcessor()
    
    # 可以处理其他train_type的记录
    train_types = ['1', '2', '4', '5']  # 根据需要调整
    
    for train_type in train_types:
        logger.info(f"\n处理train_type='{train_type}'的记录...")
        try:
            results = processor.process_resume_data_batch(train_type=train_type)
            logger.info(f"train_type='{train_type}' - 找到: {results['total_found']}, 更新: {results['total_updated']}, 错误: {results['errors']}")
        except Exception as e:
            logger.error(f"处理train_type='{train_type}'时出错: {e}")

if __name__ == "__main__":
    print("=== 批量处理智联简历记录 ===")
    print("使用统一经历处理器同时处理工作经历、项目经历和教育经历的'至今'数据")
    print("")
    
    # 询问用户要处理的类型
    choice = input("请选择处理类型:\n1. 仅处理train_type='3'的记录\n2. 处理所有train_type的记录\n请输入选择 (1 或 2): ")
    
    if choice == '1':
        success = main()
        if success:
            print("\n✅ 处理完成")
        else:
            print("\n❌ 处理失败，请检查日志")
    elif choice == '2':
        success = main()  # 先处理train_type='3'
        if success:
            print("\n继续处理其他train_type...")
            process_other_train_types()
            print("\n✅ 所有处理完成")
        else:
            print("\n❌ 处理失败，请检查日志")
    else:
        print("无效选择，退出程序")