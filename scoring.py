"""Transparent, deterministic lead scoring."""

BASE_SCORE = 20
KNOWN_INDUSTRY_WEIGHT = 15
QUALIFIED_COMPANY_SIZE_WEIGHT = 20
BUYING_INTENT_WEIGHT = 25
DETAILED_MESSAGE_WEIGHT = 10
GROWTH_STAGE_WEIGHT = 10
MAX_SCORE = 100

HIGH_TIER_THRESHOLD = 70
MEDIUM_TIER_THRESHOLD = 45
DETAILED_MESSAGE_MIN_LENGTH = 80
BUYING_INTENT_KEYWORDS = ("demo", "pricing", "buy", "quote")
QUALIFIED_COMPANY_SIZES = {"small", "mid-market", "enterprise"}
GROWTH_FUNDING_STAGES = {"series-a", "series-b", "series-c", "late-stage", "public"}


def score_lead(lead: dict, enrichment: dict) -> dict:
    """Score a lead and return a tier with explanations for every applied rule."""
    score = BASE_SCORE
    reasons = ["Lead submission received."]
    message = str(lead.get("message", "")).strip()

    if enrichment.get("industry") not in {None, "", "unknown"}:
        score += KNOWN_INDUSTRY_WEIGHT
        reasons.append("Company industry is known.")

    if enrichment.get("company_size") in QUALIFIED_COMPANY_SIZES:
        score += QUALIFIED_COMPANY_SIZE_WEIGHT
        reasons.append("Company size meets the qualified-lead threshold.")

    if any(keyword in message.lower() for keyword in BUYING_INTENT_KEYWORDS):
        score += BUYING_INTENT_WEIGHT
        reasons.append("Message shows purchase intent (for example, demo or pricing interest).")

    if len(message) >= DETAILED_MESSAGE_MIN_LENGTH:
        score += DETAILED_MESSAGE_WEIGHT
        reasons.append("Message provides detailed context.")

    if enrichment.get("funding_stage") in GROWTH_FUNDING_STAGES:
        score += GROWTH_STAGE_WEIGHT
        reasons.append("Company is in a growth or public funding stage.")

    score = min(score, MAX_SCORE)
    if score >= HIGH_TIER_THRESHOLD:
        tier = "Hot"
    elif score >= MEDIUM_TIER_THRESHOLD:
        tier = "Warm"
    else:
        tier = "Cold"

    return {"score": score, "tier": tier, "reasons": reasons}