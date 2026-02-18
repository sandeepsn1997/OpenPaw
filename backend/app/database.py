"""Database models for persistent storage."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AgentDB(Base):
    """Agent database model."""

    __tablename__ = "agents"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    config = Column(Text, nullable=False)  # JSON string
    state = Column(String, default="idle")
    memory_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SkillDB(Base):
    """Skill database model."""

    __tablename__ = "skills"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    manifest = Column(Text, nullable=False)  # JSON string
    status = Column(String, default="active")
    last_executed = Column(DateTime, nullable=True)
    execution_count = Column(String, default="0")  # Integer as string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MemoryDB(Base):
    """Memory database model."""

    __tablename__ = "memory"

    id = Column(String, primary_key=True)
    content = Column(Text, nullable=False)
    memory_type = Column(String, nullable=False)  # knowledge, task, log
    tags = Column(String, default="")  # Comma-separated
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ConversationDB(Base):
    """Conversation history database model."""

    __tablename__ = "conversations"

    id = Column(String, primary_key=True)
    messages = Column(Text, nullable=False)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TaskDB(Base):
    """Task tracking database model."""

    __tablename__ = "tasks"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="pending")  # pending, in_progress, completed, failed
    task_type = Column(String, default="one_time")  # one_time, daily, monthly
    scheduled_time = Column(String, nullable=True)  # HH:MM format e.g. "09:00"
    scheduled_date = Column(String, nullable=True)  # YYYY-MM-DD for one_time, day-of-month for monthly
    recurrence = Column(String, default="one_time")  # one_time, daily, monthly
    next_run_at = Column(DateTime, nullable=True)  # Next scheduled execution
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
