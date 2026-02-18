from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class BaseRequest(BaseModel):
    """Base request model."""

    pass


class BaseResponse(BaseModel):
    """Base response model."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentRequest(BaseRequest):
    """Agent chat request."""

    message: str = Field(..., min_length=1, max_length=4000, description="User message")


class AgentResponse(BaseResponse):
    """Agent chat response."""

    reply: str = Field(..., description="Agent response")
    tool_used: Optional[str] = Field(None, description="Tool used by agent")


class ChatRequest(BaseRequest):
    """Chat endpoint request."""

    conversation_id: Optional[str] = Field(None, description="Conversation ID (create new if not provided)")
    agent_id: Optional[str] = Field(None, description="Agent ID (use default if not provided)")
    message: str = Field(..., min_length=1, max_length=4000, description="User message")


class ChatMessage(BaseModel):
    """Chat message in response."""

    id: str = Field(..., description="Message ID")
    role: str = Field(..., description="Role: user, assistant, system")
    content: str = Field(..., description="Message content")
    tool_used: Optional[str] = Field(None, description="Tool used if any")
    created_at: datetime = Field(..., description="Creation timestamp")


class ChatResponse(BaseResponse):
    """Chat endpoint response."""

    conversation_id: str = Field(..., description="Conversation ID")
    message: ChatMessage = Field(..., description="Latest message")
    reply: str = Field(..., description="Agent response")
    messages: List[ChatMessage] = Field(default_factory=list, description="Recent messages")


class ConversationResponse(BaseResponse):
    """Conversation list response."""

    conversation_id: str = Field(..., description="Conversation ID")
    messages: List[ChatMessage] = Field(default_factory=list, description="Message history")
