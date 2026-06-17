# Week9：AI Agent核心概念 + Tool Use

## 本周核心内容
从零实现了AI Agent的核心机制——Tool Use（工具调用/Function Calling）。

## 关键理解
- **Agent vs 普通AI**：普通AI只会"说"，Agent还能"做"
- **Tool Use流程**：定义工具 → AI决策 → 执行工具 → 返回结果 → AI继续思考
- **finish_reason**：`tool_calls`=AI要调工具，`stop`=AI给最终答案
- **多步骤**：前一步工具的结果可以作为下一步工具的输入

## 主要文件
- `day57_concept.py`：Agent概念对比演示
- `day58_function_calling.py`：Tool Use基本原理
- `day59_real_tools.py`：真实工具（时间/计算/GitHub搜索）
- `day60_multi_tool.py`：多工具Agent + 详细日志
- `day61_multi_step.py`：多步骤任务（后一步依赖前一步结果）
- `calculator_agent.py`：完整可交互计算助手

## 如何运行计算助手
1. 配置 `.env`：`DEEPSEEK_API_KEY=你的key`
2. 安装依赖：`pip install -r requirements.txt`
3. 运行：`python calculator_agent.py`