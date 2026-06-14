# Week3：数据库基础 + 完整Todo后端API

## 主要成果
基于FastAPI + SQLite的完整Todo后端API，支持增删改查、搜索、分页。

## 接口列表
| 接口 | 方法 | 描述 |
|------|------|------|
| /todos | GET | 获取待办列表（支持搜索/分页） |
| /todos/{id} | GET | 获取单条待办 |
| /todos | POST | 新增待办 |
| /todos/{id} | PATCH | 更新完成状态 |
| /todos/{id} | DELETE | 删除待办 |
| /health | GET | 健康检查 |

## 查询参数
- `page`：页码（默认1）
- `size`：每页数量（默认10）
- `keyword`：搜索关键词
- `done`：筛选完成状态（true/false）

## 技术栈
- FastAPI：Web框架
- SQLite：数据库
- Pydantic：数据校验

## 如何运行
1. 安装依赖：`pip install -r requirements.txt`
2. 启动服务器：`uvicorn todo_api:app --reload`
3. 访问文档：`http://127.0.0.1:8000/docs`
4. 运行测试：`python test_api.py`

## 本周学到的核心概念
- SQL基本语法（SELECT/INSERT/UPDATE/DELETE）
- SQLite数据库的Python操作
- FastAPI与数据库的整合方式
- API的搜索、分页、错误处理设计