# AI Customer Support Copilot

An enterprise-grade **Human-in-the-Loop (HITL) Customer Support Copilot** designed to triage incoming support tickets, retrieve approved company policies, draft empathetic grounded replies, and enforce deterministic safety escalations before a human agent approves and dispatches the response.

---

## Key Features

- **Structured Ticket Triage (FR-01):** Automatically classifies **Sentiment** (`Positive`, `Neutral`, `Frustrated`, `Angry`), **Category** (`Billing`, `Technical Support`, `Account Security`, `Shipping & Delivery`, `Cancellation`, `Other`), and **Urgency** (`Low`, `Medium`, `High`, `Critical`) using strict Pydantic V2 schemas.
- **Grounded Policy Retrieval (FR-02):** Matches ticket inquiries against the approved support handbook (`data/knowledge_base/support_policies.md`) and attaches explicit policy citations (`policy_name`, `section`, `rule_applied`).
- **Hybrid Safety & Escalation Guardrails (FR-04):** Deterministic pre-guards detect legal/chargeback threats, unauthorized login breaches, and refund requests exceeding **$100.00 USD**, locking dispatch behind mandatory **Supervisor Escalation** (`100.0%` escalation accuracy).
- **Human-in-the-Loop Review Desk (FR-05 & FR-06):** Interactive FastAPI web dashboard where support agents inspect triage badges, edit the AI draft in a live editor, track ticket statuses (`Pending`, `Escalated`, `Approved`), and log an audit trail.
- **100% Local & Offline Stack:** Powered by Python, FastAPI, Pydantic V2, LangChain, and local Ollama (`llama3.2`) — zero third-party API costs.

---

## Repository Structure

```text
project-2-support-copilot/
├── data/
│   ├── knowledge_base/
│   │   └── support_policies.md        # Approved support policy handbook
│   └── sample_tickets/
│       └── benchmark_tickets.json     # 12 realistic benchmark tickets with ground truth
├── docs/
│   ├── requirements.md                # Project scope, FRs, and acceptance criteria
│   ├── eval_results.md                # 12-ticket live benchmark scores & before/after log
│   └── viva_prep.md                   # Interview & oral defense guide (Handbook Sec 16)
├── src/
│   ├── __init__.py
│   ├── models.py                      # Pydantic V2 domain & review schemas
│   ├── copilot.py                     # Triage classifier, KB retriever & grounded drafter
│   ├── api.py                         # FastAPI REST service & HITL audit endpoints
│   └── static/
│       └── index.html                 # Interactive Support Agent Review Desk UI
├── tests/
│   ├── test_copilot.py                # Fast deterministic unit & guardrail tests
│   └── evaluate_benchmark.py          # 12-ticket end-to-end LLM benchmark runner
└── README.md
```

---

## Quickstart Guide

### 1. Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com/) installed and running locally:
  ```bash
  ollama serve
  ollama pull llama3.2
  ```

### 2. Environment Setup
From the root `Internship/` workspace:
```bash
source .venv/bin/activate
cd project-2-support-copilot
```

### 3. Launch the FastAPI Service & Review Desk UI
```bash
uvicorn src.api:app --reload --port 8000
```
- **Agent Review Desk UI:** Open **[http://localhost:8000/](http://localhost:8000/)**
- **Swagger API Docs:** Open **[http://localhost:8000/docs](http://localhost:8000/docs)**

### 4. API Endpoints
- `GET /health` — Service readiness, model name, and loaded policy sections.
- `GET /api/tickets` — Returns the 12-ticket queue with live status (`Pending Review`, `Escalated to Supervisor`, `Approved`).
- `POST /api/copilot/draft` — Runs triage, policy retrieval, escalation checks, and draft synthesis.
- `POST /api/review/submit` — Submits human review decision (`Approved (As-Is)`, `Approved (Edited)`, `Escalated to Supervisor`) and updates the audit log.
- `GET /api/audit-log` — Returns all reviewed and dispatched ticket records.

---

## Testing & Benchmark Evaluation

### 1. Deterministic Unit Tests (`< 1 sec`, no LLM required)
Validates Pydantic V2 schemas, policy retrieval, and deterministic `$100` / legal escalation rules:
```bash
python tests/test_copilot.py
```

### 2. Full 12-Ticket LLM Benchmark (`llama3.2`)
Runs all 12 tickets in `data/sample_tickets/benchmark_tickets.json` and computes live accuracy scores:
```bash
python tests/evaluate_benchmark.py
```

**Observed Benchmark Results:**
- **Structured Output Schema Compliance:** `12/12 (100.0%)`
- **Category Classification Accuracy:** `11/12 (91.7%)`
- **Urgency Classification Accuracy:** `9/12 (75.0%)`
- **Escalation Trigger Accuracy:** `12/12 (100.0%)`
- **Grounding & Citation Compliance:** `12/12 (100.0%)`

