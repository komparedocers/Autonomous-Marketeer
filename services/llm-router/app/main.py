"""LLM Router main application."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import redis
import json
import hashlib
import logging
from app.config import get_settings
from app.providers.openai_provider import OpenAIProvider
from app.providers.local_provider import LocalLLMProvider

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="LLM Router",
    debug=settings.DEBUG,
)

# Global providers
openai_provider = None
local_provider = None
redis_client = None


class GenerateRequest(BaseModel):
    """Generate request schema."""

    prompt: str
    system_prompt: Optional[str] = None
    provider: Optional[str] = None  # openai, local (override default)
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    use_cache: bool = True


class ModerateRequest(BaseModel):
    """Moderate request schema."""

    text: str
    provider: Optional[str] = None


def get_cache_key(prompt: str, system_prompt: Optional[str], params: dict) -> str:
    """Generate cache key for request."""
    cache_str = f"{prompt}:{system_prompt}:{json.dumps(params, sort_keys=True)}"
    return f"llm_cache:{hashlib.md5(cache_str.encode()).hexdigest()}"


@app.on_event("startup")
async def startup_event():
    """Initialize providers on startup."""
    global openai_provider, local_provider, redis_client

    logger.info("Starting LLM Router...")
    logger.info(f"Default provider: {settings.LLM_DEFAULT_PROVIDER}")

    # Initialize Redis client
    try:
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        redis_client.ping()
        logger.info("Redis connection established")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}")
        redis_client = None

    # Initialize OpenAI provider
    if settings.OPENAI_ENABLED and settings.OPENAI_API_KEY:
        try:
            openai_provider = OpenAIProvider(
                api_key=settings.OPENAI_API_KEY,
                model=settings.OPENAI_MODEL,
                max_tokens=settings.OPENAI_MAX_TOKENS,
                temperature=settings.OPENAI_TEMPERATURE,
            )
            logger.info("OpenAI provider initialized")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI provider: {e}")

    # Initialize Local LLM provider
    if settings.LOCAL_LLM_ENABLED:
        try:
            local_provider = LocalLLMProvider(
                model_name=settings.LOCAL_LLM_MODEL,
                max_tokens=settings.LOCAL_LLM_MAX_TOKENS,
                temperature=settings.LOCAL_LLM_TEMPERATURE,
            )
            logger.info("Local LLM provider initialized")
        except Exception as e:
            logger.error(f"Failed to initialize local LLM provider: {e}")
            logger.warning("Local LLM provider will not be available")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "providers": {
            "openai": openai_provider is not None,
            "local": local_provider is not None,
        },
        "default_provider": settings.LLM_DEFAULT_PROVIDER,
    }


@app.post("/generate")
async def generate(request: GenerateRequest):
    """Generate text using LLM."""
    # Determine provider
    provider_name = request.provider or settings.LLM_DEFAULT_PROVIDER

    # Check cache if enabled
    if request.use_cache and settings.LLM_CACHE_ENABLED and redis_client:
        cache_key = get_cache_key(
            request.prompt,
            request.system_prompt,
            {
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "provider": provider_name,
            },
        )
        try:
            cached_response = redis_client.get(cache_key)
            if cached_response:
                logger.info("Cache hit for request")
                response = json.loads(cached_response)
                response["cached"] = True
                return response
        except Exception as e:
            logger.warning(f"Cache lookup failed: {e}")

    # Get provider
    provider = None
    if provider_name == "openai":
        if not openai_provider:
            raise HTTPException(
                status_code=503,
                detail="OpenAI provider not available"
            )
        provider = openai_provider
    elif provider_name == "local":
        if not local_provider:
            raise HTTPException(
                status_code=503,
                detail="Local LLM provider not available"
            )
        provider = local_provider
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid provider: {provider_name}"
        )

    # Moderate content if enabled
    if settings.LLM_MODERATION_ENABLED:
        moderation = await provider.moderate(request.prompt)
        if moderation.get("flagged"):
            raise HTTPException(
                status_code=400,
                detail="Content flagged by moderation"
            )

    # Generate response
    response = await provider.generate(
        prompt=request.prompt,
        system_prompt=request.system_prompt,
        max_tokens=request.max_tokens,
        temperature=request.temperature,
    )

    if not response.get("success"):
        raise HTTPException(
            status_code=500,
            detail=response.get("error", "Generation failed")
        )

    # Cache response if enabled
    if request.use_cache and settings.LLM_CACHE_ENABLED and redis_client:
        try:
            cache_key = get_cache_key(
                request.prompt,
                request.system_prompt,
                {
                    "max_tokens": request.max_tokens,
                    "temperature": request.temperature,
                    "provider": provider_name,
                },
            )
            redis_client.setex(
                cache_key,
                settings.LLM_CACHE_TTL,
                json.dumps(response),
            )
        except Exception as e:
            logger.warning(f"Cache write failed: {e}")

    response["cached"] = False
    return response


@app.post("/moderate")
async def moderate(request: ModerateRequest):
    """Moderate content."""
    provider_name = request.provider or settings.LLM_DEFAULT_PROVIDER

    # Get provider
    provider = None
    if provider_name == "openai":
        if not openai_provider:
            raise HTTPException(
                status_code=503,
                detail="OpenAI provider not available"
            )
        provider = openai_provider
    elif provider_name == "local":
        if not local_provider:
            raise HTTPException(
                status_code=503,
                detail="Local LLM provider not available"
            )
        provider = local_provider
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid provider: {provider_name}"
        )

    # Moderate content
    result = await provider.moderate(request.text)
    return result


@app.get("/providers")
async def list_providers():
    """List available providers and their status."""
    return {
        "default": settings.LLM_DEFAULT_PROVIDER,
        "providers": {
            "openai": {
                "enabled": settings.OPENAI_ENABLED,
                "available": openai_provider is not None,
                "model": settings.OPENAI_MODEL if settings.OPENAI_ENABLED else None,
            },
            "local": {
                "enabled": settings.LOCAL_LLM_ENABLED,
                "available": local_provider is not None,
                "model": settings.LOCAL_LLM_MODEL if settings.LOCAL_LLM_ENABLED else None,
            },
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.LLM_ROUTER_HOST,
        port=settings.LLM_ROUTER_PORT,
        reload=settings.DEBUG,
    )
