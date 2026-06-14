# Week4：前端基础 + 全栈Todo应用

## 主要成果
全栈Todo应用（`todo_app.html` + Week3的后端API），前后端完整打通。

## 功能
- 添加/删除/标记完成待办事项
- 关键词搜索
- 全部/未完成/已完成过滤
- 数据持久化（存储在SQLite数据库）

## 文件说明
- `todo_app.html`：主项目，全栈Todo应用前端
- `day22_html.html`：HTML基础练习
- `day23_javascript.html`：JavaScript基础练习
- `day24_fetch.html`：Fetch API练习

## 如何运行
1. 先启动后端（在week3目录下）：
   `uvicorn todo_api:app --reload`
2. 双击打开 `todo_app.html`

## 本周学到的核心概念
- HTML标签和CSS样式基础
- JavaScript DOM操作和事件监听
- Fetch API发送HTTP请求
- CORS跨域问题的原因和解决方式
- 前后端联调