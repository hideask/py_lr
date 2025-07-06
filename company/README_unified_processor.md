# 统一经历处理器 (Unified Experience Processor)

## 概述

统一经历处理器是一个集成的解决方案，用于处理简历数据中工作经历、项目经历和教育经历的"至今"类型数据。它将原来的 `process_remaining_zhijin_records.py` 脚本的功能整合到面向对象的架构中，提供更好的可维护性和扩展性。

## 主要功能

### 1. 统一处理"至今"数据
- **工作经历**: 将"至今"转换为"2025.05"并重新计算持续时间
- **项目经历**: 将"至今"转换为"2025.05"并重新计算持续时间  
- **教育经历**: 根据学历类型智能计算结束时间
  - 本科: 开始时间 + 4年
  - 硕士/大专: 开始时间 + 3年

### 2. 集成到现有架构
- 与 `WorkExperienceProcessor` 和 `EducationExperienceProcessor` 协同工作
- 集成到 `简历数据去重处理脚本.py` 中
- 支持批量数据库处理

### 3. 数据库操作
- 自动更新 `resume_processed_info` 字段
- 设置 `work_years` 为 '1'
- 支持事务处理和错误回滚

## 文件结构

```
company/
├── unified_experience_processor.py          # 统一经历处理器核心类
├── batch_process_zhijin_records.py         # 批量处理脚本（替代原process_remaining_zhijin_records.py）
├── test_unified_processor.py               # 测试脚本
├── 简历数据去重处理脚本.py                    # 已集成统一处理器
├── work_experience_processor.py            # 工作经历处理器
├── education_experience_processor.py       # 教育经历处理器
└── README_unified_processor.md             # 本文档
```

## 使用方法

### 1. 基本使用

```python
from unified_experience_processor import UnifiedExperienceProcessor

# 创建处理器
processor = UnifiedExperienceProcessor()

# 处理单个简历数据
resume_data = {
    "resume": {
        "workExperiences": [...],
        "projectExperiences": [...],
        "educationExperiences": [...]
    }
}

has_updates = processor.process_single_resume(resume_data)
print(f"是否有更新: {has_updates}")
```

### 2. 批量数据库处理

```python
# 方法1: 直接使用统一处理器
processor = UnifiedExperienceProcessor()
results = processor.process_resume_data_batch(train_type='3')

# 方法2: 使用批量处理脚本
python batch_process_zhijin_records.py
```

### 3. 集成到去重处理

```python
from 简历数据去重处理脚本 import ResumeDataProcessor

# 创建处理器（已自动集成统一处理器）
processor = ResumeDataProcessor()

# 处理工作经历（自动处理"至今"数据并去重）
processed_work = processor.deduplicate_work_experiences(work_experiences)

# 处理项目经历（自动处理"至今"数据并去重）
processed_project = processor.deduplicate_project_experiences(project_experiences)

# 处理教育经历（自动处理"至今"数据并去重）
processed_education = processor.deduplicate_education_experiences(education_experiences)
```

## API 参考

### UnifiedExperienceProcessor 类

#### 主要方法

- `process_single_resume(resume_data: Dict) -> bool`
  - 处理单个简历的所有经历数据
  - 返回是否有更新

- `process_resume_data_batch(train_type: str = '3') -> Dict[str, int]`
  - 批量处理数据库中的简历记录
  - 返回处理结果统计

- `process_work_experiences(experiences: List[Dict]) -> bool`
  - 处理工作经历列表中的"至今"数据

- `process_project_experiences(experiences: List[Dict]) -> bool`
  - 处理项目经历列表中的"至今"数据

- `process_education_experiences_zhijin(experiences: List[Dict]) -> bool`
  - 处理教育经历列表中的"至今"数据（智联格式）

#### 辅助方法

- `calculate_duration(start_time: str, end_time: str = '2025.05') -> str`
  - 计算时间持续时间

- `update_time_label(time_label: str) -> Tuple[str, bool]`
  - 更新时间标签，将"至今"替换为具体日期

## 处理示例

### 工作经历处理

```
输入: "2020.03 - 至今 (4年 8个月)"
输出: "2020.03 - 2025.05 (5年 2个月)"
```

### 教育经历处理

```
输入: "2014.09 - 至今" (本科)
输出: "2014.09 - 2018.09" (开始时间 + 4年)

输入: "2020.09 - 至今" (硕士)
输出: "2020.09 - 2023.09" (开始时间 + 3年)
```

## 测试

运行测试脚本验证功能：

```bash
python test_unified_processor.py
```

测试包括：
- 统一处理器基本功能测试
- 集成处理器测试
- 时间计算功能测试
- 去重功能测试

## 迁移指南

### 从 process_remaining_zhijin_records.py 迁移

1. **替换脚本**:
   ```bash
   # 旧方式
   python process_remaining_zhijin_records.py
   
   # 新方式
   python batch_process_zhijin_records.py
   ```

2. **功能对比**:
   - ✅ 处理工作经历"至今"数据
   - ✅ 处理项目经历"至今"数据
   - ✅ 新增：处理教育经历"至今"数据
   - ✅ 更新work_years字段
   - ✅ 数据库事务处理
   - ✅ 错误处理和日志记录

3. **优势**:
   - 面向对象设计，更好的可维护性
   - 统一处理多种经历类型
   - 集成到现有处理流程
   - 更完善的测试覆盖

## 配置

### 日志配置

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('unified_experience_processor.log'),
        logging.StreamHandler()
    ]
)
```

### 数据库配置

确保 `db_connection.py` 中的数据库连接配置正确。

## 注意事项

1. **数据备份**: 在批量处理前建议备份数据库
2. **测试环境**: 先在测试环境验证功能
3. **日志监控**: 关注处理日志，及时发现问题
4. **性能考虑**: 大批量数据处理时注意内存使用

## 错误处理

- JSON解析错误会被记录但不会中断处理
- 数据库错误会触发事务回滚
- 所有错误都会记录到日志文件

## 更新历史

- **v1.0.0**: 初始版本，集成工作经历、项目经历和教育经历处理
- 替代 `process_remaining_zhijin_records.py` 脚本
- 集成到 `简历数据去重处理脚本.py`

## 支持

如有问题或建议，请查看日志文件或联系开发团队。