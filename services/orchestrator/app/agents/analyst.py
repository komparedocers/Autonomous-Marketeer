"""Analyst Agent for generating insights and reports."""
import httpx
import json
import logging
import os

logger = logging.getLogger(__name__)

LLM_ROUTER_URL = os.getenv("LOCAL_LLM_URL", "http://llmrouter:9090")


def run(context: dict, provider: str = "local") -> dict:
    """
    Generate insights and narrative reports from campaign data.

    Args:
        context: Dict with keys:
            - metrics: Campaign metrics data
            - time_period: Time period for analysis
            - campaigns: List of campaign summaries
        provider: LLM provider to use

    Returns:
        Dict with analysis and recommendations
    """
    logger.info("AnalystAgent running...")

    metrics = context.get("metrics", {})
    time_period = context.get("time_period", "last 7 days")
    campaigns = context.get("campaigns", [])

    # Build summary of metrics
    spend = metrics.get("spend", 0)
    impressions = metrics.get("impressions", 0)
    clicks = metrics.get("clicks", 0)
    conversions = metrics.get("conversions", 0)
    revenue = metrics.get("revenue", 0)

    ctr = (clicks / impressions * 100) if impressions > 0 else 0
    cvr = (conversions / clicks * 100) if clicks > 0 else 0
    cpc = spend / clicks if clicks > 0 else 0
    cpa = spend / conversions if conversions > 0 else 0
    roas = revenue / spend if spend > 0 else 0

    metrics_summary = f"""
Spend: ${spend:,.2f}
Impressions: {impressions:,}
Clicks: {clicks:,}
Conversions: {conversions:,}
Revenue: ${revenue:,.2f}

CTR: {ctr:.2f}%
CVR: {cvr:.2f}%
CPC: ${cpc:.2f}
CPA: ${cpa:.2f}
ROAS: {roas:.2f}x
"""

    system_prompt = f"""You are a senior marketing analyst. Analyze the campaign performance data and provide insights and recommendations.

Time Period: {time_period}

Performance Metrics:
{metrics_summary}

Provide your analysis in this structure:
1. Performance Overview (2-3 sentences)
2. Key Insights (bullet points)
3. Anomalies or Concerns (if any)
4. Recommendations for Next Steps (actionable)

Keep your response concise and focused on actionable insights.
"""

    user_prompt = "Analyze the campaign performance and provide insights."

    try:
        response = httpx.post(
            f"{LLM_ROUTER_URL}/generate",
            json={
                "prompt": user_prompt,
                "system_prompt": system_prompt,
                "provider": provider,
                "max_tokens": 1000,
                "temperature": 0.7,
            },
            timeout=60.0,
        )
        response.raise_for_status()
        llm_result = response.json()

        if not llm_result.get("success"):
            # Fallback analysis
            analysis = {
                "overview": f"Campaign performance over {time_period} shows a ROAS of {roas:.2f}x with {conversions} conversions.",
                "insights": [
                    f"CTR of {ctr:.2f}% indicates {'strong' if ctr > 2 else 'moderate' if ctr > 1 else 'weak'} ad engagement",
                    f"CVR of {cvr:.2f}% shows {'effective' if cvr > 2 else 'moderate'} conversion optimization",
                ],
                "recommendations": [
                    "Continue monitoring performance trends",
                    "Consider A/B testing different ad variations" if ctr < 2 else "Scale winning variants",
                ],
            }
        else:
            # Parse LLM response
            analysis = {
                "overview": llm_result.get("text", ""),
                "insights": [],
                "recommendations": [],
            }

        return {
            "success": True,
            "analysis": analysis,
            "metrics": {
                "ctr": ctr,
                "cvr": cvr,
                "cpc": cpc,
                "cpa": cpa,
                "roas": roas,
            },
            "tokens_used": llm_result.get("tokens_used", 0) if llm_result.get("success") else 0,
            "provider": provider,
        }

    except Exception as e:
        logger.error(f"AnalystAgent failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
        }
