import os
import psycopg2
import pandas as pd
import argparse
from datetime import datetime
from db_connection import DatabaseConnection


def backup_table_to_excel(table_name, fields=None, db_config=None, backup_dir=None):
    """
    从PostgreSQL数据库的指定表中查询指定字段的数据，并将结果保存到Excel文件中。
    
    :param table_name: 要备份的表名
    :param fields: 要查询的字段列表，如果为None，则查询所有字段
    :param db_config: 数据库连接配置，字典格式，包含dbname, user, password, host, port
    :param backup_dir: 备份目录路径，如果为None，则使用当前目录下的'backup'目录
    :return: 备份文件的路径
    """
    # 使用公共数据库连接类
    if db_config is None:
        # 使用默认配置
        db_connection = DatabaseConnection()
    else:
        # 使用自定义配置
        db_connection = DatabaseConnection(
            dbname=db_config.get("dbname", "yhaimg"),
            user=db_config.get("user", "yhaimg"),
            password=db_config.get("password", "Zq*6^pD6g2%JJ!z8"),
            host=db_config.get("host", "172.31.255.227"),
            port=db_config.get("port", "5588")
        )
    
    # 设置备份目录
    if backup_dir is None:
        backup_dir = os.path.join(os.getcwd(), 'backup')
    
    try:
        # 连接PostgreSQL数据库
        conn = db_connection.get_connection()
        
        # 创建游标
        cursor = conn.cursor()
        
        # 构建SQL查询
        if fields is None:
            # 获取表的所有字段
            cursor.execute(f"""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
            """)
            fields = [row[0] for row in cursor.fetchall()]
            query = f"SELECT * FROM {table_name}"
        else:
            # 使用指定的字段
            query = f"SELECT {', '.join(fields)} FROM {table_name}"
        
        # 执行查询
        cursor.execute(query)
        
        # 获取查询结果
        data = cursor.fetchall()
        
        # 创建DataFrame
        df = pd.DataFrame(data, columns=fields)
        
        # 创建备份目录
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # 生成备份文件名（表名+日期）
        current_date = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f"{table_name}_{current_date}.xlsx")
        
        # 将数据保存到Excel文件
        df.to_excel(backup_file, index=False)
        
        print(f"成功备份表 {table_name} 到文件 {backup_file}")
        print(f"共备份 {len(data)} 条记录，字段：{', '.join(fields)}")
        
        # 关闭连接
        cursor.close()
        conn.close()
        
        return backup_file
    
    except Exception as e:
        print(f"备份表 {table_name} 时出错：{str(e)}")
        return None


def batch_backup_tables(tables_config, db_config=None, backup_dir=None):
    """
    批量备份多个表到Excel文件
    
    :param tables_config: 表配置列表，每个元素是一个字典，包含'table_name'和可选的'fields'
    :param db_config: 数据库连接配置
    :param backup_dir: 备份目录路径
    :return: 备份文件路径列表
    """
    backup_files = []
    
    for config in tables_config:
        table_name = config['table_name']
        fields = config.get('fields', None)  # 如果没有指定fields，则为None
        
        backup_file = backup_table_to_excel(
            table_name=table_name,
            fields=fields,
            db_config=db_config,
            backup_dir=backup_dir
        )
        
        if backup_file:
            backup_files.append(backup_file)
    
    return backup_files


def get_all_tables(db_config=None):
    """
    获取数据库中的所有表名
    
    :param db_config: 数据库连接配置
    :return: 表名列表
    """
    # 默认数据库配置
    default_db_config = {
        "dbname": "yhaimg",
        "user": "yhaimg",
        "password": "Zq*6^pD6g2%JJ!z8",
        "host": "172.31.255.227",
        "port": "5588"
    }
    
    # 使用提供的配置或默认配置
    if db_config is None:
        db_config = default_db_config
    else:
        # 合并配置，确保所有必要的键都存在
        for key, value in default_db_config.items():
            if key not in db_config:
                db_config[key] = value
    
    try:
        # 连接PostgreSQL数据库
        conn = psycopg2.connect(
            dbname=db_config["dbname"],
            user=db_config["user"],
            password=db_config["password"],
            host=db_config["host"],
            port=db_config["port"]
        )
        
        # 创建游标
        cursor = conn.cursor()
        
        # 查询所有表名
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        
        # 关闭连接
        cursor.close()
        conn.close()
        
        return tables
    
    except Exception as e:
        print(f"获取表名列表时出错：{str(e)}")
        return []


def parse_arguments():
    """
    解析命令行参数
    
    :return: 解析后的参数
    """
    parser = argparse.ArgumentParser(description='从PostgreSQL数据库备份表数据到Excel文件')
    
    # 添加参数
    parser.add_argument('--table', '-t', type=str, help='要备份的表名')
    parser.add_argument('--fields', '-f', type=str, help='要备份的字段，用逗号分隔')
    parser.add_argument('--dbname', type=str, help='数据库名称')
    parser.add_argument('--user', type=str, help='数据库用户名')
    parser.add_argument('--password', type=str, help='数据库密码')
    parser.add_argument('--host', type=str, help='数据库主机')
    parser.add_argument('--port', type=str, help='数据库端口')
    parser.add_argument('--backup-dir', '-d', type=str, help='备份目录路径')
    parser.add_argument('--list-tables', '-l', action='store_true', help='列出所有表名')
    parser.add_argument('--config-file', '-c', type=str, help='批量备份配置文件路径（JSON格式）')
    
    return parser.parse_args()


def main():
    """
    主函数，处理命令行参数并执行相应的操作
    """
    args = parse_arguments()
    
    # 构建数据库配置
    db_config = {}
    if args.dbname:
        db_config['dbname'] = args.dbname
    if args.user:
        db_config['user'] = args.user
    if args.password:
        db_config['password'] = args.password
    if args.host:
        db_config['host'] = args.host
    if args.port:
        db_config['port'] = args.port
    
    # 如果db_config为空，则使用默认配置
    if not db_config:
        db_config = None
    
    # 列出所有表名
    if args.list_tables:
        tables = get_all_tables(db_config)
        print("数据库中的所有表：")
        for table in tables:
            print(f"  - {table}")
        return
    
    # 从配置文件批量备份
    if args.config_file:
        import json
        try:
            with open(args.config_file, 'r') as f:
                tables_config = json.load(f)
            
            backup_files = batch_backup_tables(
                tables_config=tables_config,
                db_config=db_config,
                backup_dir=args.backup_dir
            )
            
            print(f"批量备份完成，共备份 {len(backup_files)} 个表")
            return
        except Exception as e:
            print(f"读取配置文件时出错：{str(e)}")
            return
    
    # 备份单个表
    if args.table:
        fields = None
        if args.fields:
            fields = [field.strip() for field in args.fields.split(',')]
        
        backup_table_to_excel(
            table_name=args.table,
            fields=fields,
            db_config=db_config,
            backup_dir=args.backup_dir
        )
        return
    
    # 如果没有指定操作，显示帮助信息
    print("请指定要备份的表名或使用 --list-tables 列出所有表名")
    print("使用 --help 查看帮助信息")


if __name__ == '__main__':
    # main()
    tables_config = [
        {'table_name': 'zhilian_job'},
        {'table_name': 'zhilian_resume'},
        # {'table_name': 'sc_pub_recruitmentnet_job'},
        # {'table_name': 'sc_pub_recruitmentnet_resume'}
    ]
    backup_files = batch_backup_tables(
        tables_config=tables_config,
    )
    print(f"批量备份完成，共备份 {len(backup_files)} 个表")
