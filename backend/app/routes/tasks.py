from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

from ..db import get_db
from ..database import TaskDB
from ..schemas import TaskCreate, TaskUpdate

router = APIRouter()


def task_to_dict(task: TaskDB) -> dict:
    """Convert a TaskDB record to a serializable dict."""
    next_run = getattr(task, "next_run_at", None)
    created = getattr(task, "created_at", None)
    updated = getattr(task, "updated_at", None)
    return {
        "id": task.id,
        "title": task.title,
        "description": getattr(task, "description", None),
        "status": getattr(task, "status", "pending"),
        "task_type": getattr(task, "task_type", "one_time") or "one_time",
        "scheduled_time": getattr(task, "scheduled_time", None),
        "scheduled_date": getattr(task, "scheduled_date", None),
        "recurrence": getattr(task, "recurrence", "one_time") or "one_time",
        "next_run_at": next_run.isoformat() if next_run else None,
        "created_at": created.isoformat() if created else None,
        "updated_at": updated.isoformat() if updated else None,
    }


@router.get("")
def list_tasks(db: Session = Depends(get_db)):
    """List all tasks."""
    try:
        tasks = db.query(TaskDB).order_by(TaskDB.created_at.desc()).all()
        return [task_to_dict(t) for t in tasks]
    except Exception:
        return []


@router.get("/{task_id}")
def get_task(task_id: str, db: Session = Depends(get_db)):
    """Get a single task by ID."""
    db_task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_to_dict(db_task)


@router.post("")
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    """Create a new task."""
    from ..services import TaskService
    task_service = TaskService(db)
    db_task = task_service.create_task(
        title=payload.title,
        description=payload.description,
        task_type=payload.task_type,
        scheduled_time=payload.scheduled_time,
        scheduled_date=payload.scheduled_date,
        recurrence=payload.recurrence,
    )
    return task_to_dict(db_task)


@router.put("/{task_id}")
def update_task(task_id: str, payload: TaskUpdate, db: Session = Depends(get_db)):
    """Update task details or status."""
    from ..services import TaskService
    task_service = TaskService(db)
    db_task = task_service.update_task(task_id, **payload.model_dump(exclude_unset=True))
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_to_dict(db_task)


@router.delete("/{task_id}")
def delete_task(task_id: str, db: Session = Depends(get_db)):
    """Delete a task."""
    db_task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_task)
    db.commit()
    return {"status": "deleted", "id": task_id}
