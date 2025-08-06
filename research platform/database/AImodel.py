from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
import re
from openai import OpenAI
from openpyxl import Workbook, load_workbook
import os
import pymysql
import json
from datetime import datetime
from openpyxl.utils import get_column_letter
# 输入Deepseek返回思考和答案
# 定义Excel文件路径
EXCEL_PATH = r"D:\课堂资料\Australia\thinking_log.xlsx"



def predict_future_changes(title,user_input):
    try:
        client = OpenAI(
            api_key="sk-rQ7tiidourAF6BSI1scFwx8FAKTr7xlrFfsRdYGaWKHjy5bU",
            base_url="https://api.lkeap.cloud.tencent.com/v1",
        )
        content = f"""{title}
                These are around 100 papers' publication years and abstract contents.Now I want to write a literature review. please summarize them in detail and comprehensively the variables,the theoretical foundations and the number of their occurrences in the year intervals. 
                If exist mediating or control variables, please include them into the "researchVariables".Once again, the result should be exhaustive and comprehensive! The theoreticalFrameworks should be presented particularly.
                As well as the methods and the number of their occurrences.At the same time, frequently researched variables relation and theory of supporting should be clarified.
                Refer to the following format: 
        {{  
            "researchVariables": [
                {{
                    "variable": "Academic procrastination",
                    "years": {{
                        "2025": 1,
                        "2016": 2,  
                        "2021": 3  
                    }},
                    "fiveYearCounts": {{
                        "2020-2024": 3,
                        "2025": 1,
                        "2015-2019": 2  
                    }},
                    "types": {{
                        "independent": 1,
                        "dependent": 1,  
                        "mediator": 1,  
                        if exist:"control variable": 1,  
                        if exist:"moderator variable": 2  
                    }}
                }}
            ],
            "theoreticalFrameworks": [
                {{
                    "theory": "xxx",
                    "fiveYearCounts": {{
                        "2020-2024": 3,
                        "2025": 1,
                        "2015-2019": 2
                    }},
                    "count": 6
                }}
            ],
            "researchMethods": [
                {{
                    "method": "Survey",
                    "count": 20
                }}
            ],
            "relation":[{{
                "Variable Pair": "Social interaction → Viewer engagement",
                "Mediating Variable":xx or none,
                "Moderating Variable":xx or none,
                "Controlled Variable":xx or none,
                "count": 18,
                "Theoretical Support": [
                "Social Cognitive Theory",
                "Social Exchange Theory",
                "Social Presence Theory"
                ],
                "Research Methods": [
                "Structural Equation Modeling (SEM)",
                "Experimental design with controlled variables",
                "Content analysis of chat interactions",
                "Machine learning for sentiment analysis"
                ]
                }}]

        }}
        Please note that your response should only output JSON, without any extra content. Generate as detailed results as possible.
        """
        completion = client.chat.completions.create(
            model="deepseek-r1",
            messages=[
                {'role': 'user',
                 'content': f"{content}"}
            ]
        )

        # 提取 thinking 和 answer
        thinking = completion.choices[0].message.reasoning_content  # 推理过程
        result= completion.choices[0].message.content  # 最终答案
        # 使用正则表达式去除多余字符
        # 移除所有以 ```json 开头和 ``` 结尾的内容，包括换行和空格
        cleaned_result = re.sub(r'^```json\s*|```\s*$', '', result, flags=re.MULTILINE)
        # 额外处理可能的转义字符或非法空格
        cleaned_result = cleaned_result.strip()
        save_to_database(user_input, thinking, cleaned_result)
        # 返回思考，答案，json格式
        return thinking,cleaned_result  # 现在返回元组 (thinking, answer)
        # 去除Markdown符号
        # md_patterns = [
        #     r'\*\*(.*?)\*\*',  # 去除加粗符号
        #     r'\*(.*?)\*',  # 去除斜体符号
        #     r'\[(.*?)\]\((.*?)\)'  # 去除链接符号，只保留链接文字
        # ]
        # for pattern in md_patterns:
        #     answer = re.sub(pattern, r'\1', answer)

    except TencentCloudSDKException as e:
        print(f"API调用失败: {str(e)}")
        return None, None, None  # 明确返回None
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {str(e)}")
        return None, None, None

def predict_future_changes_complement(title,user_input,old_result):
    try:
        client = OpenAI(
            api_key="sk-rQ7tiidourAF6BSI1scFwx8FAKTr7xlrFfsRdYGaWKHjy5bU",
            base_url="https://api.lkeap.cloud.tencent.com/v1",
        )
        content = f"""{title}
                These are latest papers' publication years and abstract contents.Now I want to write a literature review. please summarize them in detail and comprehensively the variables,the theoretical foundations and the number of their occurrences in the year intervals. 
                If exist mediating or control variables, please include them into the "researchVariables".Once again, the result should be exhaustive and comprehensive! The theoreticalFrameworks should be presented particularly.
                As well as the methods and the number of their occurrences.At the same time, frequently researched variables relation and theory of supporting should be clarified.
                The following is a summary of the previous results. Please update the new articles' results into this summary: if there are duplicates, please accumulate the values, and if there are new entries, please add them.
        {old_result}
        Please note that your response should only output JSON, without any extra content. Generate as detailed results as possible.
        """
        completion = client.chat.completions.create(
            model="deepseek-r1",
            messages=[
                {'role': 'user',
                 'content': f"{content}"}
            ]
        )

        # 提取 thinking 和 answer
        thinking = completion.choices[0].message.reasoning_content  # 推理过程
        result= completion.choices[0].message.content  # 最终答案
        # 使用正则表达式去除多余字符
        # 移除所有以 ```json 开头和 ``` 结尾的内容，包括换行和空格
        cleaned_result = re.sub(r'^```json\s*|```\s*$', '', result, flags=re.MULTILINE)
        # 额外处理可能的转义字符或非法空格
        cleaned_result = cleaned_result.strip()
        save_to_database(user_input, thinking, cleaned_result)
        # 返回思考，答案，json格式
        return thinking,cleaned_result  # 现在返回元组 (thinking, answer)
        # 去除Markdown符号
        # md_patterns = [
        #     r'\*\*(.*?)\*\*',  # 去除加粗符号
        #     r'\*(.*?)\*',  # 去除斜体符号
        #     r'\[(.*?)\]\((.*?)\)'  # 去除链接符号，只保留链接文字
        # ]
        # for pattern in md_patterns:
        #     answer = re.sub(pattern, r'\1', answer)

    except TencentCloudSDKException as e:
        print(f"API调用失败: {str(e)}")
        return None, None, None  # 明确返回None
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {str(e)}")
        return None, None, None

def save_to_database(user_input, thinking, cleaned_text):
    # 清洗表名（防止SQL注入）
    table_name = f"{user_input}_result"

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
            # 动态创建表（如果不存在）
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS `{table_name}` (
                id INT AUTO_INCREMENT PRIMARY KEY,
                thinking TEXT,
                cleaned_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_table_sql)

            # 插入数据
            insert_sql = f"""
            INSERT INTO `{table_name}` (thinking, cleaned_text)
            VALUES (%s, %s)
            """
            cursor.execute(insert_sql, (thinking, cleaned_text))

        connection.commit()
        print("答案数据已成功保存到数据库")
    except Exception as e:
        print(f"Database operation failed: {e}")
    finally:
        if connection:
            connection.close()


import pymysql


def get_last_cleaned_text(user_input):
    """
    从表user_input_result中查询cleaned_text列的最后一行值

    参数:
        user_input (str): 表名参数（需确保表名安全）

    返回:
        str: 最后一行的cleaned_text值，若无数据则返回None
    """
    connection = None
    result = None

    try:
        # 连接数据库
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='test',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        # 构建安全的表名（避免SQL注入）
        # 注意：实际使用中应确保user_input为合法表名，或使用更安全的参数化方式
        table_name = f"`{user_input}_result`"  # 表名添加反引号，支持包含特殊字符的表名

        with connection.cursor() as cursor:
            # SQL查询：按主键降序排列，取第一行（最后插入的记录）
            query = f"""
            SELECT cleaned_text 
            FROM {table_name} 
            ORDER BY id DESC 
            LIMIT 1
            """
            cursor.execute(query)
            row = cursor.fetchone()

            if row:
                result = row['cleaned_text']
            else:
                print(f"表 {table_name} 中无数据")

    except pymysql.Error as e:
        print(f"数据库查询出错: {e}")
    finally:
        if connection:
            connection.close()

    return result

