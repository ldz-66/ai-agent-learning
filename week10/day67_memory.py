from openai import OpenAI
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


# ===== 问题：对话历史越来越长，token越来越多 =====
def demo_context_growth():
    """演示对话历史增长的问题"""
    messages = [{"role": "system", "content": "你是一个助手"}]

    questions = [
        "我叫小明",
        "我今年20岁",
        "我是计算机专业的",
        "你还记得我叫什么？",
        "我多大了？",
        "我学什么专业？",
    ]

    for q in questions:
        messages.append({"role": "user", "content": q})
        response = client.chat.completions.create(
            model="deepseek-chat",
            max_tokens=100,
            messages=messages
        )
        reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})

        # 估算token用量（粗略）
        total_chars = sum(len(m["content"]) for m in messages)
        print(f"问：{q}")
        print(f"答：{reply}")
        print(f"  历史长度：{len(messages)}条消息，约{total_chars}字符")
        print()


# ===== 解决方案1：限制历史长度（滑动窗口） =====
class SlidingWindowMemory:
    """只保留最近N轮对话，控制token用量"""

    def __init__(self, max_turns: int = 10):
        self.max_turns = max_turns
        self.history = []  # [(user_msg, assistant_msg), ...]
        self.system_prompt = ""

    def add_turn(self, user_msg: str, assistant_msg: str):
        self.history.append((user_msg, assistant_msg))
        # 超过限制时，丢弃最早的对话
        if len(self.history) > self.max_turns:
            self.history.pop(0)

    def get_messages(self) -> list:
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        for user_msg, assistant_msg in self.history:
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": assistant_msg})
        return messages

    def get_stats(self) -> dict:
        total_chars = sum(len(u) + len(a) for u, a in self.history)
        return {
            "turns": len(self.history),
            "max_turns": self.max_turns,
            "approx_chars": total_chars
        }


# ===== 解决方案2：关键信息摘要 =====
def summarize_history(messages: list) -> str:
    """当对话历史太长时，让AI帮你总结关键信息"""
    if len(messages) < 4:
        return ""

    summary_prompt = "请用3-5句话总结以下对话的关键信息（用户说了什么、发生了什么事）：\n\n"
    for msg in messages:
        role = "用户" if msg["role"] == "user" else "助手"
        summary_prompt += f"{role}：{msg['content']}\n"

    response = client.chat.completions.create(
        model="deepseek-chat",
        max_tokens=200,
        messages=[{"role": "user", "content": summary_prompt}]
    )
    return response.choices[0].message.content


# ===== 演示 =====
print("=" * 50)
print("演示1：对话历史增长问题")
print("=" * 50)
demo_context_growth()

print("\n" + "=" * 50)
print("演示2：滑动窗口记忆（最多保留3轮）")
print("=" * 50)

memory = SlidingWindowMemory(max_turns=3)
memory.system_prompt = "你是一个助手，记住用户告诉你的信息。"

conversations = [
    "我叫小明",
    "我今年20岁",
    "我是计算机专业的",
    "我喜欢打篮球",
    "你还记得我叫什么吗？",  # 在滑动窗口内
    "我多大了？",           # 可能已经被丢弃
]

for user_msg in conversations:
    msgs = memory.get_messages()
    msgs.append({"role": "user", "content": user_msg})

    response = client.chat.completions.create(
        model="deepseek-chat",
        max_tokens=100,
        messages=msgs
    )
    reply = response.choices[0].message.content
    memory.add_turn(user_msg, reply)

    stats = memory.get_stats()
    print(f"问：{user_msg}")
    print(f"答：{reply}")
    print(f"  [记忆：{stats['turns']}/{stats['max_turns']}轮]")
    print()