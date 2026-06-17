from openai import OpenAI
import os
import json
import time
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


# ===== 工具（故意让部分情况出错，测试错误处理） =====
tools = [
    {
        "type": "function",
        "function": {
            "name": "divide",
            "description": "做除法运算",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "被除数"},
                    "b": {"type": "number", "description": "除数"}
                },
                "required": ["a", "b"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_info",
            "description": "根据用户ID获取用户信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "用户ID"}
                },
                "required": ["user_id"]
            }
        }
    }
]


def divide(a: float, b: float) -> str:
    """除法，除数为0时返回错误信息而不是抛出异常"""
    if b == 0:
        # 关键：工具出错时，返回清晰的错误描述，让AI能理解并告知用户
        return "错误：除数不能为0，请提供一个非零的除数"
    return f"{a} ÷ {b} = {a / b}"


def get_user_info(user_id: int) -> str:
    """模拟用户查询，ID>100时返回不存在"""
    fake_users = {
        1: {"name": "小明", "age": 20, "role": "学生"},
        2: {"name": "小红", "age": 25, "role": "工程师"},
    }
    if user_id in fake_users:
        user = fake_users[user_id]
        return f"用户{user_id}：{user['name']}，{user['age']}岁，{user['role']}"
    return f"错误：用户ID={user_id}不存在，请检查ID是否正确"


TOOL_MAP = {"divide": divide, "get_user_info": get_user_info}


def robust_agent(user_message: str):
    """带完善错误处理的Agent"""
    print(f"\n{'='*50}")
    print(f"用户：{user_message}")

    messages = [
        {"role": "system", "content": "你是一个助手，遇到工具返回错误时，要清楚地告诉用户出了什么问题，并给出建议。"},
        {"role": "user", "content": user_message}
    ]

    for step in range(5):
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                max_tokens=500,
                tools=tools,
                tool_choice="auto",
                messages=messages
            )
        except Exception as e:
            # API调用本身出错（网络问题、超时等）
            print(f"API调用失败：{e}")
            return "抱歉，服务暂时不可用，请稍后重试"

        msg = response.choices[0].message
        finish = response.choices[0].finish_reason

        if finish != "tool_calls":
            print(f"回答：{msg.content}")
            return msg.content

        messages.append(msg)
        for tc in msg.tool_calls:
            name = tc.function.name
            try:
                args = json.loads(tc.function.arguments) if tc.function.arguments else {}
            except json.JSONDecodeError:
                args = {}

            func = TOOL_MAP.get(name)
            if func:
                try:
                    result = func(**args)
                except Exception as e:
                    # 工具执行时抛出了未预期的异常
                    result = f"工具执行异常：{str(e)}"
            else:
                result = f"未知工具：{name}"

            print(f"  工具：{name}({args}) → {result}")
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result
            })

    return "处理超时"


# 测试各种边界情况
robust_agent("帮我算 10 除以 2")          # 正常情况
robust_agent("帮我算 10 除以 0")          # 工具返回错误
robust_agent("查一下用户ID=1的信息")       # 存在的用户
robust_agent("查一下用户ID=999的信息")     # 不存在的用户