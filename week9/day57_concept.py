from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


# ===== 对比1：普通AI应用 =====
print("=" * 50)
print("普通AI应用：直接回答，不调用工具")
print("=" * 50)

response = client.chat.completions.create(
    model="deepseek-chat",
    max_tokens=200,
    messages=[
        {"role": "system", "content": "你是一个助手。"},
        {"role": "user", "content": "北京今天天气怎么样？"}
    ]
)
print("回答：", response.choices[0].message.content)
print("（注意：AI只能根据训练数据猜测，无法获取真实天气）")


# ===== 对比2：有工具的Agent =====
print("\n" + "=" * 50)
print("Agent思路：先思考，再用工具，再回答")
print("=" * 50)

# 模拟一个"天气工具"的返回结果
def fake_weather_tool(city: str) -> str:
    """模拟天气查询工具（实际项目里这里会真的调用天气API）"""
    weather_data = {
        "北京": "晴天，28°C，东南风3级，空气质量良",
        "上海": "多云，25°C，南风2级，空气质量优",
        "广州": "小雨，32°C，东风2级，空气质量良",
    }
    return weather_data.get(city, f"未找到{city}的天气数据")


# Agent工作流程（手动模拟）
print("\n步骤1：用户提问")
user_question = "北京今天天气怎么样？"
print(f"用户：{user_question}")

print("\n步骤2：AI思考需要用什么工具")
print("AI思考：用户想知道天气，我需要调用天气查询工具")

print("\n步骤3：调用工具")
tool_result = fake_weather_tool("北京")
print(f"工具返回：{tool_result}")

print("\n步骤4：AI根据工具结果生成最终回答")
response2 = client.chat.completions.create(
    model="deepseek-chat",
    max_tokens=200,
    messages=[
        {"role": "system", "content": "你是一个天气助手，根据提供的天气数据回答用户问题。"},
        {"role": "user", "content": user_question},
        {"role": "assistant", "content": f"我查询了天气数据，结果是：{tool_result}"},
        {"role": "user", "content": "好的，请根据这个数据给我一个简洁的天气播报。"}
    ]
)
print(f"AI最终回答：{response2.choices[0].message.content}")

print("\n关键理解：Agent = AI大脑 + 工具集合 + 循环执行")