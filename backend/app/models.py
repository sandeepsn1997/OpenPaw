from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)


class AgentResponse(BaseModel):
    reply: str
    tool_used: str | None = None
