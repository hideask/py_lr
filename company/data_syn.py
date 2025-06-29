from datetime import datetime

import cx_Oracle
import psycopg2
from db_connection import get_db_connection

# 连接 Oracle 数据库
dsn = cx_Oracle.makedsn('192.168.26.10', '1521', service_name='rsjydev')
ora_conn = cx_Oracle.connect(user="yhaimq", password="yhaimq", dsn=dsn)
# 连接 PostgreSQL 数据库
pg_conn = get_db_connection()

i = 0
# 创建游标
ora_cursor = ora_conn.cursor()
pg_cursor = pg_conn.cursor()

def get_oracle_table_columns(ora_cursor, table_name):
    """
    获取 Oracle 表的字段名列表。

    :param ora_cursor: Oracle 数据库游标对象
    :param table_name: 表名
    :return: 字段名列表
    """
    ora_cursor.execute(f"""
        SELECT column_name
        FROM all_tab_columns
        WHERE table_name = UPPER('{table_name}')
        ORDER BY column_id
    """)
    columns = list(dict.fromkeys([row[0].lower() for row in ora_cursor.fetchall()]))
    return columns

def get_oracle_table_structure(ora_cursor, table_name):
    """
    获取 Oracle 表的结构信息。

    :param ora_cursor: Oracle 数据库游标对象
    :param table_name: 表名
    :return: 表结构信息字典
    """
    # 获取列信息
    ora_cursor.execute(f"""
        SELECT column_name, data_type, data_length, nullable, data_default
        FROM all_tab_columns
        WHERE table_name = UPPER('{table_name}')
        ORDER BY column_id
    """)
    columns = ora_cursor.fetchall()

    # 获取主键信息
    ora_cursor.execute(f"""
        SELECT cols.column_name
        FROM all_constraints cons
        JOIN all_cons_columns cols
        ON cons.constraint_name = cols.constraint_name
        WHERE cons.constraint_type = 'P'
        AND cons.table_name = UPPER('{table_name}')
    """)
    primary_keys = [row[0].lower() for row in ora_cursor.fetchall()]

    # 获取唯一约束信息
    ora_cursor.execute(f"""
        SELECT cols.column_name
        FROM all_constraints cons
        JOIN all_cons_columns cols
        ON cons.constraint_name = cols.constraint_name
        WHERE cons.constraint_type = 'U'
        AND cons.table_name = UPPER('{table_name}')
    """)
    unique_constraints = [row[0].lower() for row in ora_cursor.fetchall()]

    return {
        'columns': columns,
        'primary_keys': primary_keys,
        'unique_constraints': unique_constraints
    }

def create_oracle_table(ora_cursor, table_name, table_structure):
    """
    在 Oracle 数据库中创建表。

    :param ora_cursor: Oracle 数据库游标对象
    :param table_name: 表名
    :param table_structure: 表结构信息字典
    """
    columns = table_structure['columns']
    primary_keys = table_structure['primary_keys']
    unique_constraints = table_structure['unique_constraints']

    # 构建列定义
    column_definitions = []
    for column in columns:
        column_name, data_type, char_max_length, is_nullable, column_default = column
        if data_type == 'integer':
            ora_data_type = 'NUMBER'
        elif data_type == 'bigint':
            ora_data_type = 'NUMBER(19)'
        elif data_type == 'smallint':
            ora_data_type = 'NUMBER(5)'
        elif data_type == 'character varying':
            ora_data_type = f'VARCHAR2({char_max_length})'
        elif data_type == 'text':
            ora_data_type = 'CLOB'
        elif data_type == 'timestamp without time zone':
            ora_data_type = 'TIMESTAMP'
        elif data_type == 'boolean':
            ora_data_type = 'NUMBER(1)'
        else:
            ora_data_type = data_type

        if column_default:
            column_definition = f"{column_name} {ora_data_type} DEFAULT {column_default}"
        else:
            column_definition = f"{column_name} {ora_data_type}"

        if is_nullable == 'NO':
            column_definition += " NOT NULL"

        column_definitions.append(column_definition)

    # 构建主键约束
    primary_key_constraint = ""
    if primary_keys:
        primary_key_constraint = f", PRIMARY KEY ({', '.join(primary_keys)})"

    # 构建唯一约束
    unique_constraints_sql = ""
    for unique_column in unique_constraints:
        unique_constraints_sql += f", CONSTRAINT uk_{table_name}_{unique_column} UNIQUE ({unique_column})"

    # 构建完整的 SQL 创建表语句
    sql = f"""
        CREATE TABLE {table_name} (
            {', '.join(column_definitions)}
            {primary_key_constraint}
            {unique_constraints_sql}
        )
    """
    try:
        ora_cursor.execute(sql)
        print(f"Table {table_name} created successfully.")
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(f"Error creating table {table_name}: {error.message}")


def get_postgresql_table_columns(pg_cursor, table_name):
    """
    获取 PostgreSQL 表的字段名列表。

    :param pg_cursor: PostgreSQL 数据库游标对象
    :param table_name: 表名
    :return: 字段名列表
    """
    pg_cursor.execute(f"""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = '{table_name}'
        ORDER BY ordinal_position
    """)
    columns = [row[0] for row in pg_cursor.fetchall()]
    return columns
def get_postgresql_table_structure(pg_cursor, table_name):
    """
    获取 PostgreSQL 表的结构信息。

    :param pg_cursor: PostgreSQL 数据库游标对象
    :param table_name: 表名
    :return: 表结构信息字典
    """
    # 获取列信息
    pg_cursor.execute(f"""
        SELECT column_name, data_type, character_maximum_length, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = '{table_name}'
        ORDER BY ordinal_position
    """)
    columns = pg_cursor.fetchall()

    # 获取主键信息
    pg_cursor.execute(f"""
        SELECT kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
        ON tc.constraint_name = kcu.constraint_name
        WHERE tc.constraint_type = 'PRIMARY KEY'
        AND tc.table_name = '{table_name}'
    """)
    primary_keys = [row[0] for row in pg_cursor.fetchall()]

    # 获取唯一约束信息
    pg_cursor.execute(f"""
        SELECT kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
        ON tc.constraint_name = kcu.constraint_name
        WHERE tc.constraint_type = 'UNIQUE'
        AND tc.table_name = '{table_name}'
    """)
    unique_constraints = [row[0] for row in pg_cursor.fetchall()]

    return {
        'columns': columns,
        'primary_keys': primary_keys,
        'unique_constraints': unique_constraints
    }

def create_postgresql_table(pg_cursor, table_name, table_structure):
    """
    在 PostgreSQL 数据库中创建表。

    :param pg_cursor: PostgreSQL 数据库游标对象
    :param table_name: 表名
    :param table_structure: 表结构信息字典
    """
    columns = table_structure['columns']
    primary_keys = table_structure['primary_keys']
    unique_constraints = table_structure['unique_constraints']

    # 构建列定义
    column_definitions = []
    for column in columns:
        column_name, data_type, data_length, nullable, data_default = column
        if data_type == 'NUMBER':
            if data_length == 1:
                pg_data_type = 'BOOLEAN'
            elif data_length == 5:
                pg_data_type = 'SMALLINT'
            elif data_length == 19:
                pg_data_type = 'BIGINT'
            else:
                pg_data_type = 'INTEGER'
        elif data_type == 'VARCHAR2':
            pg_data_type = f'VARCHAR({data_length})'
        elif data_type == 'CLOB':
            pg_data_type = 'TEXT'
        elif data_type == 'TIMESTAMP':
            pg_data_type = 'TIMESTAMP WITHOUT TIME ZONE'
        else:
            pg_data_type = data_type

        if data_default:
            column_definition = f"{column_name} {pg_data_type} DEFAULT {data_default}"
        else:
            column_definition = f"{column_name} {pg_data_type}"

        if nullable == 'N':
            column_definition += " NOT NULL"

        column_definitions.append(column_definition)

    # 构建主键约束
    primary_key_constraint = ""
    if primary_keys:
        primary_key_constraint = f", PRIMARY KEY ({', '.join(primary_keys)})"

    # 构建唯一约束
    unique_constraints_sql = ""
    for unique_column in unique_constraints:
        unique_constraints_sql += f", CONSTRAINT uk_{table_name}_{unique_column} UNIQUE ({unique_column})"

    # 构建完整的 SQL 创建表语句
    sql = f"""
        CREATE TABLE {table_name} (
            {', '.join(column_definitions)}
            {primary_key_constraint}
            {unique_constraints_sql}
        )
    """
    try:
        pg_cursor.execute(sql)
        print(f"Table {table_name} created successfully.")
    except psycopg2.Error as e:
        print(f"Error creating table {table_name}: {e}")

def check_oracle_table_exists(ora_cursor, table_name):
    """
    检查 Oracle 数据库中是否存在指定的表。

    :param ora_cursor: Oracle 数据库游标对象
    :param table_name: 表名
    :return: 如果表存在返回 True，否则返回 False
    """
    ora_cursor.execute(f"""
        SELECT COUNT(*)
        FROM all_tables
        WHERE table_name = UPPER('{table_name}')
    """)
    count = ora_cursor.fetchone()[0]
    return count > 0

def check_postgresql_table_exists(pg_cursor, table_name):
    """
    检查 PostgreSQL 数据库中是否存在指定的表。

    :param pg_cursor: PostgreSQL 数据库游标对象
    :param table_name: 表名
    :return: 如果表存在返回 True，否则返回 False
    """
    pg_cursor.execute(f"""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_name = '{table_name}'
    """)
    count = pg_cursor.fetchone()[0]
    return count > 0
def drop_oracle_table(ora_cursor, table_name):
    """
    删除 Oracle 数据库中的指定表。

    :param ora_cursor: Oracle 数据库游标对象
    :param table_name: 表名
    """
    try:
        ora_cursor.execute(f"DROP TABLE {table_name} CASCADE CONSTRAINTS")
        print(f"Table {table_name} dropped successfully.")
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(f"Error dropping table {table_name}: {error.message}")

def drop_postgresql_table(pg_cursor, table_name):
    """
    删除 PostgreSQL 数据库中的指定表。

    :param pg_cursor: PostgreSQL 数据库游标对象
    :param table_name: 表名
    """
    try:
        pg_cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
        print(f"Table {table_name} dropped successfully.")
    except psycopg2.Error as e:
        print(f"Error dropping table {table_name}: {e}")
def sync_tables(target_cursor, source_cursor, table_names, source_db_type, target_db_type):
    """
    将多个表的数据从 PostgreSQL 同步到 Oracle。

    :param target_cursor: 目标数据库游标对象（Oracle 或 PostgreSQL）
    :param source_cursor: 源数据库游标对象（PostgreSQL 或 Oracle）
    :param table_names: 表名列表
    :param target_db_type: 目标数据库类型，'oracle' 或 'postgresql'
    """
    for table_name in table_names:
        print(f"Processing table: {table_name}")

        # 根据源数据库类型获取表结构
        if source_db_type == 'oracle':
            source_structure = get_oracle_table_structure(source_cursor, table_name)
        elif source_db_type == 'postgresql':
            source_structure = get_postgresql_table_structure(source_cursor, table_name)
        else:
            print(f"Unsupported source database type: {source_db_type}. Skipping.")
            continue

        # 根据目标数据库类型检查表是否存在。酌情使用，可能会导致误删；同时因为pg和Oracle对中文长度计算不一致，可能Oracle里面存中文按照pg的长度定义会导致报错
        # if target_db_type == 'oracle':
        #     if check_oracle_table_exists(target_cursor, table_name):
        #         drop_oracle_table(target_cursor, table_name)
        #     create_oracle_table(target_cursor, table_name, source_structure)
        # elif target_db_type == 'postgresql':
        #     if check_postgresql_table_exists(target_cursor, table_name):
        #         drop_postgresql_table(target_cursor, table_name)
        #     create_postgresql_table(target_cursor, table_name, source_structure)
        # else:
        #     print(f"Unsupported target database type: {target_db_type}. Skipping.")
        #     continue

        # 获取目标数据库的字段名
        if target_db_type == 'oracle':
            target_columns = get_oracle_table_columns(target_cursor, table_name)
        elif target_db_type == 'postgresql':
            target_columns = get_postgresql_table_columns(target_cursor, table_name)

        # 获取源数据库的字段名
        source_columns = [col[0].lower() for col in source_structure['columns']]

        # 确保字段名一致
        if set(source_columns) != set(target_columns):
            print(f"Columns mismatch for table {table_name}. Skipping.")
            continue

        # 查询 PostgreSQL 数据
        source_cursor.execute(f"SELECT * FROM {table_name}")
        data = source_cursor.fetchall()

        # 删除 Oracle 中的数据
        target_cursor.execute(f"DELETE FROM {table_name}")

        i = 0
        # 插入数据到 Oracle
        for row in data:
            insert_into_table(target_cursor, table_name, target_columns, row, target_db_type)
            print(f"syn table {table_name}: {i + 1}")
            i += 1

        # 提交事务
        ora_conn.commit()
        print(f"Data synced for table: {table_name}")


def insert_into_table(cursor, table_name, columns, row, target_db_type):
    """
    将数据插入到指定的表中。

    :param cursor: 数据库游标对象
    :param table_name: 目标表名
    :param columns: 字段名列表
    :param row: 要插入的数据行（元组或列表）
    :param target_db_type: 目标数据库类型，'oracle' 或 'postgresql'
    """
    # 构建列名字符串
    columns_str = ', '.join(columns)

    # 根据目标数据库类型选择占位符
    if target_db_type == 'oracle':
        placeholders = ', '.join([f':{i + 1}' for i in range(len(columns))])
    elif target_db_type == 'postgresql':
        placeholders = ', '.join(['%s'] * len(columns))
    else:
        print(f"Unsupported target database type: {target_db_type}. Skipping.")
        return

    # 构建完整的 SQL 插入语句
    sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"

    # 执行插入操作
    try:
        # 打印插入语句
        print(f"Executing SQL: {sql}")
        cursor.execute(sql, row)
    except Exception as e:
        print(f"Error inserting into table {table_name}: {e}")


# 定义表名和字段名的字典
# table_dict = {
#     "t_business_tag": [
#         "id", "tag_name", "create_time", "update_time", "create_by", "update_by", "valid_status"
#     ],
    # "taresource": [
    #     "resourceid", "presourceid", "name", "code", "syscode", "url", "orderno", "idpath", "namepath", "resourcelevel",
    #     "icon", "iconcolor", "securitypolicy", "securitylevel", "resourcetype", "effective", "isdisplay",
    #     "isfiledscontrol",
    #     "createdate", "createuser", "uiauthoritypolicy", "field01", "field02", "field03", "field04", "field05",
    #     "field06",
    #     "field07", "field08", "field09", "field10", "workbench", "image"
    # ],
    # 可以继续添加其他表和字段
# }

# 定义表名列表
table_names = [
    # "t_business_tag_copy1",
    # "t_business_tag",
    # "t_business_tag_data_relation",
    # "t_business_tag_group",
    # "t_business_tag_group_relation",
    # "t_business_tag_group_metadata_relation",
    # "t_faq_management",
    # "t_government_service",
    # "t_government_service_channel",
    # "t_policy_interpretation",
    # "t_policy_management",

    # "t_service_info",
    # "t_interface_info",
    # "t_message_conversion"
    # "t_faq_management",
    # "t_business_tag",
    # "t_business_tag_data_relation"
    "t_service_info",
    "t_interface_info"
    # 可以继续添加其他表
]

# 同步数据
sync_tables(target_cursor=ora_cursor, source_cursor=pg_cursor, table_names=table_names, source_db_type='postgresql', target_db_type='oracle')

# 关闭连接
ora_cursor.close()
ora_conn.close()
pg_cursor.close()
pg_conn.close()
