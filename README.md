# research-platform
主界面
<img width="2511" height="1353" alt="image" src="https://github.com/user-attachments/assets/c19dc72a-0995-4bbe-8339-6aba0ce90997" />
第二界面
<img width="2496" height="1345" alt="image" src="https://github.com/user-attachments/assets/d04b8383-e6b4-4e10-b9a4-b829dd492775" />
本平台旨在构建一个自动化、可视化的科研辅助系统，实现对用户输入的关键词进行文献抓取、智能分析与图形展示。系统采用 Flask 构建后端框架，配合 MySQL 数据库进行数据存储，并结合腾讯云 DeepSeek 大模型对文献信息进行结构化分析。

## 一、项目简介  
本平台旨在构建一个自动化、可视化的科研辅助系统，实现对用户输入的关键词进行 **文献抓取、智能分析与图形展示**。系统采用 Flask 构建后端框架，配合 MySQL 数据库进行数据存储，并结合腾讯云 DeepSeek 大模型对文献信息进行结构化分析。

---

## 二、核心功能实现路径  

### 主线功能：

1. **关键词搜索与数据抓取**  
   - 用户在前端输入关键词，后端通过 Flask 接收请求。
   - 调用 Selenium + `undetected_chromedriver` 模拟浏览器行为，绕过 Scopus 反爬机制进行爬取。

2. **数据存储**  
   - 抓取的文献与 LLM 分析结果通过 PyMySQL 存入 MySQL 数据库，便于管理与调用。

3. **智能分析（LLM）**  
   - 使用腾讯云 DeepSeek API 对文献摘要进行结构化分析（如提取变量、理论、方法等），参考文档见：[Tencent DeepSeek 文档](https://cloud.tencent.com/document/product/1772/115969)。

4. **结果展示与美化**  
   - LLM 返回 JSON 格式数据。
   - 前端使用 JavaScript + ECharts 进行可视化呈现，界面通过 HTML + CSS 优化布局和交互。

---

### 支线功能：

- 支持 **历史关键词回查与可视化**，无重复抓取；
- **历史数据更新**：与数据库比对后增量补充，并更新分析；
- **前后端通信**：使用 Flask 路由机制实现双向数据交互；
- **结构化输出规范化**：所有 LLM 分析统一返回 JSON 格式，确保前端处理一致性。

---

## 三、关键文件路径说明

| 功能模块       | 文件路径                  | 说明                                   |
|----------------|----------------------------|----------------------------------------|
| 前端页面结构   | `static/index.html`        | 页面输入框、结果展示区域结构           |
| 页面样式美化   | `static/style.css`         | 控制前端视觉风格与响应式布局           |
| 数据抓取模块   | `crawler/crawl_to_sql.py` | 使用 Selenium + undetected_chromedriver 实现爬虫 |
| 数据存储模块   | `crawler/crawl_to_sql.py`       | 使用 PyMySQL 保存数据至 MySQL          |
| LLM 接口调用   | `database/AImodel.py`   | 腾讯云 DeepSeek 接口封装与调用逻辑     |
| 可视化逻辑     | `static/script.js`       | 使用 ECharts 渲染变量图、柱状图等图表   |
| 路由主逻辑     | `app.py`     | 管理路由与前后端交互                   |

---

## 四、未来优化方向  

考虑到 Scopus 每日新增数据较少，可通过定时任务（如 `APScheduler` 或 `cron`）实现关键词分组更新：

- 高优先级关键词可 4~6 小时轮询更新；
- 低频关键词每隔 24 小时或更长周期更新；
- 所有任务可异步执行，避免阻塞主程序运行。

---

