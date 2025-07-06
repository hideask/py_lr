# -*- coding: utf-8 -*-
"""
数据库处理器使用示例
展示如何使用抽象处理器处理不同的表
"""

from abstract_db_processor import DatabaseProcessor, TableConfig, ResumeProcessor
from typing import Dict


class CustomProcessor(DatabaseProcessor):
    """自定义处理器示例"""
    
    def __init__(self):
        # 数据库配置
        db_config = {
            "dbname": "yhaimg",
            "user": "yhaimg",
            "password": "Zq*6^pD6g2%JJ!z8",
            "host": "172.31.255.227",
            "port": "5588"
        }
        super().__init__(db_config)
    
    def process_job_table(self, batch_size: int = 1000):
        """处理岗位表示例"""
        config = TableConfig(
            table_name="zhilian_job",  # 岗位表名
            json_source_field="processed_info",  # JSON源字段
            description_field="job_description_detail",  # 描述字段
            json_target_field="processed_info_ch",  # 中文JSON目标字段
            train_data_field="train_data_ch",  # 训练数据字段
            system_field="system_ch",
            context_field="context_ch",
            target_field="target_ch",
            batch_size=batch_size
        )
        
        def system_generator(data: Dict) -> str:
            return "你是一个专业的岗位分析助手，请根据提供的岗位信息生成简洁的职位描述。"
        
        def context_generator(data: Dict) -> str:
            # 提取岗位关键信息作为上下文
            context_parts = []
            
            if 'position_name' in data:
                context_parts.append(f"职位：{data['position_name']}")
            if 'company_name' in data:
                context_parts.append(f"公司：{data['company_name']}")
            if 'salary_range' in data:
                context_parts.append(f"薪资：{data['salary_range']}")
            if 'work_location' in data:
                context_parts.append(f"地点：{data['work_location']}")
            if 'experience_requirement' in data:
                context_parts.append(f"经验要求：{data['experience_requirement']}")
            
            return "；".join(context_parts)
        
        def target_generator(data: Dict) -> str:
            # 可以根据需要生成目标内容
            return ""
        
        self.process_table(config, system_generator, context_generator, target_generator)
    
    def process_custom_table(self, table_name: str, json_field: str, desc_field: str, batch_size: int = 1000):
        """处理自定义表的通用方法"""
        config = TableConfig(
            table_name=table_name,
            json_source_field=json_field,
            description_field=desc_field,
            json_target_field=f"{json_field}_ch",
            train_data_field="train_data_ch",
            system_field="system_ch",
            context_field="context_ch",
            target_field="target_ch",
            batch_size=batch_size
        )
        
        def default_system_generator(data: Dict) -> str:
            return "你是一个数据分析助手，请根据提供的信息生成相应的描述。"
        
        def default_context_generator(data: Dict) -> str:
            # 通用的上下文生成逻辑
            context_parts = []
            
            # 尝试提取常见字段
            common_fields = ['name', 'title', 'type', 'category', 'status']
            for field in common_fields:
                if field in data and data[field]:
                    context_parts.append(f"{field}: {data[field]}")
            
            return "；".join(context_parts) if context_parts else "无特定上下文"
        
        def default_target_generator(data: Dict) -> str:
            return ""
        
        self.process_table(config, default_system_generator, default_context_generator, default_target_generator)


def example_zhilian_resume():
    """处理智联招聘简历表示例"""
    print("=== 处理智联招聘简历表 ===")
    processor = ResumeProcessor()
    processor.process_zhilian_resume(batch_size=100)


def example_job_table():
    """处理岗位表示例"""
    print("=== 处理岗位表 ===")
    processor = CustomProcessor()
    processor.process_job_table(batch_size=100)


def example_custom_table():
    """处理自定义表示例"""
    print("=== 处理自定义表 ===")
    processor = CustomProcessor()
    
    # 处理自定义表，只需要指定表名和字段名
    processor.process_custom_table(
        table_name="your_custom_table",
        json_field="your_json_field",
        desc_field="your_description_field",
        batch_size=50
    )


def example_multiple_tables():
    """批量处理多个表的示例"""
    print("=== 批量处理多个表 ===")
    processor = CustomProcessor()
    
    # 定义要处理的表配置
    tables_config = [
        {
            "table_name": "zhilian_resume",
            "json_field": "resume_processed_info",
            "desc_field": "resume_description_detail"
        },
        {
            "table_name": "zhilian_job",
            "json_field": "processed_info",
            "desc_field": "job_description_detail"
        },
        # 可以添加更多表配置
    ]
    
    for table_config in tables_config:
        try:
            print(f"正在处理表: {table_config['table_name']}")
            processor.process_custom_table(
                table_name=table_config['table_name'],
                json_field=table_config['json_field'],
                desc_field=table_config['desc_field'],
                batch_size=100
            )
            print(f"表 {table_config['table_name']} 处理完成")
        except Exception as e:
            print(f"处理表 {table_config['table_name']} 时出错: {str(e)}")
            continue


def example_with_custom_generators():
    """使用自定义生成器的示例"""
    print("=== 使用自定义生成器处理表 ===")
    
    processor = CustomProcessor()
    
    # 创建表配置
    config = TableConfig(
        table_name="zhilian_resume",
        json_source_field="resume_processed_info",
        description_field="resume_description_detail",
        batch_size=50
    )
    
    # 自定义system生成器
    def custom_system_generator(data: Dict) -> str:
        return "你是一个高级HR助手，专门负责简历分析和人才评估。"
    
    # 自定义context生成器
    def custom_context_generator(data: Dict) -> str:
        context_info = []
        
        # 提取用户基本信息
        if 'user' in data:
            user = data['user']
            if 'workYearsLabel' in user:
                context_info.append(f"工作经验：{user['workYearsLabel']}")
            if 'maxEducationLabel' in user:
                context_info.append(f"学历水平：{user['maxEducationLabel']}")
            if 'cityLabel' in user:
                context_info.append(f"所在城市：{user['cityLabel']}")
        
        # 提取技能信息
        if 'resume' in data and 'skillTags' in data['resume']:
            skills = data['resume']['skillTags']
            if skills:
                context_info.append(f"核心技能：{', '.join(skills[:5])}")
        
        return " | ".join(context_info)
    
    # 自定义target生成器
    def custom_target_generator(data: Dict) -> str:
        # 生成结构化的简历摘要
        summary_parts = []
        
        if 'user' in data:
            user = data['user']
            if 'workYearsLabel' in user and 'maxEducationLabel' in user:
                summary_parts.append(f"{user['workYearsLabel']}工作经验，{user['maxEducationLabel']}学历")
        
        if 'resume' in data and 'workExperiences' in data['resume']:
            work_exp = data['resume']['workExperiences']
            if work_exp and len(work_exp) > 0:
                latest_job = work_exp[0]
                if 'jobTitle' in latest_job and 'orgName' in latest_job:
                    summary_parts.append(f"曾任{latest_job['orgName']}{latest_job['jobTitle']}")
        
        return "，".join(summary_parts) if summary_parts else "待完善简历信息"
    
    # 使用自定义生成器处理表
    processor.process_table(
        config, 
        custom_system_generator, 
        custom_context_generator, 
        custom_target_generator
    )


if __name__ == "__main__":
    print("数据库处理器使用示例")
    print("=" * 50)
    
    # 选择要运行的示例
    examples = {
        "1": ("处理智联招聘简历表", example_zhilian_resume),
        "2": ("处理岗位表", example_job_table),
        "3": ("处理自定义表", example_custom_table),
        "4": ("批量处理多个表", example_multiple_tables),
        "5": ("使用自定义生成器", example_with_custom_generators)
    }
    
    print("可用示例:")
    for key, (desc, _) in examples.items():
        print(f"{key}. {desc}")
    
    # 默认运行第一个示例
    print("\n运行默认示例: 处理智联招聘简历表")
    example_zhilian_resume()