from nltk.corpus.reader import titles
# from testfile.testdata import cleaned_result
from crawler.crawl_to_sql import crawl_and_store
from database.AImodel import predict_future_changes
from database.AImodel import get_last_cleaned_text
from database.AImodel import predict_future_changes_complement
from flask import Flask, request, jsonify,session
import time  # 用于模拟处理延迟
from collections import Counter
import os
import spacy
import json
from flask import send_from_directory
import mysql.connector
from config.fetch_from_sql import db_config
from flask_cors import CORS
from database.keyword import keyword_to_database
from crawler.crawl_to_sql import crawl_and_store_complement
from crawler.wordfrequency import countfrequent
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

app = Flask(__name__,static_folder='static', static_url_path='')
app.secret_key = os.environ.get('FLASK_SECRET_KEY') or os.urandom(24)
CORS(app, supports_credentials=True)

# # 定义需要定时更新的关键词列表
# KEYWORDS_TO_UPDATE = [
#     "social media",
#     "artificial intelligence",
#     "machine learning"
#     # 添加更多需要更新的关键词
# ]
#
# def update_keyword_data(keyword):
#     """更新单个关键词的数据"""
#     try:
#         print(f"开始更新关键词: {keyword} - {datetime.now()}")
#         # 获取旧的结果
#         old_result = get_last_cleaned_text(keyword)
#
#         # 使用第二条逻辑更新数据
#         crawl_data = crawl_and_store_complement(keyword, 9)
#
#         if crawl_data:  # 如果有新数据
#             # 提取年份和摘要并格式化
#             formatted_items = [f"{item['年份']}{item['摘要']}" for item in crawl_data]
#             content = "|".join(formatted_items)
#
#             # 更新预测结果
#             thinking, prediction = predict_future_changes(content, keyword, old_result)
#             print(f"关键词 {keyword} 更新完成")
#         else:
#             print(f"关键词 {keyword} 没有新数据需要更新")
#
#     except Exception as e:
#         print(f"更新关键词 {keyword} 时发生错误: {str(e)}")
#
# def scheduled_update():
#     """定时更新所有关键词的任务"""
#     print(f"开始定时更新任务 - {datetime.now()}")
#     for keyword in KEYWORDS_TO_UPDATE:
#         update_keyword_data(keyword)
#     print(f"定时更新任务完成 - {datetime.now()}")
#
# # 创建调度器
# scheduler = BackgroundScheduler()
#
# # 添加定时任务，每天早上9点执行
# scheduler.add_job(
#     func=scheduled_update,
#     trigger=CronTrigger(hour=9, minute=0),
#     id='daily_update',
#     name='Update keywords data daily at 9:00 AM',
#     replace_existing=True
# )
#
# # 启动调度器
# scheduler.start()
#
# # 在应用关闭时关闭调度器
# @app.teardown_appcontext
# def shutdown_scheduler(exception=None):
#     scheduler.shutdown()

@app.route('/api/predict', methods=['POST'])
def predict():

    data = request.get_json()
    user_input = data.get('query', '').strip()

    old_result=get_last_cleaned_text(user_input)  #获取旧的结果
    # 共享变量
    # session['user_input'] = user_input
    # 硬编码的answer补充完整字段（与前端期望一致）


    # answer_json = json.dumps(answer, ensure_ascii=False)
    # 获取预测结果
    try:
        if  keyword_to_database(user_input):  #如果关键词能插入表，说明该关键词是第一次输入，执行第一条逻辑

            crawl_data = crawl_and_store(user_input,9)
            # 提取年份和摘要并格式化
            formatted_items = [f"{item['年份']}{item['摘要']}" for item in crawl_data]
            # # # titles=[item['摘要'] for item in crawl_data]
            content = "|".join(formatted_items)
            # # print(content)
            # # # # 用竖线连接所有格式化后的条目
            # # # content = "|".join(formatted_items)
            thinking,prediction=predict_future_changes_complement(content,user_input,old_result)  #思考，旧的结果进行更新

            print(type(prediction))
    #         # 检查返回值有效性（避免返回None）
    #         # if not answer:
    #         #     raise ValueError("AI model returned empty data")
    #         # print("AI model output")
    #         # print("后端返回的answer:", answer)
    #
    # #要导入的是json字符串，不需要进行loads或dumps进行对象类型转换。

            # try:
            #     # 在 predict 函数中：


            # prediction = json.loads(answer)
            # prediction=json.dumps(prediction)


            # except json.JSONDecodeError as e:
            #     print(f"JSON解析失败: {answer}")
            #     return jsonify({
            #         "error": "Invalid JSON from AI model",
            #         "message": str(e)
            #     }), 400

            return jsonify({
                "paragraphs":prediction ,
                "format": "segmented"
            })
        else:
            crawl_data = crawl_and_store_complement(user_input, 9)  #按日期最新排序，查询最新文献
            # 提取年份和摘要并格式化
            formatted_items = [f"{item['年份']}{item['摘要']}" for item in crawl_data]
            # # # titles=[item['摘要'] for item in crawl_data]
            content = "|".join(formatted_items)
            thinking, prediction = predict_future_changes(content, user_input,old_result)  # 思考，答案，json格式
            return jsonify({
                "paragraphs": prediction,
                "format": "segmented"
            })


    except Exception as e:  # 捕获所有异常并返回错误响应
        print(f"获取失败: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": "Failed to generate prediction"
        }), 500  # 显式返回500错误响应

@app.route('/api/echarts_data', methods=['GET'])
def get_echarts_data():
    user_input = request.args.get('user_input')
    titles = request.args.get('titles')
    print("titles in echarts_data:", titles)  # 新增日志
    if not titles:
        return jsonify({'error': 'Titles not available'}), 400
    try:
        titles = json.loads(titles)
        all_text = " ".join(titles)
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(all_text)
        filtered_tokens = [token.text.lower() for token in doc if not token.is_stop and not token.is_punct and not token.is_space]
        word_freq = Counter(filtered_tokens)
        top_words = word_freq.most_common(10)
        print("top_words:", top_words)  # 新增日志
        echarts_data = [{"value": freq, "name": word} for word, freq in top_words]
        legend_data = [word for word, _ in top_words]
        return jsonify({
            "echarts_data": echarts_data,
            "legend_data": legend_data
        })
    except Exception as e:
        return jsonify({'error': f'Error generating ECharts data: {str(e)}'}), 500

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )
@app.route('/')
def index():
    return app.send_static_file('index.html')
@app.route('/api/at_prediction', methods=['GET'])
def get_at_prediction():
    table_name = request.args.get('table_name')
    if not table_name:
        return jsonify({'error': 'Missing table_name parameter'}), 400
    try:
        connection = mysql.connector.connect(**db_config)
        with connection.cursor(dictionary=True) as cursor:
            # 参数化查询（注意：表名不能参数化，需直接拼接）
            cursor.execute(f"""
                SELECT thinking, cleaned_text AS prediction 
                FROM `{table_name}` 
                ORDER BY created_at DESC 
                LIMIT 1
            """)
            result = cursor.fetchone()

        if not result:
            return jsonify({'error': 'Data not found'}), 404

        return jsonify({
            "thinking": result['thinking'],
            "prediction": result['prediction']
        })

    except Exception as err:
        return jsonify({'error': str(err)}), 500
    finally:
        if connection:
            connection.close()

@app.route('/api/scopus', methods=['GET'])
def get_scopus_data():
    user_input = request.args.get('user_input')
    if not user_input:
        return jsonify({'error': 'User session expired'}), 400
    table_name = user_input
    # 验证表名合法性（防止 SQL 注入）
    if not table_name:
        return jsonify({'error': 'Missing table_name parameter'}), 400
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        # 执行查询语句，获取精简数据
        cursor.execute(f'''
            SELECT *
            FROM `{table_name}`
            ORDER BY year DESC
        ''')

        data = cursor.fetchall()
        cursor.close()
        connection.close()

        return jsonify(data)
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500

@app.route('/api/search_keywords', methods=['GET'])
def search_keywords():
    search_term = request.args.get('term', '')
    print(f"Searching for term: {search_term}")  # 添加日志
    
    if not search_term:
        return jsonify([])
    
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        # 修改查询语句，使用更宽松的匹配
        query = """
            SELECT DISTINCT keyword 
            FROM keyword_table 
            WHERE LOWER(keyword) LIKE LOWER(%s)
            LIMIT 10
        """
        search_pattern = f'%{search_term}%'
        print(f"Executing query with pattern: {search_pattern}")  # 添加日志
        
        cursor.execute(query, (search_pattern,))
        results = [row['keyword'] for row in cursor.fetchall()]
        print(f"Found results: {results}")  # 添加日志
        
        return jsonify(results)
        
    except Exception as e:
        print(f"Error in search_keywords: {str(e)}")  # 添加错误日志
        return jsonify({'error': str(e)}), 500
    finally:
        if connection:
            connection.close()

@app.route('/api/get_keyword_result', methods=['GET'])
def get_keyword_result():
    keyword = request.args.get('keyword', '')
    print(f"Getting result for keyword: {keyword}")
    
    if not keyword:
        return jsonify({'error': 'No keyword provided'}), 400
    
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        # 修改表名处理，确保安全
        table_name = f"{keyword}_result"
        print(f"Querying table: {table_name}")
        
        # 获取指定关键词的最新结果
        query = f"""
            SELECT cleaned_text, created_at
            FROM `{table_name}` 
            ORDER BY created_at DESC 
            LIMIT 1
        """
        cursor.execute(query)
        
        result = cursor.fetchone()
        if result:
            print("Result found")
            try:
                # 尝试解析JSON数据
                cleaned_text = result['cleaned_text']
                if isinstance(cleaned_text, str):
                    # 如果结果是字符串，尝试解析为JSON
                    json_data = json.loads(cleaned_text)
                    return jsonify({
                        'result': cleaned_text,
                        'created_at': result['created_at'].isoformat() if result['created_at'] else None
                    })
                else:
                    # 如果结果已经是JSON对象
                    return jsonify({
                        'result': json.dumps(cleaned_text),
                        'created_at': result['created_at'].isoformat() if result['created_at'] else None
                    })
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {str(e)}")
                return jsonify({'error': 'Invalid JSON data'}), 500
        else:
            print("No result found")
            return jsonify({'error': 'No result found'}), 404
            
    except Exception as e:
        print(f"Error in get_keyword_result: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        if connection:
            connection.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)