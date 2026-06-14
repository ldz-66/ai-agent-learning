import requests
import json

BASE_URL = "http://127.0.0.1:8000"


def test_basic_analysis():
    print("=" * 40)
    print("测试：基础文本分析")
    print("=" * 40)
    
    response = requests.post(
        f"{BASE_URL}/analyze/basic",
        json={"text": "今天天气很好，我去公园散步。The weather is nice."}
    )
    print("状态码:", response.status_code)
    print("结果:", json.dumps(response.json(), ensure_ascii=False, indent=2))


def test_keywords():
    print("\n" + "=" * 40)
    print("测试：关键词提取")
    print("=" * 40)
    
    response = requests.post(
        f"{BASE_URL}/analyze/keywords",
        json={
            "text": "人工智能技术发展迅速，大模型应用越来越广泛，AI应用开发成为热门技术方向",
            "top_n": 3
        }
    )
    print("状态码:", response.status_code)
    result = response.json()
    print("高频词:", json.dumps(result.get("高频词TOP3"), ensure_ascii=False, indent=2))


def test_error_handling():
    print("\n" + "=" * 40)
    print("测试：错误处理（空文本）")
    print("=" * 40)
    
    response = requests.post(
        f"{BASE_URL}/analyze/basic",
        json={"text": "   "}  # 只有空格，应该返回400
    )
    print("状态码:", response.status_code)  # 预期400
    print("错误信息:", response.json())


def test_health():
    print("\n" + "=" * 40)
    print("测试：健康检查")
    print("=" * 40)
    
    response = requests.get(f"{BASE_URL}/health")
    print("状态码:", response.status_code)
    print("结果:", response.json())


if __name__ == "__main__":
    test_basic_analysis()
    test_keywords()
    test_error_handling()
    test_health()