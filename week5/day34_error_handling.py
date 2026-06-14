import anthropic
from dotenv import load_dotenv
import time
import os

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
    return "（未获取到文本回复）"


# ===== 1. 正确处理各种API错误 =====
def safe_api_call(client, messages, max_retries=3):
    """带重试机制的API调用"""
    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model="deepseek-v4-pro",
                max_tokens=2000,  # 调大 token，防止思考耗尽额度
                messages=messages
            )
            return get_final_text(response.content)

        except anthropic.AuthenticationError:
            # API Key错误，重试没用，直接抛出
            print("✗ API Key错误，请检查.env文件")
            raise

        except anthropic.RateLimitError:
            # 请求太频繁，等待后重试
            wait_time = 2 ** attempt  # 指数退避：1秒、2秒、4秒
            print(f"  请求频率超限，等待{wait_time}秒后重试（第{attempt+1}次）...")
            time.sleep(wait_time)

        except anthropic.APIStatusError as e:
            # 其他API错误
            print(f"✗ API错误 {e.status_code}：{e.message}")
            if attempt < max_retries - 1:
                print(f"  等待1秒后重试...")
                time.sleep(1)
            else:
                raise

        except Exception as e:
            # 网络错误等
            print(f"✗ 未知错误：{e}")
            raise

    return None


# ===== 2. 测试正常调用 =====
print("=" * 50)
print("测试1：正常调用")
print("=" * 50)

result = safe_api_call(client, [{"role": "user", "content": "说一句话"}])
print("✓ 调用成功：", result)


# ===== 3. 测试错误的API Key =====
print("\n" + "=" * 50)
print("测试2：错误的API Key")
print("=" * 50)

try:
    # 故意使用错误的 Key 触发异常
    bad_client = anthropic.Anthropic(
        api_key="sk-wrong-key-12345",
        base_url="https://api.deepseek.com/anthropic"
    )
    result = safe_api_call(bad_client, [{"role": "user", "content": "你好"}])
except anthropic.AuthenticationError as e:
    print(f"✓ 正确捕获到认证错误：{type(e).__name__}")


# ===== 4. 检查API Key是否正确加载 =====
print("\n" + "=" * 50)
print("测试3：验证API Key加载")
print("=" * 50)

api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    print("✗ 未找到API Key，请检查.env文件是否存在且格式正确")
elif not api_key.startswith("sk-"):
    print(f"✗ API Key格式可能不对，当前值开头：{api_key[:10]}...")
else:
    print(f"✓ API Key已正确加载，开头：{api_key[:15]}...")
    print(f"✓ Key长度：{len(api_key)} 个字符")


# ===== 5. 简单的token预算控制 =====
print("\n" + "=" * 50)
print("测试4：token用量追踪")
print("=" * 50)

class TokenTracker:
    """追踪API调用的token用量"""
    def __init__(self, budget=10000):
        self.total_input = 0
        self.total_output = 0
        self.call_count = 0
        self.budget = budget  # token预算

    def track(self, response):
        self.total_input += response.usage.input_tokens
        self.total_output += response.usage.output_tokens
        self.call_count += 1

    def remaining_budget(self):
        return self.budget - self.total_input - self.total_output

    def report(self):
        print(f"  调用次数：{self.call_count}")
        print(f"  总输入token：{self.total_input}")
        print(f"  总输出token：{self.total_output}")
        print(f"  总消耗：{self.total_input + self.total_output}")
        print(f"  剩余预算：{self.remaining_budget()}")


tracker = TokenTracker(budget=100000)  # DeepSeek思考消耗较大，预算调大一点

questions = ["你好", "什么是API？", "Python有什么优点？"]
for q in questions:
    r = client.messages.create(
        model="deepseek-v4-pro",
        max_tokens=2000,
        messages=[{"role": "user", "content": q}]
    )
    tracker.track(r)
    print(f"  问：{q} → 消耗{r.usage.input_tokens + r.usage.output_tokens} tokens")

print("\n最终统计：")
tracker.report()