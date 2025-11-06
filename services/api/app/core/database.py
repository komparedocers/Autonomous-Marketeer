"""Database connection and session management."""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from .config import get_settings

settings = get_settings()

# Create database engine
engine = create_engine(
    settings.POSTGRES_DSN,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.DEBUG,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database."""
    # Import all models here to ensure they are registered
    from app.models import (
        tenant,
        user,
        channel,
        campaign,
        ad_asset,
        ad_set,
        ad,
        experiment,
        agent_run,
        event_inbox,
        attribution,
        audit_log,
    )

    Base.metadata.create_all(bind=engine)
