"""HubSpot contact creation."""

import os
import httpx


async def create_contact(lead: dict[str, str], score: int, route: str) -> str | None:
    api_key = os.getenv("HUBSPOT_API_KEY")
    if not api_key:
        return None
    properties = {"firstname": lead["name"], "email": lead["email"],
                  "company": lead["company_domain"], "message": lead["message"],
                  "lead_score": str(score), "hs_lead_status": "NEW"}
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.post(
                "https://api.hubapi.com/crm/v3/objects/contacts",
                headers={"Authorization": f"Bearer {api_key}"},
                json={"properties": properties},
            )
            response.raise_for_status()
            return str(response.json()["id"])
    except (httpx.HTTPError, KeyError):
        return None
