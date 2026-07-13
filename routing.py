"""Lead ownership rules."""

from typing import Any


def route_lead(enrichment: dict[str, Any], priority: str) -> str:
    if priority == "high" or enrichment.get("employees", 0) >= 200:
        return "enterprise-sales"
    if priority == "medium":
        return "sales-development"
    return "nurture"
