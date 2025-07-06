# 智联招聘简历数据处理器

## 概述

`ZhilianResumeProcessor` 是一个统一的工具类，集成了智联招聘简历数据的多种处理功能，包括：

- **数据去重**：去除教育经历、工作经历、项目经历中的重复数据
- **"至今"数据处理**：将包含"至今"的时间标签转换为标准格式
- **证书分割**：将包含多个证书的字符串分割成单独的证书记录
- **格式清洗**：统一数据格式，提高数据质量

## 功能特性

### 1. 灵活的配置系统
- 支持通过配置类 `ZhilianResumeProcessorConfig` 自定义处理行为
- 可以选择性启用或禁用特定功能
- 支持多线程处理，可配置线程数和批次大小

### 2. 数据去重功能
- **教育经历去重**：根据学校名称和专业去重
- **工作经历去重**：根据公司名称、职位和时间标签去重
- **项目经历去重**：根据项目名称和时间标签去重，支持模糊匹配

### 3. "至今"数据处理
- 自动识别包含"至今"的时间标签
- 将"至今"替换为指定的结束日期（默认2025.05）
- 重新计算持续时间
- 支持工作经历、项目经历和教育经历

### 4. 证书处理
- 自动分割包含多个证书的字符串
- 支持多种分隔符（逗号、分号、顿号等）
- 保留原有证书的其他属性

### 5. 数据库操作
- 自动从 `zhilian_resume` 表获取待处理数据
- 支持事务处理，确保数据一致性
- 智能判断数据是否发生变化，避免不必要的更新
- 错误处理和回滚机制

## 安装和依赖

确保已安装以下依赖：

```python
# 需要的模块
from db_connection import get_db_connection, close_db_connection, DatabaseConnection
from education_experience_processor import EducationExperienceProcessor
from work_experience_processor import WorkExperienceProcessor
```

## 快速开始

### 基础使用

```python
from zhilian_resume_processor import ZhilianResumeProcessor

# 使用默认配置
processor = ZhilianResumeProcessor()

# 开始处理
processor.start_processing()
```

### 自定义配置

```python
from zhilian_resume_processor import ZhilianResumeProcessor, ZhilianResumeProcessorConfig

# 创建自定义配置
config = ZhilianResumeProcessorConfig()
config.num_threads = 10  # 使用10个线程
config.batch_size = 100  # 每批处理100条数据
config.enable_deduplication = True  # 启用去重
config.enable_zhijin_processing = True  # 启用"至今"处理

# 创建处理器
processor = ZhilianResumeProcessor(config)
processor.start_processing()
```

## 配置选项详解

### ZhilianResumeProcessorConfig 类

#### 基础配置
- `num_threads`: 线程数量（默认：5）
- `batch_size`: 每批处理的数据量（默认：50）

#### 功能开关
- `enable_deduplication`: 启用去重功能（默认：True）
- `enable_zhijin_processing`: 启用"至今"数据处理（默认：True）
- `enable_certificate_splitting`: 启用证书分割功能（默认：True）
- `enable_format_cleaning`: 启用格式清洗功能（默认：True）

#### 去重配置
- `deduplicate_education`: 去重教育经历（默认：True）
- `deduplicate_work`: 去重工作经历（默认：True）
- `deduplicate_project`: 去重项目经历（默认：True）

#### "至今"处理配置
- `zhijin_end_date`: "至今"替换的结束日期（默认：'2025.05'）
- `process_work_zhijin`: 处理工作经历的"至今"（默认：True）
- `process_project_zhijin`: 处理项目经历的"至今"（默认：True）
- `process_education_zhijin`: 处理教育经历的"至今"（默认：True）

#### 数据库配置
- `train_type`: 训练类型过滤（默认：'3'）
- `update_work_years`: 是否更新work_years字段（默认：True）

#### 日志配置
- `log_level`: 日志级别（默认：logging.INFO）
- `log_file`: 日志文件名（默认：'zhilian_resume_processor.log'）
- `enable_console_log`: 是否启用控制台日志（默认：True）

## 使用场景示例

### 1. 仅去重处理

```python
config = ZhilianResumeProcessorConfig()
config.enable_deduplication = True
config.enable_zhijin_processing = False
config.enable_certificate_splitting = False

processor = ZhilianResumeProcessor(config)
processor.start_processing()
```

### 2. 仅"至今"数据处理

```python
config = ZhilianResumeProcessorConfig()
config.enable_deduplication = False
config.enable_zhijin_processing = True
config.zhijin_end_date = '2025.06'  # 自定义结束日期

processor = ZhilianResumeProcessor(config)
processor.start_processing()
```

### 3. 高性能处理

```python
config = ZhilianResumeProcessorConfig()
config.num_threads = 20
config.batch_size = 200
config.log_level = logging.WARNING  # 减少日志输出
config.enable_console_log = False

processor = ZhilianResumeProcessor(config)
processor.start_processing()
```

### 4. 调试模式

```python
config = ZhilianResumeProcessorConfig()
config.num_threads = 1  # 单线程便于调试
config.batch_size = 10
config.log_level = logging.DEBUG

processor = ZhilianResumeProcessor(config)
processor.start_processing()
```

### 5. 处理单个简历

```python
processor = ZhilianResumeProcessor()
result = processor.process_single_resume_by_id(12345)
print(result)
```

## 数据库表结构要求

处理器需要 `zhilian_resume` 表包含以下字段：

- `id`: 主键
- `resume_processed_info`: JSON格式的简历数据
- `train_type`: 训练类型
- `check_type`: 处理状态标记
- `work_years`: 工作年限（可选）

## 处理状态说明

- `NULL`: 未处理
- `'processing'`: 正在处理
- `'12'`: 已处理且数据有变化
- `'13'`: 已处理但数据无变化
- `'json_error'`: JSON解析错误

## 日志和监控

处理器提供详细的日志记录和统计信息：

- 处理进度日志
- 错误日志和异常处理
- 处理统计信息（总处理数、更新数、错误数等）
- 线程安全的日志记录

## 错误处理

- **JSON解析错误**：标记为 `json_error` 状态
- **数据库错误**：自动回滚事务，重置处理状态
- **处理异常**：记录错误日志，继续处理其他数据

## 性能优化建议

1. **线程数配置**：根据数据库连接池大小和服务器性能调整
2. **批次大小**：平衡内存使用和处理效率
3. **日志级别**：生产环境建议使用 WARNING 或 ERROR 级别
4. **数据库索引**：确保 `id`、`train_type`、`check_type` 字段有适当索引

## 注意事项

1. **数据备份**：处理前建议备份重要数据
2. **并发控制**：使用 `FOR UPDATE SKIP LOCKED` 避免并发冲突
3. **内存管理**：大批量处理时注意内存使用
4. **事务管理**：每条记录独立事务，避免长事务锁定

## 扩展和定制

可以通过继承 `ZhilianResumeProcessor` 类来添加自定义处理逻辑：

```python
class CustomResumeProcessor(ZhilianResumeProcessor):
    def process_resume_data(self, resume_data):
        # 调用父类方法
        processed_data = super().process_resume_data(resume_data)
        
        # 添加自定义处理逻辑
        # ...
        
        return processed_data
```

## 版本历史

- v1.0.0: 初始版本，集成去重、"至今"处理、证书分割功能

## 支持和反馈

如有问题或建议，请联系开发团队。