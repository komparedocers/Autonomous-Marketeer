"""Optimizer Agent using multi-armed bandits for ad optimization."""
import logging
import numpy as np
from typing import List, Dict

logger = logging.getLogger(__name__)


def run(context: dict, provider: str = "local") -> dict:
    """
    Optimize ad performance using Thompson Sampling (multi-armed bandit).

    Args:
        context: Dict with keys:
            - variants: List of ad variants with performance data
                [{"id": 1, "clicks": 100, "impressions": 1000}, ...]
            - metric: Optimization metric (ctr, cvr, cpa)
            - budget: Remaining budget
        provider: Not used for optimizer (rule-based)

    Returns:
        Dict with optimization recommendations
    """
    logger.info("Optimizer running...")

    variants = context.get("variants", [])
    metric = context.get("metric", "ctr")
    budget = context.get("budget", 1000)

    if not variants:
        return {
            "success": False,
            "error": "No variants provided",
        }

    # Thompson Sampling for CTR optimization
    recommendations = []

    for variant in variants:
        variant_id = variant.get("id")
        impressions = variant.get("impressions", 0)
        clicks = variant.get("clicks", 0)
        conversions = variant.get("conversions", 0)

        # Calculate metrics
        ctr = clicks / max(impressions, 1)
        cvr = conversions / max(clicks, 1)

        # Thompson Sampling: Beta distribution
        # Success = clicks, Failures = impressions - clicks
        alpha = clicks + 1
        beta = impressions - clicks + 1

        # Sample from Beta distribution to get expected CTR
        sampled_ctr = np.random.beta(alpha, beta)

        # Determine action
        if impressions < 100:
            action = "explore"
            reason = "Insufficient data, continue exploring"
            budget_allocation = budget * 0.2  # Allocate 20% for exploration
        elif ctr < 0.01:
            action = "pause"
            reason = f"Low CTR ({ctr:.2%}), pausing variant"
            budget_allocation = 0
        elif ctr > 0.05:
            action = "scale"
            reason = f"High CTR ({ctr:.2%}), increasing budget"
            budget_allocation = budget * 0.5  # Allocate 50% to winner
        else:
            action = "maintain"
            reason = f"Moderate performance (CTR {ctr:.2%}), maintaining current spend"
            budget_allocation = budget * 0.3

        recommendations.append({
            "variant_id": variant_id,
            "action": action,
            "reason": reason,
            "budget_allocation": budget_allocation,
            "metrics": {
                "ctr": ctr,
                "cvr": cvr,
                "sampled_ctr": sampled_ctr,
            },
        })

    # Sort by sampled CTR (highest first)
    recommendations.sort(key=lambda x: x["metrics"]["sampled_ctr"], reverse=True)

    return {
        "success": True,
        "recommendations": recommendations,
        "summary": {
            "total_variants": len(variants),
            "to_pause": len([r for r in recommendations if r["action"] == "pause"]),
            "to_scale": len([r for r in recommendations if r["action"] == "scale"]),
            "to_explore": len([r for r in recommendations if r["action"] == "explore"]),
        },
        "provider": "rule_based",
    }
