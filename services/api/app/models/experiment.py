"""Experiment model for A/B testing."""
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Experiment(Base):
    """Experiment model for A/B testing and multi-armed bandits."""

    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    hypothesis = Column(Text, nullable=True)
    metric = Column(String, nullable=False)  # ctr, cvr, cpa, roas
    type = Column(
        String, default="ab_test"
    )  # ab_test, multivariate, bandit
    status = Column(
        String, default="draft"
    )  # draft, running, paused, completed
    variants_json = Column(Text, nullable=True)  # JSON with variant definitions
    bandit_cfg_json = Column(
        Text, nullable=True
    )  # JSON with bandit configuration
    results_json = Column(Text, nullable=True)  # JSON with experiment results
    winner_variant = Column(String, nullable=True)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="experiments")
