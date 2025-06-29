# 抽象数据库处理器使用指南

## 概述

这个抽象数据库处理器是一个高度可配置的工具，用于处理PostgreSQL数据库中的JSON数据转换和训练数据构建。主要功能包括：

1. **JSON键值翻译**：将英文键转换为中文键
2. **训练数据构建**：按照指定格式构建训练数据
3. **批量数据库更新**：同时更新多个字段
4. **高度抽象**：支持处理不同的表和字段配置

## 文件结构

```
├── abstract_db_processor.py    # 核心抽象处理器
├── usage_examples.py          # 使用示例
└── README_db_processor.md     # 使用指南（本文件）
```

## 核心组件

### 1. TableConfig 类

表配置类，用于定义要处理的表和字段信息：

```python
@dataclass
class TableConfig:
    table_name: str              # 表名
    id_field: str = "id"         # ID字段名
    json_source_field: str       # JSON源字段
    description_field: str       # 描述字段
    json_target_field: str       # 中文JSON目标字段
    train_data_field: str        # 训练数据字段
    system_field: str            # system字段
    context_field: str           # context字段
    target_field: str            # target字段
    batch_size: int = 1000       # 批处理大小
```

### 2. JSONTranslator 类

JSON键值翻译器，负责将英文键转换为中文键：

- 支持嵌套JSON结构
- 智能上下文识别（如根据父级键判断name字段的翻译）
- 可扩展的键值映射

### 3. TrainingDataBuilder 类

训练数据构建器，按照以下格式构建数据：

```json
{
  "system": ["系统提示内容"],
  "context": ["上下文内容"],
  "target": "目标内容"
}
```

### 4. DatabaseProcessor 类

数据库处理器基类，提供核心的数据库操作功能。

## 使用方法

### 基础使用

#### 1. 多线程处理（推荐）

```python
from abstract_db_processor import ResumeProcessor

# 创建处理器实例
processor = ResumeProcessor()

# 多线程处理智联招聘简历表
processor.process_zhilian_resume(
    batch_size=20,      # 批次大小
    max_workers=4,      # 线程数
    use_multithread=True # 使用多线程（默认）
)
```

#### 2. 单线程处理

```python
# 单线程处理（适用于调试或资源受限环境）
processor.process_zhilian_resume(
    batch_size=10,
    use_multithread=False
)
```

#### 3. 处理自定义表（多线程）

```python
from abstract_db_processor import DatabaseProcessor, TableConfig

class CustomProcessor(DatabaseProcessor):
    def __init__(self):
        db_config = {
            "dbname": "your_db",
            "user": "your_user",
            "password": "your_password",
            "host": "your_host",
            "port": "your_port"
        }
        super().__init__(db_config)

# 使用自定义处理器
processor = CustomProcessor()

# 配置要处理的表
config = TableConfig(
    table_name="your_table",
    json_source_field="your_json_field",
    description_field="your_description_field",
    batch_size=50
)

# 多线程处理表
processor.process_table(config, max_workers=6)

# 单线程处理表
processor.process_table_single_thread(config)
```

#### 4. 性能优化建议

```python
# 根据数据量和系统资源调整参数

# 小数据量（< 100条）
processor.process_zhilian_resume(
    batch_size=20,
    max_workers=2,
    use_multithread=True
)

# 中等数据量（100-1000条）
processor.process_zhilian_resume(
    batch_size=50,
    max_workers=4,
    use_multithread=True
)

# 大数据量（> 1000条）
processor.process_zhilian_resume(
    batch_size=100,
    max_workers=8,
    use_multithread=True
)
```

### 高级使用

#### 自定义生成器函数

可以为system、context、target字段提供自定义生成器：

```python
def custom_system_generator(data: Dict) -> str:
    return "你是一个专业的数据分析助手"

def custom_context_generator(data: Dict) -> str:
    # 从JSON数据中提取关键信息
    context_parts = []
    if 'name' in data:
        context_parts.append(f"姓名：{data['name']}")
    if 'experience' in data:
        context_parts.append(f"经验：{data['experience']}")
    return "；".join(context_parts)

def custom_target_generator(data: Dict) -> str:
    # 生成目标内容
    return "根据数据生成的目标描述"

# 使用自定义生成器
processor.process_table(
    config, 
    custom_system_generator, 
    custom_context_generator, 
    custom_target_generator
)
```

#### 批量处理多个表

```python
# 定义多个表的配置
tables_config = [
    {
        "table_name": "table1",
        "json_field": "json_field1",
        "desc_field": "desc_field1"
    },
    {
        "table_name": "table2",
        "json_field": "json_field2",
        "desc_field": "desc_field2"
    }
]

# 批量处理
for table_config in tables_config:
    processor.process_custom_table(
        table_name=table_config['table_name'],
        json_field=table_config['json_field'],
        desc_field=table_config['desc_field']
    )
```

## 数据库字段说明

处理器会在目标表中创建或更新以下字段：

- `{json_source_field}_ch`：存储转换后的中文JSON
- `train_data_ch`：存储训练数据JSON
- `system_ch`：存储system内容
- `context_ch`：存储context内容
- `target_ch`：存储target内容

## JSON键值映射

当前支持的英文到中文键值映射包括：

### 用户信息
- `user` → `用户`
- `name` → `姓名`
- `genderLabel` → `性别`
- `age` → `年龄`
- `workYears` → `工作年限`
- `cityLabel` → `城市`
- `email` → `邮箱`

### 简历信息
- `resume` → `简历`
- `skillTags` → `技能标签`
- `educationExperiences` → `教育经历`
- `workExperiences` → `工作经历`
- `projectExperiences` → `项目经历`
- `certificates` → `证书`

### 特殊处理
- `name`字段根据上下文智能翻译：
  - 在`workSkillTags`中 → `技能名称`
  - 在`certificates`中 → `证书名称`
  - 在`projectExperiences`中 → `项目名称`
  - 在`languageSkills`中 → `语言名称`
  - 其他情况 → `姓名`

## 错误处理

- 自动跳过无法解析的JSON数据
- 记录处理失败的记录ID
- 支持事务回滚
- 批量提交减少数据库压力

## 性能优化

### 多线程优化

1. **线程数量选择**：
   - CPU密集型任务：线程数 = CPU核心数
   - I/O密集型任务：线程数 = CPU核心数 × 2-4
   - 数据库处理通常是I/O密集型，建议4-8个线程

2. **批次大小调整**：
   - 小批次（10-20）：适合调试和测试
   - 中批次（50-100）：平衡性能和内存使用
   - 大批次（100+）：适合大量数据处理

3. **资源监控**：
   - 监控CPU使用率
   - 监控内存使用情况
   - 监控数据库连接数

### 性能对比

| 处理模式 | 批次大小 | 线程数 | 适用场景 |
|---------|---------|--------|-----------|
| 单线程   | 10-50   | 1      | 调试、小数据量 |
| 多线程   | 20-50   | 2-4    | 中等数据量 |
| 多线程   | 50-100  | 4-8    | 大数据量 |

### 其他优化建议

- 支持批量处理，默认1000条记录一批
- 每100条记录提交一次事务
- 使用连接池管理数据库连接
- 支持并发处理（可扩展）

## 扩展指南

### 添加新的处理器

1. 继承 `DatabaseProcessor` 基类
2. 实现特定的数据库配置
3. 根据需要重写生成器方法
4. 配置多线程参数

```python
class NewProcessor(DatabaseProcessor):
    def __init__(self):
        db_config = {"dbname": "new_db", ...}
        super().__init__(db_config)
    
    def process_new_data(self, batch_size=30, max_workers=4):
        config = TableConfig(
            table_name="new_table",
            json_source_field="data_field",
            description_field="desc_field",
            batch_size=batch_size
        )
        self.process_table(config, max_workers=max_workers)
```

### 添加新的键值映射

在`JSONTranslator`类的`key_mapping`字典中添加新的映射：

```python
self.key_mapping.update({
    "new_english_key": "新的中文键",
    "another_key": "另一个中文键"
})
```

### 创建专用处理器

继承`DatabaseProcessor`类创建专用处理器：

```python
class JobProcessor(DatabaseProcessor):
    def __init__(self):
        super().__init__(db_config)
    
    def process_jobs(self):
        # 实现岗位处理逻辑
        pass
```

### 自定义训练数据格式

继承`TrainingDataBuilder`类自定义数据格式：

```python
class CustomTrainingDataBuilder(TrainingDataBuilder):
    def build_training_data(self, system, context, target):
        return {
            "instruction": system,
            "input": context,
            "output": target
        }
```

### 多线程安全注意事项

1. **数据库连接**：每个线程使用独立的数据库连接
2. **共享资源**：使用锁保护共享资源访问
3. **异常处理**：确保线程异常不影响其他线程
4. **资源清理**：正确关闭数据库连接和线程池

## 注意事项

### 数据安全
1. **数据库权限**：确保数据库用户有读写权限
2. **字段存在性**：目标字段需要预先在表中创建
3. **数据备份**：处理前建议备份重要数据
4. **网络连接**：确保数据库连接稳定

### 多线程注意事项
1. **资源限制**：不要设置过多线程数，避免系统资源耗尽
2. **数据库连接**：注意数据库最大连接数限制
3. **内存使用**：大批量处理时监控内存使用情况
4. **异常处理**：单个线程异常不会影响其他线程

### 数据格式
1. **JSON格式**：确保源JSON数据格式正确
2. **中文编码**：注意中文字符的编码处理
3. **字段过滤**：只保留key_mapping中定义的字段

### 性能监控
1. **处理进度**：关注控制台输出的处理进度
2. **错误日志**：及时查看和处理错误信息
3. **系统资源**：监控CPU、内存和数据库连接使用情况

## 示例运行

查看`usage_examples.py`文件获取完整的使用示例，包括：

- 基础表处理
- 自定义生成器使用
- 批量处理多个表
- 错误处理示例

运行示例：

```bash
python usage_examples.py
```

## 技术支持

如需技术支持或功能扩展，请参考代码注释或联系开发团队。