"""Tenant model."""
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Tenant(Base):
    """Tenant model for multi-tenancy."""

    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    plan = Column(String, default="free")  # free, starter, professional, enterprise
    status = Column(String, default="active")  # active, suspended, cancelled
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    channels = relationship(
        "Channel", back_populates="tenant", cascade="all, delete-orphan"
    )
    campaigns = relationship(
        "Campaign", back_populates="tenant", cascade="all, delete-orphan"
    )
    ad_assets = relationship(
        "AdAsset", back_populates="tenant", cascade="all, delete-orphan"
    )
    experiments = relationship(
        "Experiment", back_populates="tenant", cascade="all, delete-orphan"
    )
    agent_runs = relationship(
        "AgentRun", back_populates="tenant", cascade="all, delete-orphan"
    )
    events = relationship(
        "EventInbox", back_populates="tenant", cascade="all, delete-orphan"
    )
    attributions = relationship(
        "Attribution", back_populates="tenant", cascade="all, delete-orphan"
    )
    audit_logs = relationship(
        "AuditLog", back_populates="tenant", cascade="all, delete-orphan"
    )
