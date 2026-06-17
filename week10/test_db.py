from db import init_db
from tools import execute_tool

init_db()

# 测试创建
print(execute_tool("create_task", {"title": "完成Week10学习", "priority": "high"}))
print(execute_tool("create_task", {"title": "买菜", "priority": "low"}))
print(execute_tool("create_task", {"title": "准备期末考试", "priority": "high", "due_date": "2025-07-01"}))

# 测试查询
print("\n" + execute_tool("get_tasks", {}))

# 测试统计
print("\n" + execute_tool("get_task_stats", {}))

# 测试完成
print("\n" + execute_tool("update_task_done", {"task_id": 1, "done": True}))

# 测试筛选未完成
print("\n" + execute_tool("get_tasks", {"done": False}))