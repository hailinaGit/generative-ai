"""10-Query Benchmark Evaluation Script for Cambodia HR RAG Assistant.

Runs Q01–Q10 from `docs/eval_results.md` through `generate_answer` (ChromaDB + Ollama)
and computes the real achieved scores for:
- Grounding & Key Fact Accuracy (%)
- Citation Completeness (%)
- Fallback Trigger Accuracy (%)
- Hallucination Rate (%)

Usage:
    python tests/evaluate_rag.py
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal, TypedDict

PROJECT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from generate import generate_answer


class BenchmarkQuery(TypedDict):
    id: str
    query: str
    expected_keywords: list[str]
    expected_section: str | None
    out_of_scope: bool | Literal["partial"]


BENCHMARK_QUERIES: list[BenchmarkQuery] = [
    {
        "id": "Q01",
        "query": "How many days of annual leave do standard workers receive in Cambodia?",
        "expected_keywords": ["18"],
        "expected_section": "2. Leave & Time-Off Policies",
        "out_of_scope": False,
    },
    {
        "id": "Q02",
        "query": "What is the compensation rate for nighttime overtime or working on Sundays?",
        "expected_keywords": ["200%"],
        "expected_section": "1. Employment & Working Conditions",
        "out_of_scope": False,
    },
    {
        "id": "Q03",
        "query": "What are the overtime pay rates on official public holidays?",
        "expected_keywords": ["250%"],
        "expected_section": "1. Employment & Working Conditions",
        "out_of_scope": False,
    },
    {
        "id": "Q04",
        "query": "What is the maximum duration and pay structure for maternity leave?",
        "expected_keywords": ["90", "50%"],
        "expected_section": "2. Leave & Time-Off Policies",
        "out_of_scope": False,
    },
    {
        "id": "Q05",
        "query": "How often must employee salaries be disbursed in Cambodia?",
        "expected_keywords": ["twice", "50%"],
        "expected_section": "3. Compensation & Benefits",
        "out_of_scope": False,
    },
    {
        "id": "Q06",
        "query": "What is the schedule for mandatory Seniority Pay for UDC contracts?",
        "expected_keywords": ["June", "December", "7.5"],
        "expected_section": "3. Compensation & Benefits",
        "out_of_scope": False,
    },
    {
        "id": "Q07",
        "query": "What is the progressive disciplinary pathway before contract termination?",
        "expected_keywords": ["Verbal", "Written", "suspension"],
        "expected_section": "4. Workplace Discipline & Code of Conduct",
        "out_of_scope": False,
    },
    {
        "id": "Q08",
        "query": "What are the probationary limits for regular vs. non-skilled workers?",
        "expected_keywords": ["3 months", "1 month"],
        "expected_section": "1. Employment & Working Conditions",
        "out_of_scope": False,
    },
    {
        "id": "Q09",
        "query": "What is the 401(k) company matching percentage in California?",
        "expected_keywords": ["I cannot find this information in the approved policy documents"],
        "expected_section": None,
        "out_of_scope": True,
    },
    {
        "id": "Q10",
        "query": "Can an employee take 4 weeks of paid paternity leave?",
        "expected_keywords": ["cannot find", "7 days", "Special Leave"],
        "expected_section": "2. Leave & Time-Off Policies",
        "out_of_scope": "partial",
    },
]


def run_evaluation() -> None:
    db_dir = str(PROJECT_DIR / "chroma_db")
    total = len(BENCHMARK_QUERIES)
    grounded_pass = 0
    citation_pass = 0
    fallback_total = 0
    fallback_pass = 0
    hallucinations = 0

    print("=" * 72)
    print("Evaluating 10 Benchmark Queries for Cambodia HR RAG Assistant")
    print("=" * 72)

    for item in BENCHMARK_QUERIES:
        qid = item["id"]
        res = generate_answer(query=item["query"], top_k=3, temperature=0.0, db_dir=db_dir)
        answer_lower = res["answer"].lower()
        citations = res["citations"]

        if item["out_of_scope"] is True:
            fallback_total += 1
            triggered = "i cannot find this information in the approved policy documents" in answer_lower
            if triggered:
                fallback_pass += 1
                grounded_pass += 1
            else:
                hallucinations += 1
            status = "PASS" if triggered else "FAIL"
            print(f"[{qid}] Out-of-Scope Fallback: {status} | Answer: {res['answer'][:70]}...")
        elif item["out_of_scope"] == "partial":
            fallback_total += 1
            # Should clarify no paternity leave provision exists (or mention 7-day Special Leave), never approve 4 weeks
            safe = (
                "cannot find" in answer_lower
                or "no specific provision" in answer_lower
                or "7 days" in answer_lower
                or "special leave" in answer_lower
            ) and "yes, an employee can take 4 weeks" not in answer_lower
            if safe:
                fallback_pass += 1
                grounded_pass += 1
            else:
                hallucinations += 1
            if citations:
                citation_pass += 1
            status = "PASS" if safe else "FAIL"
            print(f"[{qid}] Policy Gap Safety   : {status} | Citations: {len(citations)}")
        else:
            # Factual in-scope query
            facts_ok = all(kw.lower() in answer_lower for kw in item["expected_keywords"])
            expected_section = item["expected_section"]
            sec_ok = expected_section is not None and any(expected_section in c["section"] for c in citations)
            if facts_ok:
                grounded_pass += 1
            else:
                hallucinations += 1
            if citations and sec_ok:
                citation_pass += 1
            status = "PASS" if (facts_ok and sec_ok) else "WARN"
            print(f"[{qid}] Facts: {'OK' if facts_ok else 'MISS'} | Section Cited: {'OK' if sec_ok else 'MISS'} | Status: {status}")

    in_scope_count = sum(1 for q in BENCHMARK_QUERIES if q["out_of_scope"] is not True)
    print("\n" + "=" * 72)
    print("ACHIEVED BENCHMARK SCORES (PROJECT 1)")
    print("=" * 72)
    print(f"Grounding & Faithfulness    : {grounded_pass}/{total} ({grounded_pass / total * 100:.1f}%)")
    print(f"Hallucination Rate          : {hallucinations}/{total} ({hallucinations / total * 100:.1f}%)")
    print(f"Citation Completeness       : {citation_pass}/{in_scope_count} ({citation_pass / in_scope_count * 100:.1f}%)")
    print(f"Fallback & Safety Accuracy  : {fallback_pass}/{fallback_total} ({fallback_pass / fallback_total * 100:.1f}%)")
    print("=" * 72)


if __name__ == "__main__":
    run_evaluation()
