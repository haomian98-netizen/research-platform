import pymysql


def keyword_to_database(user_input):
    """
    将用户输入的关键词保存到数据库
    返回True表示插入成功，返回False表示插入失败（已存在或出错）
    """
    connection = None
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='test',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        with connection.cursor() as cursor:
            # 创建表（如果不存在）
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS `keyword_table` (
                id INT AUTO_INCREMENT PRIMARY KEY,
                keyword TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_keyword (keyword(255))
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
            cursor.execute(create_table_sql)

            # 插入关键词（使用INSERT IGNORE自动处理重复）
            insert_sql = "INSERT IGNORE INTO `keyword_table` (keyword) VALUES (%s)"
            cursor.execute(insert_sql, (user_input,))

            # 判断插入是否成功（rowcount > 0表示有新记录插入）
            return cursor.rowcount > 0

    except pymysql.Error:
        # 发生错误时返回False
        return False
    finally:
        if connection:
            connection.close()


# 使用示例
if __name__ == "__main__":
    user_keyword = input("请输入关键词: ")

    if keyword_to_database(user_keyword):
        print("插入成功，执行后续操作...")
        # 后续操作代码
    else:
        print("插入失败（可能已存在或发生错误）")