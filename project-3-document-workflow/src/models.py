"""Pydantic V2 Domain & Validation Schemas for Document-to-Workflow Automation (FR-01, FR-03, FR-04, FR-06).

Defines strict validated schemas for:
- Incoming operational documents
- Extracted action items with confidence scores and verbatim source quotes
- Simulated team routing targets and validation states
- Coordinator review submissions and audit records
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class TeamEnum(str, Enum):
    ENGINEERING = "Engineering"
    FINANCE = "Finance"
    HR = "HR & People"
    LEGAL = "Legal & Compliance"
    SUPPORT = "Customer Support"
    OPERATIONS = "Operations"
    MANUAL_REVIEW = "Manual Review"


class PriorityEnum(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class ExtractionStatusEnum(str, Enum):
    COMPLETED = "Completed"
    NEEDS_REVIEW = "Needs Review"
    REJECTED = "Rejected"


class ValidationStatusEnum(str, Enum):
    AUTO_ROUTED = "Auto-Routed"
    PENDING_VALIDATION = "Pending Validation"
    APPROVED = "Approved"
    OVERRIDDEN = "Approved (Overridden)"
    REJECTED = "Rejected"


TEAM_QUEUE_CHANNELS: dict[TeamEnum, str] = {
    TeamEnum.ENGINEERING: "#eng-triage",
    TeamEnum.FINANCE: "#ap-finance",
    TeamEnum.HR: "#people-ops",
    TeamEnum.LEGAL: "#legal-review",
    TeamEnum.SUPPORT: "#cx-escalations",
    TeamEnum.OPERATIONS: "#ops-desk",
    TeamEnum.MANUAL_REVIEW: "#workflow-exceptions",
}


class DocumentInput(BaseModel):
    doc_id: str = Field(..., description="Unique document identifier, e.g. DOC-301")
    title: str = Field(..., description="Document title")
    doc_type: str = Field(default="Operational Document", description="Document category")
    content: str = Field(..., description="Raw document text body")
    confidence_threshold: float = Field(default=0.70, ge=0.0, le=1.0, description="Minimum confidence before Manual Review")
    model_name: str = Field(default="llama3.2", description="Local Ollama model name")
    submitted_at: str = Field(default_factory=_utc_now_iso)


class ActionItem(BaseModel):
    item_id: str = Field(..., description="Unique extracted action item ID, e.g. ACT-301-1")
    title: str = Field(..., description="Concise actionable task description")
    owner_role: Optional[str] = Field(default=None, description="Mentioned person or role")
    target_team: TeamEnum = Field(..., description="Approved destination team")
    queue_channel: str = Field(..., description="Simulated team Slack/queue channel")
    priority: PriorityEnum = Field(default=PriorityEnum.MEDIUM)
    due_date: Optional[str] = Field(default=None, description="Extracted deadline if present")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Extraction & routing confidence")
    source_quote: str = Field(..., description="Verbatim quote from source document")
    quote_verified: bool = Field(default=False, description="True if source_quote matches source text")
    requires_manual_review: bool = Field(default=False)
    review_reason: Optional[str] = Field(default=None)
    validation_status: ValidationStatusEnum = Field(default=ValidationStatusEnum.PENDING_VALIDATION)


class WorkflowResult(BaseModel):
    doc_id: str
    title: str
    extraction_status: ExtractionStatusEnum
    document_summary: str = Field(..., description="Short summary of document & routing outcome")
    action_items: list[ActionItem] = Field(default_factory=list)
    rejection_reason: Optional[str] = Field(default=None)
    processed_at: str = Field(default_factory=_utc_now_iso)


class ValidationSubmission(BaseModel):
    doc_id: str
    item_id: str
    reviewer_name: str = Field(default="Ops_Coordinator_01")
    action: ValidationStatusEnum
    override_title: Optional[str] = None
    override_team: Optional[TeamEnum] = None
    override_priority: Optional[PriorityEnum] = None
    override_due_date: Optional[str] = None
    review_notes: Optional[str] = None
    reviewed_at: str = Field(default_factory=_utc_now_iso)
