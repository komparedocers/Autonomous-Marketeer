"""Ad Set model."""
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class AdSet(Base):
    """Ad Set model for grouping ads."""

    __tablename__ = "ad_sets"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    audience_json = Column(Text, nullable=True)  # JSON with audience targeting
    placements_json = Column(Text, nullable=True)  # JSON with placement settings
    bid_strategy = Column(String, default="lowest_cost")  # lowest_cost, target_cost
    bid_amount = Column(Float, nullable=True)
    budget_split = Column(Float, nullable=True)  # Percentage of campaign budget
    status = Column(String, default="active")  # active, paused
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    campaign = relationship("Campaign", back_populates="ad_sets")
    ads = relationship("Ad", back_populates="ad_set", cascade="all, delete-orphan")
