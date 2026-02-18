"""Extended models for Agent, Skill, and Memory management."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SkillStatus(str, Enum):
    """Skill status enum."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


class TaskStatus(str, Enum):
    """Task status enum."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class SkillInputSchema(BaseModel):
    """Skill input schema definition."""

    properties: Dict[str, Any] = Field(..., description="JSON schema properties")
    required: List[str] = Field(default_factory=list, description="Required fields")


class SkillManifest(BaseModel):
    """Skill manifest configuration."""

    name: str = Field(..., description="Skill name")
    description: str = Field(..., description="Skill description")
    version: str = Field(default="1.0.0", description="Skill version")
    triggers: List[str] = Field(default_factory=list, description="Trigger phrases")
    cron_capable: bool = Field(default=False, description="Can be scheduled")
    input_schema: Optional[SkillInputSchema] = Field(None, description="Input schema")


class Skill(BaseModel):
    """Skill model."""

    id: str = Field(..., description="Unique skill ID")
    manifest: SkillManifest = Field(..., description="Skill manifest")
    status: SkillStatus = Field(default=SkillStatus.ACTIVE, description="Skill status")
    last_executed: Optional[datetime] = Field(None, description="Last execution time")
    execution_count: int = Field(default=0, description="Total executions")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AgentConfig(BaseModel):
    """Agent configuration."""

    model_name: str = Field(default="llama-3.3-70b-versatile", description="LLM model name")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0, description="Temperature")
    max_tokens: int = Field(default=2000, ge=1, description="Max tokens")
    system_prompt: str = Field(default="You are a helpful AI assistant.", description="System prompt")


class AgentState(str, Enum):
    """Agent state enum."""

    IDLE = "idle"
    THINKING = "thinking"
    EXECUTING = "executing"
    ERROR = "error"


class Agent(BaseModel):
    """Agent model."""

    id: str = Field(..., description="Unique agent ID")
    name: str = Field(..., description="Agent name")
    config: AgentConfig = Field(default_factory=AgentConfig, description="Agent config")
    state: AgentState = Field(default=AgentState.IDLE, description="Current state")
    skills: List[str] = Field(default_factory=list, description="Registered skill IDs")
    memory_enabled: bool = Field(default=True, description="Memory persistence enabled")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Memory(BaseModel):
    """Memory entry model."""

    id: str = Field(..., description="Unique memory ID")
    content: str = Field(..., description="Memory content")
    memory_type: str = Field(..., description="Type: knowledge, task, or log")
    tags: List[str] = Field(default_factory=list, description="Tags for search")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ConversationMessage(BaseModel):
    """Conversation message model."""

    id: str = Field(..., description="Unique message ID")
    role: str = Field(..., description="Role: user, assistant, system")
    content: str = Field(..., description="Message content")
    tool_used: Optional[str] = Field(None, description="Tool used if any")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ConversationHistory(BaseModel):
    """Conversation history model."""

    id: str = Field(..., description="Unique conversation ID")
    messages: List[ConversationMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def add_message(self, role: str, content: str, tool_used: Optional[str] = None) -> ConversationMessage:
        """Add message to history."""
        import uuid
        
        msg = ConversationMessage(
            id=str(uuid.uuid4()),
            role=role,
            content=content,
            tool_used=tool_used,
        )
        self.messages.append(msg)
        self.updated_at = datetime.utcnow()
        return msg

    def get_messages_for_context(self, limit: int = 10) -> List[Dict[str, str]]:
        """Get last N messages in LLM context format."""
        recent_messages = self.messages[-limit:]
        return [
            {"role": msg.role, "content": msg.content}
            for msg in recent_messages
        ]


class TaskType(str, Enum):
    """Task type enum."""

    ONE_TIME = "one_time"
    DAILY = "daily"
    MONTHLY = "monthly"


class Task(BaseModel):
    """Task model."""

    id: str = Field(..., description="Unique task ID")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Task status")
    task_type: TaskType = Field(default=TaskType.ONE_TIME, description="Task type")
    scheduled_time: Optional[str] = Field(None, description="Scheduled time in HH:MM format")
    scheduled_date: Optional[str] = Field(None, description="Scheduled date YYYY-MM-DD or day of month")
    recurrence: TaskType = Field(default=TaskType.ONE_TIME, description="Recurrence pattern")
    next_run_at: Optional[datetime] = Field(None, description="Next scheduled execution")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TaskCreate(BaseModel):
    """Task creation schema."""
    title: str
    description: Optional[str] = None
    task_type: TaskType = TaskType.ONE_TIME
    scheduled_time: Optional[str] = None
    scheduled_date: Optional[str] = None
    recurrence: TaskType = TaskType.ONE_TIME


class TaskUpdate(BaseModel):
    """Task update schema."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    task_type: Optional[TaskType] = None
    scheduled_time: Optional[str] = None
    scheduled_date: Optional[str] = None
    recurrence: Optional[TaskType] = None
