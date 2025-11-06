"""Agent schemas."""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class AgentRunRequest(BaseModel):
    """Agent run request schema."""

    agent: str  # CreativeAgent, ComplianceAgent, etc.
    context: Dict[str, Any]
    llm_provider: Optional[str] = None  # openai, local (override default)


class AgentRunResponse(BaseModel):
    """Agent run response schema."""

    id: int
    tenant_id: int
    agent: str
    status: str
    output_json: Optional[str]
    error_message: Optional[str]
    tokens_used: int
    cost: float
    llm_provider: Optional[str]
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class AgentConfig(BaseModel):
    """Agent configuration schema."""

    name: str
    enabled: bool
    description: str
    llm_provider: str  # openai, local


class AgentConfigUpdate(BaseModel):
    """Agent configuration update schema."""

    enabled: Optional[bool] = None
    llm_provider: Optional[str] = None
