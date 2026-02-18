"""Task management service."""

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from ..database import TaskDB
from ..schemas import Task, TaskCreate, TaskUpdate, TaskStatus, TaskType


class TaskService:
    """Service for managing tasks."""

    def __init__(self, db: Session):
        """Initialize task service."""
        self.db = db

    def list_tasks(self) -> List[TaskDB]:
        """List all tasks."""
        return self.db.query(TaskDB).order_by(TaskDB.created_at.desc()).all()

    def get_task(self, task_id: str) -> Optional[TaskDB]:
        """Get a single task by ID."""
        return self.db.query(TaskDB).filter(TaskDB.id == task_id).first()

    def create_task(self, title: str, description: Optional[str] = None, 
                   task_type: str = "one_time", scheduled_time: Optional[str] = None,
                   scheduled_date: Optional[str] = None, recurrence: str = "one_time") -> TaskDB:
        """Create a new task."""
        task_id = str(uuid.uuid4())
        db_task = TaskDB(
            id=task_id,
            title=title,
            description=description,
            status="pending",
            task_type=task_type,
            scheduled_time=scheduled_time,
            scheduled_date=scheduled_date,
            recurrence=recurrence,
        )
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        return db_task

    def update_task(self, task_id: str, **kwargs) -> Optional[TaskDB]:
        """Update task details."""
        db_task = self.get_task(task_id)
        if not db_task:
            return None

        for key, value in kwargs.items():
            if value is not None and hasattr(db_task, key):
                setattr(db_task, key, value)

        db_task.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_task)
        return db_task

    def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        db_task = self.get_task(task_id)
        if not db_task:
            return False
        self.db.delete(db_task)
        self.db.commit()
        return True
