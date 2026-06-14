import anthropic
from dotenv import load_dotenv

load_dotenv()

# 创建客户端，指定 DeepSeek 的兼容接口
client = anthropic.Anthropic(
    base_url="https://api.deepseek.com/anthropic"
)

# 封装安全提取文本的函数
def get_final_text(content_blocks):
    for block in content_blocks:
        if getattr(block, 'type', None) == 'text':
            return block.text
    return "（未获取到文本回复，可能是 max_tokens 太小）"

question = "给这家餐厅写一句广告词：一家卖重庆火锅的小店"

# ===== 实验1：temperature对输出随机性的影响 =====
print("=" * 50)
print("实验1：temperature参数（0=保守固定，1=创意随机）")
print("=" * 50)

# temperature=0：每次输出几乎相同，适合需要固定答案的场景（如JSON提取、代码生成）
print("\n【temperature=0，运行3次，观察结果是否一致】")
for i in range(3):
    r = client.messages.create(
        model="deepseek-v4-pro",
        max_tokens=2000,
        temperature=0,
        messages=[{"role": "user", "content": question}]
    )
    print(f"  第{i+1}次：{get_final_text(r.content).strip()}")

# temperature=1：每次输出都不同，适合创意写作
print("\n【temperature=1，运行3次，观察结果是否有变化】")
for i in range(3):
    r = client.messages.create(
        model="deepseek-v4-pro",
        max_tokens=2000,
        temperature=1,
        messages=[{"role": "user", "content": question}]
    )
    print(f"  第{i+1}次：{get_final_text(r.content).strip()}")


# ===== 实验2：max_tokens对输出长度的影响 =====
print("\n" + "=" * 50)
print("实验2：max_tokens参数（控制最大输出长度）")
print("=" * 50)

prompt = "介绍一下人工智能的发展历史"

# 注意：测试 max_tokens 截断时，需要保留较小的值，但为了防止思考耗尽，这里稍微调大测试区间
for max_tok in [2000, 3000, 5000]: 
    r = client.messages.create(
        model="deepseek-v4-pro",
        max_tokens=max_tok,
        messages=[{"role": "user", "content": prompt}]
    )
    text = get_final_text(r.content)
    print(f"\n【max_tokens={max_tok}，stop_reason={r.stop_reason}】")
    print(f"  实际输出token数：{r.usage.output_tokens}")
    print(f"  输出内容：{text[:100]}{'...' if len(text) > 100 else ''}")
    # stop_reason=end_turn：AI自然结束
    # stop_reason=max_tokens：被截断了，没说完


# ===== 实验3：token计费估算 =====
print("\n" + "=" * 50)
print("实验3：token用量统计")
print("=" * 50)

messages_list = [
    "你好",
    "用Python写一个冒泡排序",
    "解释一下量子计算的基本原理，要详细",
]

total_input = 0
total_output = 0

for msg in messages_list:
    r = client.messages.create(
        model="deepseek-v4-pro",
        max_tokens=2000,
        messages=[{"role": "user", "content": msg}]
    )
    input_tok = r.usage.input_tokens
    output_tok = r.usage.output_tokens
    total_input += input_tok
    total_output += output_tok
    print(f"\n问题：{msg[:20]}...")
    print(f"  输入token：{input_tok}，输出token：{output_tok}")

print(f"\n3次调用合计：输入{total_input} + 输出{total_output} = {total_input + total_output} tokens")

# 这里保留了你原来的 Claude 价格作为对比参考
# 实际 DeepSeek 的价格要便宜得多，你可以后续替换为 DeepSeek 的官方价格
claude_cost = (total_input * 3 + total_output * 15) / 1_000_000
print(f"如果按 Claude Sonnet 价格估算：约 ${claude_cost:.6f} 美元")