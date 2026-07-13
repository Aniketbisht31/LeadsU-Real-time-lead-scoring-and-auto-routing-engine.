"""FastAPI entry point for the lead intake service."""

from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, status
from pydantic import BaseModel, EmailStr, Field

from crm import upsert_hubspot_contact
from enrichment import enrich_lead
from routing import assign_rep
from scoring import score_lead
from slack import notify_slack


@asynccontextmanager
async def lifespan(_: FastAPI):
    load_dotenv()
    yield


app = FastAPI(title="AutoLeads API", version="1.0.0", lifespan=lifespan)


class LeadRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    company_domain: str = Field(min_length=3, max_length=255)
    message: str = Field(min_length=1, max_length=5000)
    title: str | None = Field(default=None, max_length=120)


class LeadResponse(BaseModel):
    score: int
    tier: str
    reasons: list[str]
    assigned_rep: str
    hubspot_contact_id: str | None
    slack_notified: bool


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/leads", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(lead: LeadRequest) -> LeadResponse:
    payload = lead.model_dump()
    enrichment = await enrich_lead(lead.company_domain)
    score_result = score_lead(payload, enrichment)
    assigned_rep = assign_rep(score_result["tier"])
    contact_id = await upsert_hubspot_contact(payload, enrichment, score_result, assigned_rep)
    slack_notified = await notify_slack(payload, score_result, assigned_rep)
    return LeadResponse(
        score=score_result["score"],
        tier=score_result["tier"],
        reasons=score_result["reasons"],
        assigned_rep=assigned_rep,
        hubspot_contact_id=contact_id,
        slack_notified=slack_notified,
    )