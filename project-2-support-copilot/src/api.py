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
import sys
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

# Ensure project root and src are in python search path
SRC_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SRC_DIR.parent
for p in (str(SRC_DIR), str(PROJECT_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from copilot import SupportCopilotEngine
from models import (
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

# Shared in-memory engine, live ticket status map, and audit trail
copilot_engine = SupportCopilotEngine()
audit_log: list[dict[str, Any]] = []
ticket_status_map: dict[str, ReviewStatusEnum] = {}


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
    """Load benchmark queue of incoming customer support tickets with current review status."""
    if not TICKETS_FILE.exists():
        raise HTTPException(status_code=404, detail="Benchmark tickets dataset not found.")
    try:
        raw_data = json.loads(TICKETS_FILE.read_text(encoding="utf-8"))
        ticket_list: list[CustomerTicket] = []
        for t in raw_data:
            tid = t["ticket_id"]
            current_status = ticket_status_map.get(tid, ReviewStatusEnum.PENDING)
            ticket_list.append(
                CustomerTicket(
                    ticket_id=tid,
                    customer_name=t["customer_name"],
                    customer_tier=t.get("customer_tier", "Standard"),
                    subject=t["subject"],
                    message=t["message"],
                    status=current_status,
                )
            )
        return ticket_list
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed loading tickets: {str(exc)}")


@app.post("/api/copilot/draft", response_model=CopilotDraftResponse)
def generate_ticket_draft(ticket: CustomerTicket):
    """Run full Copilot workflow: Triage + Grounded Knowledge Retrieval + Draft Generation."""
    try:
        draft_response = copilot_engine.generate_draft(ticket)
        # If triage detects escalation need, automatically update ticket status to Escalated to Supervisor
        if draft_response.triage.escalate_to_human:
            ticket_status_map[ticket.ticket_id] = ReviewStatusEnum.ESCALATED
        return draft_response
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Copilot inference failed: {str(exc)}. Ensure Ollama is running (`ollama serve`).",
        )


@app.post("/api/review/submit")
def submit_agent_review(review: ReviewSubmission):
    """Human-in-the-loop action: updates ticket live status and audit trail."""
    ticket_status_map[review.ticket_id] = review.action
    record = review.model_dump()
    audit_log.append(record)
    return {
        "status": "success",
        "message": f"Ticket {review.ticket_id} marked as '{review.action.value}'.",
        "record": record,
        "new_status": review.action.value,
    }


@app.get("/api/audit-log")
def get_audit_trail():
    """Retrieve full history of human-reviewed and dispatched support tickets."""
    return {
        "total_dispatched": len(audit_log),
        "audit_records": audit_log,
    }

