
# AI学习历程

记录我从零开始学习AI应用开发与Agent开发的过程。


## 进度
- [x] Week1: 环境搭建、Python工程化基础、Git/GitHub、命令行待办事项管理器
# Week2：HTTP/API基础 + FastAPI入门

## 主要成果
文本分析API（`text_analyzer.py`）——一个基于FastAPI的RESTful API，提供中文文本分析功能。

## 功能接口
| 接口 | 方法 | 描述 |
|------|------|------|
| /analyze/basic | POST | 基础统计（字数、行数、中英文数量） |
| /analyze/keywords | POST | 中文分词 + 高频词提取 |
| /analyze/sensitive | POST | 敏感词检测 |
| /health | GET | 服务健康检查 |

## 技术栈
- FastAPI：Web框架
- Uvicorn：ASGI服务器
- jieba：中文分词
- requests：HTTP客户端

## 如何运行
1. 安装依赖：`pip install -r requirements.txt`
2. 启动服务器：`uvicorn text_analyzer:app --reload`
3. 访问文档：`http://127.0.0.1:8000/docs`
4. 运行测试客户端：`python day13_client.py`

## 本周学到的核心概念
- HTTP请求方法（GET/POST/PUT/DELETE）和状态码
- FastAPI路径参数、查询参数、请求体的用法
- Pydantic做数据验证
- 用requests库在Python代码里调用API