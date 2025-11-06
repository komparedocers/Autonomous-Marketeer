"""Attribution model."""
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Attribution(Base):
    """Attribution model for conversion attribution."""

    __tablename__ = "attributions"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    session_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=True, index=True)
    touchpoints_json = Column(Text, nullable=False)  # JSON array of touchpoints
    model = Column(
        String, nullable=False
    )  # last_touch, first_touch, position_based, time_decay
    conversion_event = Column(String, nullable=True)  # purchase, lead, signup
    conversion_value = Column(Float, default=0.0)
    currency = Column(String, default="USD")
    attribution_scores_json = Column(
        Text, nullable=True
    )  # JSON with attribution scores
    ts = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="attributions")
