from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from ..database import SkillDB, MemoryDB, ConversationDB, TaskDB

router = APIRouter()

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Get aggregate statistics for the dashboard."""
    return {
        "skills_count": db.query(SkillDB).count(),
        "docs_count": db.query(MemoryDB).filter(MemoryDB.memory_type == "knowledge").count(),
        "conversations_count": db.query(ConversationDB).count(),
        "tasks_count": db.query(TaskDB).count(),
        "tasks_pending": db.query(TaskDB).filter(TaskDB.status == "pending").count(),
        "tasks_completed": db.query(TaskDB).filter(TaskDB.status == "completed").count(),
    }
