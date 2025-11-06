"""Campaign schemas."""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class CampaignCreate(BaseModel):
    """Campaign creation schema."""

    name: str
    objective: str  # awareness, traffic, leads, conversions, sales
    budget_daily: Optional[float] = None
    budget_total: Optional[float] = None
    currency: str = "USD"
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    target_audience_json: Optional[str] = None
    brand_voice_json: Optional[str] = None


class CampaignUpdate(BaseModel):
    """Campaign update schema."""

    name: Optional[str] = None
    objective: Optional[str] = None
    status: Optional[str] = None
    budget_daily: Optional[float] = None
    budget_total: Optional[float] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    target_audience_json: Optional[str] = None
    brand_voice_json: Optional[str] = None


class CampaignResponse(BaseModel):
    """Campaign response schema."""

    id: int
    tenant_id: int
    name: str
    objective: str
    status: str
    budget_daily: Optional[float]
    budget_total: Optional[float]
    currency: str
    start_at: Optional[datetime]
    end_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CampaignPublishRequest(BaseModel):
    """Campaign publish request schema."""

    channels: list[str]  # List of channel IDs or types
