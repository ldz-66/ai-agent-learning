from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# ===== 1. 路径参数 =====
@app.get("/users/{user_id}")
def get_user(user_id: int):
    # 模拟数据库里有id为1和2的用户
    fake_users = {
        1: {"id": 1, "name": "小明", "age": 20},
        2: {"id": 2, "name": "小红", "age": 19},
    }
    if user_id not in fake_users:
        # 用户不存在时，返回404错误
        raise HTTPException(status_code=404, detail=f"用户 {user_id} 不存在")
    return fake_users[user_id]


# ===== 2. 查询参数（可选） =====
@app.get("/items")
def get_items(
    page: int = 1,           # 有默认值，可以不传
    size: int = 10,          # 有默认值，可以不传
    keyword: Optional[str] = None  # Optional表示可以不传，默认None
):
    return {
        "page": page,
        "size": size,
        "keyword": keyword,
        "message": f"查询第{page}页，每页{size}条" + (f"，关键词：{keyword}" if keyword else "")
    }


# ===== 3. 请求体（POST请求） =====
class UserCreate(BaseModel):
    name: str
    age: int
    email: Optional[str] = None  # 可选字段


@app.post("/users")
def create_user(user: UserCreate):
    # 实际项目里这里会存数据库，现在先假装存了
    return {
        "message": "用户创建成功",
        "user": {
            "id": 999,  # 假装数据库生成了一个id
            "name": user.name,
            "age": user.age,
            "email": user.email
        }
    }