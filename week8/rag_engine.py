import chromadb
import re
import os
from sentence_transformers import SentenceTransformer
from typing import List, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class RAGEngine:
    """RAG核心引擎：负责文档的存储、检索和问答生成"""

    def __init__(self, db_path: str = "./chroma_db", collection_name: str = "knowledge_base"):
        print("正在初始化RAG引擎...")

        # 初始化Embedding模型（本地模型，不需要API）
        self.embed_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

        # 初始化向量数据库
        self.db = chromadb.PersistentClient(path=db_path)
        self.collection = self.db.get_or_create_collection(collection_name)

        # 用openai库连接DeepSeek（接口兼容OpenAI格式）
        self.deepseek = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )

        print(f"RAG引擎初始化完成，当前知识库文档块数：{self.collection.count()}")


    def get_embedding(self, text: str) -> list:
        """将文本转换为向量"""
        return self.embed_model.encode(text).tolist()


    def chunk_text(self, text: str, max_length: int = 300, overlap: int = 50) -> List[str]:
        """将长文本切分为适合检索的小块"""
        # 按段落切分
        paragraphs = text.strip().split('\n\n')
        chunks = []

        for para in paragraphs:
            para = para.strip()
            if not para or len(para) < 10:  # 跳过太短的段落
                continue

            if len(para) <= max_length:
                chunks.append(para)
            else:
                # 按句子进一步切分
                sentences = re.split(r'([。！？\.\!\?])', para)
                current = ""
                for i in range(0, len(sentences) - 1, 2):
                    s = sentences[i] + (sentences[i + 1] if i + 1 < len(sentences) else "")
                    if len(current) + len(s) <= max_length:
                        current += s
                    else:
                        if current.strip():
                            chunks.append(current.strip())
                        current = s
                if current.strip():
                    chunks.append(current.strip())

        return [c for c in chunks if c.strip()]


    def add_document(self, doc_id: str, title: str, content: str) -> dict:
        """添加文档到知识库"""
        chunks = self.chunk_text(content)
        if not chunks:
            return {"success": False, "error": "文档内容为空或无法切分"}

        chunk_ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        embeddings = [self.get_embedding(chunk) for chunk in chunks]
        metadatas = [
            {"doc_id": doc_id, "title": title, "chunk_index": i, "total_chunks": len(chunks)}
            for i in range(len(chunks))
        ]

        self.collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=chunk_ids,
            metadatas=metadatas
        )

        return {
            "success": True,
            "doc_id": doc_id,
            "title": title,
            "chunks": len(chunks),
            "total_chars": len(content)
        }


    def delete_document(self, doc_id: str) -> bool:
        """删除文档的所有chunks"""
        results = self.collection.get(where={"doc_id": doc_id})
        if not results["ids"]:
            return False
        self.collection.delete(ids=results["ids"])
        return True


    def get_document_list(self) -> List[dict]:
        """获取所有文档的列表（去重，每个文档只显示一次）"""
        if self.collection.count() == 0:
            return []

        results = self.collection.get(include=["metadatas"])
        seen_docs = {}
        for meta in results["metadatas"]:
            doc_id = meta["doc_id"]
            if doc_id not in seen_docs:
                seen_docs[doc_id] = {
                    "doc_id": doc_id,
                    "title": meta["title"],
                    "chunks": meta["total_chunks"]
                }
        return list(seen_docs.values())


    def retrieve(self, query: str, top_k: int = 4) -> List[dict]:
        """检索与问题最相关的文档块"""
        if self.collection.count() == 0:
            return []

        query_embedding = self.get_embedding(query)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, self.collection.count()),
            include=["documents", "metadatas", "distances"]
        )

        retrieved = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        ):
            retrieved.append({
                "content": doc,
                "source": meta["title"],
                "doc_id": meta["doc_id"],
                "distance": dist
            })
        return retrieved


    def generate_answer_stream(self, query: str, retrieved: List[dict]):
        """流式生成回答（返回一个生成器）"""
        if not retrieved:
            yield "知识库中暂无相关文档，请先上传一些文档。"
            return

        # 构建上下文
        context_parts = []
        for i, r in enumerate(retrieved, 1):
            context_parts.append(f"[参考{i}·来源：{r['source']}]\n{r['content']}")
        context = "\n\n".join(context_parts)

        system_prompt = """你是一个知识库问答助手。
请严格根据提供的参考资料回答问题。

规则：
1. 只使用参考资料中的信息，不添加资料之外的内容
2. 回答时在句子末尾用【参考1】【参考2】等标注信息来源
3. 如果参考资料中没有相关信息，明确说"根据现有文档，暂无相关信息"
4. 回答要简洁有条理"""

        user_message = f"""参考资料：
{context}

用户问题：{query}"""

        # DeepSeek支持流式输出，stream=True开启
        stream = self.deepseek.chat.completions.create(
            model="deepseek-chat",
            max_tokens=800,
            stream=True,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content


    def reset(self):
        """清空整个知识库"""
        if self.collection.count() > 0:
            existing = self.collection.get()
            self.collection.delete(ids=existing["ids"])
        return {"success": True, "message": "知识库已清空"}


    def get_stats(self) -> dict:
        """获取知识库统计信息"""
        docs = self.get_document_list()
        return {
            "total_chunks": self.collection.count(),
            "total_documents": len(docs),
            "documents": docs
        }