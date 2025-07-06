# -*- coding: utf-8 -*-
"""
智联招聘简历数据处理器增强版测试脚本
测试合并resume_process.py后的新功能
"""

import json
import sys
import os
from unittest.mock import Mock, patch

# 模拟数据库连接模块
sys.modules['db_connection'] = Mock()
sys.modules['education_experience_processor'] = Mock()
sys.modules['work_experience_processor'] = Mock()

# 模拟数据库连接函数
def mock_get_db_connection():
    return Mock()

def mock_close_db_connection(cursor, connection):
    pass

# 设置模拟
sys.modules['db_connection'].get_db_connection = mock_get_db_connection
sys.modules['db_connection'].close_db_connection = mock_close_db_connection
sys.modules['db_connection'].DatabaseConnection = Mock

# 模拟处理器类
sys.modules['education_experience_processor'].EducationExperienceProcessor = Mock
sys.modules['work_experience_processor'].WorkExperienceProcessor = Mock

# 导入要测试的类
from zhilian_resume_processor import ZhilianResumeProcessor, ZhilianResumeProcessorConfig

def test_enhanced_config():
    """测试增强配置"""
    print("=== 测试增强配置 ===")
    
    config = ZhilianResumeProcessorConfig()
    
    # 测试新增的配置项
    assert hasattr(config, 'enable_data_filtering'), "缺少enable_data_filtering配置"
    assert hasattr(config, 'enable_html_cleaning'), "缺少enable_html_cleaning配置"
    assert hasattr(config, 'enable_excel_export'), "缺少enable_excel_export配置"
    assert hasattr(config, 'retain_fields'), "缺少retain_fields配置"
    assert hasattr(config, 'excel_platform'), "缺少excel_platform配置"
    assert hasattr(config, 'excel_start_id'), "缺少excel_start_id配置"
    assert hasattr(config, 'excel_end_id'), "缺少excel_end_id配置"
    assert hasattr(config, 'excel_output_dir'), "缺少excel_output_dir配置"
    
    print("✓ 所有新增配置项都存在")
    
    # 测试默认值
    assert config.enable_data_filtering == True, "enable_data_filtering默认值错误"
    assert config.enable_html_cleaning == True, "enable_html_cleaning默认值错误"
    assert config.enable_excel_export == False, "enable_excel_export默认值错误"
    assert isinstance(config.retain_fields, dict), "retain_fields应该是字典类型"
    
    print("✓ 配置默认值正确")
    print("配置测试通过！\n")

def test_enhanced_methods():
    """测试增强方法"""
    print("=== 测试增强方法 ===")
    
    config = ZhilianResumeProcessorConfig()
    processor = ZhilianResumeProcessor(config)
    
    # 测试新增的方法是否存在
    methods_to_test = [
        'deep_clean',
        'clean_html',
        'filter_resume_data',
        'replace_none_with_empty',
        'remove_empty_fields',
        'export_to_excel',
        'process_single_resume_job_info',
        'export_resumes_to_excel',
        'process_job_info_extraction',
        'process_data_filtering_only',
        'process_sc_platform_resumes',
        '_convert_sc_to_unified_format'
    ]
    
    for method_name in methods_to_test:
        assert hasattr(processor, method_name), f"缺少方法: {method_name}"
        print(f"✓ 方法 {method_name} 存在")
    
    print("✓ 所有新增方法都存在")
    print("方法测试通过！\n")

def test_html_cleaning():
    """测试HTML清理功能"""
    print("=== 测试HTML清理功能 ===")
    
    config = ZhilianResumeProcessorConfig()
    processor = ZhilianResumeProcessor(config)
    
    # 测试HTML清理
    test_html = "<p>这是一个&nbsp;测试&lt;文本&gt;</p>"
    cleaned = processor.clean_html(test_html)
    
    print(f"原始HTML: {test_html}")
    print(f"清理后: {cleaned}")
    
    # 验证HTML标签和实体被清理
    assert '<p>' not in cleaned, "HTML标签未被清理"
    assert '&nbsp;' not in cleaned, "HTML实体未被清理"
    assert '&lt;' not in cleaned, "HTML实体未被清理"
    assert '&gt;' not in cleaned, "HTML实体未被清理"
    
    print("✓ HTML清理功能正常")
    print("HTML清理测试通过！\n")

def test_data_filtering():
    """测试数据过滤功能"""
    print("=== 测试数据过滤功能 ===")
    
    config = ZhilianResumeProcessorConfig()
    processor = ZhilianResumeProcessor(config)
    
    # 测试数据
    test_data = {
        "user": {
            "name": "张三",
            "genderLabel": "男",
            "age": 30,
            "unwanted_field": "应该被过滤"
        },
        "resume": {
            "workExperiences": [
                {
                    "orgName": "公司A",
                    "jobTitle": "工程师",
                    "timeLabel": "2020.01-2023.01",
                    "unwanted_field": "应该被过滤"
                }
            ],
            "unwanted_section": "应该被过滤"
        },
        "unwanted_root": "应该被过滤"
    }
    
    # 自定义过滤规则
    retain_fields = {
        "user": {
            "name": True,
            "genderLabel": True,
            "age": True
        },
        "resume": {
            "workExperiences": {
                "orgName": True,
                "jobTitle": True,
                "timeLabel": True
            }
        }
    }
    
    filtered_data = processor.filter_resume_data(test_data, retain_fields)
    
    print("原始数据:")
    print(json.dumps(test_data, ensure_ascii=False, indent=2))
    print("\n过滤后数据:")
    print(json.dumps(filtered_data, ensure_ascii=False, indent=2))
    
    # 验证过滤结果
    assert "unwanted_root" not in filtered_data, "根级别不需要的字段未被过滤"
    assert "unwanted_field" not in filtered_data["user"], "用户级别不需要的字段未被过滤"
    assert "unwanted_section" not in filtered_data["resume"], "简历级别不需要的字段未被过滤"
    assert "unwanted_field" not in filtered_data["resume"]["workExperiences"][0], "工作经历不需要的字段未被过滤"
    
    # 验证保留的字段存在
    assert filtered_data["user"]["name"] == "张三", "用户姓名字段丢失"
    assert filtered_data["resume"]["workExperiences"][0]["orgName"] == "公司A", "工作经历字段丢失"
    
    print("✓ 数据过滤功能正常")
    print("数据过滤测试通过！\n")

def run_all_tests():
    """运行所有测试"""
    print("智联招聘简历数据处理器增强版测试")
    print("=" * 50)
    
    try:
        test_enhanced_config()
        test_enhanced_methods()
        test_html_cleaning()
        test_data_filtering()
        
        print("=" * 50)
        print("🎉 所有测试通过！")
        print("\n增强功能验证结果:")
        print("✓ 配置系统增强完成")
        print("✓ HTML清理功能正常")
        print("✓ 数据过滤功能正常")
        print("\n合并resume_process.py功能成功！")
        
    except AssertionError as e:
        print(f"❌ 测试失败: {e}")
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()