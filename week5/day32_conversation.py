import anthropic
from dotenv import load_dotenv

load_dotenv()

# 创建客户端，指定 DeepSeek 的兼容接口
client = anthropic.Anthropic(
    base_url="https://api.deepseek.com/anthropic"
)


def chat_with_history():
    """实现一个能记住历史的命令行聊天机器人"""

    print("=" * 50)
    print("AI聊天机器人（输入 'quit' 退出，输入 'clear' 清空历史）")
    print("=" * 50)

    # 存储对话历史
    conversation_history = []

    system_prompt = "你是一个友好的AI助手，名字叫小智。你记得对话中提到的所有信息，回答简洁有帮助。"

    while True:
        # 获取用户输入
        user_input = input("\n你：").strip()

        if user_input.lower() == "quit":
            print("再见！")
            break

        if user_input.lower() == "clear":
            conversation_history = []
            print("--- 对话历史已清空 ---")
            continue

        if not user_input:
            continue

        # 把用户的消息加入历史
        conversation_history.append({
            "role": "user",
            "content": user_input
        })

        # 每次都把完整的历史发给AI
        print("小智：", end="", flush=True)

        full_response = ""

        # 流式输出AI回复
        with client.messages.stream(
            model="deepseek-v4-pro",
            max_tokens=2000,  # 调大 token，防止思考耗尽额度
            system=system_prompt,
            messages=conversation_history  # 关键：把所有历史都发过去
        ) as stream:
            # 遍历流式返回的原始事件，安全过滤掉思考过程
            for event in stream:
                # 检查是否为文本增量事件
                if event.type == 'content_block_delta' and getattr(event.delta, 'type', None) == 'text_delta':
                    text_chunk = event.delta.text
                    print(text_chunk, end="", flush=True)
                    full_response += text_chunk

        print()  # 换行

        # 把AI的回复也加入历史，下次一起发过去
        conversation_history.append({
            "role": "assistant",
            "content": full_response
        })

        # 显示当前历史长度
        print(f"  [当前对话轮数：{len(conversation_history) // 2}]")


def demo_memory():
    """演示AI如何记住之前说的内容"""
    print("\n" + "=" * 50)
    print("演示：AI的记忆机制")
    print("=" * 50)

    history = []

    def ask(question):
        history.append({"role": "user", "content": question})
        response = client.messages.create(
            model="deepseek-v4-pro",
            max_tokens=2000,
            messages=history
        )
        
        # 安全提取最终文本
        final_text = ""
        for block in response.content:
            if getattr(block, 'type', None) == 'text':
                final_text += block.text
                
        history.append({"role": "assistant", "content": final_text})
        print(f"\n问：{question}")
        print(f"答：{final_text}")
        return final_text

    # 第1轮：告诉AI一个信息
    ask("我叫小明，今年20岁，是一名计算机专业的大二学生")

    # 第2轮：问一个需要记住上文的问题
    ask("你还记得我叫什么名字吗？")

    # 第3轮：基于上文做推理
    ask("根据我的情况，你觉得我现在最适合学什么技术？")

    print(f"\n--- 完整历史共 {len(history)} 条消息 ---")
    for i, msg in enumerate(history):
        role = "你" if msg["role"] == "user" else "AI"
        print(f"{i+1}. [{role}]: {msg['content'][:50]}...")


if __name__ == "__main__":
    # 先运行演示
    demo_memory()

    # 再运行交互式聊天
    print("\n\n现在开始交互式聊天...")
    chat_with_history()