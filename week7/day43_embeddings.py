from sentence_transformers import SentenceTransformer
import numpy as np
import math

# 加载本地Embedding模型（第一次会自动下载，约100MB）
print("加载Embedding模型（首次需要下载，请稍候）...")
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
print("模型加载完成！")


def get_embedding(text: str) -> list:
    """把文字转成向量"""
    return model.encode(text).tolist()


def cosine_similarity(vec1, vec2) -> float:
    """计算两个向量的余弦相似度（-1到1，越接近1越相似）"""
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))


# ===== 实验1：相似度对比 =====
print("=" * 50)
print("实验1：语义相似度对比")
print("=" * 50)

texts = [
    "Python是一种编程语言",
    "Python是用于编写程序的语言",
    "苹果是一种水果",
    "我今天吃了一个苹果",
    "FastAPI是一个Python Web框架",
]

print("\n正在生成Embedding...")
embeddings = [get_embedding(t) for t in texts]
print(f"每个向量的维度：{len(embeddings[0])}")

print("\n两两相似度（越接近1越相似）：")
for i in range(len(texts)):
    for j in range(i + 1, len(texts)):
        sim = cosine_similarity(embeddings[i], embeddings[j])
        print(f"  [{sim:.4f}] '{texts[i][:20]}' vs '{texts[j][:20]}'")


# ===== 实验2：语义搜索 =====
print("\n" + "=" * 50)
print("实验2：语义搜索（找最相关的句子）")
print("=" * 50)

knowledge_base = [
    "FastAPI是一个现代的Python Web框架，性能很高",
    "Python的列表推导式可以简化代码",
    "SQLite是一种轻量级的嵌入式数据库",
    "大模型（LLM）是基于Transformer架构的神经网络",
    "向量数据库用于存储和检索Embedding向量",
    "RAG技术结合了检索和生成，让AI能回答特定领域的问题",
    "Git是一个分布式版本控制系统",
    "JavaScript是网页前端开发的主要语言",
]

print("\n正在为知识库生成Embedding...")
kb_embeddings = [get_embedding(text) for text in knowledge_base]

query = "什么是向量数据库？"
print(f"\n查询：{query}")
query_embedding = get_embedding(query)

similarities = [
    (cosine_similarity(query_embedding, kb_emb), kb_text)
    for kb_emb, kb_text in zip(kb_embeddings, knowledge_base)
]
similarities.sort(reverse=True)

print("\n检索结果（按相关性排序）：")
for rank, (score, text) in enumerate(similarities[:3], 1):
    print(f"  第{rank}名 [{score:.4f}]：{text}")   