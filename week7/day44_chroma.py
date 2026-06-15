import chromadb
from sentence_transformers import SentenceTransformer
import os

# 初始化本地Embedding模型
print("加载Embedding模型...")
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def get_embedding(text):
    return model.encode(text).tolist()


# ===== 1. 创建Chroma客户端 =====
# persist_directory：数据库文件保存在本地的路径
client = chromadb.PersistentClient(path="./chroma_db")
print("Chroma数据库初始化完成")


# ===== 2. 创建或获取一个Collection（类似数据库里的表） =====
# get_or_create：已存在则获取，不存在则创建
collection = client.get_or_create_collection(
    name="my_knowledge_base",
    metadata={"description": "我的知识库"}
)
print(f"Collection：{collection.name}")


# ===== 3. 添加文档 =====
documents = [
    "FastAPI是一个现代的Python Web框架，基于Python 3.6+的类型注解，性能极高",
    "Python的虚拟环境（venv）用于隔离不同项目的依赖包",
    "SQLite是一种轻量级的关系型数据库，数据存储在单个文件中",
    "Git的commit命令用于保存当前的代码快照到本地仓库",
    "RAG（检索增强生成）让AI能基于特定文档回答问题",
    "向量数据库存储文本的Embedding向量，支持语义相似度检索",
    "大模型的temperature参数控制输出的随机性，0最保守，1最随机",
    "HTTP的POST方法用于向服务器提交数据，GET方法用于获取数据",
    "JavaScript的async/await语法用于处理异步操作",
    "Pydantic是FastAPI使用的数据验证库，通过类型注解自动验证数据",
]

# 生成所有文档的embedding
print("\n正在生成文档Embedding...")
embeddings = [get_embedding(doc) for doc in documents]

# 添加到数据库
# ids：每条文档的唯一标识符（必须是字符串）
collection.add(
    documents=documents,
    embeddings=embeddings,
    ids=[f"doc_{i}" for i in range(len(documents))],
    metadatas=[{"source": "tutorial", "index": i} for i in range(len(documents))]
)
print(f"已添加 {len(documents)} 条文档，当前总数：{collection.count()}")


# ===== 4. 查询——语义搜索 =====
print("\n" + "=" * 50)
print("语义搜索测试")
print("=" * 50)

queries = [
    "怎么管理Python包？",
    "如何让AI回答我自己文档里的问题？",
    "网页请求是怎么工作的？",
]

for query in queries:
    print(f"\n查询：{query}")
    query_embedding = get_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=2,  # 返回最相关的2条
        include=["documents", "distances", "metadatas"]
    )

    for i, (doc, dist) in enumerate(zip(
        results["documents"][0],
        results["distances"][0]
    )):
        # distance越小越相似（Chroma默认用L2距离）
        print(f"  第{i+1}名 [距离={dist:.4f}]：{doc}")


# ===== 5. 删除和更新 =====
print("\n" + "=" * 50)
print("删除和更新操作")
print("=" * 50)

# 删除一条
collection.delete(ids=["doc_0"])
print(f"删除后文档数：{collection.count()}")

# 更新一条（先删后加）
collection.upsert(
    documents=["FastAPI是一个现代高性能的Python Web框架，支持自动生成API文档"],
    embeddings=[get_embedding("FastAPI是一个现代高性能的Python Web框架，支持自动生成API文档")],
    ids=["doc_0"],
)
print(f"更新后文档数：{collection.count()}")