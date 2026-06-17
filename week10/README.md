# Week10：Agent进阶实践——智能任务管理助手

## 项目介绍
基于AI Agent的智能任务管理系统，用自然语言操作任务数据库。
用户说"帮我添加一个任务"，AI自动理解意图并操作数据库，返回自然语言结果。

## 技术亮点
- Tool Use：6个数据库操作工具，AI自动选择调用
- 记忆管理：对话历史管理，支持多轮上下文
- 错误处理：工具执行失败时AI能理解并友好提示
- FastAPI封装：Agent逻辑通过HTTP接口暴露，支持多会话

## 文件说明
- `db.py`：SQLite数据库操作层
- `tools.py`：工具定义和执行层
- `agent.py`：Agent核心逻辑
- `main.py`：FastAPI接口层

## 如何运行
1. 配置 `.env`：`DEEPSEEK_API_KEY=你的key`
2. `pip install -r requirements.txt`
3. `uvicorn main:app --reload`
4. 访问 `/docs` 测试接口，或运行 `python agent.py` 命令行交互