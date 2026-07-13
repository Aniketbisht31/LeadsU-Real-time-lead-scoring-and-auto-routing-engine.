"""FastAPI entry point for the lead intake service."""

from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, status
from pydantic import BaseModel, EmailStr, Field

from crm import create_contact
from enrichment import enrich_lead
from routing import route_lead
from scoring import score_lead
from slack import notify_new_lead


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


class LeadResponse(BaseModel):
    score: int
    priority: str
    route: str
    hubspot_contact_id: str | None
    slack_notified: bool


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/leads", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(lead: LeadRequest) -> LeadResponse:
    payload = lead.model_dump()
    enrichment = await enrich_lead(lead.company_domain)
    score, priority = score_lead(lead.message, enrichment)
    route = route_lead(enrichment, priority)
    contact_id = await create_contact(payload, score, route)
    slack_notified = await notify_new_lead(lead.name, lead.email, lead.company_domain, score, route)
    return LeadResponse(score=score, priority=priority, route=route,
                        hubspot_contact_id=contact_id, slack_notified=slack_notified)
