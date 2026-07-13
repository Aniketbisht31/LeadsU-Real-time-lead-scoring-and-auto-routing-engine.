"""Company enrichment integrations."""

import os
from typing import Any

import httpx


async def enrich_company(company_domain: str) -> dict[str, Any]:
    """Return available company data for a domain."""
    api_key = os.getenv("CLEARBIT_API_KEY")
    if not api_key:
        return {"domain": company_domain, "enriched": False}
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(
                "https://company.clearbit.com/v2/companies/find",
                params={"domain": company_domain}, auth=(api_key, ""),
            )
            response.raise_for_status()
            company = response.json()
    except httpx.HTTPError:
        return {"domain": company_domain, "enriched": False}
    return {"domain": company_domain, "enriched": True, "name": company.get("name"),
            "industry": company.get("category", {}).get("industry"),
            "employees": company.get("metrics", {}).get("employees"),
            "country": company.get("geo", {}).get("country")}
