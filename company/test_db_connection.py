#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据库连接重构后的功能
"""

from db_connection import DatabaseConnection, get_db_connection, close_db_connection

def test_database_connection():
    """
    测试数据库连接功能
    """
    print("开始测试数据库连接...")
    
    # 测试1: 使用类方式
    print("\n1. 测试DatabaseConnection类:")
    try:
        db = DatabaseConnection()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # 执行简单查询
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"   数据库版本: {version[0]}")
        
        # 关闭连接
        DatabaseConnection.close_connection(cursor, conn)
        print("   ✓ DatabaseConnection类测试成功")
        
    except Exception as e:
        print(f"   ✗ DatabaseConnection类测试失败: {e}")
    
    # 测试2: 使用向后兼容函数
    print("\n2. 测试向后兼容函数:")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 执行简单查询
        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()
        print(f"   当前数据库: {db_name[0]}")
        
        # 关闭连接
        close_db_connection(cursor, conn)
        print("   ✓ 向后兼容函数测试成功")
        
    except Exception as e:
        print(f"   ✗ 向后兼容函数测试失败: {e}")
    
    # 测试3: 使用自定义配置
    print("\n3. 测试自定义配置:")
    try:
        custom_db = DatabaseConnection(
            dbname="yhaimg",
            user="yhaimg",
            password="Zq*6^pD6g2%JJ!z8",
            host="172.31.255.227",
            port="5588"
        )
        conn = custom_db.get_connection()
        cursor = conn.cursor()
        
        # 执行简单查询
        cursor.execute("SELECT 1 as test_value;")
        result = cursor.fetchone()
        print(f"   测试查询结果: {result[0]}")
        
        # 关闭连接
        custom_db.close_connection(cursor, conn)
        print("   ✓ 自定义配置测试成功")
        
    except Exception as e:
        print(f"   ✗ 自定义配置测试失败: {e}")
    
    print("\n数据库连接测试完成!")

if __name__ == "__main__":
    test_database_connection()