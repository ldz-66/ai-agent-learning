# Week7：RAG原理 + 向量数据库

## 本周学到的核心技术
1. **Embedding**：把文字转成向量，让计算机能理解语义
2. **余弦相似度**：衡量两个向量的相似程度
3. **Chroma**：本地向量数据库，用于存储和检索Embedding
4. **文档切分（Chunking）**：把长文档切成适合检索的小块
5. **RAG流程**：问题 → 检索相关块 → 拼接上下文 → 大模型生成回答
6. **LangChain**：AI应用开发框架，简化常见操作

## 主要文件
- `day43_local_embeddings.py`：Embedding相似度实验
- `day44_chroma.py`：Chroma向量数据库基本操作
- `day45_chunking.py`：文档切分策略对比
- `day46_rag_pipeline.py`：完整RAG流程实现
- `day47_langchain.py`：LangChain基本用法
- `my_notes_qa.py`：基于个人笔记的问答工具

## 如何运行笔记问答工具
1. 把自己的笔记写入 `my_notes.txt`
2. 安装依赖：`pip install -r requirements.txt`
3. 运行：`python my_notes_qa.py`