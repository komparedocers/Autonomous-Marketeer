"""Agent Run model."""
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class AgentRun(Base):
    """Agent Run model for tracking agent executions."""

    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    agent = Column(
        String, nullable=False
    )  # CreativeAgent, ComplianceAgent, ChannelPlanner, BudgetPacer, Optimizer, AnalystAgent
    input_ctx_json = Column(Text, nullable=True)  # JSON with input context
    output_json = Column(Text, nullable=True)  # JSON with output/results
    status = Column(
        String, default="pending"
    )  # pending, running, completed, failed
    error_message = Column(Text, nullable=True)
    tokens_used = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    llm_provider = Column(String, nullable=True)  # openai, local
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="agent_runs")
