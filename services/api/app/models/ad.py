"""Ad model."""
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Ad(Base):
    """Ad model for individual advertisements."""

    __tablename__ = "ads"

    id = Column(Integer, primary_key=True, index=True)
    ad_set_id = Column(Integer, ForeignKey("ad_sets.id"), nullable=False, index=True)
    asset_id = Column(Integer, ForeignKey("ad_assets.id"), nullable=False, index=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    status = Column(
        String, default="draft"
    )  # draft, pending_review, approved, active, paused, rejected
    external_id = Column(String, nullable=True)  # ID from the ad platform
    meta_json = Column(Text, nullable=True)  # Additional metadata as JSON
    approval_status = Column(
        String, default="pending"
    )  # pending, approved, rejected
    rejection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)

    # Relationships
    ad_set = relationship("AdSet", back_populates="ads")
    asset = relationship("AdAsset", back_populates="ads")
    channel = relationship("Channel", back_populates="ads")
