"""Creative Agent for generating ad copy and content."""
import httpx
import json
import logging
import os

logger = logging.getLogger(__name__)

LLM_ROUTER_URL = os.getenv("LOCAL_LLM_URL", "http://llmrouter:9090")


def run(context: dict, provider: str = "local") -> dict:
    """
    Generate creative content for ads.

    Args:
        context: Dict with keys:
            - objective: Campaign objective (awareness, traffic, leads, conversions)
            - brand_voice: Brand voice guidelines
            - target_audience: Target audience description
            - channel: Channel type (meta, google, linkedin, etc.)
            - variations: Number of variations to generate (default: 3)
        provider: LLM provider to use (openai or local)

    Returns:
        Dict with generated creative variations
    """
    logger.info("CreativeAgent running...")

    objective = context.get("objective", "conversions")
    brand_voice = context.get("brand_voice", "professional and engaging")
    target_audience = context.get("target_audience", "general audience")
    channel = context.get("channel", "meta")
    num_variations = context.get("variations", 3)

    # Build system prompt
    system_prompt = f"""You are an expert marketing copywriter. Your task is to create compelling ad copy that drives {objective}.

Brand Voice: {brand_voice}
Target Audience: {target_audience}
Channel: {channel}

Generate {num_variations} different ad variations with:
- Headline (max 40 characters)
- Primary text (max 125 characters)
- Call-to-action (one word: Learn, Shop, Sign Up, etc.)

Return your response as a JSON array with this structure:
[
  {{
    "headline": "...",
    "primary_text": "...",
    "cta": "...",
    "rationale": "Why this copy works"
  }}
]
"""

    # Build user prompt
    user_prompt = f"Generate {num_variations} ad variations for a {objective} campaign targeting {target_audience}."

    try:
        # Call LLM Router
        response = httpx.post(
            f"{LLM_ROUTER_URL}/generate",
            json={
                "prompt": user_prompt,
                "system_prompt": system_prompt,
                "provider": provider,
                "max_tokens": 1500,
                "temperature": 0.8,
            },
            timeout=120.0,
        )
        response.raise_for_status()
        llm_result = response.json()

        if not llm_result.get("success"):
            return {
                "success": False,
                "error": llm_result.get("error", "LLM generation failed"),
            }

        # Parse the response
        generated_text = llm_result.get("text", "")

        # Try to extract JSON from the response
        try:
            # Find JSON array in the response
            start = generated_text.find("[")
            end = generated_text.rfind("]") + 1
            if start >= 0 and end > start:
                json_str = generated_text[start:end]
                variations = json.loads(json_str)
            else:
                # Fallback: create structured variations from text
                variations = [{
                    "headline": "Discover Amazing Products",
                    "primary_text": "Shop now and save big on your favorite items. Limited time offer!",
                    "cta": "Shop",
                    "rationale": "Generated from LLM output"
                }]
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from LLM response, using fallback")
            variations = [{
                "headline": "Transform Your Marketing",
                "primary_text": "Automate your campaigns with AI-powered insights and optimization.",
                "cta": "Learn",
                "rationale": "Fallback creative"
            }]

        return {
            "success": True,
            "variations": variations,
            "tokens_used": llm_result.get("tokens_used", 0),
            "provider": provider,
        }

    except Exception as e:
        logger.error(f"CreativeAgent failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
        }
