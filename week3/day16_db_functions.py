import sqlite3
from typing import Optional

DB_PATH = "todo_app.db"  # 数据库文件路径


def get_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    # 让查询结果可以用列名访问（比如 row["name"]），而不只是下标（row[0]）
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库：创建表（如果不存在）"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            done INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
    """)
    conn.commit()
    conn.close()
    print("数据库初始化完成")


def create_todo(content: str) -> dict:
    """新增一条待办事项，返回新增的记录"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO todos (content) VALUES (?)",
        (content,)
    )
    conn.commit()
    # 获取刚刚插入的记录的id
    new_id = cursor.lastrowid
    conn.close()
    return get_todo_by_id(new_id)


def get_all_todos() -> list:
    """获取所有待办事项"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM todos ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    # 把Row对象转成普通字典
    return [dict(row) for row in rows]


def get_todo_by_id(todo_id: int) -> Optional[dict]:
    """根据id获取单条待办事项"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    return dict(row)


def update_todo_done(todo_id: int, done: bool) -> Optional[dict]:
    """更新待办事项的完成状态"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE todos SET done = ? WHERE id = ?",
        (1 if done else 0, todo_id)
    )
    conn.commit()
    affected = cursor.rowcount  # 受影响的行数，0表示没找到这条记录
    conn.close()
    if affected == 0:
        return None
    return get_todo_by_id(todo_id)


def delete_todo(todo_id: int) -> bool:
    """删除待办事项，返回是否删除成功"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


# ===== 测试所有函数 =====
if __name__ == "__main__":
    # 初始化数据库
    init_db()

    # 测试新增
    print("\n--- 新增待办 ---")
    todo1 = create_todo("完成Week3学习")
    todo2 = create_todo("复习FastAPI知识")
    todo3 = create_todo("推送代码到GitHub")
    print(f"新增成功：{todo1}")
    print(f"新增成功：{todo2}")
    print(f"新增成功：{todo3}")

    # 测试查询所有
    print("\n--- 查询所有 ---")
    all_todos = get_all_todos()
    for todo in all_todos:
        status = "✓" if todo["done"] else " "
        print(f"[{status}] id={todo['id']} {todo['content']} ({todo['created_at']})")

    # 测试标记完成
    print("\n--- 标记第1条完成 ---")
    updated = update_todo_done(todo1["id"], True)
    print(f"更新结果：{updated}")

    # 测试删除
    print("\n--- 删除第3条 ---")
    success = delete_todo(todo3["id"])
    print(f"删除结果：{success}")

    # 最终状态
    print("\n--- 最终状态 ---")
    final_todos = get_all_todos()
    for todo in final_todos:
        status = "✓" if todo["done"] else " "
        print(f"[{status}] {todo['content']}")