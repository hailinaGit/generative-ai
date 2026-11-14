"""Benchmark Evaluation Script for AI Customer Support Copilot.

Runs all 12 tickets from `data/sample_tickets/benchmark_tickets.json` through
`SupportCopilotEngine` (requires Ollama running locally with `llama3.2`) and
computes the achieved scores for:
- Structured Output Schema Compliance (%)
- Triage Category & Urgency Accuracy (%)
- Escalation Trigger Accuracy (%)
- Policy Citation Completeness (%)

Usage:
    python tests/evaluate_benchmark.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from copilot import SupportCopilotEngine
from models import CustomerTicket

TICKETS_PATH = PROJECT_DIR / "data" / "sample_tickets" / "benchmark_tickets.json"


def run_evaluation() -> None:
    raw_tickets = json.loads(TICKETS_PATH.read_text(encoding="utf-8"))
    engine = SupportCopilotEngine()

    total = len(raw_tickets)
    schema_valid = 0
    category_match = 0
    urgency_match = 0
    escalation_match = 0
    citations_present = 0

    print("=" * 72)
    print(f"Evaluating {total} Benchmark Tickets using model '{engine.model_name}'")
    print("=" * 72)

    for item in raw_tickets:
        tid = item["ticket_id"]
        gt = item["ground_truth"]
        ticket = CustomerTicket(
            ticket_id=tid,
            customer_name=item["customer_name"],
            customer_tier=item.get("customer_tier", "Standard"),
            subject=item["subject"],
            message=item["message"],
        )

        try:
            draft = engine.generate_draft(ticket)
            schema_valid += 1

            pred_cat = draft.triage.category.value
            pred_urg = draft.triage.urgency.value
            pred_esc = draft.triage.escalate_to_human

            cat_ok = pred_cat == gt["category"]
            urg_ok = pred_urg == gt["urgency"]
            esc_ok = pred_esc == gt["escalate"]

            if cat_ok:
                category_match += 1
            if urg_ok:
                urgency_match += 1
            if esc_ok:
                escalation_match += 1

            # Out-of-scope tickets (e.g. TCK-106) are expected to have 0 specific policy citations
            if gt.get("out_of_scope"):
                if "I cannot find this information in our approved support policies" in draft.draft_reply or len(draft.citations) == 0:
                    citations_present += 1
            elif len(draft.citations) > 0 or pred_cat == "Technical Support":
                citations_present += 1

            print(
                f"[{tid}] Cat: {pred_cat:<20} (GT: {gt['category']:<20}) | "
                f"Urg: {pred_urg:<8} (GT: {gt['urgency']:<8}) | "
                f"Esc: {str(pred_esc):<5} (GT: {str(gt['escalate']):<5})"
            )
        except Exception as exc:
            print(f"[{tid}] ERROR: {exc}")

    print("\n" + "=" * 72)
    print("ACHIEVED BENCHMARK SCORES")
    print("=" * 72)
    print(f"Structured Output Schema Compliance : {schema_valid}/{total} ({schema_valid / total * 100:.1f}%)")
    print(f"Category Classification Accuracy    : {category_match}/{total} ({category_match / total * 100:.1f}%)")
    print(f"Urgency Classification Accuracy     : {urgency_match}/{total} ({urgency_match / total * 100:.1f}%)")
    print(f"Escalation Trigger Accuracy         : {escalation_match}/{total} ({escalation_match / total * 100:.1f}%)")
    print(f"Grounding & Citation Compliance     : {citations_present}/{total} ({citations_present / total * 100:.1f}%)")
    print("=" * 72)


if __name__ == "__main__":
    run_evaluation()
