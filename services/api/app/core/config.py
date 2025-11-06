"""Application configuration."""
from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "Autonomous Marketeer API"
    APP_ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8080
    API_WORKERS: int = 4
    PUBLIC_API_HOST: str = "http://localhost:8080"

    # Database
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "agentic"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "example_change_me"
    POSTGRES_DSN: str = "postgresql+psycopg://postgres:example_change_me@db:5432/agentic"

    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: str = "redis://redis:6379/0"

    # ClickHouse
    CLICKHOUSE_HOST: str = "clickhouse"
    CLICKHOUSE_PORT: int = 8123
    CLICKHOUSE_DB: str = "analytics"
    CLICKHOUSE_URL: str = "http://clickhouse:8123"

    # MinIO
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ACCESS_KEY: str = "minio"
    MINIO_SECRET_KEY: str = "minio123"
    MINIO_SECURE: bool = False
    MINIO_BUCKET_ASSETS: str = "assets"

    # Security
    JWT_SECRET: str = "dev-jwt-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION: int = 86400  # 24 hours
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ENCRYPTION_KEY: str = "vF3jK9mN2pQ5sT8vY0zC3fJ6kM9nP2rU5xA8bE1dH4="

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:8080"
    CORS_ALLOW_CREDENTIALS: bool = True

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    # LLM Configuration
    LLM_PROVIDER: str = "local"  # 'openai', 'local', 'both'
    LLM_DEFAULT_PROVIDER: str = "local"

    # OpenAI
    OPENAI_ENABLED: bool = False
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_MAX_TOKENS: int = 4000
    OPENAI_TEMPERATURE: float = 0.7

    # Local LLM
    LOCAL_LLM_ENABLED: bool = True
    LOCAL_LLM_URL: str = "http://llmrouter:9090"
    LOCAL_LLM_MODEL: str = "mistralai/Mistral-7B-Instruct-v0.2"
    LOCAL_LLM_MAX_TOKENS: int = 4000
    LOCAL_LLM_TEMPERATURE: float = 0.7

    # Attribution
    ATTRIBUTION_SESSION_TIMEOUT: int = 1800
    ATTRIBUTION_DEFAULT_MODEL: str = "last_touch"

    # Celery
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/1"

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000

    # Feature Flags
    FEATURE_AB_TESTING: bool = True
    FEATURE_MULTI_ARMED_BANDITS: bool = True
    FEATURE_AUTO_OPTIMIZATION: bool = True
    FEATURE_AGENT_APPROVALS: bool = True
    FEATURE_AUDIT_LOGS: bool = True

    # Agent Configuration
    AGENT_CREATIVE_ENABLED: bool = True
    AGENT_COMPLIANCE_ENABLED: bool = True
    AGENT_PLANNER_ENABLED: bool = True
    AGENT_BUDGET_PACER_ENABLED: bool = True
    AGENT_OPTIMIZER_ENABLED: bool = True
    AGENT_ANALYST_ENABLED: bool = True

    # OAuth Channels
    GOOGLE_ADS_ENABLED: bool = False
    META_ENABLED: bool = False
    LINKEDIN_ENABLED: bool = False
    TIKTOK_ENABLED: bool = False
    X_ENABLED: bool = False
    YOUTUBE_ENABLED: bool = False
    REDDIT_ENABLED: bool = False
    EMAIL_ENABLED: bool = True

    # Default Tenant
    DEFAULT_TENANT_NAME: str = "Demo Company"
    DEFAULT_TENANT_EMAIL: str = "admin@demo.com"
    DEFAULT_TENANT_PASSWORD: str = "demo123"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
