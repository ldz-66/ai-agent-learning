import chromadb
import os
import re
from openai import OpenAI
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

# 初始化
embed_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# 用openai库连接DeepSeek
deepseek = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

db = chromadb.PersistentClient(path="./notes_db")
collection = db.get_or_create_collection("notes")


def get_embedding(text):
    return embed_model.encode(text).tolist()


def load_and_index_notes(filepath="my_notes.txt"):
    """读取笔记文件并建立索引"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 按行切分，过滤空行
    lines = [line.strip() for line in content.split('\n') if line.strip()]

    # 清空旧数据
    if collection.count() > 0:
        existing = collection.get()
        collection.delete(ids=existing["ids"])

    # 建立索引
    embeddings = [get_embedding(line) for line in lines]
    collection.add(
        documents=lines,
        embeddings=embeddings,
        ids=[f"note_{i}" for i in range(len(lines))]
    )
    print(f"已索引 {len(lines)} 条笔记")


def ask(question: str):
    """问答函数"""
    # 检索
    query_emb = get_embedding(question)
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=5,
        include=["documents"]
    )
    context = "\n".join(results["documents"][0])

    # 生成回答
    response = deepseek.chat.completions.create(
        model="deepseek-chat",
        max_tokens=300,
        messages=[
            {"role": "system", "content": "你是一个学习助手，根据用户的学习笔记回答问题。只根据笔记内容回答，笔记里没有的说'笔记中暂无相关内容'。"},
            {"role": "user", "content": f"笔记内容:\n{context}\n\n问题：{question}"}
        ]
    )
    return response.choices[0].message.content


# 主程序
print("正在加载笔记...")
load_and_index_notes()

print("\n笔记问答助手已启动（输入 quit 退出）")
while True:
    question = input("\n请问：").strip()
    if question.lower() == "quit":
        break
    if not question:
        continue
    print("\n回答：", ask(question))