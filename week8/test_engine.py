from rag_engine import RAGEngine

engine = RAGEngine()

# 测试添加文档
result = engine.add_document(
    doc_id="test_001",
    title="Python学习笔记",
    content="""
Python是一种高级编程语言。

虚拟环境用于隔离项目依赖，创建命令是python -m venv venv。
激活虚拟环境后，使用pip install安装包。
pip freeze > requirements.txt可以导出依赖列表。

Git是版本控制系统，git add添加文件，git commit提交，git push推送到远程。
"""
)
print("添加文档：", result)

# 测试查询
print("\n文档列表：", engine.get_document_list())

# 测试检索
retrieved = engine.retrieve("怎么创建虚拟环境？")
print("\n检索结果：")
for r in retrieved:
    print(f"  [{r['distance']:.4f}] {r['source']}：{r['content'][:60]}...")

# 测试生成（非流式，用于测试）
print("\n生成回答：")
answer = ""
for chunk in engine.generate_answer_stream("怎么创建虚拟环境？", retrieved):
    answer += chunk
    print(chunk, end="", flush=True)
print()