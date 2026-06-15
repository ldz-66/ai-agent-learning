import re
from typing import List


def chunk_by_paragraph(text: str, max_length: int = 300) -> List[str]:
    """按段落切分，如果段落太长则进一步切分"""
    paragraphs = text.strip().split('\n\n')
    chunks = []

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if len(para) <= max_length:
            chunks.append(para)
        else:
            # 段落太长，按句子切分
            sentences = re.split(r'([。！？\.!?])', para)
            current_chunk = ""
            for i in range(0, len(sentences) - 1, 2):
                sentence = sentences[i] + (sentences[i + 1] if i + 1 < len(sentences) else "")
                if len(current_chunk) + len(sentence) <= max_length:
                    current_chunk += sentence
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence
            if current_chunk:
                chunks.append(current_chunk.strip())

    return [c for c in chunks if c]


def chunk_with_overlap(text: str, chunk_size: int = 200, overlap: int = 50) -> List[str]:
    """固定大小切分，带重叠（防止在切分点丢失上下文）"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap  # 下一个chunk从overlap之前开始
    return chunks


# ===== 测试用的长文档 =====
sample_doc = """
Python是一种高级编程语言，由Guido van Rossum于1991年首次发布。
Python的设计哲学强调代码的可读性和简洁性，使用缩进来划分代码块。

Python有丰富的标准库，涵盖了字符串处理、数学运算、文件操作、网络通信等各种功能。
同时，Python拥有庞大的第三方库生态系统，例如NumPy用于科学计算，Django和FastAPI用于Web开发，TensorFlow和PyTorch用于机器学习。

Python在人工智能领域的应用非常广泛。大多数主流的AI框架都提供Python接口。
机器学习库如scikit-learn让数据科学家能够快速实验各种算法。
深度学习框架如PyTorch和TensorFlow让研究者能够构建复杂的神经网络模型。

FastAPI是一个基于Python的现代Web框架，专为构建API而设计。
它基于Python 3.6+的类型注解，能够自动生成API文档。
FastAPI的性能接近NodeJS和Go，是目前最快的Python Web框架之一。

向量数据库是存储和检索高维向量的专用数据库。
在AI应用中，文本通常被转换成向量（Embedding）再存入向量数据库。
检索时，用查询文本的向量找到最相似的向量，从而找到最相关的文档。
Chroma、Pinecone、Weaviate都是常见的向量数据库。
"""

print("=" * 50)
print(f"原始文档长度：{len(sample_doc)} 字符")
print("=" * 50)

# 方法1：按段落切分
chunks1 = chunk_by_paragraph(sample_doc, max_length=200)
print(f"\n方法1（按段落）：切分为 {len(chunks1)} 块")
for i, chunk in enumerate(chunks1):
    print(f"  块{i+1}（{len(chunk)}字）：{chunk[:50]}...")

# 方法2：固定大小切分
chunks2 = chunk_with_overlap(sample_doc, chunk_size=150, overlap=30)
print(f"\n方法2（固定大小+重叠）：切分为 {len(chunks2)} 块")
for i, chunk in enumerate(chunks2[:3]):  # 只显示前3块
    print(f"  块{i+1}（{len(chunk)}字）：{chunk[:50]}...")
print(f"  ...（共{len(chunks2)}块）")

# ===== 对比：切分大小对搜索质量的影响 =====
print("\n" + "=" * 50)
print("切分大小的影响分析")
print("=" * 50)
for size in [50, 150, 300]:
    chunks = chunk_by_paragraph(sample_doc, max_length=size)
    print(f"  max_length={size}：{len(chunks)}块，平均{sum(len(c) for c in chunks)//len(chunks)}字/块")