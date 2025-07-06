# 教育经历处理器使用说明

## 概述

教育经历处理器 (`EducationExperienceProcessor`) 是一个专门用于处理简历中教育经历数据的工具类，特别针对包含"至今"的 `educationTimeLabel` 字段进行智能处理。

## 主要功能

### 1. "至今"类型数据处理

根据学历类型自动计算结束时间：
- **大专/专科**: 开始时间 + 3年
- **硕士/研究生**: 开始时间 + 3年  
- **本科/学士**: 开始时间 + 4年
- **默认**: 如果学历类型未知，默认按本科4年计算

### 2. 支持的时间格式

- `"2013.09 - 2017.06"` (标准格式)
- `"2013.09 - 至今"` (至今格式)

### 3. 数据验证和错误处理

- 自动处理异常情况
- 提供详细的处理日志
- 计算教育持续时间

## 使用示例

### 基本使用

```python
from education_experience_processor import EducationExperienceProcessor

# 创建处理器实例
processor = EducationExperienceProcessor()

# 示例教育经历数据
education_experiences = [
    {
        "schoolName": "北京大学",
        "educationTimeLabel": "2013.09 - 至今",
        "major": "计算机科学与技术",
        "educationLabel": "本科"
    },
    {
        "schoolName": "清华大学",
        "educationTimeLabel": "2015.09 - 至今",
        "major": "软件工程",
        "educationLabel": "硕士"
    }
]

# 处理教育经历
processed = processor.process_education_experiences(education_experiences)
```

### 处理结果

```
教育经历时间计算: 2013.09 + 4年(本科) -> 2017.09
处理教育经历: 2013.09 - 至今 -> 2013.09 - 2017.09 (学历: 本科)

教育经历时间计算: 2015.09 + 3年(硕士) -> 2018.09
处理教育经历: 2015.09 - 至今 -> 2015.09 - 2018.09 (学历: 硕士)
```

## 与简历数据去重处理脚本的集成

教育经历处理器已经集成到 `简历数据去重处理脚本.py` 中：

```python
from 简历数据去重处理脚本 import ResumeDataProcessor

# 创建处理器（自动包含教育经历处理功能）
processor = ResumeDataProcessor()

# 处理教育经历（自动处理"至今"类型数据并去重）
processed_education = processor.deduplicate_education_experiences(education_experiences)
```

## API 参考

### EducationExperienceProcessor 类

#### 方法

##### `parse_education_time_label(time_label, education_label=None)`
解析教育时间标签，提取开始和结束时间。

**参数:**
- `time_label` (str): 时间标签字符串
- `education_label` (str, optional): 学历标签

**返回:**
- `tuple`: (开始时间, 结束时间) 或 None

##### `calculate_end_time_from_start(start_time, education_label=None)`
根据开始时间和学历类型计算结束时间。

**参数:**
- `start_time` (str): 开始时间，格式为 "yyyy.mm"
- `education_label` (str, optional): 学历标签

**返回:**
- `str`: 结束时间，格式为 "yyyy.mm"

##### `process_education_experiences(education_experiences)`
处理教育经历列表，主要处理"至今"类型的数据。

**参数:**
- `education_experiences` (list): 教育经历列表

**返回:**
- `list`: 处理后的教育经历列表

##### `get_education_duration_years(time_label, education_label=None)`
计算教育经历的持续年数。

**参数:**
- `time_label` (str): 时间标签
- `education_label` (str, optional): 学历标签

**返回:**
- `float`: 持续年数

## 学历类型映射

| 学历标签关键词 | 学制年限 | 示例 |
|---------------|----------|------|
| 大专、专科 | 3年 | "2020.09 - 至今" → "2020.09 - 2023.09" |
| 硕士、研究生 | 3年 | "2015.09 - 至今" → "2015.09 - 2018.09" |
| 本科、学士 | 4年 | "2013.09 - 至今" → "2013.09 - 2017.09" |
| 其他/未知 | 4年 | 默认按本科处理 |

## 测试

运行测试脚本验证功能：

```bash
# 测试教育经历处理器
python education_experience_processor.py

# 测试集成功能
python test_education_integration.py

# 综合测试
python test_combined_processors.py
```

## 注意事项

1. **学历识别**: 系统通过关键词匹配识别学历类型，建议使用标准的学历名称
2. **时间格式**: 目前支持 "yyyy.mm" 格式，其他格式可能无法正确解析
3. **错误处理**: 如果计算失败，系统会回退到默认时间 "2025.05"
4. **日志输出**: 处理过程会输出详细日志，便于调试和验证

## 更新历史

- **v1.0**: 初始版本，支持"至今"类型数据处理
- 集成到简历数据去重处理脚本
- 支持大专、本科、硕士三种学历类型的智能识别