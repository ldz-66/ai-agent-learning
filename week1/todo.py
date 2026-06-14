import json
import os

DATA_FILE = "todos.json"


def load_todos():
    """从json文件读取所有待办事项，如果文件不存在则返回空列表"""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_todos(todos):
    """把待办事项列表保存到json文件"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, ensure_ascii=False, indent=2)


def add_todo(todos):
    content = input("请输入待办内容: ")
    todos.append({"content": content, "done": False})
    save_todos(todos)
    print(f"已添加: {content}")


def list_todos(todos):
    if not todos:
        print("暂无待办事项")
        return
    for i, todo in enumerate(todos):
        status = "✓" if todo["done"] else " "
        print(f"[{status}] {i + 1}. {todo['content']}")


def complete_todo(todos):
    list_todos(todos)
    if not todos:
        return
    try:
        index = int(input("请输入要标记完成的序号: ")) - 1
        if 0 <= index < len(todos):
            todos[index]["done"] = True
            save_todos(todos)
            print("已标记完成")
        else:
            print("序号不存在")
    except ValueError:
        print("请输入数字")


def delete_todo(todos):
    list_todos(todos)
    if not todos:
        return
    try:
        index = int(input("请输入要删除的序号: ")) - 1
        if 0 <= index < len(todos):
            removed = todos.pop(index)
            save_todos(todos)
            print(f"已删除: {removed['content']}")
        else:
            print("序号不存在")
    except ValueError:
        print("请输入数字")


def main():
    todos = load_todos()
    while True:
        print("\n===== 待办事项管理器 =====")
        print("1. 查看所有事项")
        print("2. 添加事项")
        print("3. 标记完成")
        print("4. 删除事项")
        print("5. 退出")
        choice = input("请选择操作 (1-5): ")

        if choice == "1":
            list_todos(todos)
        elif choice == "2":
            add_todo(todos)
        elif choice == "3":
            complete_todo(todos)
        elif choice == "4":
            delete_todo(todos)
        elif choice == "5":
            print("再见!")
            break
        else:
            print("无效选择，请重新输入")


if __name__ == "__main__":
    main()