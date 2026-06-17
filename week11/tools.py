import json
from db import db_create_task, db_get_tasks, db_update_done, db_delete_task, db_get_stats

# RAG引擎在agent.py里初始化后注入进来
_rag_engine = None

def set_rag_engine(rag):
    global _rag_engine
    _rag_engine = rag


TOOLS = [
    # ===== 任务管理工具 =====
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "创建新的待办任务，用户提到'添加/新建/帮我记/提醒我'时调用",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "任务标题"},
                    "priority": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                        "description": "优先级，默认medium"
                    },
                    "due_date": {"type": "string", "description": "截止日期YYYY-MM-DD，可选"}
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_tasks",
            "description": "查询任务列表，用户说'查看/列出/有哪些任务'时调用",
            "parameters": {
                "type": "object",
                "properties": {
                    "done": {"type": "boolean", "description": "true=已完成，false=未完成，不传=全部"},
                    "keyword": {"type": "string", "description": "搜索关键词，可选"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "标记任务为已完成，用户说'完成了/做完了'时调用",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "任务ID"},
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "删除任务，用户说'删除/取消/不需要了'时调用",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "任务ID"}
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_task_stats",
            "description": "获取任务统计，用户说'统计/总共几个/完成率'时调用",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    # ===== 知识库工具 =====
    {
        "type": "function",
        "function": {
            "name": "search_knowledge",
            "description": "从已上传的文档知识库中检索相关信息，回答文档相关问题时调用",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索查询词"}
                },
                "required": ["query"]
            }
        }
    }
]


def execute_tool(tool_name: str, tool_args: dict) -> str:
    try:
        if tool_name == "create_task":
            result = db_create_task(**tool_args)
            return f"✅ 任务创建成功！ID={result['id']}，标题：{result['title']}，优先级：{result['priority']}"

        elif tool_name == "get_tasks":
            if "done" in tool_args and tool_args["done"] is not None:
                tool_args["done"] = 1 if tool_args["done"] else 0
            tasks = db_get_tasks(**tool_args)
            if not tasks:
                return "没有找到符合条件的任务"
            priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}
            lines = [f"找到 {len(tasks)} 个任务："]
            for t in tasks:
                status = "✓" if t["done"] else "○"
                icon = priority_icon.get(t["priority"], "")
                due = f" [截止:{t['due_date']}]" if t["due_date"] else ""
                lines.append(f"[{status}] ID={t['id']} {icon}{t['title']}{due}")
            return "\n".join(lines)

        elif tool_name == "complete_task":
            result = db_update_done(tool_args["task_id"], True)
            if not result:
                return f"未找到ID={tool_args['task_id']}的任务，请先查询任务列表确认ID"
            return f"✅ 任务 '{result['title']}' 已标记完成！"

        elif tool_name == "delete_task":
            success = db_delete_task(tool_args["task_id"])
            if success:
                return f"🗑 任务ID={tool_args['task_id']}已删除"
            return f"未找到ID={tool_args['task_id']}的任务"

        elif tool_name == "get_task_stats":
            stats = db_get_stats()
            return (f"📊 任务统计：总共{stats['total']}个，"
                    f"已完成{stats['done']}个，待完成{stats['pending']}个")

        elif tool_name == "search_knowledge":
            if not _rag_engine:
                return "知识库未初始化"
            if not _rag_engine.has_documents():
                return "知识库暂无文档，请先上传文档"
            retrieved = _rag_engine.retrieve(tool_args["query"], top_k=3)
            if not retrieved:
                return "知识库中未找到相关内容"
            parts = []
            for r in retrieved:
                parts.append(f"【来源：{r['source']}】\n{r['content']}")
            return "\n\n".join(parts)

        else:
            return f"未知工具：{tool_name}"

    except Exception as e:
        return f"工具执行出错：{str(e)}"