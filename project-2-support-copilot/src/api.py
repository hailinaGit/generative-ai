"""FastAPI Service & Human-in-the-Loop Review Desk for AI Customer Support Copilot.

Endpoints:
- GET  /health            : Service health & Ollama readiness check.
- GET  /api/tickets       : Fetch benchmark incoming ticket queue.
- POST /api/copilot/draft : Generate triage tags, policy citations & drafted reply.
- POST /api/review/submit : Human agent review action (Approve As-Is, Edit & Approve, Escalate).
- GET  /api/audit-log     : Review history and agent edit-distance audit trail.
- GET  /                  : Interactive Support Agent Review Desk UI.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

try:
    from src.copilot import SupportCopilotEngine
    from src.models import (
        CopilotDraftResponse,
        CustomerTicket,
        ReviewStatusEnum,
        ReviewSubmission,
    )
except ModuleNotFoundError:
    from copilot import SupportCopilotEngine  # type: ignore
    from models import (  # type: ignore
        CopilotDraftResponse,
        CustomerTicket,
        ReviewStatusEnum,
        ReviewSubmission,
    )

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = Path(__file__).resolve().parent / "static"
TICKETS_FILE = BASE_DIR / "data" / "sample_tickets" / "benchmark_tickets.json"

app = FastAPI(
    title="AI Customer Support Copilot API",
    description="Enterprise Copilot with Triage, Policy Grounding, and Human-in-the-Loop Review.",
    version="1.0.0",
)

# Shared in-memory engine and audit trail
copilot_engine = SupportCopilotEngine()
audit_log: list[dict[str, Any]] = []


# --- Health & Status Schema ---
class HealthResponse(BaseModel):
    status: str
    model: str
    policy_sections_loaded: int
    total_reviews_logged: int


@app.get("/", response_class=FileResponse)
def serve_ui():
    """Serve the Human-in-the-Loop Support Agent Dashboard."""
    index_html = STATIC_DIR / "index.html"
    if not index_html.exists():
        raise HTTPException(status_code=404, detail="Web interface not found.")
    return FileResponse(index_html)


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Verify backend and policy knowledge base readiness."""
    return HealthResponse(
        status="healthy",
        model=copilot_engine.model_name,
        policy_sections_loaded=len(copilot_engine.kb._sections),
        total_reviews_logged=len(audit_log),
    )


@app.get("/api/tickets", response_model=list[CustomerTicket])
def list_incoming_tickets():
    """Load benchmark queue of incoming customer support tickets."""
    if not TICKETS_FILE.exists():
        raise HTTPException(status_code=404, detail="Benchmark tickets dataset not found.")
    try:
        raw_data = json.loads(TICKETS_FILE.read_text(encoding="utf-8"))
        return [
            CustomerTicket(
                ticket_id=t["ticket_id"],
                customer_name=t["customer_name"],
                customer_tier=t.get("customer_tier", "Standard"),
                subject=t["subject"],
                message=t["message"],
            )
            for t in raw_data
        ]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed loading tickets: {str(exc)}")


@app.post("/api/copilot/draft", response_model=CopilotDraftResponse)
def generate_ticket_draft(ticket: CustomerTicket):
    """Run full Copilot workflow: Triage + Grounded Knowledge Retrieval + Draft Generation."""
    try:
        draft_response = copilot_engine.generate_draft(ticket)
        return draft_response
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Copilot inference failed: {str(exc)}. Ensure Ollama is running (`ollama serve`).",
        )


@app.post("/api/review/submit")
def submit_agent_review(review: ReviewSubmission):
    """Human-in-the-loop action: records agent edits, approval decisions, and audit trail."""
    record = review.model_dump()
    audit_log.append(record)
    return {
        "status": "success",
        "message": f"Ticket {review.ticket_id} marked as '{review.action.value}'.",
        "record": record,
    }


@app.get("/api/audit-log")
def get_audit_trail():
    """Retrieve full history of human-reviewed and dispatched support tickets."""
    return {
        "total_dispatched": len(audit_log),
        "audit_records": audit_log,
    }
