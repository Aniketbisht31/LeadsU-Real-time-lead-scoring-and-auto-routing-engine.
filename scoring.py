"""Deterministic lead scoring."""

from typing import Any


def score_lead(message: str, enrichment: dict[str, Any]) -> tuple[int, str]:
    score = 25
    if enrichment.get("enriched"):
        score += 15
    if enrichment.get("employees", 0) >= 50:
        score += 20
    if any(word in message.lower() for word in ("demo", "pricing", "buy", "quote")):
        score += 25
    if len(message.strip()) >= 80:
        score += 10
    score = min(score, 100)
    return score, "high" if score >= 65 else "medium" if score >= 40 else "low"
