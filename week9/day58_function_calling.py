from openai import OpenAI
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


# ===== 第一步：定义工具（工具的"说明书"） =====
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",           # 工具名字（AI会用这个名字调用）
            "description": "查询指定城市的天气信息",  # 描述（AI靠这个决定要不要用这个工具）
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称，例如：北京、上海"
                    }
                },
                "required": ["city"]         # 必填参数
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "执行数学计算，支持加减乘除和括号",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式，例如：(3 + 5) * 2"
                    }
                },
                "required": ["expression"]
            }
        }
    }
]


# ===== 第二步：实现真正的工具函数 =====
def get_weather(city: str) -> str:
    """真正的天气查询（这里用模拟数据，实际项目里调真实API）"""
    data = {
        "北京": {"temp": "28°C", "weather": "晴天", "wind": "东南风3级"},
        "上海": {"temp": "25°C", "weather": "多云", "wind": "南风2级"},
        "广州": {"temp": "32°C", "weather": "小雨", "wind": "东风2级"},
        "成都": {"temp": "22°C", "weather": "阴天", "wind": "微风"},
    }
    if city in data:
        d = data[city]
        return f"{city}天气：{d['weather']}，{d['temp']}，{d['wind']}"
    return f"暂无{city}的天气数据"


def calculate(expression: str) -> str:
    """执行数学计算"""
    try:
        # 只允许数字和基本运算符（安全考虑）
        allowed = set("0123456789+-*/()., ")
        if not all(c in allowed for c in expression):
            return "表达式包含不允许的字符"
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算错误：{str(e)}"


# 工具调用分发函数
def call_tool(tool_name: str, tool_args: dict) -> str:
    """根据AI选择的工具名，调用对应的函数"""
    if tool_name == "get_weather":
        return get_weather(**tool_args)
    elif tool_name == "calculate":
        return calculate(**tool_args)
    else:
        return f"未知工具：{tool_name}"


# ===== 第三步：完整的Tool Use流程 =====
def agent_with_tools(user_message: str):
    """完整的Agent执行流程"""
    print(f"\n{'='*50}")
    print(f"用户：{user_message}")
    print(f"{'='*50}")

    messages = [
        {"role": "system", "content": "你是一个有用的助手，可以查询天气和执行数学计算。"},
        {"role": "user", "content": user_message}
    ]

    # 第一次调用：让AI决定要不要用工具
    response = client.chat.completions.create(
        model="deepseek-chat",
        max_tokens=500,
        tools=tools,
        tool_choice="auto",   # auto：AI自己决定要不要用工具
        messages=messages
    )

    message = response.choices[0].message
    print(f"\nAI决策：stop_reason = {response.choices[0].finish_reason}")

    # 判断AI是否要调用工具
    if response.choices[0].finish_reason == "tool_calls":
        # AI决定调用工具
        tool_calls = message.tool_calls
        print(f"AI要调用 {len(tool_calls)} 个工具：")

        # 把AI的决策加入消息历史
        messages.append(message)

        # 执行每个工具调用
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            print(f"  → 调用工具：{tool_name}，参数：{tool_args}")

            # 执行工具
            tool_result = call_tool(tool_name, tool_args)
            print(f"  ← 工具返回：{tool_result}")

            # 把工具结果加入消息历史
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result
            })

        # 第二次调用：让AI根据工具结果生成最终回答
        final_response = client.chat.completions.create(
            model="deepseek-chat",
            max_tokens=500,
            messages=messages
        )
        final_answer = final_response.choices[0].message.content
    else:
        # AI直接回答，不需要工具
        final_answer = message.content
        print("AI直接回答，未调用任何工具")

    print(f"\nAI最终回答：{final_answer}")
    return final_answer


# ===== 测试各种情况 =====
# 测试1：需要查天气（AI应该调用get_weather）
agent_with_tools("北京今天天气怎么样？")

# 测试2：需要计算（AI应该调用calculate）
agent_with_tools("帮我算一下 (123 + 456) * 2 等于多少？")

# 测试3：普通问题（AI应该直接回答，不调用工具）
agent_with_tools("Python和JavaScript哪个更适合初学者？")

# 测试4：需要同时查多个城市天气
agent_with_tools("北京和上海今天天气分别怎么样？")