from openai import OpenAI
import os
import json
from dotenv import load_dotenv
from tools import TOOLS, execute_tool, set_rag_engine
from rag_engine import RAGEngine

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

SYSTEM_PROMPT = """你是一个个人智能助手，名字叫"小智"。你有以下能力：

【任务管理】
- 创建任务（用户说"添加/新建/帮我记"）
- 查询任务（用户说"查看/列出/有哪些"）
- 完成任务（用户说"完成了/做完了"，先查任务找ID）
- 删除任务（用户说"删除/取消"，先查任务找ID）
- 查统计（用户说"统计/总共几个"）

【知识库问答】
- 当用户提问时，先用search_knowledge检索知识库
- 如果知识库有相关内容，基于内容回答并注明来源
- 如果知识库没有内容，用自己的知识回答

【普通对话】
- 对于不需要工具的问题，直接友好地回答

工作原则：
1. 优先使用工具，不要用脑子猜数据
2. 需要ID才能操作时，先调用get_tasks查到ID再操作
3. 回答简洁友好，像朋友一样聊天
4. 每次回答后，如果有任务相关操作，简要确认结果"""


class SmartAssistant:
    def __init__(self):
        # 初始化RAG引擎
        self.rag = RAGEngine()
        set_rag_engine(self.rag)

        # 对话历史（最多保留20轮）
        self.history = []
        self.max_history = 20

    def chat(self, user_message: str) -> str:
        """处理用户消息"""
        # 添加到历史
        self.history.append({"role": "user", "content": user_message})

        # 控制历史长度（滑动窗口）
        if len(self.history) > self.max_history * 2:
            self.history = self.history[-(self.max_history * 2):]

        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + self.history

        # Agent执行循环
        for step in range(8):
            response = client.chat.completions.create(
                model="deepseek-chat",
                max_tokens=1000,
                tools=TOOLS,
                tool_choice="auto",
                messages=messages
            )

            msg = response.choices[0].message
            finish = response.choices[0].finish_reason

            if finish != "tool_calls":
                reply = msg.content
                self.history.append({"role": "assistant", "content": reply})
                return reply

            # 执行工具
            messages.append(msg)
            for tc in msg.tool_calls:
                name = tc.function.name
                args = json.loads(tc.function.arguments) if tc.function.arguments else {}
                result = execute_tool(name, args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result
                })

        return "处理超时，请重试"

    def clear_history(self):
        self.history = []

    def get_history_count(self):
        return len(self.history) // 2