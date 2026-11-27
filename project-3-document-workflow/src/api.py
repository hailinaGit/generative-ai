"""FastAPI Service & Simulated Team Queue Desk for Document-to-Workflow Automation.

Endpoints:
- GET  /                     : Interactive Workflow Validation & Team Queue UI.
- GET  /health               : Service readiness, model name, and routing directory status.
- GET  /api/documents        : Fetch sample operational documents queue.
- POST /api/workflow/process : Extract action items, verify quotes, and route to simulated teams.
- POST /api/workflow/validate: Coordinator validation/override of extracted action items.
- GET  /api/team-queues      : Inspect simulated team queues.
- GET  /api/audit-log        : Inspect validation and routing audit trail.
"""
from __future__ import annotations

import io
import json
import sys
import urllib.request
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

SRC_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SRC_DIR.parent
for p in (str(SRC_DIR), str(PROJECT_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from models import (
    TEAM_QUEUE_CHANNELS,
    ActionItem,
    DocumentInput,
    ExtractionStatusEnum,
    TeamEnum,
    ValidationStatusEnum,
    ValidationSubmission,
    WorkflowResult,
)
from workflow import DocumentWorkflowEngine

STATIC_DIR = SRC_DIR / "static"
DOCS_FILE = PROJECT_DIR / "data" / "sample_documents" / "benchmark_docs.json"

app = FastAPI(
    title="Document-to-Workflow Automation API",
    description="Extracts grounded action items from operational documents, routes to simulated teams, and enforces confidence/validation guardrails.",
    version="1.0.0",
)

workflow_engine = DocumentWorkflowEngine()
processed_results: dict[str, WorkflowResult] = {}
team_queues: dict[str, list[dict[str, Any]]] = {team.value: [] for team in TeamEnum}
audit_log: list[dict[str, Any]] = []


class HealthResponse(BaseModel):
    status: str
    model: str
    routing_sections_loaded: int
    total_documents_processed: int
    total_audit_records: int


def _sync_team_queues() -> None:
    """Rebuild simulated team queues from current processed_results."""
    for team_name in team_queues:
        team_queues[team_name] = []

    for res in processed_results.values():
        for item in res.action_items:
            if item.validation_status == ValidationStatusEnum.REJECTED:
                continue
            team_queues[item.target_team.value].append({
                "doc_id": res.doc_id,
                "doc_title": res.title,
                **item.model_dump(),
            })


@app.get("/", response_class=FileResponse)
def serve_ui():
    """Serve the Workflow Validation & Simulated Team Queue Dashboard."""
    index_html = STATIC_DIR / "index.html"
    if not index_html.exists():
        raise HTTPException(status_code=404, detail="Web interface not found.")
    return FileResponse(index_html)


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Verify backend and routing directory readiness."""
    return HealthResponse(
        status="healthy",
        model=workflow_engine.model_name,
        routing_sections_loaded=workflow_engine.directory.section_count,
        total_documents_processed=len(processed_results),
        total_audit_records=len(audit_log),
    )


@app.get("/api/documents")
def list_sample_documents():
    """Load sample operational documents with current processing status."""
    if not DOCS_FILE.exists():
        raise HTTPException(status_code=404, detail="Sample documents dataset not found.")
    try:
        raw_docs = json.loads(DOCS_FILE.read_text(encoding="utf-8"))
        docs_out: list[dict[str, Any]] = []
        for d in raw_docs:
            doc_id = d["doc_id"]
            existing = processed_results.get(doc_id)
            docs_out.append({
                "doc_id": doc_id,
                "title": d["title"],
                "doc_type": d.get("doc_type", "Operational Document"),
                "content": d["content"],
                "extraction_status": existing.extraction_status.value if existing else "Pending",
            })
        return docs_out
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed loading documents: {exc}")


@app.post("/api/workflow/process", response_model=WorkflowResult)
def process_document(doc: DocumentInput):
    """Run full Document-to-Workflow extraction, quote verification, and team routing."""
    try:
        result = workflow_engine.process_document(doc)
        processed_results[doc.doc_id] = result
        _sync_team_queues()
        audit_log.append({
            "event": "DOCUMENT_PROCESSED",
            "doc_id": doc.doc_id,
            "extraction_status": result.extraction_status.value,
            "item_count": len(result.action_items),
            "timestamp": result.processed_at,
        })
        return result
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Workflow processing failed: {exc}. Ensure Ollama is running (`ollama serve`).",
        )


@app.get("/api/models")
def list_available_models():
    """Fetch locally installed Ollama models, falling back to default llama3.2."""
    default_model = workflow_engine.model_name
    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=2.0) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        names = [m["name"] for m in payload.get("models", []) if m.get("name")]
        if default_model not in names:
            names.insert(0, default_model)
        return {"models": names}
    except Exception:
        return {"models": [default_model]}


@app.get("/api/routing-rules")
def get_routing_rules():
    """Return the approved team routing directory markdown for UI inspection."""
    return {
        "section_count": workflow_engine.directory.section_count,
        "content": workflow_engine.directory.raw_text,
    }


def _extract_uploaded_text(raw_bytes: bytes, filename: str) -> str:
    """Extract UTF-8 text from .txt/.md/.json or PDF bytes."""
    if Path(filename).suffix.lower() != ".pdf":
        return raw_bytes.decode("utf-8", errors="replace").strip()
    try:
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(raw_bytes))
        return "\n".join((p.extract_text() or "") for p in reader.pages).strip()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to parse PDF '{filename}': {exc}")


def _apply_validation_overrides(item: ActionItem, submission: ValidationSubmission) -> None:
    """Apply coordinator overrides and validation status to an ActionItem."""
    if submission.override_title is not None and submission.override_title.strip():
        item.title = submission.override_title.strip()
    if submission.override_team is not None:
        item.target_team = submission.override_team
        item.queue_channel = TEAM_QUEUE_CHANNELS[submission.override_team]
    if submission.override_priority is not None:
        item.priority = submission.override_priority
    if submission.override_due_date is not None:
        item.due_date = submission.override_due_date.strip() or None
    item.validation_status = submission.action
    item.requires_manual_review = submission.action == ValidationStatusEnum.PENDING_VALIDATION


@app.post("/api/workflow/upload", response_model=WorkflowResult)
async def upload_and_process_document(
    file: UploadFile = File(...),
    doc_id: str = Form(default="DOC-UPLOAD"),
    confidence_threshold: float = Form(default=0.70),
    model_name: str = Form(default="llama3.2"),
):
    """Upload a .txt, .md, .json, or .pdf document and run workflow extraction."""
    raw_bytes = await file.read()
    filename = file.filename or "uploaded_document"
    suffix = Path(filename).suffix.lower()
    content = _extract_uploaded_text(raw_bytes, filename)

    doc = DocumentInput(
        doc_id=doc_id.strip() or "DOC-UPLOAD",
        title=Path(filename).stem,
        doc_type=f"Uploaded ({suffix or 'text'})",
        content=content,
        confidence_threshold=max(0.0, min(1.0, confidence_threshold)),
        model_name=model_name.strip() or "llama3.2",
    )
    return process_document(doc)


@app.post("/api/workflow/validate")
def validate_action_item(submission: ValidationSubmission):
    """Human-in-the-loop validation or override of an extracted action item."""
    result = processed_results.get(submission.doc_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Document '{submission.doc_id}' not found in processed results.")

    target_item = next((i for i in result.action_items if i.item_id == submission.item_id), None)
    if not target_item:
        raise HTTPException(status_code=404, detail=f"Action item '{submission.item_id}' not found.")

    _apply_validation_overrides(target_item, submission)

    still_pending = any(
        i.validation_status == ValidationStatusEnum.PENDING_VALIDATION for i in result.action_items
    )
    if result.extraction_status != ExtractionStatusEnum.REJECTED:
        result.extraction_status = (
            ExtractionStatusEnum.NEEDS_REVIEW if still_pending else ExtractionStatusEnum.COMPLETED
        )

    _sync_team_queues()

    record = {
        "event": "ITEM_VALIDATED",
        **submission.model_dump(),
        "final_team": target_item.target_team.value,
        "final_channel": target_item.queue_channel,
    }
    audit_log.append(record)

    return {
        "status": "success",
        "doc_status": result.extraction_status.value,
        "item": target_item.model_dump(),
    }


@app.get("/api/team-queues")
def get_team_queues():
    """Return all simulated team queues and item counts."""
    return {
        "queues": team_queues,
        "counts": {team: len(items) for team, items in team_queues.items()},
    }


@app.get("/api/audit-log")
def get_audit_log():
    """Return full workflow and validation audit trail."""
    return {
        "total_events": len(audit_log),
        "audit_records": list(reversed(audit_log)),
    }


@app.post("/api/workflow/reset")
def reset_session():
    """Clear processed results, simulated team queues, and audit log for fresh demos."""
    processed_results.clear()
    audit_log.clear()
    _sync_team_queues()
    return {"status": "reset", "message": "Cleared processed results, team queues, and audit log."}
