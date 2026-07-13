"""Company enrichment with Clearbit and deterministic demo fallbacks."""

import os

import httpx


DEMO_COMPANIES = {
    "google.com": {"company_size": "enterprise", "industry": "technology", "funding_stage": "public"},
    "microsoft.com": {"company_size": "enterprise", "industry": "technology", "funding_stage": "public"},
    "apple.com": {"company_size": "enterprise", "industry": "consumer technology", "funding_stage": "public"},
    "stripe.com": {"company_size": "enterprise", "industry": "fintech", "funding_stage": "late-stage"},
    "notion.so": {"company_size": "mid-market", "industry": "productivity software", "funding_stage": "late-stage"},
    "openai.com": {"company_size": "enterprise", "industry": "artificial intelligence", "funding_stage": "late-stage"},
}
TLD_DEFAULTS = {
    ".edu": {"company_size": "mid-market", "industry": "education", "funding_stage": "not applicable"},
    ".gov": {"company_size": "enterprise", "industry": "government", "funding_stage": "not applicable"},
    ".org": {"company_size": "small", "industry": "nonprofit", "funding_stage": "not applicable"},
    ".io": {"company_size": "startup", "industry": "software", "funding_stage": "seed"},
    ".ai": {"company_size": "startup", "industry": "artificial intelligence", "funding_stage": "series-a"},
}
DEFAULT_ENRICHMENT = {"company_size": "small", "industry": "unknown", "funding_stage": "unknown"}


def _company_size(employee_count: int | None) -> str:
    if not employee_count:
        return "unknown"
    if employee_count >= 1_000:
        return "enterprise"
    if employee_count >= 200:
        return "mid-market"
    if employee_count >= 50:
        return "small"
    return "startup"


def _fallback_enrichment(domain: str) -> dict:
    normalized_domain = domain.lower().removeprefix("www.")
    if normalized_domain in DEMO_COMPANIES:
        return DEMO_COMPANIES[normalized_domain].copy()
    for tld, result in TLD_DEFAULTS.items():
        if normalized_domain.endswith(tld):
            return result.copy()
    return DEFAULT_ENRICHMENT.copy()


async def enrich_lead(domain: str) -> dict:
    """Enrich a domain with Clearbit, falling back to local demo heuristics."""
    api_key = os.getenv("CLEARBIT_API_KEY")
    if not api_key:
        return _fallback_enrichment(domain)

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(
                "https://company.clearbit.com/v2/companies/find",
                params={"domain": domain},
                auth=(api_key, ""),
            )
            response.raise_for_status()
            company = response.json()
    except (httpx.HTTPError, ValueError):
        return _fallback_enrichment(domain)

    metrics = company.get("metrics") or {}
    category = company.get("category") or {}
    return {
        "company_size": _company_size(metrics.get("employees")),
        "industry": category.get("industry") or "unknown",
        "funding_stage": company.get("fundingStage") or "unknown",
    }