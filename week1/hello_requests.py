import requests

response = requests.get("https://api.github.com")
print("状态码:", response.status_code)
print("响应内容前200字符:", response.text[:200])