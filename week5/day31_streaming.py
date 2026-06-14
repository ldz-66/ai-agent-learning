import anthropic
from dotenv import load_dotenv
import time

load_dotenv()

# 创建客户端，指定 DeepSeek 的兼容接口
client = anthropic.Anthropic(
    base_url="https://api.deepseek.com/anthropic"
)

# ===== 对比1：普通输出（等待全部完成） =====
print("=" * 50)
print("普通输出（等待全部完成后显示）")
print("=" * 50)

start_time = time.time()

message = client.messages.create(
    model="deepseek-v4-pro",
    max_tokens=2000,  # 调大 token，防止思考耗尽额度
    messages=[{"role": "user", "content": "用200字介绍一下Python语言的历史"}]
)

end_time = time.time()

# 安全提取最终文本
final_text = ""
for block in message.content:
    if getattr(block, 'type', None) == 'text':
        final_text += block.text

print(final_text)
print(f"\n等待时间：{end_time - start_time:.2f}秒（全部生成完才显示）")


# ===== 对比2：流式输出（边生成边显示） =====
print("\n" + "=" * 50)
print("流式输出（边生成边显示，体验更好）")
print("=" * 50)

start_time = time.time()

# 使用 stream 上下文管理器
with client.messages.stream(
    model="deepseek-v4-pro",
    max_tokens=2000,
    messages=[{"role": "user", "content": "用200字介绍一下Python语言的历史"}]
) as stream:
    # 遍历流式返回的原始事件，安全过滤掉思考过程
    for event in stream:
        # 检查是否为文本增量事件
        if event.type == 'content_block_delta' and getattr(event.delta, 'type', None) == 'text_delta':
            print(event.delta.text, end="", flush=True)

end_time = time.time()
print(f"\n\n总时间：{end_time - start_time:.2f}秒（但用户立刻看到第一个字）")


# ===== 实用示例：带进度提示的流式输出 =====
print("\n" + "=" * 50)
print("实用示例：带统计的流式输出")
print("=" * 50)

full_text = ""
char_count = 0

with client.messages.stream(
    model="deepseek-v4-pro",
    max_tokens=2000,
    messages=[{"role": "user", "content": "写一首关于编程的短诗"}]
) as stream:
    # 同样使用安全的事件遍历方式
    for event in stream:
        if event.type == 'content_block_delta' and getattr(event.delta, 'type', None) == 'text_delta':
            text_chunk = event.delta.text
            print(text_chunk, end="", flush=True)
            full_text += text_chunk
            char_count += len(text_chunk)

print(f"\n\n--- 统计 ---")
print(f"总字符数：{char_count}")
print(f"总字数（估算）：{len(full_text.replace(' ', '').replace(chr(10), ''))}")