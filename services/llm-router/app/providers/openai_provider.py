"""OpenAI LLM provider."""
from openai import OpenAI
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class OpenAIProvider:
    """OpenAI LLM provider."""

    def __init__(self, api_key: str, model: str, max_tokens: int, temperature: float):
        """Initialize OpenAI provider."""
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        logger.info(f"Initialized OpenAI provider with model: {model}")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Generate response using OpenAI."""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature,
            )

            return {
                "success": True,
                "text": response.choices[0].message.content,
                "model": self.model,
                "tokens_used": response.usage.total_tokens,
                "provider": "openai",
            }
        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": "openai",
            }

    async def moderate(self, text: str) -> Dict[str, Any]:
        """Moderate content using OpenAI."""
        try:
            response = self.client.moderations.create(input=text)
            result = response.results[0]

            return {
                "flagged": result.flagged,
                "categories": result.categories.model_dump(),
                "category_scores": result.category_scores.model_dump(),
            }
        except Exception as e:
            logger.error(f"OpenAI moderation error: {e}")
            return {
                "flagged": False,
                "error": str(e),
            }
