# Week5：大模型API调用 + Prompt工程

## 主要成果
AI聊天后端API（`chat_api.py`）——基于FastAPI + Anthropic Claude的聊天接口。

## 接口列表
| 接口 | 方法 | 描述 |
|------|------|------|
| /chat/simple | POST | 简单单轮对话 |
| /chat | POST | 多轮对话（支持历史记录） |
| /chat/stream | POST | 流式输出 |
| /health | GET | 健康检查 |

## 技术栈
- Anthropic Python SDK
- FastAPI
- Server-Sent Events（流式输出）

## 如何运行
1. 配置 `.env` 文件：`ANTHROPIC_API_KEY=你的key`
2. 安装依赖：`pip install -r requirements.txt`
3. 启动服务器：`uvicorn chat_api:app --reload`
4. 访问文档：`http://127.0.0.1:8000/docs`
5. 运行测试：`python test_chat_api.py`

## 本周学到的核心概念
- Anthropic API的调用方式（messages结构、model、max_tokens）
- System Prompt的作用和写法
- 流式输出（Streaming）的实现
- 多轮对话的上下文管理原理
- temperature等参数的效果
- API错误处理和token用量追踪