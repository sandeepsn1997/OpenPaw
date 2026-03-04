import json
from datetime import datetime
from typing import Optional

from ...db import SessionLocal
from ...database import TaskDB
from ...services.task import TaskService


async def run(
    action: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    task_type: str = "one_time",
    scheduled_time: Optional[str] = None,
    scheduled_date: Optional[str] = None,
    recurrence: str = "one_time",
    task_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20,
) -> str:
    """Create/update/list/delete scheduled tasks for multi-step workflows."""
    db = SessionLocal()
    try:
        service = TaskService(db)

        if action == "create":
            if not title:
                return "Error: 'title' is required for create action."
            task = service.create_task(
                title=title,
                description=description,
                task_type=task_type,
                scheduled_time=scheduled_time,
                scheduled_date=scheduled_date,
                recurrence=recurrence,
            )
            return json.dumps({
                "success": True,
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "status": task.status,
                    "task_type": task.task_type,
                    "scheduled_time": task.scheduled_time,
                    "scheduled_date": task.scheduled_date,
                    "recurrence": task.recurrence,
                },
            })

        if action == "update":
            if not task_id:
                return "Error: 'task_id' is required for update action."
            updated = service.update_task(
                task_id,
                title=title,
                description=description,
                task_type=task_type,
                scheduled_time=scheduled_time,
                scheduled_date=scheduled_date,
                recurrence=recurrence,
                status=status,
            )
            if not updated:
                return f"Error: task '{task_id}' not found."
            return json.dumps({"success": True, "task_id": updated.id, "status": updated.status})

        if action == "delete":
            if not task_id:
                return "Error: 'task_id' is required for delete action."
            deleted = service.delete_task(task_id)
            return json.dumps({"success": deleted, "task_id": task_id})

        if action == "list":
            rows = db.query(TaskDB).order_by(TaskDB.created_at.desc()).limit(max(1, min(limit, 50))).all()
            tasks = []
            for row in rows:
                tasks.append(
                    {
                        "id": row.id,
                        "title": row.title,
                        "status": row.status,
                        "task_type": row.task_type,
                        "scheduled_time": row.scheduled_time,
                        "scheduled_date": row.scheduled_date,
                        "recurrence": row.recurrence,
                        "updated_at": row.updated_at.isoformat() if isinstance(row.updated_at, datetime) else None,
                    }
                )
            return json.dumps({"success": True, "tasks": tasks})

        return f"Error: Unsupported action '{action}'."
    finally:
        db.close()
