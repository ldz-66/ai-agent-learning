import json
from db import (
    db_create_task, db_get_tasks, db_update_done,
    db_update_task, db_delete_task, db_get_stats
)

# ===== 工具说明书（发给AI的） =====
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "创建一个新的待办任务",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "任务标题，简洁描述要做的事"
                    },
                    "description": {
                        "type": "string",
                        "description": "任务的详细描述（可选）"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                        "description": "优先级：high(高)、medium(中)、low(低)，默认medium"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "截止日期，格式YYYY-MM-DD（可选）"
                    }
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_tasks",
            "description": "查询任务列表，可以按完成状态、优先级、关键词筛选",
            "parameters": {
                "type": "object",
                "properties": {
                    "done": {
                        "type": "boolean",
                        "description": "筛选完成状态：true=已完成，false=未完成，不传=全部"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                        "description": "按优先级筛选（可选）"
                    },
                    "keyword": {
                        "type": "string",
                        "description": "按关键词搜索任务标题或描述（可选）"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task_done",
            "description": "标记任务为完成或未完成状态",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "任务的ID编号"
                    },
                    "done": {
                        "type": "boolean",
                        "description": "true=标记完成，false=标记未完成"
                    }
                },
                "required": ["task_id", "done"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task_info",
            "description": "更新任务的标题、描述、优先级或截止日期",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "任务ID"},
                    "title": {"type": "string", "description": "新标题（可选）"},
                    "description": {"type": "string", "description": "新描述（可选）"},
                    "priority": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                        "description": "新优先级（可选）"
                    },
                    "due_date": {"type": "string", "description": "新截止日期YYYY-MM-DD（可选）"}
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "删除一个任务",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "要删除的任务ID"}
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_task_stats",
            "description": "获取任务统计信息：总数、已完成数、待完成数、高优先级待完成数",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    }
]


# ===== 工具执行函数 =====
def execute_tool(tool_name: str, tool_args: dict) -> str:
    """根据工具名执行对应函数，返回字符串结果"""
    try:
        if tool_name == "create_task":
            result = db_create_task(**tool_args)
            return f"任务创建成功！ID={result['id']}，标题：{result['title']}，优先级：{result['priority']}"

        elif tool_name == "get_tasks":
            # bool转int（数据库用0/1）
            if "done" in tool_args and tool_args["done"] is not None:
                tool_args["done"] = 1 if tool_args["done"] else 0
            tasks = db_get_tasks(**tool_args)
            if not tasks:
                return "没有找到符合条件的任务"
            priority_map = {"high": "🔴高", "medium": "🟡中", "low": "🟢低"}
            lines = [f"找到 {len(tasks)} 个任务："]
            for t in tasks:
                status = "✓" if t["done"] else "○"
                pri = priority_map.get(t["priority"], t["priority"])
                due = f"，截止:{t['due_date']}" if t["due_date"] else ""
                lines.append(f"[{status}] ID={t['id']} {t['title']} [{pri}]{due}")
            return "\n".join(lines)

        elif tool_name == "update_task_done":
            result = db_update_done(tool_args["task_id"], tool_args["done"])
            if not result:
                return f"未找到ID={tool_args['task_id']}的任务"
            status = "已完成✓" if result["done"] else "未完成○"
            return f"任务 '{result['title']}' 已标记为{status}"

        elif tool_name == "update_task_info":
            task_id = tool_args.pop("task_id")
            result = db_update_task(task_id, **tool_args)
            if not result:
                return f"未找到ID={task_id}的任务，或没有可更新的内容"
            return f"任务ID={task_id}已更新：{result['title']}"

        elif tool_name == "delete_task":
            success = db_delete_task(tool_args["task_id"])
            if success:
                return f"任务ID={tool_args['task_id']}已删除"
            return f"未找到ID={tool_args['task_id']}的任务"

        elif tool_name == "get_task_stats":
            stats = db_get_stats()
            return (f"任务统计：总共{stats['total']}个任务，"
                    f"已完成{stats['done']}个，"
                    f"待完成{stats['pending']}个，"
                    f"高优先级待完成{stats['high_priority_pending']}个")

        else:
            return f"未知工具：{tool_name}"

    except Exception as e:
        return f"工具执行出错：{str(e)}"