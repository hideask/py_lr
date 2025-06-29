# 数据库处理器重构迁移指南

## 概述

本指南说明如何将现有的数据库查询和更新代码迁移到新的重构架构中。新架构提供了统一的数据库处理接口，减少了代码重复，提高了可维护性。

## 重构架构概览

### 核心组件

1. **DatabaseConnection** (`db_connection.py`) - 统一的数据库连接管理
2. **BaseQueryProcessor** (`common_db_processor.py`) - 基础查询处理器抽象类
3. **JSONProcessor** - JSON数据专用处理器
4. **HTMLCleanProcessor** - HTML清理专用处理器
5. **CommonQueryBuilder** - 通用SQL查询构建器
6. **具体实现类** (`refactored_processors.py`) - 针对特定业务的处理器实现

### 架构优势

- **代码复用**: 统一的查询和更新模式
- **类型安全**: 明确的接口定义和类型提示
- **错误处理**: 统一的异常处理和日志记录
- **批量处理**: 内置的批量操作支持
- **可扩展性**: 易于添加新的处理器类型

## 迁移步骤

### 1. 数据库连接迁移

#### 原有代码模式
```python
# 旧的连接方式
def get_db_connection():
    return psycopg2.connect(
        dbname="yhaimg",
        user="yhaimg", 
        password="Zq*6^pD6g2%JJ!z8",
        host="172.31.255.227",
        port="5588"
    )

def close_db_connection(cursor=None, connection=None):
    if cursor:
        cursor.close()
    if connection:
        connection.close()
```

#### 迁移后代码
```python
# 新的连接方式
from db_connection import DatabaseConnection, get_db_connection, close_db_connection

# 方式1: 使用默认连接（向后兼容）
connection = get_db_connection()
cursor = connection.cursor()
# ... 执行操作
close_db_connection(cursor, connection)

# 方式2: 使用DatabaseConnection类（推荐）
db = DatabaseConnection()
connection = db.get_connection()
cursor = connection.cursor()
# ... 执行操作
db.close_connection(cursor, connection)

# 方式3: 自定义连接参数
custom_db = DatabaseConnection(
    dbname="custom_db",
    user="custom_user",
    password="custom_password",
    host="custom_host",
    port="5432"
)
```

### 2. 查询和更新逻辑迁移

#### 原有代码模式（以job_process.py为例）
```python
# 旧的处理方式
def process_jobs():
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT id, job_info FROM zhilian_job LIMIT 1000")
    rows = cursor.fetchall()
    
    for row in rows:
        job_id = row[0]
        job_info = row[1]
        
        # 处理逻辑
        processed_info = process_job_data(job_info)
        
        # 更新数据库
        cursor.execute(
            "UPDATE zhilian_job SET processed_info = %s WHERE id = %s",
            (processed_info, job_id)
        )
        connection.commit()
    
    close_db_connection(cursor, connection)
```

#### 迁移后代码
```python
# 新的处理方式
from refactored_processors import JobProcessor

def process_jobs():
    job_processor = JobProcessor()
    
    # 方式1: 使用预定义的处理方法
    updated_count = job_processor.process_job_info("zhilian_job", limit=1000)
    print(f"处理了 {updated_count} 条记录")
    
    # 方式2: 使用通用批量处理
    from common_db_processor import CommonQueryBuilder
    
    query_sql = CommonQueryBuilder.build_select_with_condition(
        table_name="zhilian_job",
        fields=["id", "job_info"],
        limit=1000
    )
    
    update_sql = CommonQueryBuilder.build_update_by_id(
        table_name="zhilian_job",
        update_fields=["processed_info"]
    )
    
    def custom_process_func(record):
        job_id, job_info = record
        processed_info = process_job_data(job_info)
        return (job_id, processed_info)
    
    updated_count = job_processor.batch_query_and_update(
        query_sql=query_sql,
        update_sql=update_sql,
        process_func=custom_process_func
    )
```

### 3. HTML清理逻辑迁移

#### 原有代码模式
```python
# 旧的HTML清理方式
def clean_job_data():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, job_description FROM sc_pub_recruitmentnet_job where job_description like '%<%' or job_description like '%&%' ")
    
    rows = cursor.fetchall()
    
    for row in rows:
        job_id = row[0]
        dirty_description = row[1]
        cleaned_description = clean_html(dirty_description)
        
        cursor.execute(
            "UPDATE sc_pub_recruitmentnet_job SET job_description = %s WHERE id = %s",
            (cleaned_description, job_id)
        )
        connection.commit()
    
    close_db_connection(cursor, connection)
```

#### 迁移后代码
```python
# 新的HTML清理方式
from refactored_processors import JobProcessor

def clean_job_data():
    job_processor = JobProcessor()
    updated_count = job_processor.clean_job_descriptions("sc_pub_recruitmentnet_job")
    print(f"清理了 {updated_count} 条记录")
```

### 4. JSON数据处理迁移

#### 原有代码模式
```python
# 旧的JSON处理方式
def process_resume_info():
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT id, resume_info FROM zhilian_resume WHERE resume_processed_info IS NULL LIMIT 1000")
    rows = cursor.fetchall()
    
    for row in rows:
        resume_id = row[0]
        resume_info = row[1]
        
        # 解析和处理JSON
        parsed_data = json.loads(resume_info)
        filtered_data = filter_resume_fields(parsed_data)
        processed_info = json.dumps(filtered_data, ensure_ascii=False)
        
        cursor.execute(
            "UPDATE zhilian_resume SET resume_processed_info = %s WHERE id = %s",
            (processed_info, resume_id)
        )
        connection.commit()
    
    close_db_connection(cursor, connection)
```

#### 迁移后代码
```python
# 新的JSON处理方式
from refactored_processors import ResumeProcessor

def process_resume_info():
    resume_processor = ResumeProcessor()
    updated_count = resume_processor.process_resume_info("zhilian_resume", limit=1000)
    print(f"处理了 {updated_count} 条记录")
```

### 5. 自定义处理器创建

如果现有的处理器不满足需求，可以创建自定义处理器：

```python
from common_db_processor import BaseQueryProcessor, JSONProcessor
from typing import Dict, Any, Optional

class CustomProcessor(JSONProcessor):
    """自定义处理器示例"""
    
    def __init__(self, db_connection=None):
        super().__init__(db_connection)
        # 初始化自定义配置
        self.custom_config = {}
    
    def process_json_data(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """重写JSON处理逻辑"""
        # 实现自定义的JSON处理逻辑
        processed_data = self._apply_custom_rules(json_data)
        return processed_data
    
    def _apply_custom_rules(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """应用自定义规则"""
        # 实现具体的处理规则
        return data
    
    def process_custom_table(self, table_name: str):
        """处理自定义表"""
        from common_db_processor import CommonQueryBuilder
        
        query_sql = CommonQueryBuilder.build_select_with_condition(
            table_name=table_name,
            fields=["id", "data_field"],
            where_condition="status = 'pending'"
        )
        
        update_sql = CommonQueryBuilder.build_update_by_id(
            table_name=table_name,
            update_fields=["processed_field"]
        )
        
        return self.batch_query_and_update(
            query_sql=query_sql,
            update_sql=update_sql
        )
```

## 迁移检查清单

### 代码迁移
- [ ] 替换数据库连接代码
- [ ] 迁移查询和更新逻辑
- [ ] 替换HTML清理代码
- [ ] 迁移JSON处理逻辑
- [ ] 添加错误处理和日志记录
- [ ] 更新导入语句

### 测试验证
- [ ] 验证数据库连接正常
- [ ] 测试查询功能
- [ ] 测试更新功能
- [ ] 验证批量处理性能
- [ ] 检查错误处理机制
- [ ] 验证日志输出

### 性能优化
- [ ] 调整批处理大小
- [ ] 优化查询条件
- [ ] 添加索引支持
- [ ] 监控内存使用

## 常见问题和解决方案

### Q1: 如何处理现有的自定义SQL查询？

**A1**: 可以使用`simple_query`和`simple_update`方法：

```python
processor = BaseQueryProcessor()

# 自定义查询
results = processor.simple_query(
    "SELECT * FROM custom_table WHERE custom_condition = %s",
    (condition_value,)
)

# 自定义更新
affected_rows = processor.simple_update(
    "UPDATE custom_table SET field = %s WHERE condition = %s",
    (new_value, condition_value)
)
```

### Q2: 如何处理事务？

**A2**: 对于复杂事务，可以直接使用数据库连接：

```python
processor = BaseQueryProcessor()
connection = processor.get_connection()
cursor = connection.cursor()

try:
    cursor.execute("BEGIN")
    # 执行多个操作
    cursor.execute("INSERT ...")
    cursor.execute("UPDATE ...")
    connection.commit()
except Exception as e:
    connection.rollback()
    raise e
finally:
    processor.close_connection(cursor, connection)
```

### Q3: 如何处理大量数据？

**A3**: 使用批量处理和适当的批处理大小：

```python
# 调整批处理大小
updated_count = processor.batch_query_and_update(
    query_sql=query_sql,
    update_sql=update_sql,
    batch_size=5000  # 根据内存和性能调整
)
```

### Q4: 如何添加自定义日志？

**A4**: 重写处理器的日志配置：

```python
import logging

class CustomProcessor(BaseQueryProcessor):
    def __init__(self, db_connection=None):
        super().__init__(db_connection)
        # 自定义日志配置
        self.logger = logging.getLogger('CustomProcessor')
        handler = logging.FileHandler('custom.log')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
```

## 总结

重构后的架构提供了更好的代码组织、错误处理和性能优化。通过遵循本迁移指南，可以逐步将现有代码迁移到新架构中，享受更好的开发体验和维护性。

建议采用渐进式迁移策略：
1. 首先迁移数据库连接代码
2. 然后迁移简单的查询和更新逻辑
3. 最后迁移复杂的业务逻辑
4. 在每个步骤后进行充分测试

这样可以确保迁移过程的稳定性和可控性。