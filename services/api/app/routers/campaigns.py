"""Campaigns router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.auth.dependencies import require_auth
from app.models.user import User
from app.models.campaign import Campaign
from app.schemas.campaign import (
    CampaignCreate,
    CampaignUpdate,
    CampaignResponse,
    CampaignPublishRequest,
)

router = APIRouter()


@router.post("/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign: CampaignCreate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """Create a new campaign."""
    db_campaign = Campaign(
        tenant_id=current_user.tenant_id,
        **campaign.model_dump(),
    )
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign


@router.get("/", response_model=List[CampaignResponse])
async def list_campaigns(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """List all campaigns for the current tenant."""
    campaigns = (
        db.query(Campaign)
        .filter(Campaign.tenant_id == current_user.tenant_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return campaigns


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: int,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """Get a specific campaign."""
    campaign = (
        db.query(Campaign)
        .filter(
            Campaign.id == campaign_id,
            Campaign.tenant_id == current_user.tenant_id,
        )
        .first()
    )

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    return campaign


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: int,
    campaign_update: CampaignUpdate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """Update a campaign."""
    campaign = (
        db.query(Campaign)
        .filter(
            Campaign.id == campaign_id,
            Campaign.tenant_id == current_user.tenant_id,
        )
        .first()
    )

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    # Update fields
    update_data = campaign_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(campaign, field, value)

    db.commit()
    db.refresh(campaign)
    return campaign


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: int,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """Delete a campaign."""
    campaign = (
        db.query(Campaign)
        .filter(
            Campaign.id == campaign_id,
            Campaign.tenant_id == current_user.tenant_id,
        )
        .first()
    )

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    db.delete(campaign)
    db.commit()
    return None


@router.post("/{campaign_id}/publish")
async def publish_campaign(
    campaign_id: int,
    publish_request: CampaignPublishRequest,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """Publish a campaign to specified channels."""
    campaign = (
        db.query(Campaign)
        .filter(
            Campaign.id == campaign_id,
            Campaign.tenant_id == current_user.tenant_id,
        )
        .first()
    )

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    # TODO: Trigger Celery task to publish to channels
    # For now, just update status
    campaign.status = "active"
    db.commit()

    return {
        "message": "Campaign publishing initiated",
        "campaign_id": campaign_id,
        "channels": publish_request.channels,
    }
