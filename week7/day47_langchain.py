from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
# 修复文本分割器导入
from langchain_text_splitters import RecursiveCharacterTextSplitter
# 修复prompt模板导入
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

# 读取密钥并校验
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_KEY:
    raise Exception("未读取到 DEEPSEEK_API_KEY，请检查.env文件配置")


# ===== Part 1：用LangChain调用DeepSeek =====
print("=" * 50)
print("Part 1：用LangChain调用DeepSeek")
print("=" * 50)

# 补全 /v1 接口路径，DeepSeek官方必填
llm = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key=DEEPSEEK_KEY,
    openai_api_base="https://api.deepseek.com/v1",
    max_tokens=300
)

messages = [
    SystemMessage(content="你是一个简洁的助手，用一句话回答问题。"),
    HumanMessage(content="什么是RAG？")
]

response = llm.invoke(messages)
print("回复：", response.content)


# ===== Part 2：LangChain的文本切分器 =====
print("\n" + "=" * 50)
print("Part 2：LangChain文本切分器")
print("=" * 50)

sample_text = """
Python是一种广泛使用的高级编程语言。它以简洁的语法和强大的功能著称。
Python支持多种编程范式，包括面向对象、函数式和命令式编程。

FastAPI是基于Python的现代Web框架。它利用Python的类型注解系统提供自动数据验证。
FastAPI的性能接近NodeJS，是目前最快的Python框架之一。

RAG（检索增强生成）是一种AI技术，将信息检索与文本生成结合起来。
通过检索相关文档并将其作为上下文提供给语言模型，RAG能够生成更准确和有依据的回答。
"""

splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,      # 每块最大字符数
    chunk_overlap=20,    # 重叠字符数
    separators=["\n\n", "\n", "。", "，", " ", ""]
)

chunks = splitter.split_text(sample_text)
print(f"切分为 {len(chunks)} 块：")
for i, chunk in enumerate(chunks):
    print(f"  块{i+1}（{len(chunk)}字）：{chunk[:60]}...")


# ===== Part 3：LangChain的Chain概念 =====
print("\n" + "=" * 50)
print("Part 3：Chain（链式调用）")
print("=" * 50)

# 定义Prompt模板
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "你是一个{role}，回答要{style}。"),
    ("human", "{question}")
])

# 管道链：prompt → llm
chain = prompt_template | llm

result = chain.invoke({
    "role": "技术导师",
    "style": "简洁、有条理，用要点列出",
    "question": "学习AI应用开发需要掌握哪些技术？"
})
print("链式调用结果：")
print(result.content)