import requests

# ===== 练习1：GET请求，获取一条随机笑话 =====
print("=" * 40)
print("练习1：获取随机笑话")
print("=" * 40)

response = requests.get(
    "https://official-joke-api.appspot.com/random_joke"
)

print("状态码:", response.status_code)

# 把JSON响应转成Python字典
data = response.json()
print("类型:", type(data))
print("笑话setup:", data["setup"])
print("笑话punchline:", data["punchline"])


# ===== 练习2：GET请求带参数 =====
print("\n" + "=" * 40)
print("练习2：搜索GitHub仓库")
print("=" * 40)

response2 = requests.get(
    "https://api.github.com/search/repositories",
    params={
        "q": "fastapi",
        "sort": "stars",
        "per_page": 3
    }
)

print("状态码:", response2.status_code)
data2 = response2.json()
print(f"搜索结果总数: {data2['total_count']}")
print("前3个仓库：")
for repo in data2["items"]:
    print(f"  - {repo['name']}（⭐{repo['stargazers_count']}）: {repo['description']}")


# ===== 练习3：处理请求头 =====
print("\n" + "=" * 40)
print("练习3：带请求头的请求")
print("=" * 40)

response3 = requests.get(
    "https://api.github.com/user",
     headers={"Authorization": "Bearer fake_token_12345"}
)
print("状态码:", response3.status_code)  # 应该是401，因为token是假的
print("错误信息:", response3.json().get("message"))