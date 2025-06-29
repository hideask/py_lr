# PostgreSQL数据导出工具

这个工具用于从PostgreSQL数据库的指定表中查询指定字段的数据，并将结果保存到Excel文件中。支持单表导出和批量导出，可以通过命令行参数或配置文件指定导出选项。

## 功能特点

- 支持导出指定表的所有字段或指定字段
- 支持批量导出多个表
- 自动创建备份目录
- 备份文件以表名和日期命名
- 支持自定义数据库连接参数
- 支持自定义备份目录
- 提供命令行接口，方便集成到脚本中

## 使用方法

### 命令行参数

```
python pg_to_excel.py [选项]
```

#### 选项说明

- `--table`, `-t`: 要备份的表名
- `--fields`, `-f`: 要备份的字段，用逗号分隔
- `--dbname`: 数据库名称
- `--user`: 数据库用户名
- `--password`: 数据库密码
- `--host`: 数据库主机
- `--port`: 数据库端口
- `--backup-dir`, `-d`: 备份目录路径
- `--list-tables`, `-l`: 列出所有表名
- `--config-file`, `-c`: 批量备份配置文件路径（JSON格式）
- `--help`, `-h`: 显示帮助信息

### 示例

#### 列出所有表名

```
python pg_to_excel.py --list-tables
```

#### 备份单个表的所有字段

```
python pg_to_excel.py --table zhilian_job
```

#### 备份单个表的指定字段

```
python pg_to_excel.py --table zhilian_job --fields "id,job_name,company_name,salary"
```

#### 指定数据库连接参数

```
python pg_to_excel.py --table zhilian_job --dbname mydb --user myuser --password mypass --host localhost --port 5432
```

#### 指定备份目录

```
python pg_to_excel.py --table zhilian_job --backup-dir "D:\backup"
```

#### 使用配置文件批量备份

```
python pg_to_excel.py --config-file backup_config_example.json
```

### 配置文件格式

配置文件是一个JSON数组，每个元素是一个表的配置对象，包含以下字段：

- `table_name`: 表名（必需）
- `fields`: 要备份的字段数组（可选，如果不指定则备份所有字段）

示例配置文件（backup_config_example.json）：

```json
[
    {
        "table_name": "zhilian_job",
        "fields": ["id", "job_name", "company_name", "salary"]
    },
    {
        "table_name": "zhilian_resume"
    },
    {
        "table_name": "user_info",
        "fields": ["id", "username", "email", "create_time"]
    }
]
```

## 编程接口

除了命令行接口外，该工具还提供了编程接口，可以在Python代码中直接调用：

### 备份单个表

```python
from pg_to_excel import backup_table_to_excel

# 备份表的所有字段
backup_table_to_excel('zhilian_job')

# 备份表的指定字段
backup_table_to_excel('zhilian_job', ['id', 'job_name', 'company_name', 'salary'])

# 指定数据库连接参数
db_config = {
    "dbname": "mydb",
    "user": "myuser",
    "password": "mypass",
    "host": "localhost",
    "port": "5432"
}
backup_table_to_excel('zhilian_job', db_config=db_config)

# 指定备份目录
backup_table_to_excel('zhilian_job', backup_dir='D:\\backup')
```

### 批量备份多个表

```python
from pg_to_excel import batch_backup_tables

# 批量备份多个表
tables_config = [
    {'table_name': 'zhilian_job'},  # 备份所有字段
    {'table_name': 'zhilian_resume', 'fields': ['id', 'name', 'age', 'education']}  # 只备份指定字段
]
backup_files = batch_backup_tables(tables_config)
```

## 注意事项

1. 默认情况下，备份文件保存在当前目录下的`backup`目录中
2. 备份文件名格式为`表名_年月日_时分秒.xlsx`
3. 如果指定的备份目录不存在，会自动创建
4. 如果不指定数据库连接参数，将使用默认配置
5. 如果表中的数据量很大，可能需要较长的处理时间