# LeadsU

**Real-time lead scoring and auto-routing engine.**

Inbound leads sit untriaged for hours because someone has to manually check company size, industry, and rep availability before assigning them. LeadsU automates the entire pipeline — enriching, scoring, and routing a lead the moment it comes in — cutting manual triage from ~30 minutes to under 5 seconds.

![status](https://img.shields.io/badge/status-active-brightgreen) ![python](https://img.shields.io/badge/python-3.11-blue)

---

## What it does

1. **Ingests** a lead from a form submission or webhook
2. **Enriches** it with firmographic data (company size, industry, funding stage) via Clearbit/Apollo, with a heuristic fallback if enrichment APIs are unavailable
3. **Scores** it against explicit, explainable ICP rules — not a black-box model — and returns *why* it scored the way it did
4. **Routes** it to the right rep: Hot → senior AE, Warm → round-robin across the team, Cold → nurture queue
5. **Pushes** the scored, routed lead into HubSpot and fires a Slack alert with the score, tier, assigned rep, and reasoning

```
[Lead submitted] → [Enrichment] → [Scoring] → [Routing] → [HubSpot + Slack]
```

## Why explainable scoring

Most lead-scoring demos return a number with no reasoning, which nobody trusts enough to act on. LeadsU returns a `reasons` list alongside every score — the specific rules that fired — so a rep or manager can audit the decision instead of taking it on faith. That auditability, not raw accuracy, is what makes automated scoring usable in a real sales org.


<img width="1072" height="561" alt="image" src="https://github.com/user-attachments/assets/025dede9-7430-42e2-b66f-4dff4d4aaee3" />

## Tech stack

| Layer | Tool |
|---|---|
| Backend | Python (FastAPI) |
| Enrichment | Clearbit / Apollo API (heuristic fallback) |
| CRM | HubSpot CRM API v3 |
| Notifications | Slack Incoming Webhooks |
| Hosting | Render / Railway *(if deployed)* |

## Project structure

```
leadsu/
├── main.py            # FastAPI app, POST /leads endpoint
├── enrichment.py       # firmographic enrichment + fallback heuristic
├── scoring.py          # weighted rule-based scoring engine
├── routing.py          # tier-based rep assignment
├── crm.py              # HubSpot upsert logic
├── slack.py            # Slack notification formatting/sending
├── seed_test_leads.py  # generates sample leads to demo Hot/Warm/Cold outcomes
├── requirements.txt
└── .env.example
```

## Setup

```bash
git clone https://github.com/<your-username>/leadsu.git
cd leadsu
pip install -r requirements.txt
cp .env.example .env   # add your HUBSPOT_API_KEY, CLEARBIT_API_KEY, SLACK_WEBHOOK_URL
uvicorn main:app --reload
```

### Environment variables

| Variable | Description |
|---|---|
| `HUBSPOT_API_KEY` | HubSpot private app token (CRM free tier works) |
| `CLEARBIT_API_KEY` | Clearbit API key (optional — falls back to heuristic if unset) |
| `SLACK_WEBHOOK_URL` | Slack Incoming Webhook URL for alerts |

## Usage

Submit a lead:

```bash
curl -X POST http://localhost:8000/leads \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Doe",
    "email": "jane@acme.com",
    "company_domain": "acme.com",
    "message": "Interested in enterprise plan"
  }'
```

Or run the seed script to push 10 varied sample leads and see the full spread of Hot/Warm/Cold outcomes:

```bash
python seed_test_leads.py
```

## Scoring logic

```
score = 0
+30  company size in ICP range (50–500 employees)
+25  industry matches target list
+20  title contains "VP" / "Director" / "Head of"
+15  funding stage is Series A or B
+10  message mentions "enterprise" or "pricing"

Hot  : score >= 70
Warm : score >= 40
Cold : score <  40
```

Rules are defined as named constants in `scoring.py`, not inline magic numbers, so ICP criteria can be tuned without touching logic.

## Routing logic

| Tier | Assignment |
|---|---|
| Hot | Senior AE (fixed) |
| Warm | Round-robin across mid-tier reps |
| Cold | Nurture queue (tagged, no rep assigned) |

## Roadmap / stretch goals

- [ ] Replace rule-based scoring with a logistic regression model trained on labeled conversion data
- [ ] Add a `/leads/{id}/feedback` endpoint so reps can mark leads as converted/bad-fit, closing the feedback loop
- [ ] Deploy live with a public demo URL

## License

MIT
