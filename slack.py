"""Slack notification integration."""

import os

import httpx


def _slack_blocks(lead: dict, score_result: dict, assigned_rep: str) -> list[dict]:
    name = lead.get("name", "Unknown lead")
    company = lead.get("company") or lead.get("company_domain", "Unknown company")
    reasons = score_result.get("reasons", [])
    reason_text = "\n".join(f"- {reason}" for reason in reasons) or "- No scoring rules fired."

    return [
        {"type": "header", "text": {"type": "plain_text", "text": "New lead received", "emoji": True}},
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*{name}* - {company}"},
            "fields": [
                {"type": "mrkdwn", "text": f"*Score*\n{score_result.get('score', 0)}"},
                {"type": "mrkdwn", "text": f"*Tier*\n{score_result.get('tier', 'Unknown')}"},
                {"type": "mrkdwn", "text": f"*Assigned rep*\n{assigned_rep}"},
                {"type": "mrkdwn", "text": f"*Email*\n{lead.get('email', 'Not provided')}"},
            ],
        },
        {"type": "divider"},
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*Why this lead scored*\n{reason_text}"}},
    ]


async def notify_slack(lead: dict, score_result: dict, assigned_rep: str) -> bool:
    """Send a formatted lead notification to the configured Slack webhook."""
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        return False

    fallback_text = (
        f"New lead: {lead.get('name')} at {lead.get('company_domain')}; "
        f"score {score_result.get('score')} ({score_result.get('tier')}); "
        f"assigned to {assigned_rep}."
    )
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.post(
                webhook_url,
                json={"text": fallback_text, "blocks": _slack_blocks(lead, score_result, assigned_rep)},
            )
            response.raise_for_status()
            return True
    except httpx.HTTPError:
        return False