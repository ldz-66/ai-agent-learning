import anthropic
import json
from dotenv import load_dotenv

load_dotenv()

# 创建客户端，指定 DeepSeek 的兼容接口
client = anthropic.Anthropic(
    base_url="https://api.deepseek.com/anthropic"
)

# 封装安全提取文本的函数，防止 ThinkingBlock 报错
def get_final_text(content_blocks):
    for block in content_blocks:
        if getattr(block, 'type', None) == 'text':
            return block.text
    return "（未获取到文本回复，可能是 max_tokens 太小）"

# ===== 实验1：不同System Prompt，回答同一个问题 =====
question = "如何学习编程？"

print("=" * 50)
print(f"问题：{question}")
print("=" * 50)

# 角色1：严肃的大学教授
response1 = client.messages.create(
    model="deepseek-v4-pro",
    max_tokens=2000,  # 调大 token 限制，防止思考过程耗尽额度
    system="你是一位严肃认真的大学计算机系教授，回答问题时引用学术理论，语气正式。回答控制在100字以内。",
    messages=[{"role": "user", "content": question}]
)
print("\n【教授风格】")
print(get_final_text(response1.content))

# 角色2：活泼的程序员朋友
response2 = client.messages.create(
    model="deepseek-v4-pro",
    max_tokens=2000,
    system="你是一个刚工作2年的程序员，说话轻松随意，喜欢用生活化的比喻，偶尔说'说真的'、'其实吧'这样的口头语。回答控制在100字以内。",
    messages=[{"role": "user", "content": question}]
)
print("\n【程序员朋友风格】")
print(get_final_text(response2.content))

# 角色3：专注输出结构化内容
response3 = client.messages.create(
    model="deepseek-v4-pro",
    max_tokens=2000,
    system="你是一个学习规划助手。无论用户问什么，都用以下格式回答：\n第一步：xxx\n第二步：xxx\n第三步：xxx\n注意事项：xxx\n不要有其他多余内容。",
    messages=[{"role": "user", "content": question}]
)
print("\n【结构化输出风格】")
print(get_final_text(response3.content))


# ===== 实验2：控制输出格式 =====
print("\n" + "=" * 50)
print("实验2：控制输出格式")
print("=" * 50)

# 让AI输出JSON
response4 = client.messages.create(
    model="deepseek-v4-pro",
    max_tokens=2000,
    system="""你是一个信息提取助手。
用户会给你一段文字，你需要从中提取关键信息，并严格按照以下JSON格式输出，不要输出任何其他内容：
{
  "姓名": "...",
  "年龄": ...,
  "职业": "...",
  "城市": "..."
}
如果某个字段信息不存在，填null。""",
    messages=[{
        "role": "user",
        "content": "小李是一名28岁的工程师，在上海工作，主要做后端开发。"
    }]
)
print("JSON提取结果：")
json_text = get_final_text(response4.content)
print(json_text)

# 验证是否真的是JSON
try:
    parsed = json.loads(json_text)
    print("✓ 成功解析为Python字典：", parsed)
except json.JSONDecodeError:
    print("✗ 无法解析为JSON，AI没有严格按格式输出")


# ===== 实验3：Few-shot提示（给例子） =====
print("\n" + "=" * 50)
print("实验3：Few-shot提示——给AI举例")
print("=" * 50)

response5 = client.messages.create(
    model="deepseek-v4-pro",
    max_tokens=2000,
    system="""你是一个文案改写助手，专门把普通文字改写成小红书风格。
小红书风格特点：多用emoji、语气活泼、有感叹号、用"姐妹们"或"宝子们"开头。

示例：
输入：今天吃了一家火锅店，味道不错
输出：姐妹们！！今天发现了一家超级无敌好吃的火锅店🔥🔥 味道绝了真的会上瘾那种！！！

输入：这本书值得推荐
输出：宝子们快去看这本书！！📚 真的太绝了 看完整个人都升华了✨✨

现在请按这个风格改写用户的输入。""",
    messages=[{
        "role": "user",
        "content": "今天学会了用Python调用AI接口，感觉很有成就感"
    }]
)
print("小红书风格改写：")
print(get_final_text(response5.content))