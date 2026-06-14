import requests
import json

BASE_URL = "http://127.0.0.1:8000"


def print_result(title: str, response):
    """统一打印测试结果"""
    print(f"\n{'=' * 40}")
    print(f"测试：{title}")
    print(f"状态码：{response.status_code}")
    try:
        print(f"返回：{json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except Exception:
        print(f"返回：{response.text}")


def run_tests():
    # 1. 健康检查
    r = requests.get(f"{BASE_URL}/health")
    print_result("健康检查", r)

    # 2. 新增待办
    r = requests.post(f"{BASE_URL}/todos", json={"content": "测试任务1"})
    print_result("新增待办", r)
    todo_id = r.json().get("id")

    r2 = requests.post(f"{BASE_URL}/todos", json={"content": "测试任务2"})
    print_result("新增待办2", r2)

    r3 = requests.post(f"{BASE_URL}/todos", json={"content": "数据库相关任务"})
    print_result("新增待办3", r3)

    # 3. 查询所有
    r = requests.get(f"{BASE_URL}/todos")
    print_result("查询所有待办", r)

    # 4. 搜索
    r = requests.get(f"{BASE_URL}/todos", params={"keyword": "数据库"})
    print_result("搜索关键词'数据库'", r)

    # 5. 标记完成
    r = requests.patch(f"{BASE_URL}/todos/{todo_id}", json={"done": True})
    print_result(f"标记id={todo_id}完成", r)

    # 6. 查询已完成
    r = requests.get(f"{BASE_URL}/todos", params={"done": True})
    print_result("查询已完成的待办", r)

    # 7. 查询不存在的id
    r = requests.get(f"{BASE_URL}/todos/99999")
    print_result("查询不存在的id（预期404）", r)

    # 8. 新增空内容（测试校验）
    r = requests.post(f"{BASE_URL}/todos", json={"content": "   "})
    print_result("新增空内容（预期400）", r)

    # 9. 删除
    r = requests.delete(f"{BASE_URL}/todos/{todo_id}")
    print_result(f"删除id={todo_id}", r)

    # 10. 确认删除后查询
    r = requests.get(f"{BASE_URL}/todos/{todo_id}")
    print_result(f"删除后再查询id={todo_id}（预期404）", r)


if __name__ == "__main__":
    run_tests()