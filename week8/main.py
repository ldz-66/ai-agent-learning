import os
import uuid
import json
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from rag_engine import RAGEngine
# 注意：main.py本身不直接调用AI，AI逻辑全在rag_engine.py里

load_dotenv()

app = FastAPI(title="知识库问答系统")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# 初始化RAG引擎（启动时加载模型，需要几秒）
print("正在启动服务，加载AI模型...")
rag = RAGEngine()
print("服务启动完成！")

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ===== 根路径：前端页面 =====
@app.get("/")
def root():
    return FileResponse("static/index.html")


# ===== 接口1：上传文档 =====
@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    # 检查文件类型
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="目前只支持.txt格式的文件")

    # 检查文件大小（限制1MB）
    content_bytes = await file.read()
    if len(content_bytes) > 1024 * 1024:
        raise HTTPException(status_code=400, detail="文件大小不能超过1MB")

    # 读取文件内容
    try:
        content = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        try:
            content = content_bytes.decode("gbk")
        except Exception:
            raise HTTPException(status_code=400, detail="文件编码不支持，请使用UTF-8编码")

    if not content.strip():
        raise HTTPException(status_code=400, detail="文件内容为空")

    # 生成文档ID并保存文件
    doc_id = str(uuid.uuid4())[:8]
    save_path = os.path.join(UPLOAD_DIR, f"{doc_id}_{file.filename}")
    with open(save_path, "wb") as f:
        f.write(content_bytes)

    # 添加到向量数据库
    title = file.filename.replace(".txt", "")
    result = rag.add_document(doc_id=doc_id, title=title, content=content)

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "添加失败"))

    return {
        "message": "上传成功",
        "doc_id": doc_id,
        "title": title,
        "chunks": result["chunks"],
        "chars": result["total_chars"]
    }


# ===== 接口2：获取文档列表 =====
@app.get("/documents")
def get_documents():
    return {"documents": rag.get_document_list()}


# ===== 接口3：删除文档 =====
@app.delete("/documents/{doc_id}")
def delete_document(doc_id: str):
    success = rag.delete_document(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="文档不存在")
    return {"message": "删除成功", "doc_id": doc_id}


# ===== 接口4：流式问答 =====
class AskRequest(BaseModel):
    question: str
    top_k: Optional[int] = 4


@app.post("/ask")
def ask(request: AskRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="问题不能为空")

    # 检索相关文档
    retrieved = rag.retrieve(request.question, top_k=request.top_k)

    def stream_response():
        # 先发送检索到的来源信息
        sources = [{"source": r["source"], "content": r["content"][:100]} for r in retrieved]
        yield f"data: {json.dumps({'sources': sources}, ensure_ascii=False)}\n\n"

        # 再流式发送AI回答
        for text_chunk in rag.generate_answer_stream(request.question, retrieved):
            yield f"data: {json.dumps({'text': text_chunk}, ensure_ascii=False)}\n\n"

        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(
        stream_response(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"}
    )


# ===== 接口5：获取知识库统计 =====
@app.get("/stats")
def get_stats():
    return rag.get_stats()


# ===== 接口6：重置知识库 =====
@app.post("/reset")
def reset():
    return rag.reset()


# ===== 健康检查 =====
@app.get("/health")
def health():
    return {
        "status": "ok",
        "chunks_in_db": rag.collection.count(),
        "api_key_loaded": bool(os.getenv("DEEPSEEK_API_KEY"))
    }