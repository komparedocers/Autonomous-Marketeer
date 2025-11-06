"""Channel Planner Agent for campaign strategy."""
import httpx
import json
import logging
import os

logger = logging.getLogger(__name__)

LLM_ROUTER_URL = os.getenv("LOCAL_LLM_URL", "http://llmrouter:9090")


def run(context: dict, provider: str = "local") -> dict:
    """
    Plan campaign structure and channel strategy.

    Args:
        context: Dict with keys:
            - objective: Campaign objective
            - budget: Total budget
            - target_audience: Target audience
            - channels: Available channels
        provider: LLM provider to use

    Returns:
        Dict with campaign plan
    """
    logger.info("ChannelPlanner running...")

    objective = context.get("objective", "conversions")
    budget = context.get("budget", 1000)
    target_audience = context.get("target_audience", "general audience")
    available_channels = context.get("channels", ["meta", "google"])

    system_prompt = f"""You are a digital marketing strategist. Create a campaign plan with budget allocation across channels.

Objective: {objective}
Budget: ${budget}
Target Audience: {target_audience}
Available Channels: {', '.join(available_channels)}

Return a JSON plan:
{{
  "channels": [
    {{
      "name": "meta",
      "budget_allocation": 500,
      "rationale": "Why this allocation",
      "placements": ["feed", "stories"],
      "bid_strategy": "lowest_cost"
    }}
  ],
  "recommendations": ["..."]
}}
"""

    user_prompt = "Create an optimal campaign plan with budget allocation."

    try:
        response = httpx.post(
            f"{LLM_ROUTER_URL}/generate",
            json={
                "prompt": user_prompt,
                "system_prompt": system_prompt,
                "provider": provider,
                "max_tokens": 1000,
            },
            timeout=60.0,
        )
        response.raise_for_status()
        llm_result = response.json()

        if not llm_result.get("success"):
            # Fallback plan
            budget_per_channel = budget / len(available_channels)
            return {
                "success": True,
                "channels": [
                    {
                        "name": ch,
                        "budget_allocation": budget_per_channel,
                        "rationale": "Even distribution",
                        "placements": ["automatic"],
                        "bid_strategy": "lowest_cost",
                    }
                    for ch in available_channels
                ],
                "recommendations": ["Consider A/B testing different strategies"],
            }

        generated_text = llm_result.get("text", "")
        try:
            start = generated_text.find("{")
            end = generated_text.rfind("}") + 1
            if start >= 0 and end > start:
                plan = json.loads(generated_text[start:end])
            else:
                plan = {"channels": [], "recommendations": []}
        except json.JSONDecodeError:
            plan = {"channels": [], "recommendations": []}

        return {
            "success": True,
            "plan": plan,
            "tokens_used": llm_result.get("tokens_used", 0),
            "provider": provider,
        }

    except Exception as e:
        logger.error(f"ChannelPlanner failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
        }
