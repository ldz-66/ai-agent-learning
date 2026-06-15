# Week6：AI文案助手

## 项目介绍
一个完整的AI文案生成应用，支持为不同平台（小红书、朋友圈、微博、产品描述、广告语）生成定制化文案。

## 功能特点
- 🎯 多平台风格：5种平台风格，AI自动调整语气和格式
- ⚡ 流式输出：文案边生成边显示，实时看到效果
- 📋 一键复制：生成后直接复制使用
- ⏹ 随时停止：生成过程可以随时中断
- 📚 历史记录：保留本次会话的生成历史

## 技术栈
- 后端：FastAPI + Anthropic Claude API
- 前端：原生HTML/CSS/JavaScript
- 流式输出：Server-Sent Events

## 如何运行
1. 配置 `.env` 文件：`ANTHROPIC_API_KEY=你的key`
2. 安装依赖：`pip install -r requirements.txt`
3. 启动：`uvicorn main:app --reload`
4. 访问：`http://127.0.0.1:8000`

## 项目结构