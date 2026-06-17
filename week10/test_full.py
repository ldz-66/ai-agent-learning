import requests
import json

BASE = "http://127.0.0.1:8000"
SESSION = "test_session_full"

def chat(message):
    r = requests.post(f"{BASE}/chat", json={"message": message, "session_id": SESSION})
    data = r.json()
    print(f"\n你：{message}")
    print(f"小助：{data['reply']}")
    print(f"  [轮数：{data['history_turns']}]")
    return data['reply']

# 清空会话
requests.post(f"{BASE}/clear/{SESSION}")

# 完整对话测试
chat("你好！帮我添加三个任务：1.学习Agent开发，优先级高；2.买咖啡；3.整理代码")
chat("查看一下所有任务")
chat("我完成了学习Agent开发这个任务")
chat("查看未完成的任务")
chat("现在任务统计怎么样")
chat("把买咖啡那个任务删掉")
chat("最后看一下剩余任务")