"""Pydantic V2 Domain Models for AI Customer Support Copilot (FR-01, FR-03, FR-05, FR-06).

Defines strict validated schemas for:
- Inbound customer tickets
- Triage classification (Sentiment, Category, Urgency, Escalation)
- AI Grounded Draft responses with policy citations
- Human-in-the-Loop (HITL) review states and audit logs
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class SentimentEnum(str, Enum):
    POSITIVE = "Positive"
    NEUTRAL = "Neutral"
    FRUSTRATED = "Frustrated"
    ANGRY = "Angry"


class CategoryEnum(str, Enum):
    BILLING = "Billing"
    TECHNICAL = "Technical Support"
    SECURITY = "Account Security"
    SHIPPING = "Shipping & Delivery"
    CANCELLATION = "Cancellation"
    OTHER = "Other / Uncategorized"


class UrgencyEnum(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class ReviewStatusEnum(str, Enum):
    PENDING = "Pending Review"
    APPROVED_AS_IS = "Approved (As-Is)"
    APPROVED_EDITED = "Approved (Edited)"
    REJECTED = "Rejected"
    ESCALATED = "Escalated to Supervisor"


# --- Ticket Input Schema ---
class CustomerTicket(BaseModel):
    ticket_id: str = Field(..., description="Unique ticket identifier, e.g. TCK-101")
    customer_name: str = Field(..., description="Customer full name")
    customer_tier: str = Field(default="Standard", description="Customer subscription tier (Free, Pro, Enterprise)")
    subject: str = Field(..., description="Ticket subject line")
    message: str = Field(..., description="Full customer inquiry body")
    created_at: Optional[str] = Field(default_factory=lambda: datetime.utcnow().isoformat())


# --- Triage Classification Schema ---
class TriageClassification(BaseModel):
    sentiment: SentimentEnum = Field(..., description="Customer emotional sentiment")
    category: CategoryEnum = Field(..., description="Primary support domain")
    urgency: UrgencyEnum = Field(..., description="Resolution priority")
    key_issues: list[str] = Field(default_factory=list, description="Extracted bullet points of customer concerns")
    escalate_to_human: bool = Field(
        default=False,
        description="True if inquiry involves legal threats, chargebacks, or refunds > $100"
    )
    escalation_reason: Optional[str] = Field(
        default=None,
        description="Explanation if escalation is required"
    )


# --- Citation Schema ---
class PolicyCitation(BaseModel):
    policy_name: str = Field(..., description="Approved document name")
    section: str = Field(..., description="Policy section header")
    rule_applied: str = Field(..., description="Summary of the specific rule used")


# --- Copilot Draft Response Schema ---
class CopilotDraftResponse(BaseModel):
    ticket_id: str
    triage: TriageClassification
    draft_reply: str = Field(..., description="Empathetic, customer-facing grounded response")
    internal_notes: str = Field(..., description="Reasoning and guidance for the human agent")
    citations: list[PolicyCitation] = Field(default_factory=list, description="Referenced policy sections")
    requires_supervisor_approval: bool = Field(default=False)


# --- Human-in-the-Loop Review Schema ---
class ReviewSubmission(BaseModel):
    ticket_id: str
    reviewer_name: str = Field(default="Agent_01", description="Support agent handling the ticket")
    action: ReviewStatusEnum = Field(..., description="Approval decision")
    final_reply: str = Field(..., description="Final text sent to customer (original or edited)")
    review_notes: Optional[str] = Field(default=None, description="Optional agent feedback or audit notes")
    reviewed_at: Optional[str] = Field(default_factory=lambda: datetime.utcnow().isoformat())
