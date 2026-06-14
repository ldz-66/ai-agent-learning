from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import jieba
from collections import Counter
import re

app = FastAPI(title="文本分析API", description="提供文本的各种分析功能")


class TextInput(BaseModel):
    text: str
    top_n: Optional[int] = 5  # 返回前N个高频词，默认5个


# ===== 接口1：基础统计 =====
@app.post("/analyze/basic")
def basic_analysis(input: TextInput):
    text = input.text
    if not text.strip():
        raise HTTPException(status_code=400, detail="文本不能为空")

    # 统计字符数（不含空格）
    char_count = len(text.replace(" ", ""))
    # 统计行数
    line_count = len(text.strip().split("\n"))
    # 统计中文字符数
    chinese_count = len(re.findall(r'[\u4e00-\u9fff]', text))
    # 统计英文单词数
    english_words = len(re.findall(r'\b[a-zA-Z]+\b', text))

    return {
        "字符总数": char_count,
        "行数": line_count,
        "中文字符数": chinese_count,
        "英文单词数": english_words,
    }


# ===== 接口2：关键词提取 =====
@app.post("/analyze/keywords")
def extract_keywords(input: TextInput):
    text = input.text
    if not text.strip():
        raise HTTPException(status_code=400, detail="文本不能为空")

    # 用jieba分词
    words = jieba.cut(text)
    # 过滤掉标点、空格、单字词（通常没意义）
    stop_words = {"的", "了", "是", "在", "我", "有", "和", "就", "不", "人",
                  "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去",
                  "你", "会", "着", "没有", "看", "好", "自己", "这"}
    filtered_words = [
        w for w in words
        if len(w) > 1 and w not in stop_words and not re.match(r'[\s\W]', w)
    ]

    # 统计词频
    counter = Counter(filtered_words)
    top_words = counter.most_common(input.top_n)

    return {
        "分词结果（前20个）": filtered_words[:20],
        "高频词TOP{}".format(input.top_n): [
            {"词": word, "出现次数": count} for word, count in top_words
        ]
    }


# ===== 接口3：敏感词检测 =====
SENSITIVE_WORDS = ["垃圾", "骗子", "违法", "黑客"]  # 简单示例

@app.post("/analyze/sensitive")
def check_sensitive(input: TextInput):
    text = input.text
    found = [word for word in SENSITIVE_WORDS if word in text]
    return {
        "包含敏感词": len(found) > 0,
        "发现的敏感词": found,
        "敏感词数量": len(found)
    }


# ===== 健康检查接口（标准做法，所有API都应该有） =====
@app.get("/health")
def health_check():
    return {"status": "ok"}