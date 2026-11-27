"""Deterministic Test Suite for Document-to-Workflow Automation (FR-01 to FR-06).

Validates schemas, routing directory loading, empty/invalid input rejection,
verbatim quote verification, low-confidence routing, and Legal/Finance guardrails
without requiring a live LLM call.

Usage:
    python tests/test_workflow.py
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_DIR / "src"
for p in (str(SRC_DIR), str(PROJECT_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from models import (
    TEAM_QUEUE_CHANNELS,
    DocumentInput,
    ExtractionStatusEnum,
    PriorityEnum,
    TeamEnum,
    ValidationStatusEnum,
)
from workflow import DocumentWorkflowEngine, verify_source_quote


def test_schemas_and_directory() -> None:
    engine = DocumentWorkflowEngine()
    assert engine.directory.section_count >= 7, "Expected >= 7 routing sections in team_directory.md"
    assert TEAM_QUEUE_CHANNELS[TeamEnum.ENGINEERING] == "#eng-triage"
    assert TEAM_QUEUE_CHANNELS[TeamEnum.MANUAL_REVIEW] == "#workflow-exceptions"
    print("✓ FR-01 & FR-02 (Schemas & Routing Directory): Loaded and validated.")


def test_empty_input_rejection() -> None:
    engine = DocumentWorkflowEngine()
    res = engine.process_document(DocumentInput(doc_id="TEST-EMPTY", title="Empty", content="   \n  "))
    assert res.extraction_status == ExtractionStatusEnum.REJECTED
    assert res.rejection_reason is not None
    assert res.action_items == []
    print("✓ FR-01 & FR-04 (Edge Case): Empty/whitespace document safely rejected.")


def test_quote_verification_and_low_confidence() -> None:
    engine = DocumentWorkflowEngine()
    doc = DocumentInput(
        doc_id="TEST-CONF",
        title="Ambiguous Note",
        content="Maybe someone should look into that thing we talked about last Tuesday.",
    )
    items = engine.apply_routing_guardrails(
        doc,
        [
            {
                "title": "Follow up on Tuesday topic",
                "target_team": "Operations",
                "priority": "Low",
                "confidence": 0.55,
                "source_quote": "look into that thing we talked about last Tuesday",
            },
            {
                "title": "Hallucinated task",
                "target_team": "Engineering",
                "priority": "High",
                "confidence": 0.92,
                "source_quote": "Restart production Kubernetes cluster immediately",
            },
        ],
    )
    assert len(items) == 2
    # Low confidence -> Manual Review
    assert items[0].target_team == TeamEnum.MANUAL_REVIEW
    assert items[0].requires_manual_review is True
    assert items[0].quote_verified is True
    # Ungrounded quote -> downgraded confidence & routed to Manual Review
    assert items[1].quote_verified is False
    assert items[1].confidence <= 0.65
    assert items[1].target_team == TeamEnum.MANUAL_REVIEW
    assert items[1].requires_manual_review is True
    print("✓ FR-04 (Quote & Confidence Guardrails): Low-confidence & ungrounded items routed to Manual Review.")


def test_finance_and_legal_guardrails() -> None:
    engine = DocumentWorkflowEngine()
    doc = DocumentInput(
        doc_id="TEST-ESC",
        title="PO & NDA",
        content="Wire $12,500.00 USD for PO-9920 and have Legal review the Mutual NDA.",
    )
    items = engine.apply_routing_guardrails(
        doc,
        [
            {
                "title": "Wire $12,500.00 USD for PO-9920",
                "target_team": "Finance",
                "priority": "High",
                "confidence": 0.96,
                "source_quote": "Wire $12,500.00 USD for PO-9920",
            },
            {
                "title": "Review Mutual NDA",
                "target_team": "Legal & Compliance",
                "priority": "High",
                "confidence": 0.94,
                "source_quote": "have Legal review the Mutual NDA",
            },
        ],
    )
    assert items[0].target_team == TeamEnum.FINANCE
    assert items[0].requires_manual_review is True
    assert items[0].validation_status == ValidationStatusEnum.PENDING_VALIDATION
    assert items[1].target_team == TeamEnum.LEGAL
    assert items[1].requires_manual_review is True
    assert verify_source_quote("Wire $12,500.00 USD", doc.content) is True
    print("✓ FR-04 (Policy Thresholds): >$5,000 Finance & Legal & Compliance items flagged for manual validation.")


def main() -> None:
    print("=" * 64)
    print("Running Document-to-Workflow Automation Test Suite")
    print("=" * 64)
    test_schemas_and_directory()
    test_empty_input_rejection()
    test_quote_verification_and_low_confidence()
    test_finance_and_legal_guardrails()
    print("=" * 64)
    print("All deterministic tests passed successfully! (100% compliance)")
    print("=" * 64)


if __name__ == "__main__":
    main()
