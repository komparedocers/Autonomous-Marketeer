"""Audit Log model."""
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class AuditLog(Base):
    """Audit Log model for tracking user actions."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action = Column(
        String, nullable=False
    )  # create, update, delete, approve, reject, publish
    entity_type = Column(
        String, nullable=False
    )  # campaign, ad, asset, channel, user
    entity_id = Column(Integer, nullable=True)
    before_json = Column(Text, nullable=True)  # JSON snapshot before change
    after_json = Column(Text, nullable=True)  # JSON snapshot after change
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    ts = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="audit_logs")
    user = relationship("User", back_populates="audit_logs", foreign_keys=[actor_id])
