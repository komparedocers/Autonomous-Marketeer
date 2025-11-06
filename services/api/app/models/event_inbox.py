"""Event Inbox model."""
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class EventInbox(Base):
    """Event Inbox model for storing incoming webhook events."""

    __tablename__ = "events_inbox"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    source = Column(
        String, nullable=False
    )  # stripe, meta, google, linkedin, etc.
    event_type = Column(String, nullable=True)
    payload_json = Column(Text, nullable=False)  # JSON event payload
    processed = Column(Boolean, default=False)
    processed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    received_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="events")
