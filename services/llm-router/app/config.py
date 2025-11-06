"""LLM Router configuration."""
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """LLM Router settings."""

    # Application
    APP_NAME: str = "LLM Router"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Server
    LLM_ROUTER_HOST: str = "0.0.0.0"
    LLM_ROUTER_PORT: int = 9090

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

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
    LOCAL_LLM_MODEL: str = "mistralai/Mistral-7B-Instruct-v0.2"
    LOCAL_LLM_MAX_TOKENS: int = 4000
    LOCAL_LLM_TEMPERATURE: float = 0.7
    LOCAL_LLM_GPU_MEMORY_UTILIZATION: float = 0.9

    # Cache
    LLM_CACHE_ENABLED: bool = True
    LLM_CACHE_TTL: int = 3600  # 1 hour

    # Moderation
    LLM_MODERATION_ENABLED: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
