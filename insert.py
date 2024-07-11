import mysql.connector
from mysql.connector import Error
import numpy as np
import json

# 示例用户数据
users_data = [
    ('2210613141', '张三', np.around(np.random.randn(1, 512), decimals=4).tolist()),
    ('2210613142', '李四', np.around(np.random.randn(1, 512), decimals=4).tolist())
]

def delete_table_if_exists(cursor):
    # 删除表的 SQL 语句
    drop_table_query = "DROP TABLE IF EXISTS users"
    cursor.execute(drop_table_query)

def create_table_if_not_exists(cursor):
    # 创建表的 SQL 语句
    create_table_query = """
    CREATE TABLE IF NOT EXISTS users (
        id VARCHAR(255) PRIMARY KEY,
        name VARCHAR(255),
        feature LONGTEXT
    )
    """
    cursor.execute(create_table_query)

def insert(users_data):
    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',
            port=3306,
            database='faces',
            user='root',
            password='123456'
        )

        if connection.is_connected():
            print("成功连接到 MySQL 数据库")

            cursor = connection.cursor()

            delete_table_if_exists(cursor)
            # 创建表如果它不存在
            create_table_if_not_exists(cursor)

            # 插入或更新用户数据
            for user in users_data:
                id, name, feature = user
                feature_str = json.dumps(feature)
                print(f"Inserting: id={id}, name={name}, feature_length={len(feature_str)}")

                # 插入前检查是否已存在相同的主键值
                select_query = "SELECT COUNT(*) FROM users WHERE id = %s"
                cursor.execute(select_query, (id,))
                count = cursor.fetchone()[0]

                if count == 0:
                    # 如果不存在，插入新数据
                    insert_query = "INSERT INTO users (id, name, feature) VALUES (%s, %s, %s)"
                    data_to_insert = (id, name, feature_str)
                    cursor.execute(insert_query, data_to_insert)
                    connection.commit()
                    print(f"已成功插入用户 {name} 的数据")
                else:
                    # 如果存在，更新已有数据
                    update_query = "UPDATE users SET name = %s, feature = %s WHERE id = %s"
                    data_to_update = (name, feature_str, id)
                    cursor.execute(update_query, data_to_update)
                    connection.commit()
                    print(f"已成功更新用户 {name} 的数据")

            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()

            print("users 表中的所有数据：")
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
        except NameError:
            pass

if __name__ == '__main__':
    insert(users_data)
