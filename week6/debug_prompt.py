import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# 初始化客户端，指向 DeepSeek 接口
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)

# 测试用的主题
test_topic = "一款保温杯，主打72小时保温，适合户外运动"

# 要测试的平台
platforms = ["小红书", "朋友圈", "广告语"]

# 文案风格提示词
PLATFORM_PROMPTS = {
    "小红书": """你是一个专业的小红书文案写手。
风格要求：
- 开头用"姐妹们！"或"宝子们！"
- 多用emoji（每段至少2个）
- 语气活泼，多用感叹号
- 适当分段，每段不超过3句
- 结尾加3-5个相关话题标签（#格式）
- 整体有种"真实分享"的感觉，不要太广告味""",

    "朋友圈": """你是一个朋友圈文案专家。
风格要求：
- 简短温暖，100字以内
- 有画面感，让人产生共鸣
- 不能太广告感，要像真实的生活分享
- 可以留悬念或者引发互动
- 适当用1-2个emoji点缀""",

    "广告语": """你是一个广告创意总监。
风格要求：
- 简短有力，最好不超过15个字
- 朗朗上口，有节奏感
- 直击用户痛点或欲望
- 有品牌记忆点
- 给出3-5个不同方向的版本供选择"""
}


def test_platform(platform, topic, requirements=""):
    system = PLATFORM_PROMPTS[platform]
    user_msg = f"请为以下内容生成{platform}文案：\n\n主题/产品：{topic}"
    if requirements:
        user_msg += f"\n补充要求：{requirements}"

    response = client.chat.completions.create(
        model="deepseek-chat",
        max_tokens=500,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_msg}
        ]
    )
    return response.choices[0].message.content


print("=" * 60)
print(f"测试主题：{test_topic}")
print("=" * 60)

for platform in platforms:
    print(f"\n【{platform}】")
    print("-" * 40)
    result = test_platform(platform, test_topic)
    print(result)
    print()

# ===== 调优实验：加入补充要求 =====
print("\n" + "=" * 60)
print("加入补充要求后的效果")
print("=" * 60)

print("\n【小红书 + 补充要求：强调冬天户外场景】")
result = test_platform(
    "小红书",
    test_topic,
    requirements="强调冬天户外徒步、露营场景，目标用户是20-35岁的户外爱好者"
)
print(result)