import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI, APIError, AuthenticationError, RateLimitError

load_dotenv()

app = FastAPI(title="DeepSeek AI 聊天API")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化 DeepSeek 客户端（兼容 OpenAI SDK）
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL
)
# DeepSeek 模型名称
MODEL_NAME = "deepseek-chat"


# ===== 数据模型（保持不变，前端兼容） =====
class Message(BaseModel):
    role: str   # "user" / "assistant" / "system"
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]           # 对话历史
    system: Optional[str] = None      # System Prompt（可选）
    max_tokens: Optional[int] = 1000  # 最大输出token数
    temperature: Optional[float] = 0.7


# ===== 接口1：普通聊天（一次性返回） =====
@app.post("/chat")
def chat(request: ChatRequest):
    if not request.messages:
        raise HTTPException(status_code=400, detail="messages不能为空")

    try:
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        # 拼接 system prompt
        if request.system:
            messages.insert(0, {"role": "system", "content": request.system})

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stream=False
        )

        return {
            "reply": response.choices[0].message.content,
            "usage": {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
            }
        }

    except AuthenticationError:
        raise HTTPException(status_code=401, detail="DeepSeek API Key 无效")
    except RateLimitError:
        raise HTTPException(status_code=429, detail="请求太频繁，请稍后再试")
    except APIError as e:
        raise HTTPException(status_code=500, detail=f"DeepSeek 服务错误：{str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务异常：{str(e)}")


# ===== 接口2：流式聊天（SSE 流式返回） =====
@app.post("/chat/stream")
def chat_stream(request: ChatRequest):
    if not request.messages:
        raise HTTPException(status_code=400, detail="messages不能为空")

    messages = [{"role": m.role, "content": m.content} for m in request.messages]
    if request.system:
        messages.insert(0, {"role": "system", "content": request.system})

    def generate():
        try:
            stream = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                stream=True
            )
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    text = chunk.choices[0].delta.content
                    yield f"data: {json.dumps({'text': text}, ensure_ascii=False)}\n\n"
            # 结束标记
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"}
    )


# ===== 接口3：快捷单轮对话 =====
class SimpleRequest(BaseModel):
    message: str
    system: Optional[str] = None


@app.post("/chat/simple")
def simple_chat(request: SimpleRequest):
    """最简单的接口：只传一条消息，直接返回回复"""
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="消息不能为空")

    try:
        messages = []
        if request.system:
            messages.append({"role": "system", "content": request.system})
        messages.append({"role": "user", "content": request.message})

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            max_tokens=1000,
            stream=False
        )
        return {"reply": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== 健康检查 =====
@app.get("/health")
def health():
    api_key = os.getenv("DEEPSEEK_API_KEY")
    return {
        "status": "ok",
        "api_key_loaded": bool(api_key)
    }