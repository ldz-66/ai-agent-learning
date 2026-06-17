from openai import OpenAI
import os
import json
from dotenv import load_dotenv
from tools import TOOLS, execute_tool

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

SYSTEM_PROMPT = """你是一个智能任务管理助手，名字叫"小助"。
你有以下工具可以使用：
- create_task：创建任务
- get_tasks：查询任务
- update_task_done：标记完成/未完成
- update_task_info：更新任务信息
- delete_task：删除任务
- get_task_stats：查看统计

工作原则：
1. 用户说"添加/新建/帮我记一下"→ create_task
2. 用户说"查看/列出/有哪些" → get_tasks
3. 用户说"完成了/做完了" → update_task_done（先用get_tasks找到ID）
4. 用户说"删除/取消" → delete_task（先用get_tasks找到ID）
5. 用户说"统计/总共" → get_task_stats
6. 如果需要先查ID再操作，可以连续调用多个工具
7. 回答用简洁友好的中文，像朋友聊天一样

注意：用户说"完成了xxx任务"时，先查询任务找到对应ID，再标记完成。"""


class TaskAgent:
    def __init__(self):
        self.conversation_history = []

    def chat(self, user_message: str) -> str:
        """处理一条用户消息，返回AI回复"""
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + self.conversation_history

        # Agent循环（最多执行8步，防止死循环）
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
                # 最终回答
                reply = msg.content
                self.conversation_history.append({
                    "role": "assistant",
                    "content": reply
                })
                return reply

            # 执行工具调用
            messages.append(msg)

            for tc in msg.tool_calls:
                tool_name = tc.function.name
                tool_args = json.loads(tc.function.arguments) if tc.function.arguments else {}
                tool_result = execute_tool(tool_name, tool_args)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": tool_result
                })

        return "处理超时，请重试"

    def clear_history(self):
        self.conversation_history = []

    def get_history_length(self):
        return len(self.conversation_history)


def run_interactive():
    """命令行交互测试"""
    from db import init_db
    init_db()

    agent = TaskAgent()
    print("=" * 50)
    print("智能任务助手 小助（输入quit退出，clear清空历史）")
    print("=" * 50)

    while True:
        user_input = input("\n你：").strip()
        if user_input.lower() == "quit":
            print("再见！")
            break
        if user_input.lower() == "clear":
            agent.clear_history()
            print("--- 对话历史已清空 ---")
            continue
        if not user_input:
            continue

        reply = agent.chat(user_input)
        print(f"\n小助：{reply}")
        print(f"（当前对话轮数：{agent.get_history_length() // 2}）")


if __name__ == "__main__":
    run_interactive()