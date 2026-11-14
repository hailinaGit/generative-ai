# Evaluation & Verification Report: AI Customer Support Copilot

**Project:** Project 2 — AI Customer Support Copilot  
**Domain:** Enterprise Customer Support Triage, Grounded Drafting & Human-in-the-Loop Review  
**Evaluation Standard:** Handbook Acceptance Criteria & Rubric (FR-01 to FR-06)  
**Model Evaluated:** Local Ollama (`llama3.2`, temperature `0.0`)  

---

## 1. Executive Summary & Observed Benchmark Scores

To satisfy the handbook requirements for **Quality, Accuracy & Validation (20 points)** and **Evidence-Based Delivery**, this report records the live execution of `python tests/evaluate_benchmark.py` across all **12 realistic customer support tickets** (`data/sample_tickets/benchmark_tickets.json`).

### Success Thresholds vs. Observed Achieved Results

| Metric | Target Standard | Achieved Score | Status |
| :--- | :---: | :---: | :---: |
| **Structured Output Schema Compliance** | **$100\%$** | **$100.0\%$ (12/12)** | **PASS** |
| **Category Classification Accuracy** | $\ge 90\%$ | **$91.7\%$ (11/12)** | **PASS** |
| **Urgency Classification Accuracy** | $\ge 75\%$ | **$75.0\%$ (9/12)** | **PASS** |
| **Escalation Trigger Accuracy** | **$100\%$** | **$100.0\%$ (12/12)** | **PASS** |
| **Grounding & Citation Compliance** | $\ge 95\%$ | **$100.0\%$ (12/12)** | **PASS** |

---

## 2. Before vs. After Prompt & Guardrail Optimization (Handbook Sec. 17)

During initial testing, the 3B local model (`llama3.2`) was overly conservative and falsely escalated routine high-urgency tickets (`TCK-101`, `TCK-102`, `TCK-103`, `TCK-108`, `TCK-111`), resulting in **58.3%** escalation accuracy.

By refining `TRIAGE_SYSTEM_PROMPT` and making `_check_deterministic_escalation` authoritative for policy thresholds (legal threats, security breaches, and refunds $> \$100$), we achieved measurable improvements:

| Metric | Baseline (Before) | Refined (After) | Improvement |
| :--- | :---: | :---: | :---: |
| **Category Accuracy** | 83.3% (10/12) | **91.7% (11/12)** | **+8.4%** |
| **Escalation Trigger Accuracy** | 58.3% (7/12) | **100.0% (12/12)** | **+41.7%** |
| **Schema & Grounding Compliance** | 100.0% (12/12) | **100.0% (12/12)** | Maintained |

---

## 3. 12-Ticket Live Benchmark Matrix

Observed output from `python tests/evaluate_benchmark.py`:

| Ticket ID | Customer & Tier | Ground Truth (Category / Urgency / Escalate) | Predicted (Category / Urgency / Escalate) | Policy Section Cited | Match Summary |
| :---: | :--- | :--- | :--- | :--- | :---: |
| **TCK-101** | Sarah Jenkins (`Pro`) | `Billing` / `High` / `False` | `Billing` / `High` / `False` | `1. Refund & Billing Policy` | **Exact Match** |
| **TCK-102** | Michael Chang (`Enterprise`) | `Account Security` / `High` / `False` | `Technical Support` / `Medium` / `False` | `2. Account Security & Access Recovery` | Category/Urgency mismatch (Escalation OK) |
| **TCK-103** | David Ross (`Free`) | `Shipping & Delivery` / `High` / `False` | `Shipping & Delivery` / `High` / `False` | `3. Shipping, Delivery & Missing Orders` | **Exact Match** |
| **TCK-104** | Elena Rostova (`Enterprise`) | `Billing` / `Critical` / `True` | `Billing` / `Critical` / `True` | `1. Refund & Billing Policy` | **Exact Match** |
| **TCK-105** | Liam Scott (`Standard`) | `Cancellation` / `Low` / `False` | `Cancellation` / `Low` / `False` | `4. Subscription Cancellation & Downgrades` | **Exact Match** |
| **TCK-106** | Karen Vance (`Pro`) | `Other` / `Low` / `False` | `Other / Uncategorized` / `Low` / `False` | `5. Tone Guidelines & Safety Controls` | **Exact Match** |
| **TCK-107** | Marcus Vance (`Enterprise`) | `Account Security` / `Critical` / `True` | `Account Security` / `Critical` / `True` | `2. Account Security & Access Recovery` | **Exact Match** |
| **TCK-108** | Chloe Dubois (`Standard`) | `Shipping & Delivery` / `Medium` / `False` | `Shipping & Delivery` / `High` / `False` | `3. Shipping, Delivery & Missing Orders` | Urgency mismatch (Category/Esc OK) |
| **TCK-109** | Jonathan Reed (`Pro`) | `Billing` / `High` / `True` | `Billing` / `Low` / `True` | `1. Refund & Billing Policy` | Urgency mismatch (Category/Esc OK) |
| **TCK-110** | Samantha Miller (`Free`) | `Cancellation` / `Low` / `False` | `Cancellation` / `Low` / `False` | `4. Subscription Cancellation & Downgrades` | **Exact Match** |
| **TCK-111** | Alex Mercer (`Enterprise`) | `Technical Support` / `High` / `False` | `Technical Support` / `High` / `False` | `5. Tone Guidelines & Safety Controls` | **Exact Match** |
| **TCK-112** | Robert O'Connor (`Standard`) | `Billing` / `Low` / `False` | `Billing` / `Low` / `False` | `1. Refund & Billing Policy` | **Exact Match** |

---

## 4. Reproducible Verification Commands

1. **Deterministic Unit Tests (`< 1 sec`, no LLM required):**
   ```bash
   python tests/test_copilot.py
   ```
2. **Full 12-Ticket LLM Benchmark (`llama3.2` via Ollama):**
   ```bash
   python tests/evaluate_benchmark.py
   ```
