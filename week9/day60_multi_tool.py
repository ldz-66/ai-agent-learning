from openai import OpenAI
import os
import json
import math
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# ===== 工具定义 =====
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前日期时间",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "数学计算",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "数学表达式"}
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_github",
            "description": "搜索GitHub仓库",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "搜索关键词"},
                    "limit": {"type": "integer", "description": "结果数量，默认3"}
                },
                "required": ["keyword"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_joke",
            "description": "获取随机英文笑话",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "text_stats",
            "description": "统计文本的字符数、词数、行数",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "要统计的文本"}
                },
                "required": ["text"]
            }
        }
    }
]


# ===== 工具实现 =====
def get_current_time():
    now = datetime.now()
    weekdays = ['星期一','星期二','星期三','星期四','星期五','星期六','星期日']
    return f"{now.strftime('%Y年%m月%d日 %H:%M:%S')} {weekdays[now.weekday()]}"

def calculate(expression: str):
    try:
        result = eval(expression, {"__builtins__": {}, "math": math})
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算错误：{e}"

def search_github(keyword: str, limit: int = 3):
    try:
        r = requests.get(
            "https://api.github.com/search/repositories",
            params={"q": keyword, "sort": "stars", "per_page": limit},
            timeout=5
        )
        items = r.json().get("items", [])[:limit]
        return "\n".join([f"- {i['name']}(⭐{i['stargazers_count']}): {i['description'] or ''}" for i in items])
    except:
        return "搜索失败"

def get_joke():
    try:
        r = requests.get("https://official-joke-api.appspot.com/random_joke", timeout=5)
        d = r.json()
        return f"{d['setup']} — {d['punchline']}"
    except:
        return "Why do programmers prefer dark mode? Because light attracts bugs!"

def text_stats(text: str):
    lines = text.strip().split('\n')
    words = len(text.split())
    chars = len(text)
    return f"字符数：{chars}，词数（空格分隔）：{words}，行数：{len(lines)}"

TOOL_MAP = {
    "get_current_time": get_current_time,
    "calculate": calculate,
    "search_github": search_github,
    "get_joke": get_joke,
    "text_stats": text_stats,
}

def call_tool(name, args):
    func = TOOL_MAP.get(name)
    if func:
        return func(**args) if args else func()
    return f"未知工具：{name}"


# ===== 带详细日志的Agent =====
def run_agent_verbose(user_message: str):
    """带完整日志的Agent，让你看清AI的每一步决策"""
    print(f"\n{'='*60}")
    print(f"任务：{user_message}")
    print(f"{'='*60}")

    messages = [
        {"role": "system", "content": "你是一个有用的AI助手。遇到需要工具的问题，优先使用工具而不是凭记忆回答。"},
        {"role": "user", "content": user_message}
    ]

    step = 0
    tool_call_count = 0

    while step < 8:
        step += 1

        response = client.chat.completions.create(
            model="deepseek-chat",
            max_tokens=1000,
            tools=tools,
            tool_choice="auto",
            messages=messages
        )

        msg = response.choices[0].message
        finish = response.choices[0].finish_reason

        print(f"\n[第{step}轮] finish_reason={finish}")

        if finish != "tool_calls":
            print(f"\n✅ 最终回答：\n{msg.content}")
            print(f"\n📊 统计：共调用工具 {tool_call_count} 次，共 {step} 轮对话")
            return

        messages.append(msg)

        for tc in msg.tool_calls:
            tool_call_count += 1
            name = tc.function.name
            args = json.loads(tc.function.arguments) if tc.function.arguments else {}

            print(f"  🔧 工具调用 #{tool_call_count}：{name}")
            print(f"     参数：{args}")

            result = call_tool(name, args)
            print(f"     结果：{result[:150]}{'...' if len(result) > 150 else ''}")

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result
            })


# ===== 复杂任务测试（观察AI如何拆解多步骤任务） =====
print("测试1：单工具任务")
run_agent_verbose("现在几点了？")

print("\n\n测试2：需要两个不同工具")
run_agent_verbose("帮我搜一下GitHub上最热门的langchain项目，同时告诉我现在几点")

print("\n\n测试3：需要推理+计算的任务")
run_agent_verbose("如果我每天学习4小时，100天能学习多少小时？另外搜一下GitHub上的fastapi学习资源")

print("\n\n测试4：不需要工具的问题")
run_agent_verbose("用一句话解释什么是递归")