import chromadb
import re
import os
from sentence_transformers import SentenceTransformer
from typing import List

class RAGEngine:
    def __init__(self):
        print("加载Embedding模型...")
        self.embed_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self.db = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.db.get_or_create_collection("assistant_kb")
        print(f"RAG引擎就绪，知识库文档块数：{self.collection.count()}")

    def get_embedding(self, text: str) -> list:
        return self.embed_model.encode(text).tolist()

    def chunk_text(self, text: str, max_length: int = 300) -> List[str]:
        paragraphs = text.strip().split('\n\n')
        chunks = []
        for para in paragraphs:
            para = para.strip()
            if not para or len(para) < 10:
                continue
            if len(para) <= max_length:
                chunks.append(para)
            else:
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
        chunks = self.chunk_text(content)
        if not chunks:
            return {"success": False, "error": "内容为空"}
        chunk_ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
        embeddings = [self.get_embedding(c) for c in chunks]
        metadatas = [{"doc_id": doc_id, "title": title, "chunk_index": i} for i in range(len(chunks))]
        self.collection.add(documents=chunks, embeddings=embeddings, ids=chunk_ids, metadatas=metadatas)
        return {"success": True, "chunks": len(chunks)}

    def retrieve(self, query: str, top_k: int = 3) -> List[dict]:
        if self.collection.count() == 0:
            return []
        q_emb = self.get_embedding(query)
        results = self.collection.query(
            query_embeddings=[q_emb],
            n_results=min(top_k, self.collection.count()),
            include=["documents", "metadatas", "distances"]
        )
        retrieved = []
        for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
            retrieved.append({"content": doc, "source": meta["title"], "distance": dist})
        return retrieved

    def has_documents(self) -> bool:
        return self.collection.count() > 0

    def get_doc_list(self) -> list:
        if self.collection.count() == 0:
            return []
        results = self.collection.get(include=["metadatas"])
        seen = {}
        for meta in results["metadatas"]:
            if meta["doc_id"] not in seen:
                seen[meta["doc_id"]] = meta["title"]
        return [{"doc_id": k, "title": v} for k, v in seen.items()]

    def delete_document(self, doc_id: str) -> bool:
        results = self.collection.get(where={"doc_id": doc_id})
        if not results["ids"]:
            return False
        self.collection.delete(ids=results["ids"])
        return True