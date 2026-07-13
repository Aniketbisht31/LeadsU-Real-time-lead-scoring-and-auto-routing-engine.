"""Post varied demo leads to a locally running AutoLeads server."""

import asyncio

import httpx

API_URL = "http://127.0.0.1:8000/leads"
TEST_LEADS = [
    {"name": "Maya Patel", "email": "maya@google.com", "company_domain": "google.com", "title": "VP Engineering", "message": "We need a demo and enterprise pricing for a global engineering rollout. Please share implementation options and a detailed proposal."},
    {"name": "Noah Kim", "email": "noah@microsoft.com", "company_domain": "microsoft.com", "title": "Director of IT", "message": "Please send a quote and schedule a demo for our distributed operations team."},
    {"name": "Sofia Garcia", "email": "sofia@stripe.com", "company_domain": "stripe.com", "title": "Head of Partnerships", "message": "Interested in buying an integration plan. Can we discuss enterprise pricing this week?"},
    {"name": "Ethan Reed", "email": "ethan@notion.so", "company_domain": "notion.so", "title": "Product Manager", "message": "Could you arrange a product demo and share pricing for our product organization?"},
    {"name": "Priya Shah", "email": "priya@state.gov", "company_domain": "state.gov", "title": "Program Director", "message": "We are evaluating vendors and would like a demo for our agency team."},
    {"name": "Liam Brooks", "email": "liam@acme.io", "company_domain": "acme.io", "title": "Founder", "message": "Just exploring tools for our new startup."},
    {"name": "Ava Chen", "email": "ava@vision.ai", "company_domain": "vision.ai", "title": "ML Engineer", "message": "Interested in learning more about your platform."},
    {"name": "Oliver Grant", "email": "oliver@community.org", "company_domain": "community.org", "title": "Operations Manager", "message": "We are researching options for a nonprofit program."},
    {"name": "Zara Ali", "email": "zara@college.edu", "company_domain": "college.edu", "title": "Dean of Technology", "message": "Please share a demo for our campus technology team."},
    {"name": "Henry Cole", "email": "henry@localbiz.com", "company_domain": "localbiz.com", "title": "Owner", "message": "Hello, I have a quick question."},
]


async def seed_leads() -> None:
    async with httpx.AsyncClient(timeout=15.0) as client:
        for lead in TEST_LEADS:
            response = await client.post(API_URL, json=lead)
            response.raise_for_status()
            result = response.json()
            print(f"{lead['name']}: {result['tier']} ({result['score']}) -> {result['assigned_rep']}")


if __name__ == "__main__":
    asyncio.run(seed_leads())