"""Campaign model."""
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Campaign(Base):
    """Campaign model for marketing campaigns."""

    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    objective = Column(
        String, nullable=False
    )  # awareness, traffic, leads, conversions, sales
    status = Column(
        String, default="draft"
    )  # draft, scheduled, active, paused, completed
    budget_daily = Column(Float, nullable=True)
    budget_total = Column(Float, nullable=True)
    currency = Column(String, default="USD")
    start_at = Column(DateTime, nullable=True)
    end_at = Column(DateTime, nullable=True)
    target_audience_json = Column(Text, nullable=True)  # JSON with targeting criteria
    brand_voice_json = Column(Text, nullable=True)  # JSON with brand guidelines
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="campaigns")
    ad_sets = relationship(
        "AdSet", back_populates="campaign", cascade="all, delete-orphan"
    )
