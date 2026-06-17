from openai import OpenAI
import os
import json
import requests
import math
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


# ===== 定义工具说明书 =====
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前日期和时间",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "执行数学计算，支持加减乘除、幂运算、括号",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式，例如：2**10 或 (100+200)*3"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_joke",
            "description": "获取一个随机英文笑话",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_github_repos",
            "description": "搜索GitHub上的开源仓库",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "搜索关键词"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回结果数量，默认3"
                    }
                },
                "required": ["keyword"]
            }
        }
    }
]


# ===== 实现工具函数 =====
def get_current_time() -> str:
    now = datetime.now()
    return f"当前时间：{now.strftime('%Y年%m月%d日 %H:%M:%S')}，{['星期一','星期二','星期三','星期四','星期五','星期六','星期日'][now.weekday()]}"


def calculate(expression: str) -> str:
    try:
        allowed_names = {"__builtins__": {}, "math": math}
        result = eval(expression, allowed_names)
        return f"计算结果：{expression} = {result}"
    except Exception as e:
        return f"计算错误：{str(e)}"


def get_joke() -> str:
    try:
        response = requests.get(
            "https://official-joke-api.appspot.com/random_joke",
            timeout=5
        )
        data = response.json()
        return f"笑话：{data['setup']} —— {data['punchline']}"
    except Exception:
        return "笑话：Why do programmers prefer dark mode? Because light attracts bugs!"


def search_github_repos(keyword: str, limit: int = 3) -> str:
    try:
        response = requests.get(
            "https://api.github.com/search/repositories",
            params={"q": keyword, "sort": "stars", "per_page": limit},
            timeout=5
        )
        data = response.json()
        repos = data.get("items", [])[:limit]
        if not repos:
            return f"未找到关于'{keyword}'的仓库"
        result = f"关于'{keyword}'的热门仓库：\n"
        for repo in repos:
            result += f"- {repo['name']}（⭐{repo['stargazers_count']}）：{repo['description'] or '暂无描述'}\n"
        return result
    except Exception as e:
        return f"搜索失败：{str(e)}"


def call_tool(tool_name: str, tool_args: dict) -> str:
    tool_map = {
        "get_current_time": get_current_time,
        "calculate": calculate,
        "get_joke": get_joke,
        "search_github_repos": search_github_repos,
    }
    func = tool_map.get(tool_name)
    if func:
        return func(**tool_args) if tool_args else func()
    return f"未知工具：{tool_name}"


# ===== Agent执行引擎（支持多步骤） =====
def run_agent(user_message: str, max_steps: int = 5):
    """
    Agent执行引擎：支持多步骤工具调用
    max_steps：最多执行几轮工具调用，防止无限循环
    """
    print(f"\n{'='*55}")
    print(f"用户：{user_message}")
    print(f"{'='*55}")

    messages = [
        {"role": "system", "content": "你是一个有用的AI助手，可以查询时间、执行计算、获取笑话、搜索GitHub仓库。尽量使用工具来回答用户的问题，而不是凭记忆猜测。"},
        {"role": "user", "content": user_message}
    ]

    step = 0
    while step < max_steps:
        step += 1
        print(f"\n--- 第{step}步 ---")

        response = client.chat.completions.create(
            model="deepseek-chat",
            max_tokens=1000,
            tools=tools,
            tool_choice="auto",
            messages=messages
        )

        message = response.choices[0].message
        finish_reason = response.choices[0].finish_reason

        if finish_reason != "tool_calls":
            # AI决定不再调用工具，直接输出最终答案
            print(f"AI最终回答：{message.content}")
            return message.content

        # AI要调用工具
        messages.append(message)

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}

            print(f"调用工具：{tool_name}  参数：{tool_args}")
            result = call_tool(tool_name, tool_args)
            print(f"工具结果：{result[:100]}{'...' if len(result) > 100 else ''}")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })

    print("已达到最大步骤数")
    return None


# ===== 测试 =====
run_agent("现在是几点？")
run_agent("2的10次方是多少？另外帮我搜一下GitHub上关于fastapi的仓库")
run_agent("给我讲个笑话")
run_agent("我想知道现在的时间，以及100加200乘以3等于多少")