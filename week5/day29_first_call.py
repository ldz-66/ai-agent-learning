import anthropic
import os
from dotenv import load_dotenv

# 从.env文件加载API Key
load_dotenv()

# 创建客户端，指定 DeepSeek 的兼容接口
client = anthropic.Anthropic(
    base_url="https://api.deepseek.com/anthropic"
)

# 封装一个安全提取最终文本的函数
def get_final_text(content_blocks):
    """
    遍历返回的内容块，只提取类型为 'text' 的内容。
    忽略 'thinking' (思考过程) 块，防止报错。
    """
    for block in content_blocks:
        if getattr(block, 'type', None) == 'text':
            return block.text
    return "（未获取到文本回复，可能是max_tokens太小，思考过程耗尽了token）"


print("=" * 50)
print("测试1：最简单的调用")
print("=" * 50)

message = client.messages.create(
    model="deepseek-v4-pro",
    max_tokens=2000,  # 思考模式非常消耗token，建议调大
    messages=[
        {"role": "user", "content": "用一句话介绍一下你自己"}
    ]
)

print("AI回复：", get_final_text(message.content))
print("使用的token数：", message.usage.input_tokens, "输入 +", message.usage.output_tokens, "输出")


print("\n" + "=" * 50)
print("测试2：中文对话")
print("=" * 50)

message2 = client.messages.create(
    model="deepseek-v4-pro",
    max_tokens=2000,
    messages=[
        {"role": "user", "content": "Python和JavaScript各有什么优缺点？用3点对比，每点一句话。"}
    ]
)

print("AI回复：\n", get_final_text(message2.content))


print("\n" + "=" * 50)
print("测试3：查看完整响应结构")
print("=" * 50)

message3 = client.messages.create(
    model="deepseek-v4-pro",
    max_tokens=2000,
    messages=[
        {"role": "user", "content": "说'你好'"}
    ]
)

print("完整响应：")
print("  id:", message3.id)
print("  model:", message3.model)
print("  stop_reason:", message3.stop_reason)
print("  content:", message3.content)
print("  usage:", message3.usage)