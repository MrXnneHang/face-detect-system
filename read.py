import mysql.connector
from mysql.connector import Error
import argparse
import numpy as np
import json

def read(database='faces', table='users'):
    """
    读取faces数据库中的users表
    需要先开启MYSQL,设置对root和password才能连接上。
    """
    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',
            port=3306,
            database=database,
            user='root',
            password='123456'
        )

        if connection.is_connected():
            print(f"成功连接到 MySQL 数据库: {database}")

            cursor = connection.cursor()

            if table:
                # 读取指定表的数据
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                # print(rows)
            else:
                # 获取所有表的列表
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                for (table_name,) in tables:
                    print(f"\n{table_name} 表中的数据：")
                    cursor.execute(f"SELECT * FROM {table_name}")
                    rows = cursor.fetchall()
                    for row in rows:
                        print(row)

    except Error as e:
        print(f"连接到 MySQL 出现错误: {e}")

    finally:
        try:
            if connection.is_connected():
                cursor.close()
                connection.close()
                print("MySQL 数据库连接已关闭")
                return rows
        except NameError:
            pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="读取 MySQL 数据库中的数据")
    parser.add_argument("--database", default="faces", help="指定要连接的数据库名称")
    parser.add_argument("--table", default="users", help="指定要读取的表名称，如果未指定，则读取所有表的数据")
    
    args = parser.parse_args()
    
    read(database=args.database, table=args.table)
