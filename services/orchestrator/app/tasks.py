"""Celery tasks for agent orchestration."""
from celery import Celery
import os
from datetime import datetime
import json
import httpx
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get environment variables
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")
LLM_ROUTER_URL = os.getenv("LOCAL_LLM_URL", "http://llmrouter:9090")

# Create Celery app
celery = Celery(
    "orchestrator",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)

# Configure Celery
celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=1800,  # 30 minutes
    task_soft_time_limit=1500,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
)


async def call_llm(
    prompt: str,
    system_prompt: str = None,
    provider: str = "local"
) -> dict:
    """Call LLM Router service."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{LLM_ROUTER_URL}/generate",
                json={
                    "prompt": prompt,
                    "system_prompt": system_prompt,
                    "provider": provider,
                },
                timeout=120.0,
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return {"success": False, "error": str(e)}


@celery.task(bind=True, max_retries=3, default_retry_delay=60)
def run_agent(self, agent_name: str, context: dict, run_id: int, provider: str = "local"):
    """Execute an agent with the given context."""
    logger.info(f"Running agent {agent_name} for run_id {run_id}")

    # Import agents dynamically
    from app.agents import creative, compliance, planner, optimizer, analyst

    agent_registry = {
        "CreativeAgent": creative.run,
        "ComplianceAgent": compliance.run,
        "ChannelPlanner": planner.run,
        "BudgetPacer": planner.run,  # Placeholder
        "Optimizer": optimizer.run,
        "AnalystAgent": analyst.run,
    }

    if agent_name not in agent_registry:
        logger.error(f"Unknown agent: {agent_name}")
        return {
            "success": False,
            "error": f"Unknown agent: {agent_name}",
        }

    try:
        # Execute the agent
        agent_func = agent_registry[agent_name]
        result = agent_func(context, provider=provider)

        logger.info(f"Agent {agent_name} completed successfully")
        return result

    except Exception as e:
        logger.error(f"Agent {agent_name} failed: {e}", exc_info=True)
        # Retry the task
        raise self.retry(exc=e, countdown=min(600, 2**self.request.retries))


@celery.task
def sync_channel_metrics(channel_id: int, tenant_id: int):
    """Sync metrics from a channel."""
    logger.info(f"Syncing metrics for channel {channel_id}")
    # TODO: Implement channel metric syncing
    return {"success": True, "channel_id": channel_id}


@celery.task
def optimize_campaign(campaign_id: int, tenant_id: int):
    """Optimize campaign performance."""
    logger.info(f"Optimizing campaign {campaign_id}")
    # TODO: Call optimizer agent
    return {"success": True, "campaign_id": campaign_id}


@celery.task
def generate_weekly_report(tenant_id: int):
    """Generate weekly performance report."""
    logger.info(f"Generating weekly report for tenant {tenant_id}")
    # TODO: Call analyst agent
    return {"success": True, "tenant_id": tenant_id}


# Periodic tasks (scheduled by Celery beat)
@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Setup periodic tasks."""
    # Sync channel metrics every hour
    sender.add_periodic_task(
        3600.0,  # 1 hour
        sync_all_channels.s(),
        name="sync-all-channels-hourly",
    )

    # Optimize campaigns every 6 hours
    sender.add_periodic_task(
        21600.0,  # 6 hours
        optimize_all_campaigns.s(),
        name="optimize-campaigns-6h",
    )

    # Generate weekly reports on Mondays at 9 AM
    sender.add_periodic_task(
        crontab(day_of_week=1, hour=9, minute=0),
        generate_all_weekly_reports.s(),
        name="weekly-reports-monday-9am",
    )


@celery.task
def sync_all_channels():
    """Sync all active channels."""
    logger.info("Syncing all channels")
    # TODO: Query database for active channels and sync each
    return {"success": True}


@celery.task
def optimize_all_campaigns():
    """Optimize all active campaigns."""
    logger.info("Optimizing all campaigns")
    # TODO: Query database for active campaigns and optimize each
    return {"success": True}


@celery.task
def generate_all_weekly_reports():
    """Generate weekly reports for all tenants."""
    logger.info("Generating weekly reports")
    # TODO: Query database for all tenants and generate reports
    return {"success": True}


# Import crontab for periodic tasks
from celery.schedules import crontab
