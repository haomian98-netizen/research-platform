import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pymysql
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import re
import undetected_chromedriver as uc
import random
from selenium.webdriver import Remote, ChromeOptions
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
from selenium.webdriver.common.by import By

def add_cookies(cookie_str):
    """正确添加 Cookie"""
    cookies = {}
    for cookie in cookie_str.split('; '):
        if '=' in cookie:
            key, value = cookie.split('=', 1)
            cookies[key] = value
    ua = UserAgent()
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument(f"--user-agent={ua.random}")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # 添加代理配置
    session_id = str(random.randint(1000000, 9999999))
    proxy_url = f"http://brd-customer-hl_f2e0564f-zone-residential_proxy1-session-{session_id}:z3yc4dyxgzix@brd.superproxy.io:33335"
    chrome_options.add_argument(f'--proxy-server={proxy_url}')

    driver = webdriver.Chrome(options=chrome_options)  # 替换为反检测驱动
    driver.get("https://scopus.com")
    time.sleep(3)

    for key, value in cookies.items():
        driver.add_cookie({
            'name': key,
            'value': value,
            'domain': '.weibo.com',
            'path': '/'
        })

    driver.refresh()
    print("Cookie 已成功添加")
def find_and_click_next_page(driver, max_attempts=9, start_from=9):
    for i in range(start_from, 0, -1):  # 从start_from递减到1
        try:
            # 构造动态XPath
            xpath = f'/html/body/div[1]/div/div[1]/div/div/div[3]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[2]/div[2]/div/nav/ul/li[{i}]/button/span[1]'

            # 尝试查找并点击元素
            next_page_button = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            next_page_button.click()
            print(f"成功点击第 {i} 个位置的下一页按钮")
            return True  # 点击成功，返回True

        except TimeoutException:
            print(f"未找到 li[{i}] 位置的下一页按钮，继续尝试前一个位置...")
            continue  # 继续尝试前一个位置

    # 所有尝试都失败
    print("错误: 未找到任何可用的下一页按钮")
    return False  # 点击失败，返回False

def crawl_and_store(keyword,page_num):
    # 【关键修正1：使用反检测驱动，避免被网站终止会话】

    ua = UserAgent()
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--profile-directory=Default")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--disable-plugins-discovery")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument('--no-first-run')
    chrome_options.add_argument('--no-service-autorun')
    chrome_options.add_argument('--no-default-browser-check')
    chrome_options.add_argument('--password-store=basic')
    chrome_options.add_argument('--no-sandbox')
    driver = uc.Chrome(options=chrome_options)  # 替换为反检测驱动
      # 增加等待时间到10秒


    # 存储所有爬取的数据
    all_data = []

    try:

        # 打开 Scopus 网页
        driver.get("https://www.scopus.com")

        # try:
        #     close_btn = wait.until(EC.element_to_be_clickable(
        #         (By.XPATH, '//*[@id="pendo-close-guide-e0738c57"]')))
        #
        #     close_btn.click()
        # except Exception as e:
        #     print("弹窗未出现或无法关闭:", str(e))
        #
        #     # 步骤2：点击登录
        # signin_btn = wait.until(EC.element_to_be_clickable(
        #     (By.XPATH, '//*[@id="signin_link_move"]/span')))
        #
        # signin_btn.click()
        #
        # # 步骤3：接受Cookie
        # cookie_accept = wait.until(EC.element_to_be_clickable(
        #     (By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')))
        #
        # cookie_accept.click()
        #
        # # 步骤4：通过组织登录
        # org_login = wait.until(EC.element_to_be_clickable(
        #     (By.XPATH, '//*[@id="bdd-elsSecondaryBtn"]')))
        #
        # org_login.click()
        #
        # # 步骤5：输入机构名称
        # institution_input = wait.until(EC.visibility_of_element_located(
        #     (By.XPATH, '//*[@id="bdd-email"]')))
        #
        # institution_input.send_keys("Curtin University")  # 模拟人类输入速度
        #
        #
        # # 步骤6：选择第一个结果
        # first_result = wait.until(EC.element_to_be_clickable(
        #     (By.XPATH, '//*[@id="bdd-institution-resultList"]/form[1]/button/span')))
        #
        # first_result.click()
        #
        # # 步骤7：输入账号
        # username = wait.until(EC.visibility_of_element_located(
        #     (By.XPATH, '//*[@id="username"]')))
        #
        # username.send_keys("21011261")  # 建议从环境变量读取敏感信息
        #
        # # 步骤8：输入密码
        # password = wait.until(EC.visibility_of_element_located(
        #     (By.XPATH, '//*[@id="password"]')))
        #
        # password.send_keys("Lucia2forrest")  # 建议从加密文件读取
        #
        # # 步骤9：点击登录按钮
        # login_btn = wait.until(EC.element_to_be_clickable(
        #     (By.XPATH, '/html/body/div/div/div/div[1]/form/section[5]/div/button')))
        #
        # login_btn.click()

        # 定位搜索框并输入关键词
        print("[步骤-2] 定位搜索框并输入关键词")
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH,
                                            '/html/body/div[1]/div/div[1]/div[2]/div/div[3]/div/div[2]/div[2]/micro-ui/scopus-homepage/div/div[2]/div/div/div[1]/div[3]/div/div/form/div/div[1]/div/div/div[2]/div/div[1]/div/label/input'))
        )
        search_box.send_keys(keyword)

        # 定位搜索按钮并点击
        print("[步骤-3] 点击搜索按钮")
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,
                                        '/html/body/div[1]/div/div[1]/div[2]/div/div[3]/div/div[2]/div[2]/micro-ui/scopus-homepage/div/div[2]/div/div/div[1]/div[3]/div/div/form/div/div[2]/div[2]/button/span[1]'))
        )
        search_button.click()
        time.sleep(random.uniform(2,4))
        # 首页点击展开所有摘要
        print("[步骤-4] 展开所有摘要")
        expand_buttons = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH,
                                                 '/html/body/div[1]/div/div[1]/div/div/div[3]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[1]/table/tbody/tr/td[3]/div/div/button/span'))
        )
        for button in expand_buttons:
            try:
                button.click()
                time.sleep(1)
            except Exception as e:
                print(f"点击展开摘要按钮时出错: {e}")
        # 选择排序依据为相关性
        print("[步骤-5] 选择排序依据为相关性")
        sort_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH,
                                            '//*[@id="container"]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[1]/table/tbody/tr/td[3]/div/div/div[1]/label/select'))
        )
        sort_button.click()

        relevance_option = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH,
                                            '//*[@id="container"]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[1]/table/tbody/tr/td[3]/div/div/div[1]/label/select/option[5]'))
        )
        relevance_option.click()
        # 设置年份为 2015 年至今
        print("[步骤-6] 设置年份为2015年至今")
        year_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="年份-section"]/div/div/div/div[2]/div/div[2]/div/div/div/div/div[1]/div/label/input'))
        )
        year_input.clear()
        year_input.send_keys('2015')

        # 点击空白处让输入生效
        blank_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH,
                                            '//*[@id="年份-section"]/div/div/div/div[2]/div/div[2]/div/div/div/div/div[2]/div/label/input'))
        )
        blank_element.click()

        # 点击生效后产生的框对应的按钮
        apply_year_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="年份-section"]/div/div/div/div[2]/div/div[2]/button'))
        )
        apply_year_button.click()
        print(f"[步骤-7] 开始爬取 {page_num} 条数据")
        # 定义 tr 数字列表
        tr_nums = [2, 5, 8, 12, 15, 18, 21, 24, 27, 30]

        for page in range(page_num):
            page_data = []
            for index, tr_num in enumerate(tr_nums):
                try:
                    # 爬取标题
                    title_xpath = f'//*[@id="container"]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[2]/div[1]/table/tbody/tr[{tr_num}]/td[2]/div/div/h3/a/span/span'
                    try:
                        title = WebDriverWait(driver, 2).until(
                            EC.presence_of_element_located((By.XPATH, title_xpath))
                        ).text
                    except Exception:
                        title = "no data available"

                    # 爬取作者
                    author_xpath = f'//*[@id="container"]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[2]/div[1]/table/tbody/tr[{tr_num}]/td[3]/div/div'
                    try:
                        author = WebDriverWait(driver, 2).until(
                            EC.presence_of_element_located((By.XPATH, author_xpath))
                        ).text
                    except Exception:
                        author = "no data available"

                    # 爬取出版物
                    publication_xpath = f'//*[@id="container"]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[2]/div[1]/table/tbody/tr[{tr_num}]/td[4]/div/div/a/span/span'
                    try:
                        publication = WebDriverWait(driver, 2).until(
                            EC.presence_of_element_located((By.XPATH, publication_xpath))
                        ).text
                    except Exception:
                        publication = "no data available"

                    # 爬取年份
                    year_xpath = f'//*[@id="container"]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[2]/div[1]/table/tbody/tr[{tr_num}]/td[5]/div/span'
                    try:
                        year = WebDriverWait(driver, 2).until(
                            EC.presence_of_element_located((By.XPATH, year_xpath))
                        ).text
                    except Exception:
                        year = "no data available"

                    # 爬取引用
                    citation_xpath = f'//*[@id="container"]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[2]/div[1]/table/tbody/tr[{tr_num}]/td[6]/div'
                    try:
                        citation = WebDriverWait(driver, 2).until(
                            EC.presence_of_element_located((By.XPATH, citation_xpath))
                        ).text
                    except Exception:
                        citation = "no data available"

                    # 爬取摘要
                    abstract_index = index
                    abstract_xpath = f'//*[@id="abstract-collapsible-panel-{abstract_index}"]/span/div'
                    try:
                        abstract = WebDriverWait(driver, 2).until(
                            EC.presence_of_element_located((By.XPATH, abstract_xpath))
                        ).text
                    except Exception:
                        abstract = ""

                    # 存储单条数据
                    data = {
                        '标题': title,
                        '作者': author,
                        '出版物': publication,
                        '年份': year,
                        '引用': citation,
                        '摘要': abstract
                    }
                    page_data.append(data)

                except Exception as e:
                    print(f"爬取第 {page + 1} 页，第 {index} 条记录时出错: {e}")

            # 将当前页数据添加到总数据列表
            all_data.extend(page_data)

            if page < 9:
                # 点击下一页按钮
                try:
                    # 尝试从li[9]开始查找下一页按钮
                    success = find_and_click_next_page(driver)

                    if not success:
                        print("无法翻页，可能是最后一页")
                        # 处理无法翻页的情况
                except Exception as e:
                    print(f"翻页时发生错误: {str(e)}")

    except TimeoutException as e:
        print(f"[致命错误-超时] 元素定位超时，错误：{str(e)}")
    except NoSuchElementException as e:
        print(f"[致命错误-元素未找到] XPath定位失败，错误：{str(e)}")
    except ElementClickInterceptedException as e:
        print(f"[致命错误-点击被拦截] 元素被遮挡或不可点击，错误：{str(e)}")
    except Exception as e:
        print(f"[未知错误] 爬取过程中发生意外错误：{str(e)}")
    finally:

        # 关闭浏览器
        driver.quit()

        # # 将数据保存到 Excel 文件
        # df = pd.DataFrame(all_data)
        # df.to_excel(save_path, index=False)
        # print(f"数据已保存到 {save_path}")
        legal_keyword = re.sub(r'\W+', ' ', keyword.strip())  # 仅保留字母数字和下划线
        # 连接数据库
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
                # 创建 scopus 表格
                create_table_query = f"""
                CREATE TABLE IF NOT EXISTS `{legal_keyword}` (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title TEXT,
                    author TEXT,
                    publication VARCHAR(255),
                    year VARCHAR(255),
                    citation TEXT,
                    abstract TEXT
                )
                """
                cursor.execute(create_table_query)

                # 插入数据
                for data in all_data:
                    insert_query = f"""
                    INSERT INTO `{keyword}` (title, author, publication, year, citation, abstract)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    values = (data['标题'], data['作者'], data['出版物'], data['年份'], data['引用'], data['摘要'])
                    cursor.execute(insert_query, values)

            # 提交事务
            connection.commit()
            print("数据已成功保存到数据库")
        except pymysql.Error as e:
            print(f"数据库操作出错: {e}")
        finally:
            if connection:
                connection.close()
    return all_data

def crawl_and_store_complement(keyword, page_num):
    # 存储所有爬取的数据
    all_data = []
    new_data = []  # 存储新增的数据
    driver = None  # 初始化driver为None

    try:
        ua = UserAgent()
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--profile-directory=Default")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--disable-plugins-discovery")
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument('--no-first-run')
        chrome_options.add_argument('--no-service-autorun')
        chrome_options.add_argument('--no-default-browser-check')
        chrome_options.add_argument('--password-store=basic')
        chrome_options.add_argument('--no-sandbox')
        # 代理参数
        # host = 'brd.superproxy.io'
        # port = '33335'
        # username = 'brd-customer-hl_f2e0564f-zone-residential_proxy1'
        # password = 'z3yc4dyxgzix'
        #
        # # 组合代理URL
        # proxy_url = f'http://{username}:{password}@{host}:{port}'
        #
        # chrome_options.add_argument(f'--proxy-server={proxy_url}')
        
        driver = uc.Chrome(options=chrome_options)
        driver.delete_all_cookies()

        driver.get("https://www.scopus.com")
        # 定位搜索按钮并输入关键词
        print("[步骤-2] 定位搜索框并输入关键词")
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH,
                                            '/html/body/div[1]/div/div[1]/div[2]/div/div[3]/div/div[2]/div[2]/micro-ui/scopus-homepage/div/div[2]/div/div/div[1]/div[3]/div/div/form/div/div[1]/div/div/div[2]/div/div[1]/div/label/input'))
        )
        search_box.send_keys(keyword)

        # 定位搜索按钮并点击
        print("[步骤-3] 点击搜索按钮")
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,
                                        '/html/body/div[1]/div/div[1]/div[2]/div/div[3]/div/div[2]/div[2]/micro-ui/scopus-homepage/div/div[2]/div/div/div[1]/div[3]/div/div/form/div/div[2]/div[2]/button/span[1]'))
        )
        search_button.click()
        time.sleep(random.uniform(2, 4))  # 点击后随机延迟

        # 首页点击展开所有摘要
        print("[步骤-4] 展开所有摘要")
        expand_buttons = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH,
                                                 '/html/body/div[1]/div/div[1]/div/div/div[3]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[1]/table/tbody/tr/td[3]/div/div/button/span'))
        )
        for button in expand_buttons:
            try:
                button.click()
                time.sleep(1)
            except Exception as e:
                print(f"点击展开摘要按钮时出错: {e}")

        # 设置年份为 2015 年至今
        print("[步骤-6] 设置年份为2015年至今")
        year_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="年份-section"]/div/div/div/div[2]/div/div[2]/div/div/div/div/div[1]/div/label/input'))
        )
        year_input.clear()
        year_input.send_keys('2015')

        # 点击空白处让输入生效
        blank_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH,
                                            '//*[@id="年份-section"]/div/div/div/div[2]/div/div[2]/div/div/div/div/div[2]/div/label/input'))
        )
        blank_element.click()

        # 点击生效后产生的框对应的按钮
        apply_year_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="年份-section"]/div/div/div/div[2]/div/div[2]/button'))
        )
        apply_year_button.click()
        print(f"[步骤-7] 开始爬取 {page_num} 条数据")
        # 定义 tr 数字列表
        tr_nums = [2, 5, 8, 12, 15, 18, 21, 24, 27, 30]

        for page in range(page_num):
            page_data = []
            for index, tr_num in enumerate(tr_nums):
                try:
                    # 爬取标题
                    title_xpath = f'//*[@id="container"]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[2]/div[1]/table/tbody/tr[{tr_num}]/td[2]/div/div/h3/a/span/span'
                    try:
                        title = WebDriverWait(driver, 2).until(
                            EC.presence_of_element_located((By.XPATH, title_xpath))
                        ).text
                    except Exception:
                        title = "no data available"

                    # 爬取作者
                    author_xpath = f'//*[@id="container"]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[2]/div[1]/table/tbody/tr[{tr_num}]/td[3]/div/div'
                    try:
                        author = WebDriverWait(driver, 2).until(
                            EC.presence_of_element_located((By.XPATH, author_xpath))
                        ).text
                    except Exception:
                        author = "no data available"

                    # 爬取出版物
                    publication_xpath = f'//*[@id="container"]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[2]/div[1]/table/tbody/tr[{tr_num}]/td[4]/div/div/a/span/span'
                    try:
                        publication = WebDriverWait(driver, 2).until(
                            EC.presence_of_element_located((By.XPATH, publication_xpath))
                        ).text
                    except Exception:
                        publication = "no data available"

                    # 爬取年份
                    year_xpath = f'//*[@id="container"]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[2]/div[1]/table/tbody/tr[{tr_num}]/td[5]/div/span'
                    try:
                        year = WebDriverWait(driver, 2).until(
                            EC.presence_of_element_located((By.XPATH, year_xpath))
                        ).text
                    except Exception:
                        year = "no data available"

                    # 爬取引用
                    citation_xpath = f'//*[@id="container"]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[2]/div[1]/table/tbody/tr[{tr_num}]/td[6]/div'
                    try:
                        citation = WebDriverWait(driver, 2).until(
                            EC.presence_of_element_located((By.XPATH, citation_xpath))
                        ).text
                    except Exception:
                        citation = "no data available"

                    # 爬取摘要
                    abstract_index = index
                    abstract_xpath = f'//*[@id="abstract-collapsible-panel-{abstract_index}"]/span/div'
                    try:
                        abstract = WebDriverWait(driver, 2).until(
                            EC.presence_of_element_located((By.XPATH, abstract_xpath))
                        ).text
                    except Exception:
                        abstract = ""

                    # 存储单条数据
                    data = {
                        '标题': title,
                        '作者': author,
                        '出版物': publication,
                        '年份': year,
                        '引用': citation,
                        '摘要': abstract
                    }
                    page_data.append(data)

                except Exception as e:
                    print(f"爬取第 {page + 1} 页，第 {index} 条记录时出错: {e}")

            # 将当前页数据添加到总数据列表
            all_data.extend(page_data)

            if page < 9:
                # 点击下一页按钮
                try:
                    # 尝试从li[9]开始查找下一页按钮
                    success = find_and_click_next_page(driver)

                    if not success:
                        print("无法翻页，可能是最后一页")
                        # 处理无法翻页的情况
                except Exception as e:
                    print(f"翻页时发生错误: {str(e)}")

    except TimeoutException as e:
        print(f"[致命错误-超时] 元素定位超时，错误：{str(e)}")
    except NoSuchElementException as e:
        print(f"[致命错误-元素未找到] XPath定位失败，错误：{str(e)}")
    except ElementClickInterceptedException as e:
        print(f"[致命错误-点击被拦截] 元素被遮挡或不可点击，错误：{str(e)}")
    except Exception as e:
        print(f"[未知错误] 爬取过程中发生意外错误：{str(e)}")
    finally:
        # 安全关闭浏览器
        if driver:
            try:
                driver.quit()
            except Exception as e:
                print(f"关闭浏览器时发生错误: {str(e)}")
            finally:
                driver = None

        legal_keyword = re.sub(r'\W+', ' ', keyword.strip())  # 仅保留字母数字和下划线
        # 连接数据库
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
                # 创建 scopus 表格
                create_table_query = f"""
                CREATE TABLE IF NOT EXISTS `{legal_keyword}` (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title TEXT,
                    author TEXT,
                    publication VARCHAR(255),
                    year VARCHAR(255),
                    citation TEXT,
                    abstract TEXT
                )
                """
                cursor.execute(create_table_query)

                # 获取已存在的标题列表
                cursor.execute(f"SELECT title FROM `{keyword}`")
                existing_titles = {row['title'] for row in cursor.fetchall()}

                # 插入新数据
                for data in all_data:
                    if data['标题'] not in existing_titles:
                        insert_query = f"""
                        INSERT INTO `{keyword}` (title, author, publication, year, citation, abstract)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """
                        values = (data['标题'], data['作者'], data['出版物'], data['年份'], data['引用'], data['摘要'])
                        cursor.execute(insert_query, values)
                        new_data.append(data)  # 添加到新数据列表

            # 提交事务
            connection.commit()
            print(f"成功插入 {len(new_data)} 条新数据到数据库")
        except pymysql.Error as e:
            print(f"数据库操作出错: {e}")
        finally:
            if connection:
                connection.close()
        return new_data  # 返回新增的数据

if __name__=="__main__":
    # cokkie_url='scopus.machineID=6BB2360BBCC0D2536FB8DDF13E356150.i-02a22e12a4ed61a74; b-user-id=ea098aa6-7c22-96f7-4078-9c380ea13621; scopus_key=csLZYyt8h0W_c9M0BuSMppba; SCSessionID=B82BF62C8307618876F89FE000E6E72B.i-0ab4b10f0c9b85fd3; scopusSessionUUID=d31bc7ca-1b64-44f5-9; AWSELB=CB9317D502BF07938DE10C841E762B7A33C19AADB1503C3AD2968D1E0F31076B44C0F97B461E498008624C84C8AC98FBF9CDC2D210A31AAC5A6BDE3E4B4DACF34F3854CEEBB488C897B495EC7F87E20D69451DAD8E; __cf_bm=dIaQb4wpkVC_k_.SWZiqvUvbq.TvKDImb4O2rVTQA84-1749521294-1.0.1.1-jLhP.rVqq2DthMKo8uW7CM7s5CdlA2dl4FP4P7TrtAtdzLOBVddnUuC4kz.QBOERqJI1ZU02e4Y6gU_HyMDL0yq5Llw.1CcqDulH1rceNoM; _cfuvid=JWPC_qXBdgdA47GufRXJtRi25Ok4EmSF3w8DMQhL4Qs-1749521294922-0.0.1.1-604800000; Scopus-usage-key=enable-logging; AT_CONTENT_COOKIE="KDP_FACADE_AFFILIATION_ENABLED:1,KDP_FACADE_ABSTRACT_ENABLED:1,KDP_SOURCE_ENABLED:1,KDP_FACADE_PATENT_ENABLED:1,KDP_FACADE_AUTHOR_ENABLED:1,"; at_check=true; AMCVS_4D6368F454EC41940A4C98A6@AdobeOrg=1; SCOPUS_JWT=eyJraWQiOiJjYTUwODRlNi03M2Y5LTQ0NTUtOWI3Zi1kMjk1M2VkMmRiYmMiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIzNDc5MDI4ODMiLCJkZXBhcnRtZW50SWQiOiIyNzI0NTIiLCJpc3MiOiJTY29wdXMiLCJpbnN0X2FjY3RfaWQiOiI0NDk4IiwiaXNFeHRlcm5hbFN1YnNjcmliZWRFbnRpdGxlbWVudHMiOmZhbHNlLCJwYXRoX2Nob2ljZSI6dHJ1ZSwiaW5kdl9pZGVudGl0eSI6IlJFRyIsImV4cCI6MTc0OTUyMjI2NSwiaWF0IjoxNzQ5NTIxMzY2LCJzc29fa2V5IjoiWVRnellUZGhOREUyTkRnME1UUTBOVE5rTWpnNFpUSTNOMkV6WldFeU9HRmpZelppWjNoeWNXRjhKSHcyUmtZeE1VVkVNVVV3T1VZeE5UWTVNRE0zUkRRd1FrWTVSamM1UkVZNVF6UTJOakEyTURRd01qVXhSamxFUkVVeE5FTTJRekkxUkVJeE1Ua3lNRVV3TlRSRlFUZEZNVE0yUWpVNU1EUTFRMFEwUmtJMU1rVTRNamRFTWtVeU1rSXlRa1F6TnpWRVFVVXlNalUzT0RBeE5VSXlOemt4TXpnNVJEbEVRemc1UlRBMk1UTTFSa1kzTUVKRU56RXlORFpEUXpWQ1FURXpOVEpHTXpoQ1JqQkNNVVl4TkVNME5ESkZORVJCUXpaRk9URXdRakZFTkRrd1JrTkROVVJFUWpJPSIsImVtYWlsIjoibGluZ3h1ZS56aGFuQGN1cnRpbi5lZHUuYXUiLCJhbmFseXRpY3NfaW5mbyI6eyJhY2Nlc3NUeXBlIjoiYWU6UkVHOlNISUJCT0xFVEg6SU5TVDpTSElCQk9MRVRIIiwiYWNjb3VudElkIjoiNDQ5OCIsImFjY291bnROYW1lIjoiQ3VydGluIFVuaXZlcnNpdHkiLCJ1c2VySWQiOiJhZTozNDc5MDI4ODMifSwiZGVwYXJ0bWVudE5hbWUiOiJTaGliYm9sZXRoIC0gMjMyOSIsImluc3RfYWNjdF9uYW1lIjoiQ3VydGluIFVuaXZlcnNpdHkiLCJzdWJzY3JpYmVyIjp0cnVlLCJ3ZWJVc2VySWQiOiIzNDc5MDI4ODMiLCJpbmRpdmlkdWFsIjp0cnVlLCJpbnN0X2Fzc29jX21ldGhvZCI6IlNISUJCT0xFVEgiLCJnaXZlbl9uYW1lIjoiTGluZ3h1ZSIsImFjY291bnROdW1iZXIiOiJDMDAwMDA0NDk4IiwicGFja2FnZUlkcyI6W10sImF1ZCI6IlNjb3B1cyIsIm5iZiI6MTc0OTUyMTM2NiwiZmVuY2VzIjpbXSwiaW5kdl9pZGVudGl0eV9tZXRob2QiOiJTSElCQk9MRVRIIiwiaW5zdF9hc3NvYyI6IklOU1QiLCJuYW1lIjoiTGluZ3h1ZSBaaGFuIiwidXNhZ2VQYXRoSW5mbyI6IigzNDc5MDI4ODMsVXwyNzI0NTIsRHw0NDk4LEF8NSxQfDEsUEwpKFNDT1BVUyxDT058YTgzYTdhNDE2NDg0MTQ0NTNkMjg4ZTI3N2EzZWEyOGFjYzZiZ3hycWEsU1NPfFJFR19TSElCQk9MRVRILEFDQ0VTU19UWVBFKSIsInByaW1hcnlBZG1pblJvbGVzIjpbXSwiYXV0aF90b2tlbiI6ImE4M2E3YTQxNjQ4NDE0NDUzZDI4OGUyNzdhM2VhMjhhY2M2Ymd4cnFhIiwiZmFtaWx5X25hbWUiOiJaaGFuIn0.JBWq8_p2PAddLosoylDedSAl8nzYqzZGcIM1gapjSvP9fugjajndRYTolpLsZGZa7569gz6pXPTllDhPeoU_SXYZsc5wzuhO0qzDLQa1SE-P59s0MJJ3_NTV78-GoP7uGB7y16qcFAdcWg0tenuqMaHpe-lPcmjsGOfxL1rl_od7Qi2pX4iD_m7Ezi5_yweMxQd62ZPIUTng-SBJF9DFohf7CUi5NKNR3vp4xyUPfHBUA5qHXr39HMGfs4Cyn-cX-BazUXKjjReGqJEOsow5EI3G4Q8Tnfox_WXLLK_HMnDm13n3rTjU_U5z5onuZ3omTEbRpo6gakdEob4VHrz0mQ; OptanonConsent=isGpcEnabled=0&datestamp=Tue+Jun+10+2025+10:09:29+GMT+0800+(中国标准时间)&version=202411.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=af3dfe87-1925-4046-a59e-983d03e2e98b&interactionCount=0&isAnonUser=1&groups=1:1,2:1,4:1,3:1&geolocation=AU;WA&landingPath=NotLandingPage&AwaitingReconsent=false; OptanonAlertBoxClosed=2025-06-10T02:09:29.281Z; s_pers= v8=1749521369328|1844129369328; v8_s=Less%20than%201%20day|1749523169328; c19=sc%3Asearch%3Adocument%20searchform|1749523169334; v68=1749521368254|1749523169343;; AMCV_4D6368F454EC41940A4C98A6@AdobeOrg=-2121179033|MCMID|61248512140296811663235518165289120001|MCAAMLH-1750126169|8|MCAAMB-1750126169|RKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y|MCOPTOUT-1749528569s|NONE|MCAID|NONE|MCCIDH|438747875|vVersion|5.3.0|MCIDTS|20249; s_sess= s_sq=; s_ppvl=sc%253Asearch%253Adocument%2520searchform%2C68%2C68%2C977.3333320617676%2C1707%2C916%2C1707%2C1067%2C1.5%2CP; e41=1; s_cpc=0; s_cc=true; s_ppv=sc%253Asearch%253Adocument%2520searchform%2C68%2C68%2C977.3333320617676%2C944%2C916%2C1707%2C1067%2C1.5%2CP;; mbox=PC#fbfccfbb3a88488aa0f30a0a02310eee.36_0#1812766170|session#eee36b676b134a1892e8be3f3009877e#1749523234'
    # add_cookies( cokkie_url)
    print(crawl_and_store("social media",1))