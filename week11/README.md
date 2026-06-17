# Week11：综合项目——个人智能助手

## 项目介绍
一个完整的AI Agent应用，整合了任务管理、知识库问答和智能对话三大功能。
用自然语言驱动，AI自动判断意图并调用合适的工具。

## 功能
- 🗂 任务管理：用自然语言增删改查待办任务
- 📚 知识库问答：上传文档，AI基于文档内容精准回答
- 💬 智能对话：普通问题直接回答，多轮对话有记忆
- 🔧 自动决策：AI根据用户意图自动选择工具，无需手动选

## 技术架构
用户输入 → Agent（DeepSeek + Tool Use）→ 判断意图
  → 任务类：调用数据库工具（SQLite）
  → 知识类：检索向量数据库（ChromaDB）→ 生成回答
  → 普通类：直接回答

## 技术栈
- AI：DeepSeek（openai库调用）+ sentence-transformers
- 后端：FastAPI + SQLite + ChromaDB
- 前端：原生HTML/CSS/JS

## 如何运行
1. 配置 `.env`：`DEEPSEEK_API_KEY=你的key`
2. `pip install -r requirements.txt`
3. `uvicorn main:app --reload`（首次需要20秒加载模型）
4. 访问：`http://127.0.0.1:8000`