from flask import Flask, jsonify
import mysql.connector



# 数据库连接配置
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'test'
}

# @app.route('/', methods=['GET'])
# def get_scopus_data():
#     try:
#         # 建立数据库连接
#         connection = mysql.connector.connect(**db_config)
#         cursor = connection.cursor(dictionary=True)
#         # 执行查询语句
#         cursor.execute('SELECT * FROM scopus')
#         # 获取查询结果
#         data = cursor.fetchall()
#         # 关闭游标和连接
#         cursor.close()
#         connection.close()
#         return jsonify(data)
#     except mysql.connector.Error as err:
#         return jsonify({'error': str(err)}), 500

