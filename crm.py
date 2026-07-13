"""HubSpot CRM contact upsert integration."""

import os

import httpx

HUBSPOT_CONTACTS_URL = "https://api.hubapi.com/crm/v3/objects/contacts"


def _contact_properties(lead: dict, enrichment: dict, score_result: dict, assigned_rep: str) -> dict:
    return {
        "firstname": str(lead.get("name", "")),
        "email": str(lead["email"]),
        "website": str(lead.get("company_domain", "")),
        "jobtitle": str(lead.get("title", "")),
        "message": str(lead.get("message", "")),
        "lead_score": str(score_result["score"]),
        "lead_tier": str(score_result["tier"]),
        "assigned_rep": assigned_rep,
    }


async def upsert_hubspot_contact(
    lead: dict, enrichment: dict, score_result: dict, assigned_rep: str
) -> str | None:
    """Find a HubSpot contact by email, then update it or create a new one."""
    api_key = os.getenv("HUBSPOT_API_KEY")
    if not api_key:
        return None

    headers = {"Authorization": f"Bearer {api_key}"}
    properties = _contact_properties(lead, enrichment, score_result, assigned_rep)
    search_body = {
        "filterGroups": [
            {"filters": [{"propertyName": "email", "operator": "EQ", "value": lead["email"]}]}
        ],
        "limit": 1,
    }

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            search_response = await client.post(
                f"{HUBSPOT_CONTACTS_URL}/search", headers=headers, json=search_body
            )
            search_response.raise_for_status()
            results = search_response.json().get("results", [])
            if results:
                contact_id = str(results[0]["id"])
                response = await client.patch(
                    f"{HUBSPOT_CONTACTS_URL}/{contact_id}",
                    headers=headers,
                    json={"properties": properties},
                )
            else:
                response = await client.post(
                    HUBSPOT_CONTACTS_URL,
                    headers=headers,
                    json={"properties": properties},
                )
            response.raise_for_status()
            return str(response.json()["id"])
    except (httpx.HTTPError, KeyError, ValueError):
        return None