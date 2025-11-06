"""Channel model for OAuth connections."""
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Channel(Base):
    """Channel model for connected advertising platforms."""

    __tablename__ = "channels"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    type = Column(
        String, nullable=False
    )  # googleads, meta, linkedin, tiktok, x, youtube, reddit, email
    name = Column(String, nullable=False)  # User-friendly name
    oauth_json = Column(
        Text, nullable=True
    )  # Encrypted OAuth tokens and metadata as JSON
    account_id = Column(String, nullable=True)  # External account ID
    status = Column(String, default="connected")  # connected, disconnected, error
    last_sync_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="channels")
    ads = relationship("Ad", back_populates="channel", cascade="all, delete-orphan")
