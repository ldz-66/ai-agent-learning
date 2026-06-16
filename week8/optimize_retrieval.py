from rag_engine import RAGEngine
import time

engine = RAGEngine(db_path="./test_optimize_db")

# 准备测试文档
test_doc = """
FastAPI是一个现代的Python Web框架，基于Python类型注解。
启动FastAPI服务器的命令是uvicorn main:app --reload。
--reload参数让代码改动后自动重启，开发时很方便。

路径参数定义在URL中，用大括号括起来：@app.get("/users/{user_id}")。
查询参数是函数里有默认值的参数，通过URL的?传递，例如/items?page=1&size=10。
POST请求的请求体需要用Pydantic的BaseModel来定义数据结构。

FastAPI会在/docs路径自动生成交互式API文档，无需额外配置。
CORS配置使用CORSMiddleware，开发时allow_origins设为["*"]表示允许所有来源。
"""

# 同一个文档，用不同chunk_size建索引
test_query = "FastAPI怎么定义查询参数？"

for chunk_size in [100, 200, 400]:
    # 重新建索引
    from sentence_transformers import SentenceTransformer
    import chromadb, re

    db = chromadb.EphemeralClient()  # 使用内存数据库，不持久化
    col = db.create_collection(f"test_{chunk_size}")
    embed_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    # 切分
    paras = [p.strip() for p in test_doc.split('\n\n') if p.strip()]
    chunks = []
    for para in paras:
        if len(para) <= chunk_size:
            chunks.append(para)
        else:
            sentences = re.split(r'([。！？])', para)
            curr = ""
            for i in range(0, len(sentences)-1, 2):
                s = sentences[i] + sentences[i+1]
                if len(curr) + len(s) <= chunk_size:
                    curr += s
                else:
                    if curr: chunks.append(curr)
                    curr = s
            if curr: chunks.append(curr)

    col.add(
        documents=chunks,
        embeddings=[embed_model.encode(c).tolist() for c in chunks],
        ids=[f"c{i}" for i in range(len(chunks))]
    )

    # 查询
    q_emb = embed_model.encode(test_query).tolist()
    results = col.query(query_embeddings=[q_emb], n_results=2)

    print(f"\nchunk_size={chunk_size}，共{len(chunks)}块：")
    for doc, dist in zip(results["documents"][0], results["distances"][0]):
        print(f"  [{dist:.4f}] {doc[:80]}...")