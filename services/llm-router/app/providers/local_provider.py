"""Local LLM provider using Transformers."""
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class LocalLLMProvider:
    """Local LLM provider using Hugging Face Transformers."""

    def __init__(self, model_name: str, max_tokens: int, temperature: float):
        """Initialize local LLM provider."""
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        logger.info(f"Initializing local LLM provider with model: {model_name}")
        self._load_model()

    def _load_model(self):
        """Load the model and tokenizer."""
        try:
            logger.info(f"Loading tokenizer for {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

            logger.info(f"Loading model {self.model_name}")
            # Use device_map for automatic device placement
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                device_map="auto",
                torch_dtype=torch.float16,
                low_cpu_mem_usage=True,
            )

            # Create text generation pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device_map="auto",
            )

            logger.info(f"Successfully loaded model {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            # Fallback to CPU-only mode with smaller model if GPU fails
            logger.info("Attempting to load in CPU mode...")
            try:
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float32,
                    low_cpu_mem_usage=True,
                )
                self.pipeline = pipeline(
                    "text-generation",
                    model=self.model,
                    tokenizer=self.tokenizer,
                )
                logger.info("Successfully loaded model in CPU mode")
            except Exception as cpu_error:
                logger.error(f"Failed to load model in CPU mode: {cpu_error}")
                raise

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Generate response using local LLM."""
        if not self.pipeline:
            return {
                "success": False,
                "error": "Model not loaded",
                "provider": "local",
            }

        try:
            # Combine system and user prompts
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"<s>[INST] {system_prompt}\n\n{prompt} [/INST]"
            else:
                full_prompt = f"<s>[INST] {prompt} [/INST]"

            # Generate response
            outputs = self.pipeline(
                full_prompt,
                max_new_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature,
                do_sample=True,
                top_p=0.95,
                top_k=50,
                return_full_text=False,
            )

            generated_text = outputs[0]["generated_text"]

            # Calculate token usage (approximate)
            input_tokens = len(self.tokenizer.encode(full_prompt))
            output_tokens = len(self.tokenizer.encode(generated_text))
            total_tokens = input_tokens + output_tokens

            return {
                "success": True,
                "text": generated_text,
                "model": self.model_name,
                "tokens_used": total_tokens,
                "provider": "local",
            }
        except Exception as e:
            logger.error(f"Local LLM generation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": "local",
            }

    async def moderate(self, text: str) -> Dict[str, Any]:
        """Simple moderation for local LLM (basic heuristics)."""
        # Simple heuristic-based moderation
        # In production, you'd want to use a dedicated moderation model
        flagged_keywords = [
            "violence",
            "hate",
            "harassment",
            "illegal",
            "explicit",
        ]

        text_lower = text.lower()
        flagged = any(keyword in text_lower for keyword in flagged_keywords)

        return {
            "flagged": flagged,
            "categories": {
                "violence": "violence" in text_lower,
                "hate": "hate" in text_lower,
                "harassment": "harassment" in text_lower,
            },
        }
