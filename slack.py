"""Slack notification integration."""

import os
import httpx


async def notify_new_lead(name: str, email: str, domain: str, score: int, route: str) -> bool:
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        return False
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.post(webhook_url, json={
                "text": f"New lead: {name} ({email}) — {domain}; score {score}; route: {route}"
            })
            response.raise_for_status()
            return True
    except httpx.HTTPError:
        return False
