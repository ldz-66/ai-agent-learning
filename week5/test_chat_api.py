import requests
import json

BASE_URL = "http://127.0.0.1:8000"


def test_simple():
    print("=" * 40)
    print("测试：简单聊天")
    print("=" * 40)
    r = requests.post(f"{BASE_URL}/chat/simple", json={
        "message": "用一句话解释什么是API",
        "system": "你是一个技术老师，用最简单的话解释复杂概念"
    })
    print("状态码:", r.status_code)
    print("回复:", r.json()["reply"])


def test_multi_turn():
    print("\n" + "=" * 40)
    print("测试：多轮对话")
    print("=" * 40)
    r = requests.post(f"{BASE_URL}/chat", json={
        "messages": [
            {"role": "user", "content": "我在学Python，目前学完了基础语法"},
            {"role": "assistant", "content": "太好了！学完基础语法是很好的开始。"},
            {"role": "user", "content": "根据我的情况，下一步该学什么？"}
        ],
        "system": "你是一个编程学习顾问，给出具体可操作的建议",
        "temperature": 0.5
    })
    data = r.json()
    print("状态码:", r.status_code)
    print("回复:", data["reply"])
    print("token用量:", data["usage"])


def test_health():
    print("\n" + "=" * 40)
    print("测试：健康检查")
    print("=" * 40)
    r = requests.get(f"{BASE_URL}/health")
    print("状态码:", r.status_code)
    print("结果:", r.json())


if __name__ == "__main__":
    test_health()
    test_simple()
    test_multi_turn()