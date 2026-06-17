import sqlite3
import os
from datetime import datetime

DB_PATH = "./tasks.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            priority TEXT DEFAULT 'medium',
            done INTEGER DEFAULT 0,
            due_date TEXT DEFAULT NULL,
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
    """)
    conn.commit()
    conn.close()
    print("数据库初始化完成")


def row_to_dict(row) -> dict:
    """sqlite3.Row转普通dict"""
    return dict(row) if row else None


# ===== CRUD操作 =====

def db_create_task(title: str, description: str = "", priority: str = "medium", due_date: str = None) -> dict:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, description, priority, due_date) VALUES (?, ?, ?, ?)",
        (title, description, priority, due_date)
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (new_id,))
    row = cursor.fetchone()
    conn.close()
    return row_to_dict(row)


def db_get_tasks(done: int = None, priority: str = None, keyword: str = None) -> list:
    conn = get_conn()
    cursor = conn.cursor()

    conditions = []
    params = []

    if done is not None:
        conditions.append("done = ?")
        params.append(done)
    if priority:
        conditions.append("priority = ?")
        params.append(priority)
    if keyword:
        conditions.append("(title LIKE ? OR description LIKE ?)")
        params.extend([f"%{keyword}%", f"%{keyword}%"])

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    cursor.execute(f"SELECT * FROM tasks {where} ORDER BY id DESC", params)
    rows = cursor.fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


def db_update_done(task_id: int, done: bool) -> dict:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET done = ? WHERE id = ?", (1 if done else 0, task_id))
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        return None
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    return row_to_dict(row)


def db_update_task(task_id: int, title: str = None, description: str = None,
                   priority: str = None, due_date: str = None) -> dict:
    conn = get_conn()
    cursor = conn.cursor()
    updates = []
    params = []
    if title is not None:
        updates.append("title = ?")
        params.append(title)
    if description is not None:
        updates.append("description = ?")
        params.append(description)
    if priority is not None:
        updates.append("priority = ?")
        params.append(priority)
    if due_date is not None:
        updates.append("due_date = ?")
        params.append(due_date)
    if not updates:
        conn.close()
        return None
    params.append(task_id)
    cursor.execute(f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?", params)
    conn.commit()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    return row_to_dict(row)


def db_delete_task(task_id: int) -> bool:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success


def db_get_stats() -> dict:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM tasks")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE done = 1")
    done_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE done = 0")
    pending = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE priority = 'high' AND done = 0")
    high_priority = cursor.fetchone()[0]
    conn.close()
    return {
        "total": total,
        "done": done_count,
        "pending": pending,
        "high_priority_pending": high_priority
    }