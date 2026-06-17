from openai import OpenAI
import os
import json
import math
from dotenv import load_dotenv

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
            "name": "calculate",
            "description": "执行数学计算，支持加减乘除、幂运算(用**)、平方根(math.sqrt)、圆周率(math.pi)等",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Python数学表达式，例如：2**10，math.sqrt(144)，(100+200)*3/2"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "unit_convert",
            "description": "单位换算，支持长度(km/m/cm/mm/inch/feet)、重量(kg/g/lb/oz)、温度(celsius/fahrenheit/kelvin)",
            "parameters": {
                "type": "object",
                "properties": {
                    "value": {"type": "number", "description": "要转换的数值"},
                    "from_unit": {"type": "string", "description": "源单位"},
                    "to_unit": {"type": "string", "description": "目标单位"}
                },
                "required": ["value", "from_unit", "to_unit"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "statistics_calc",
            "description": "对一组数字进行统计计算（平均值、最大值、最小值、总和、方差）",
            "parameters": {
                "type": "object",
                "properties": {
                    "numbers": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "数字列表"
                    }
                },
                "required": ["numbers"]
            }
        }
    }
]


# ===== 工具实现 =====
def calculate(expression: str) -> str:
    try:
        safe_globals = {"__builtins__": {}, "math": math}
        result = eval(expression, safe_globals)
        return f"计算结果：{expression} = {result}"
    except Exception as e:
        return f"计算错误：{e}"


def unit_convert(value: float, from_unit: str, to_unit: str) -> str:
    conversions = {
        # 长度（统一转换为米）
        ("km", "m"): 1000, ("m", "km"): 0.001,
        ("m", "cm"): 100, ("cm", "m"): 0.01,
        ("m", "mm"): 1000, ("mm", "m"): 0.001,
        ("inch", "cm"): 2.54, ("cm", "inch"): 1/2.54,
        ("feet", "m"): 0.3048, ("m", "feet"): 1/0.3048,
        ("km", "mile"): 0.621371, ("mile", "km"): 1.60934,
        # 重量
        ("kg", "g"): 1000, ("g", "kg"): 0.001,
        ("kg", "lb"): 2.20462, ("lb", "kg"): 0.453592,
        ("g", "oz"): 0.035274, ("oz", "g"): 28.3495,
        # 温度（特殊处理）
    }

    from_unit = from_unit.lower()
    to_unit = to_unit.lower()

    # 温度特殊处理
    if from_unit == "celsius" and to_unit == "fahrenheit":
        result = value * 9/5 + 32
        return f"{value}°C = {result:.2f}°F"
    if from_unit == "fahrenheit" and to_unit == "celsius":
        result = (value - 32) * 5/9
        return f"{value}°F = {result:.2f}°C"
    if from_unit == "celsius" and to_unit == "kelvin":
        result = value + 273.15
        return f"{value}°C = {result:.2f}K"

    key = (from_unit, to_unit)
    if key in conversions:
        result = value * conversions[key]
        return f"{value} {from_unit} = {result:.4f} {to_unit}"

    return f"不支持的单位换算：{from_unit} → {to_unit}"


def statistics_calc(numbers: list) -> str:
    if not numbers:
        return "数字列表为空"
    n = len(numbers)
    total = sum(numbers)
    mean = total / n
    variance = sum((x - mean) ** 2 for x in numbers) / n
    std_dev = math.sqrt(variance)
    return (f"数据分析结果（共{n}个数）：\n"
            f"  总和：{total}\n"
            f"  平均值：{mean:.4f}\n"
            f"  最大值：{max(numbers)}\n"
            f"  最小值：{min(numbers)}\n"
            f"  标准差：{std_dev:.4f}")


TOOL_MAP = {
    "calculate": calculate,
    "unit_convert": unit_convert,
    "statistics_calc": statistics_calc,
}

def call_tool(name, args):
    func = TOOL_MAP.get(name)
    return func(**args) if func and args else (func() if func else f"未知工具：{name}")


# ===== 交互式Agent =====
def run_interactive_agent():
    print("=" * 55)
    print("智能计算助手（输入 quit 退出，clear 清空历史）")
    print("支持：数学计算、单位换算、统计分析")
    print("=" * 55)

    conversation_history = []
    system_prompt = """你是一个专业的计算助手。
你有三个工具：calculate（数学计算）、unit_convert（单位换算）、statistics_calc（统计分析）。
遇到计算相关的问题，优先使用工具，不要用脑子硬算。
回答要简洁，直接给出结果即可。"""

    while True:
        user_input = input("\n你：").strip()

        if user_input.lower() == "quit":
            print("再见！")
            break
        if user_input.lower() == "clear":
            conversation_history = []
            print("--- 对话历史已清空 ---")
            continue
        if not user_input:
            continue

        conversation_history.append({"role": "user", "content": user_input})

        messages = [{"role": "system", "content": system_prompt}] + conversation_history

        # Agent循环
        while True:
            response = client.chat.completions.create(
                model="deepseek-chat",
                max_tokens=800,
                tools=tools,
                tool_choice="auto",
                messages=messages
            )

            msg = response.choices[0].message
            finish = response.choices[0].finish_reason

            if finish != "tool_calls":
                print(f"助手：{msg.content}")
                conversation_history.append({"role": "assistant", "content": msg.content})
                break

            messages.append(msg)
            for tc in msg.tool_calls:
                name = tc.function.name
                args = json.loads(tc.function.arguments) if tc.function.arguments else {}
                result = call_tool(name, args)
                print(f"  [调用工具 {name}：{result[:80]}{'...' if len(result) > 80 else ''}]")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result
                })


if __name__ == "__main__":
    run_interactive_agent()