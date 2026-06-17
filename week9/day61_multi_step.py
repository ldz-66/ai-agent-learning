from openai import OpenAI
import os
import json
import math
import requests
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "执行数学计算",
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
            "description": "搜索GitHub仓库，返回仓库名、Star数、描述",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {"type": "string"},
                    "limit": {"type": "integer"}
                },
                "required": ["keyword"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_repo_languages",
            "description": "获取指定GitHub仓库使用的编程语言分布",
            "parameters": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "仓库所有者用户名"},
                    "repo": {"type": "string", "description": "仓库名称"}
                },
                "required": ["owner", "repo"]
            }
        }
    }
]


def calculate(expression: str) -> str:
    try:
        result = eval(expression, {"__builtins__": {}, "math": math})
        return f"{expression} = {result}"
    except Exception as e:
        return f"错误：{e}"


def search_github(keyword: str, limit: int = 3) -> str:
    try:
        r = requests.get(
            "https://api.github.com/search/repositories",
            params={"q": keyword, "sort": "stars", "per_page": limit},
            timeout=8
        )
        items = r.json().get("items", [])[:limit]
        result = []
        for item in items:
            # 返回owner信息，方便下一步调用get_repo_languages
            result.append({
                "name": item["name"],
                "owner": item["owner"]["login"],
                "stars": item["stargazers_count"],
                "description": item.get("description", "")
            })
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return f"搜索失败：{e}"


def get_repo_languages(owner: str, repo: str) -> str:
    try:
        r = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}/languages",
            timeout=8
        )
        langs = r.json()
        if not langs:
            return "暂无语言数据"
        total = sum(langs.values())
        lang_str = ", ".join([f"{k}({v/total*100:.1f}%)" for k, v in
                              sorted(langs.items(), key=lambda x: -x[1])[:5]])
        return f"{owner}/{repo} 语言分布：{lang_str}"
    except Exception as e:
        return f"获取失败：{e}"


TOOL_MAP = {
    "calculate": calculate,
    "search_github": search_github,
    "get_repo_languages": get_repo_languages,
}

def call_tool(name, args):
    func = TOOL_MAP.get(name)
    return func(**args) if func and args else (func() if func else f"未知工具：{name}")


def run_agent(user_message: str):
    print(f"\n{'='*60}")
    print(f"任务：{user_message}")
    print(f"{'='*60}")

    messages = [
        {"role": "system", "content": "你是一个研究助手。善于利用工具完成多步骤任务，将前一步的结果用于下一步的查询。"},
        {"role": "user", "content": user_message}
    ]

    step = 0
    while step < 10:
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
        print(f"\n第{step}轮 [{finish}]")

        if finish != "tool_calls":
            print(f"\n最终回答：\n{msg.content}")
            return

        messages.append(msg)
        for tc in msg.tool_calls:
            name = tc.function.name
            args = json.loads(tc.function.arguments) if tc.function.arguments else {}
            print(f"  调用：{name}({args})")
            result = call_tool(name, args)
            print(f"  结果：{result[:200]}...")
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result
            })


# 测试多步骤任务：先搜仓库，再查语言分布
run_agent("帮我搜索GitHub上最热门的RAG相关项目（返回前2个），然后查询这些项目使用的编程语言分布")

# 测试依赖计算的多步骤任务
run_agent("先计算 365 * 24 * 60，然后告诉我这代表什么含义（一年有多少分钟）")