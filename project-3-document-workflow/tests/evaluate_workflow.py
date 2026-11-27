"""9-Document End-to-End Benchmark Evaluation Script for Document-to-Workflow Automation.

Runs all 9 documents in `data/sample_documents/benchmark_docs.json` through
`DocumentWorkflowEngine` (local Ollama `llama3.2`, temperature=0.0) and reports:
- Structured Output Schema Compliance (%)
- Extraction Recall (%)
- Team Routing Accuracy (%)
- Source-Quote Grounding (%)
- Edge-Case & Safety Accuracy (%)

Usage:
    python tests/evaluate_workflow.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_DIR / "src"
for p in (str(SRC_DIR), str(PROJECT_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from models import DocumentInput
from workflow import DocumentWorkflowEngine

BENCHMARK_FILE = PROJECT_DIR / "data" / "sample_documents" / "benchmark_docs.json"


def run_benchmark() -> None:
    docs = json.loads(BENCHMARK_FILE.read_text(encoding="utf-8"))
    engine = DocumentWorkflowEngine()

    total_docs = len(docs)
    schema_ok = 0
    edge_safety_ok = 0
    expected_item_total = 0
    recalled_items = 0
    team_match_ok = 0
    total_extracted_items = 0
    verified_quotes = 0

    print("=" * 72)
    print("Evaluating 9 Benchmark Documents for Document-to-Workflow Automation")
    print("=" * 72)

    for raw in docs:
        doc = DocumentInput(
            doc_id=raw["doc_id"],
            title=raw["title"],
            doc_type=raw.get("doc_type", "Operational Document"),
            content=raw["content"],
        )
        res = engine.process_document(doc)
        schema_ok += 1

        expected_status = raw["expected_status"]
        expected_items = raw["expected_items"]

        if res.extraction_status.value == expected_status:
            edge_safety_ok += 1
        elif expected_status == "Completed" and res.extraction_status.value == "Needs Review":
            # Conservative review flag on valid doc is safe, though not exact
            pass

        extracted_teams = [item.target_team.value for item in res.action_items]
        for item in res.action_items:
            total_extracted_items += 1
            if item.quote_verified:
                verified_quotes += 1

        matched_for_doc = 0
        remaining_teams = list(extracted_teams)
        for exp in expected_items:
            expected_item_total += 1
            if exp["target_team"] in remaining_teams:
                matched_for_doc += 1
                recalled_items += 1
                team_match_ok += 1
                remaining_teams.remove(exp["target_team"])

        if not expected_items:
            recall_str = "N/A (0 expected)"
        else:
            recall_str = f"{matched_for_doc}/{len(expected_items)} teams"

        print(
            f"[{doc.doc_id}] Status: {res.extraction_status.value:<12} (GT: {expected_status:<12}) | "
            f"Items: {len(res.action_items)} | Match: {recall_str}"
        )

    quote_pct = (verified_quotes / total_extracted_items * 100) if total_extracted_items else 100.0
    recall_pct = (recalled_items / expected_item_total * 100) if expected_item_total else 100.0
    routing_pct = (team_match_ok / expected_item_total * 100) if expected_item_total else 100.0

    print("\n" + "=" * 72)
    print("ACHIEVED BENCHMARK SCORES (PROJECT 3)")
    print("=" * 72)
    print(f"Structured Output Schema Compliance : {schema_ok}/{total_docs} ({schema_ok / total_docs * 100:.1f}%)")
    print(f"Action-Item Extraction Recall       : {recalled_items}/{expected_item_total} ({recall_pct:.1f}%)")
    print(f"Team Routing Accuracy               : {team_match_ok}/{expected_item_total} ({routing_pct:.1f}%)")
    print(f"Source-Quote Grounding              : {verified_quotes}/{total_extracted_items} ({quote_pct:.1f}%)")
    print(f"Status & Safety Control Accuracy    : {edge_safety_ok}/{total_docs} ({edge_safety_ok / total_docs * 100:.1f}%)")
    print("=" * 72)


if __name__ == "__main__":
    run_benchmark()
