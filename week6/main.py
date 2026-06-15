import os
import json
import requests

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI文案助手 - Stable Version")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态目录（确保存在）
if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/static", StaticFiles(directory="static"), name="static")

# ===== DeepSeek API =====
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_URL = "https://api.deepseek.com/chat/completions"


# ===== 平台 Prompt =====
PLATFORM_PROMPTS = {
    "小红书": "你是小红书文案专家，风格活泼+emoji+分段+话题标签",
    "朋友圈": "你是朋友圈文案专家，温暖简短有画面感",
    "微博": "你是微博文案专家，简洁有观点",
    "产品描述": "你是电商文案专家，突出卖点和利益",
    "广告语": "你是广告创意专家，输出多版本短句"
}


# ===== 请求模型（不会422风险写法）=====
class GenerateRequest(BaseModel):
    topic: str
    platform: str
    requirements: Optional[str] = ""
    max_length: Optional[int] = 300


# =========================
# 🧠 调用 DeepSeek（稳定版）
# =========================
def call_deepseek(messages, stream=False):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "stream": stream
    }

    return requests.post(API_URL, headers=headers, json=payload, stream=stream)


# =========================
# 🚀 文案生成接口（流式）
# =========================
@app.post("/generate")
def generate(request: GenerateRequest):

    if request.platform not in PLATFORM_PROMPTS:
        raise HTTPException(status_code=400, detail="不支持的平台")

    system_prompt = PLATFORM_PROMPTS[request.platform]

    user_prompt = f"""
主题：{request.topic}
要求：{request.requirements}
字数：{request.max_length}
"""

    def stream():
        try:
            resp = call_deepseek([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ], stream=True)

            for line in resp.iter_lines():
                if line:
                    line = line.decode("utf-8")

                    if line.startswith("data:"):
                        chunk = line.replace("data: ", "")

                        if chunk != "[DONE]":
                            try:
                                data = json.loads(chunk)
                                text = data["choices"][0]["delta"].get("content", "")
                                if text:
                                    yield f"data: {json.dumps({'text': text}, ensure_ascii=False)}\n\n"
                            except:
                                pass

            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


# =========================
# 📦 平台列表
# =========================
@app.get("/platforms")
def platforms():
    return {"platforms": list(PLATFORM_PROMPTS.keys())}


# =========================
# ❤️ health
# =========================
@app.get("/health")
def health():
    return {
        "status": "ok",
        "model": "deepseek-chat"
    }


# =========================
# 🏠 首页
# =========================
@app.get("/")
def home():
    return FileResponse("static/index.html")