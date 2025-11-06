"""Compliance Agent for checking ad content against platform policies."""
import httpx
import json
import logging
import os
import re

logger = logging.getLogger(__name__)

LLM_ROUTER_URL = os.getenv("LOCAL_LLM_URL", "http://llmrouter:9090")


def run(context: dict, provider: str = "local") -> dict:
    """
    Check ad content for compliance with platform policies.

    Args:
        context: Dict with keys:
            - content: Ad content to check (headline, text, etc.)
            - channel: Channel type (meta, google, linkedin, etc.)
        provider: LLM provider to use

    Returns:
        Dict with compliance check results
    """
    logger.info("ComplianceAgent running...")

    content = context.get("content", "")
    channel = context.get("channel", "meta")

    # Heuristic checks
    heuristic_flags = []

    # Check for prohibited words
    prohibited_words = [
        "guaranteed",
        "miracle",
        "free money",
        "get rich quick",
        "lose weight fast",
    ]

    content_lower = content.lower()
    for word in prohibited_words:
        if word in content_lower:
            heuristic_flags.append({
                "type": "prohibited_word",
                "word": word,
                "severity": "high",
                "message": f"Contains prohibited phrase: '{word}'",
            })

    # Check for excessive capitalization
    caps_ratio = sum(1 for c in content if c.isupper()) / max(len(content), 1)
    if caps_ratio > 0.5:
        heuristic_flags.append({
            "type": "excessive_caps",
            "severity": "medium",
            "message": "Excessive capitalization detected",
        })

    # Check for excessive punctuation
    punct_count = len(re.findall(r"[!?]{2,}", content))
    if punct_count > 0:
        heuristic_flags.append({
            "type": "excessive_punctuation",
            "severity": "low",
            "message": "Excessive punctuation (!!!, ???) detected",
        })

    # Build system prompt for LLM check
    system_prompt = f"""You are a compliance expert for {channel} advertising. Analyze the following ad content for policy violations.

Check for:
1. Misleading or false claims
2. Prohibited content (violence, adult content, illegal products)
3. Trademark or copyright issues
4. Discriminatory language
5. Platform-specific policy violations for {channel}

Return your response as JSON with this structure:
{{
  "compliant": true/false,
  "violations": [
    {{"type": "...", "severity": "high/medium/low", "message": "..."}}
  ],
  "recommendations": ["..."]
}}
"""

    user_prompt = f"Analyze this ad content for compliance:\n\n{content}"

    try:
        # Call LLM Router for AI-based compliance check
        response = httpx.post(
            f"{LLM_ROUTER_URL}/generate",
            json={
                "prompt": user_prompt,
                "system_prompt": system_prompt,
                "provider": provider,
                "max_tokens": 800,
                "temperature": 0.3,  # Lower temperature for more consistent results
            },
            timeout=60.0,
        )
        response.raise_for_status()
        llm_result = response.json()

        if not llm_result.get("success"):
            # If LLM fails, fall back to heuristic checks only
            logger.warning("LLM compliance check failed, using heuristics only")
            llm_violations = []
        else:
            # Parse LLM response
            generated_text = llm_result.get("text", "")
            try:
                start = generated_text.find("{")
                end = generated_text.rfind("}") + 1
                if start >= 0 and end > start:
                    json_str = generated_text[start:end]
                    llm_check = json.loads(json_str)
                    llm_violations = llm_check.get("violations", [])
                else:
                    llm_violations = []
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON from LLM compliance response")
                llm_violations = []

        # Combine heuristic and LLM violations
        all_violations = heuristic_flags + llm_violations

        # Determine overall compliance
        high_severity_count = sum(1 for v in all_violations if v.get("severity") == "high")
        compliant = high_severity_count == 0

        return {
            "success": True,
            "compliant": compliant,
            "violations": all_violations,
            "summary": {
                "total_violations": len(all_violations),
                "high_severity": high_severity_count,
                "medium_severity": sum(1 for v in all_violations if v.get("severity") == "medium"),
                "low_severity": sum(1 for v in all_violations if v.get("severity") == "low"),
            },
            "tokens_used": llm_result.get("tokens_used", 0) if llm_result.get("success") else 0,
            "provider": provider,
        }

    except Exception as e:
        logger.error(f"ComplianceAgent failed: {e}", exc_info=True)
        # Return heuristic results even if LLM fails
        return {
            "success": True,
            "compliant": len([f for f in heuristic_flags if f.get("severity") == "high"]) == 0,
            "violations": heuristic_flags,
            "summary": {
                "total_violations": len(heuristic_flags),
                "high_severity": sum(1 for v in heuristic_flags if v.get("severity") == "high"),
            },
            "error": f"LLM check failed: {str(e)}",
        }
