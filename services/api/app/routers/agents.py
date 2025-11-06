"""Agents router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json
from app.core.database import get_db
from app.core.config import get_settings
from app.auth.dependencies import require_auth
from app.models.user import User
from app.models.agent_run import AgentRun
from app.schemas.agent import AgentRunRequest, AgentRunResponse, AgentConfig, AgentConfigUpdate

router = APIRouter()
settings = get_settings()


@router.post("/run", response_model=AgentRunResponse, status_code=status.HTTP_201_CREATED)
async def run_agent(
    request: AgentRunRequest,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """Run an agent with the given context."""
    # Validate agent name
    valid_agents = [
        "CreativeAgent",
        "ComplianceAgent",
        "ChannelPlanner",
        "BudgetPacer",
        "Optimizer",
        "AnalystAgent",
    ]

    if request.agent not in valid_agents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid agent. Must be one of: {', '.join(valid_agents)}"
        )

    # Determine LLM provider
    llm_provider = request.llm_provider or settings.LLM_DEFAULT_PROVIDER

    # Create agent run record
    agent_run = AgentRun(
        tenant_id=current_user.tenant_id,
        agent=request.agent,
        input_ctx_json=json.dumps(request.context),
        status="pending",
        llm_provider=llm_provider,
    )
    db.add(agent_run)
    db.commit()
    db.refresh(agent_run)

    # TODO: Trigger Celery task to execute agent
    # from app.tasks import run_agent_task
    # run_agent_task.delay(agent_run.id)

    return agent_run


@router.get("/runs", response_model=List[AgentRunResponse])
async def list_agent_runs(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
    agent: str = None,
    skip: int = 0,
    limit: int = 100,
):
    """List all agent runs for the current tenant."""
    query = db.query(AgentRun).filter(AgentRun.tenant_id == current_user.tenant_id)

    if agent:
        query = query.filter(AgentRun.agent == agent)

    agent_runs = query.order_by(AgentRun.created_at.desc()).offset(skip).limit(limit).all()
    return agent_runs


@router.get("/runs/{run_id}", response_model=AgentRunResponse)
async def get_agent_run(
    run_id: int,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """Get a specific agent run."""
    agent_run = (
        db.query(AgentRun)
        .filter(
            AgentRun.id == run_id,
            AgentRun.tenant_id == current_user.tenant_id,
        )
        .first()
    )

    if not agent_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent run not found"
        )

    return agent_run


@router.get("/config", response_model=List[AgentConfig])
async def get_agent_configs(
    current_user: User = Depends(require_auth),
):
    """Get agent configurations."""
    configs = [
        AgentConfig(
            name="CreativeAgent",
            enabled=settings.AGENT_CREATIVE_ENABLED,
            description="Generates multi-variant ad copy aligned with brand voice",
            llm_provider=settings.LLM_DEFAULT_PROVIDER,
        ),
        AgentConfig(
            name="ComplianceAgent",
            enabled=settings.AGENT_COMPLIANCE_ENABLED,
            description="Checks ad content against platform policies",
            llm_provider=settings.LLM_DEFAULT_PROVIDER,
        ),
        AgentConfig(
            name="ChannelPlanner",
            enabled=settings.AGENT_PLANNER_ENABLED,
            description="Plans campaign structure and channel strategy",
            llm_provider=settings.LLM_DEFAULT_PROVIDER,
        ),
        AgentConfig(
            name="BudgetPacer",
            enabled=settings.AGENT_BUDGET_PACER_ENABLED,
            description="Monitors and optimizes budget pacing",
            llm_provider=settings.LLM_DEFAULT_PROVIDER,
        ),
        AgentConfig(
            name="Optimizer",
            enabled=settings.AGENT_OPTIMIZER_ENABLED,
            description="Optimizes ad performance using multi-armed bandits",
            llm_provider=settings.LLM_DEFAULT_PROVIDER,
        ),
        AgentConfig(
            name="AnalystAgent",
            enabled=settings.AGENT_ANALYST_ENABLED,
            description="Generates insights and weekly narrative reports",
            llm_provider=settings.LLM_DEFAULT_PROVIDER,
        ),
    ]
    return configs


@router.get("/llm/status")
async def get_llm_status(
    current_user: User = Depends(require_auth),
):
    """Get LLM provider status."""
    return {
        "default_provider": settings.LLM_DEFAULT_PROVIDER,
        "openai": {
            "enabled": settings.OPENAI_ENABLED,
            "model": settings.OPENAI_MODEL,
        },
        "local": {
            "enabled": settings.LOCAL_LLM_ENABLED,
            "model": settings.LOCAL_LLM_MODEL,
            "url": settings.LOCAL_LLM_URL,
        },
    }
