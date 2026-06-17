import os
import uuid
import json
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from db import init_db
from agent import SmartAssistant

load_dotenv()

app = FastAPI(title="个人智能助手")
app.add_middleware(CORSMiddleware, allow_origins=["https://ai-agent-learning.vercel.app"], allow_methods=["*"], allow_headers=["*"])
import os
os.makedirs("static", exist_ok=True)
os.makedirs("uploads", exist_ok=True)
os.makedirs("chroma_db", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

print("正在初始化智能助手（加载AI模型，约10-20秒）...")
init_db()
assistant = SmartAssistant()
print("智能助手初始化完成！")

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def root():
    return FileResponse("static/index.html")


# ===== 对话接口 =====
class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="消息不能为空")
    try:
        reply = assistant.chat(request.message)
        return {
            "reply": reply,
            "history_turns": assistant.get_history_count()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/clear")
def clear_chat():
    assistant.clear_history()
    return {"message": "对话已清空"}


# ===== 文档上传接口 =====
@app.post("/upload")
async def upload_doc(file: UploadFile = File(...)):
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="只支持.txt格式")

    content_bytes = await file.read()
    if len(content_bytes) > 1024 * 1024:
        raise HTTPException(status_code=400, detail="文件不能超过1MB")

    try:
        content = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        content = content_bytes.decode("gbk", errors="ignore")

    if not content.strip():
        raise HTTPException(status_code=400, detail="文件内容为空")

    doc_id = str(uuid.uuid4())[:8]
    title = file.filename.replace(".txt", "")
    result = assistant.rag.add_document(doc_id=doc_id, title=title, content=content)

    if not result["success"]:
        raise HTTPException(status_code=500, detail="文档添加失败")

    return {"message": "上传成功", "title": title, "chunks": result["chunks"]}


# ===== 文档管理接口 =====
@app.get("/documents")
def get_docs():
    return {"documents": assistant.rag.get_doc_list()}


@app.delete("/documents/{doc_id}")
def delete_doc(doc_id: str):
    success = assistant.rag.delete_document(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="文档不存在")
    return {"message": "删除成功"}


# ===== 健康检查 =====
@app.get("/health")
def health():
    return {
        "status": "ok",
        "api_key_loaded": bool(os.getenv("DEEPSEEK_API_KEY")),
        "kb_chunks": assistant.rag.collection.count(),
        "history_turns": assistant.get_history_count()
    }