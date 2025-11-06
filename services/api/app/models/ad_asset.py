"""Ad Asset model."""
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class AdAsset(Base):
    """Ad Asset model for creative content."""

    __tablename__ = "ad_assets"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    type = Column(String, nullable=False)  # image, video, text, carousel
    title = Column(String, nullable=True)
    headline = Column(String, nullable=True)
    text = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    cta = Column(String, nullable=True)  # Call to action
    media_url = Column(String, nullable=True)  # URL to MinIO/S3
    thumbnail_url = Column(String, nullable=True)
    tags = Column(Text, nullable=True)  # JSON array of tags
    policy_flags = Column(
        Text, nullable=True
    )  # JSON with compliance check results
    agent_generated = Column(String, default="false")  # true/false
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="ad_assets")
    ads = relationship("Ad", back_populates="asset", cascade="all, delete-orphan")
