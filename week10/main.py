import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from db import init_db
from agent import TaskAgent

load_dotenv()

app = FastAPI(title="智能任务管理助手API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化数据库
init_db()

# 用dict存储每个会话的Agent实例（实际生产用Redis，这里简化）
sessions: dict[str, TaskAgent] = {}


def get_or_create_agent(session_id: str) -> TaskAgent:
    if session_id not in sessions:
        sessions[session_id] = TaskAgent()
    return sessions[session_id]


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"


@app.post("/chat")
def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="消息不能为空")

    agent = get_or_create_agent(request.session_id)

    try:
        reply = agent.chat(request.message)
        return {
            "reply": reply,
            "session_id": request.session_id,
            "history_turns": agent.get_history_length() // 2
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/clear/{session_id}")
def clear_session(session_id: str):
    if session_id in sessions:
        sessions[session_id].clear_history()
    return {"message": "会话已清空"}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "active_sessions": len(sessions),
        "api_key_loaded": bool(os.getenv("DEEPSEEK_API_KEY"))
    }