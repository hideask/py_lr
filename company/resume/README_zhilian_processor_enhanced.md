# 智联招聘简历数据处理器 - 增强版

## 概述

本工具类是智联招聘简历数据处理的统一解决方案，集成了原有的去重、"至今"处理、证书分割功能，并新增了来自 `resume_process.py` 的数据过滤、HTML清理、Excel导出、多线程工作信息提取等功能。

## 新增功能

### 1. 数据过滤功能
- **功能描述**: 根据配置的字段保留规则过滤简历数据
- **配置项**: `enable_data_filtering`、`retain_fields`
- **使用场景**: 只保留需要的字段，减少数据冗余

### 2. HTML清理功能
- **功能描述**: 清理简历数据中的HTML标签和实体
- **配置项**: `enable_html_cleaning`
- **使用场景**: 清理从网页抓取的简历数据

### 3. Excel导出功能
- **功能描述**: 将简历数据导出为Excel文件
- **配置项**: `enable_excel_export`、`excel_platform`、`excel_start_id`、`excel_end_id`、`excel_output_dir`
- **支持平台**: 智联招聘(默认)、网易(wy)、SC平台(sc)

### 4. 工作信息提取
- **功能描述**: 多线程提取简历中的工作信息并更新到数据库
- **使用方法**: `process_job_info_extraction(max_workers=10)`

### 5. SC平台简历处理
- **功能描述**: 处理SC平台的简历数据，转换为统一格式
- **使用方法**: `process_sc_platform_resumes()`

### 6. 仅数据过滤处理
- **功能描述**: 只执行数据过滤，不进行其他处理
- **使用方法**: `process_data_filtering_only(limit=None)`

## 配置说明

### 新增配置项

```python
class ZhilianResumeProcessorConfig:
    def __init__(self):
        # 新增功能开关
        self.enable_data_filtering = True      # 启用数据过滤
        self.enable_html_cleaning = True       # 启用HTML清理
        self.enable_excel_export = False       # 启用Excel导出
        
        # 数据过滤配置
        self.retain_fields = {
            "user": {
                "name": True,
                "genderLabel": True,
                "age": True,
                "maxEducationLabel": True,
                "workYears": True,
                "cityLabel": True,
                "unlockedPhone": True,
                "email": True
            },
            "resume": {
                "educationExperiences": {
                    "schoolName": True,
                    "educationTimeLabel": True,
                    "major": True,
                    "educationLabel": True
                },
                "workExperiences": {
                    "orgName": True,
                    "jobTitle": True,
                    "description": True,
                    "timeLabel": True
                },
                # ... 更多字段配置
            }
        }
        
        # Excel导出配置
        self.excel_platform = ""              # 'wy', 'sc', 或空字符串
        self.excel_start_id = 5000
        self.excel_end_id = 15000
        self.excel_output_dir = "./"
```

## 使用示例

### 1. Excel导出

```python
from zhilian_resume_processor import ZhilianResumeProcessor, ZhilianResumeProcessorConfig

# 创建配置
config = ZhilianResumeProcessorConfig()
config.enable_excel_export = True
config.excel_start_id = 1000
config.excel_end_id = 2000
config.excel_output_dir = "./output/"

# 创建处理器
processor = ZhilianResumeProcessor(config)

# 导出智联招聘简历
output_file = processor.export_resumes_to_excel(platform="", limit=100)
print(f"导出完成: {output_file}")

# 导出SC平台简历
output_file = processor.export_resumes_to_excel(platform="sc", limit=50)
print(f"导出完成: {output_file}")
```

### 2. 工作信息提取

```python
# 创建处理器
processor = ZhilianResumeProcessor()

# 多线程提取工作信息
result = processor.process_job_info_extraction(max_workers=5)

if result['success']:
    print(f"成功处理: {result['processed_count']} 条")
    print(f"失败: {result['failed_count']} 条")
    print(f"总耗时: {result['total_time']:.2f} 秒")
else:
    print(f"处理失败: {result['message']}")
```

### 3. 仅数据过滤

```python
# 创建配置
config = ZhilianResumeProcessorConfig()
config.enable_data_filtering = True
config.enable_deduplication = False
config.enable_zhijin_processing = False
config.enable_certificate_splitting = False

# 自定义保留字段
config.retain_fields = {
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

# 创建处理器并执行过滤
processor = ZhilianResumeProcessor(config)
result = processor.process_data_filtering_only(limit=100)
```

### 4. SC平台简历处理

```python
# 创建配置
config = ZhilianResumeProcessorConfig()
config.enable_html_cleaning = True
config.enable_data_filtering = True

# 创建处理器
processor = ZhilianResumeProcessor(config)

# 处理SC平台简历
result = processor.process_sc_platform_resumes()

if result['success']:
    print(f"SC平台简历处理完成！")
    print(f"成功处理: {result['processed_count']} 条")
    print(f"失败: {result['failed_count']} 条")
else:
    print(f"处理失败: {result['message']}")
```

### 5. 综合处理

```python
# 创建配置
config = ZhilianResumeProcessorConfig()

# 启用所有功能
config.enable_deduplication = True
config.enable_zhijin_processing = True
config.enable_certificate_splitting = True
config.enable_format_cleaning = True
config.enable_data_filtering = True
config.enable_html_cleaning = True

# 设置线程和批次
config.num_threads = 8
config.batch_size = 50

# 创建处理器并启动处理
processor = ZhilianResumeProcessor(config)
processor.start_processing()
```

## 新增方法说明

### 数据处理方法

- `deep_clean(data)`: 深度清理数据，移除空值和无效字段
- `clean_html(text)`: 清理HTML标签和实体
- `filter_resume_data(data, retain_fields)`: 根据配置过滤简历数据
- `replace_none_with_empty(data)`: 将None值替换为空字符串
- `remove_empty_fields(data)`: 递归删除空值字段

### 导出方法

- `export_to_excel(resume_data, platform)`: 导出数据到Excel文件
- `export_resumes_to_excel(platform, limit)`: 从数据库导出简历到Excel

### 处理方法

- `process_single_resume_job_info(resume)`: 处理单个简历的工作信息
- `process_job_info_extraction(max_workers)`: 多线程工作信息提取
- `process_data_filtering_only(limit)`: 仅执行数据过滤
- `process_sc_platform_resumes()`: 处理SC平台简历

### 工具方法

- `DateEncoder`: JSON编码器，处理日期类型
- `_convert_sc_to_unified_format(sc_data)`: SC平台数据格式转换
- `_apply_html_cleaning(data)`: 应用HTML清理

## 处理流程

增强版的处理流程如下：

1. **数据获取**: 从数据库获取简历数据
2. **数据解析**: 解析JSON格式的简历数据
3. **去重处理**: 根据配置进行教育、工作、项目经历去重
4. **"至今"处理**: 更新时间标签中的"至今"为指定日期
5. **证书分割**: 将包含多个证书的字符串分割为单独证书
6. **数据过滤**: 根据配置保留指定字段
7. **HTML清理**: 清理HTML标签和实体
8. **格式清洗**: 应用格式清洗规则
9. **数据更新**: 将处理后的数据更新到数据库

## 性能优化

- **多线程处理**: 支持多线程并发处理，提高处理效率
- **批量处理**: 支持批量获取和处理数据
- **内存优化**: 及时释放不需要的数据，避免内存泄漏
- **数据库连接管理**: 合理管理数据库连接，避免连接泄漏

## 错误处理

- **异常捕获**: 完善的异常处理机制
- **错误日志**: 详细的错误日志记录
- **数据回滚**: 处理失败时的数据回滚机制
- **状态标记**: 处理状态的标记和跟踪

## 监控和日志

- **处理统计**: 详细的处理统计信息
- **进度跟踪**: 实时的处理进度跟踪
- **性能监控**: 处理时间和性能监控
- **日志配置**: 灵活的日志配置选项

## 注意事项

1. **数据库连接**: 确保数据库连接配置正确
2. **权限设置**: 确保有足够的数据库读写权限
3. **内存使用**: 大批量处理时注意内存使用情况
4. **备份数据**: 处理前建议备份重要数据
5. **测试环境**: 建议先在测试环境中验证功能

## 扩展性

- **插件化设计**: 支持自定义处理插件
- **配置驱动**: 通过配置控制处理行为
- **接口标准**: 标准化的接口设计
- **模块化**: 功能模块化，便于维护和扩展

## 版本历史

- **v2.0**: 合并resume_process.py功能，新增数据过滤、HTML清理、Excel导出等功能
- **v1.0**: 基础版本，包含去重、"至今"处理、证书分割功能

## 技术支持

如有问题或建议，请联系开发团队或查看相关文档。