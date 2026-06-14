from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from typing import Optional
import sqlite3

# ===== 数据库相关 =====
DB_PATH = "todo_app.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
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


# ===== FastAPI应用 =====
app = FastAPI(title="Todo API", description="一个有数据库的待办事项API")
# 全局处理参数校验错误（比如传了错误类型的参数）
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"error": "参数格式错误", "detail": str(exc.errors())}
    )


# 启动时自动初始化数据库
@app.on_event("startup")
def startup():
    init_db()


class TodoCreate(BaseModel):
    content: str

    def validate_content(self):
        if not self.content.strip():
            raise ValueError("内容不能为空")
        if len(self.content) > 200:
            raise ValueError("内容不能超过200个字符")
        return self


class TodoUpdate(BaseModel):
    done: bool  # 完成状态


# ===== 接口 =====

# 获取所有待办事项（支持搜索和分页）
@app.get("/todos")
def get_todos(
    page: int = 1,
    size: int = 10,
    keyword: Optional[str] = None,
    done: Optional[bool] = None
):
    conn = get_connection()
    cursor = conn.cursor()

    # 动态构建查询条件
    conditions = []
    params = []

    if keyword:
        conditions.append("content LIKE ?")
        params.append(f"%{keyword}%")

    if done is not None:
        conditions.append("done = ?")
        params.append(1 if done else 0)

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    # 先查总数
    cursor.execute(f"SELECT COUNT(*) FROM todos {where_clause}", params)
    total = cursor.fetchone()[0]

    # 再查分页数据
    offset = (page - 1) * size
    cursor.execute(
        f"SELECT * FROM todos {where_clause} ORDER BY id DESC LIMIT ? OFFSET ?",
        params + [size, offset]
    )
    rows = cursor.fetchall()
    conn.close()

    return {
        "total": total,
        "page": page,
        "size": size,
        "items": [dict(row) for row in rows]
    }


# 获取单条待办事项
@app.get("/todos/{todo_id}")
def get_todo(todo_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail=f"待办事项 {todo_id} 不存在")
    return dict(row)


# 新增待办事项
@app.post("/todos", status_code=201)
def create_todo(todo: TodoCreate):
    if not todo.content.strip():
        raise HTTPException(status_code=400, detail="内容不能为空")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO todos (content) VALUES (?)",
        (todo.content,)
    )
    conn.commit()
    new_id = cursor.lastrowid
    # 查询刚插入的记录并返回
    cursor.execute("SELECT * FROM todos WHERE id = ?", (new_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row)


# 更新完成状态
@app.patch("/todos/{todo_id}")
def update_todo(todo_id: int, update: TodoUpdate):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE todos SET done = ? WHERE id = ?",
        (1 if update.done else 0, todo_id)
    )
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail=f"待办事项 {todo_id} 不存在")
    cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row)


# 删除待办事项
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail=f"待办事项 {todo_id} 不存在")
    conn.close()
    return {"message": f"待办事项 {todo_id} 已删除"}


# 健康检查
@app.get("/health")
def health():
    return {"status": "ok"}