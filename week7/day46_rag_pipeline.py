import chromadb
import os
import re
from openai import OpenAI
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from typing import List

load_dotenv()

# 初始化
print("初始化中...")
embed_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# 用openai库连接DeepSeek（接口兼容OpenAI格式）
deepseek = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

db = chromadb.PersistentClient(path="./rag_db")
collection = db.get_or_create_collection("rag_docs")
print("初始化完成")


def get_embedding(text: str) -> list:
    return embed_model.encode(text).tolist()


def chunk_text(text: str, max_length: int = 200) -> List[str]:
    """简单的段落切分"""
    paragraphs = text.strip().split('\n\n')
    chunks = []
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(para) <= max_length:
            chunks.append(para)
        else:
            sentences = re.split(r'([。！？])', para)
            current = ""
            for i in range(0, len(sentences) - 1, 2):
                s = sentences[i] + (sentences[i + 1] if i + 1 < len(sentences) else "")
                if len(current) + len(s) <= max_length:
                    current += s
                else:
                    if current:
                        chunks.append(current)
                    current = s
            if current:
                chunks.append(current)
    return [c for c in chunks if c.strip()]


# ===== 步骤1：建立知识库 =====
def build_knowledge_base(documents: dict):
    """
    documents: {"文档标题": "文档内容", ...}
    """
    print("\n正在建立知识库...")
    all_chunks = []
    all_ids = []
    all_metadatas = []

    for doc_title, doc_content in documents.items():
        chunks = chunk_text(doc_content)
        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_ids.append(f"{doc_title}_{i}")
            all_metadatas.append({"source": doc_title, "chunk_index": i})

    # 生成embedding
    embeddings = [get_embedding(c) for c in all_chunks]

    # 清空旧数据，重新添加
    if collection.count() > 0:
        existing = collection.get()
        collection.delete(ids=existing["ids"])

    collection.add(
        documents=all_chunks,
        embeddings=embeddings,
        ids=all_ids,
        metadatas=all_metadatas
    )
    print(f"知识库建立完成，共 {len(all_chunks)} 个文本块")


# ===== 步骤2：检索相关内容 =====
def retrieve(query: str, top_k: int = 3) -> List[dict]:
    """根据问题检索最相关的文本块"""
    query_embedding = get_embedding(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )
    retrieved = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        retrieved.append({"content": doc, "source": meta["source"], "distance": dist})
    return retrieved


# ===== 步骤3：生成回答 =====
def generate_answer(query: str, context_chunks: List[dict]) -> str:
    """把检索到的内容 + 问题一起发给Claude生成回答"""
    # 构建上下文
    context = "\n\n".join([
        f"【来源：{c['source']}】\n{c['content']}"
        for c in context_chunks
    ])

    system_prompt = """你是一个知识库问答助手。
请根据提供的参考资料回答问题。
要求：
1. 只根据参考资料中的内容回答，不要添加资料中没有的信息
2. 如果资料中没有相关信息，明确说"根据现有资料无法回答此问题"
3. 回答时注明信息来源（用【来源：xxx】格式）
4. 回答简洁清晰"""

    user_message = f"""参考资料：
{context}

问题：{query}"""

    response = deepseek.chat.completions.create(
        model="deepseek-chat",
        max_tokens=500,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    )
    return response.choices[0].message.content


# ===== 完整RAG流程 =====
def rag_query(query: str) -> dict:
    """完整的RAG查询：检索 + 生成"""
    print(f"\n问题：{query}")

    # 检索
    retrieved = retrieve(query, top_k=3)
    print(f"检索到 {len(retrieved)} 条相关内容：")
    for r in retrieved:
        print(f"  [{r['distance']:.4f}] {r['source']}：{r['content'][:60]}...")

    # 生成
    answer = generate_answer(query, retrieved)
    print(f"\n回答：\n{answer}")
    return {"query": query, "retrieved": retrieved, "answer": answer}


# ===== 测试知识库 =====
# 用你自己的学习笔记作为知识库（模拟）
knowledge = {
    "Python基础": """
Python是一种高级编程语言，语法简洁易读。
虚拟环境（venv）用于隔离不同项目的依赖，创建命令是 python -m venv venv。
pip是Python的包管理工具，用于安装和管理第三方库。
列表推导式是Python的特色语法，可以简化列表创建：[x**2 for x in range(10)]。
""",
    "FastAPI教程": """
FastAPI是一个现代的Python Web框架，基于类型注解自动生成API文档。
启动命令：uvicorn main:app --reload，其中--reload表示代码改动后自动重启。
路径参数用大括号定义：@app.get("/users/{user_id}")。
查询参数直接写在函数参数里，有默认值的是可选参数。
POST请求的请求体需要用Pydantic的BaseModel定义数据结构。
""",
    "数据库知识": """
SQLite是轻量级数据库，数据存在单个.db文件中，Python内置sqlite3库支持它。
SQL基本操作：SELECT查询、INSERT插入、UPDATE更新、DELETE删除。
row_factory = sqlite3.Row 可以让查询结果用列名访问而不是下标。
ORM（对象关系映射）让你用Python对象操作数据库，不需要写SQL语句。
""",
    "AI开发入门": """
大模型API通过messages列表传入对话历史，每条消息有role（user/assistant）和content。
System Prompt用于设定AI的角色和行为规范，在messages之外单独传入。
temperature参数控制输出随机性：0最保守固定，1最有创意随机。
流式输出（Streaming）让AI回复像打字机一样逐字显示，提升用户体验。
RAG（检索增强生成）让AI基于特定文档回答问题，而不只用训练时的知识。
"""
}

# 建立知识库
build_knowledge_base(knowledge)

# 测试查询
print("\n" + "=" * 60)
print("RAG问答测试")
print("=" * 60)

test_questions = [
    "如何创建Python虚拟环境？",
    "FastAPI怎么启动服务器？",
    "什么是RAG技术？",
    "如何让AI的输出更有创意？",
    "今天天气怎么样？",  # 知识库里没有的问题
]

for question in test_questions:
    print("\n" + "-" * 40)
    rag_query(question)