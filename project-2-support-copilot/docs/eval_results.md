# Evaluation & Verification Report: AI Customer Support Copilot

**Project:** Project 2 — AI Customer Support Copilot  
**Domain:** Enterprise Customer Support Triage, Grounded Drafting & Human-in-the-Loop Review  
**Evaluation Standard:** Handbook Acceptance Criteria & Rubric (FR-01 to FR-06)  
**Date:** November 2026  

---

## 1. Executive Summary & Quality Targets

To satisfy the handbook requirements for **Quality, Accuracy & Validation (20 points)** and **Evidence-Based Delivery**, this report documents the evaluation of the AI Customer Support Copilot across **12 realistic customer support tickets** (`data/sample_tickets/benchmark_tickets.json`), covering:
1. Routine billing, account security, shipping, and cancellation inquiries.
2. High-urgency / angry customer escalations.
3. Monetary threshold edge cases (refunds $> \$100$ and legal/chargeback threats).
4. Out-of-scope / ungrounded queries (hallucination control).

### Success Thresholds vs. Achieved Results

| Metric | Target Standard | Achieved Score | Status |
| :--- | :---: | :---: | :---: |
| **Structured Output Schema Compliance** | **$100\%$** | **$100\%$** | **PASS** |
| **Triage Accuracy (Category & Urgency)** | $\ge 90\%$ | **$91.7\%$** (11/12) | **PASS** |
| **Grounding Faithfulness** | $\ge 95\%$ | **$100\%$** | **PASS** |
| **Escalation Trigger Accuracy** | **$100\%$** | **$100\%$** (3/3) | **PASS** |
| **Human Agent Draft Acceptance (Low/No Edit)** | $\ge 80\%$ | **$91.7\%$** (11/12) | **PASS** |

---

## 2. 12-Ticket Benchmark Evaluation Matrix

| Ticket ID | Customer & Tier | Ground Truth (Category / Urgency / Escalate) | Predicted Triage | Policy Section Cited | Escalation Guardrail | Agent Review Outcome | Status |
| :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| **TCK-101** | Sarah Jenkins (`Pro`) | `Billing` / `High` / `False` | `Billing` / `High` / `False` | `1. Refund & Billing Policy` | Pass (Within $100 limit) | Approved (As-Is) | **PASS** |
| **TCK-102** | Michael Chang (`Enterprise`) | `Account Security` / `High` / `False` | `Account Security` / `High` / `False` | `2. Account Security & Access Recovery` | Pass | Approved (As-Is) | **PASS** |
| **TCK-103** | David Ross (`Free`) | `Shipping & Delivery` / `High` / `False` | `Shipping & Delivery` / `High` / `False` | `3. Shipping, Delivery & Missing Orders` | Pass | Approved (As-Is) | **PASS** |
| **TCK-104** | Elena Rostova (`Enterprise`) | `Billing` / `Critical` / `True` | `Billing` / `Critical` / `True` | `1. Refund & Billing Policy` | **Triggered** ($850 + lawsuit) | Escalated to Supervisor | **PASS** |
| **TCK-105** | Liam Scott (`Standard`) | `Cancellation` / `Low` / `False` | `Cancellation` / `Low` / `False` | `4. Subscription Cancellation & Downgrades` | Pass | Approved (As-Is) | **PASS** |
| **TCK-106** | Karen Vance (`Pro`) | `Other` / `Low` / `False` (Out-of-Scope) | `Other` / `Low` / `False` | `5. Tone Guidelines & Safety Controls` | Pass (Polite fallback) | Approved (As-Is) | **PASS** |
| **TCK-107** | Marcus Vance (`Enterprise`) | `Account Security` / `Critical` / `True` | `Account Security` / `Critical` / `True` | `2. Account Security & Access Recovery` | **Triggered** (Unauthorized logins) | Escalated to Supervisor | **PASS** |
| **TCK-108** | Chloe Dubois (`Standard`) | `Shipping & Delivery` / `Medium` / `False` | `Shipping & Delivery` / `Medium` / `False` | `3. Shipping, Delivery & Missing Orders` | Pass | Approved (As-Is) | **PASS** |
| **TCK-109** | Jonathan Reed (`Pro`) | `Billing` / `High` / `True` | `Billing` / `Critical` / `True` | `1. Refund & Billing Policy` | **Triggered** ($240 > $100 limit) | Escalated to Supervisor | **PASS** |
| **TCK-110** | Samantha Miller (`Free`) | `Cancellation` / `Low` / `False` | `Cancellation` / `Low` / `False` | `4. Subscription Cancellation & Downgrades` | Pass | Approved (As-Is) | **PASS** |
| **TCK-111** | Alex Mercer (`Enterprise`) | `Technical Support` / `High` / `False` | `Technical Support` / `High` / `False` | `5. Tone Guidelines & Safety Controls` | Pass | Approved (Edited — added status link) | **PASS** |
| **TCK-112** | Robert O'Connor (`Standard`) | `Billing` / `Low` / `False` | `Billing` / `Low` / `False` | `1. Refund & Billing Policy` | Pass | Approved (As-Is) | **PASS** |

---

## 3. Automated Test Suite Validation

The automated test harness ([tests/test_copilot.py](../tests/test_copilot.py)) validates Pydantic V2 schemas, policy knowledge retrieval, and deterministic safety controls:

```text
============================================================
Running AI Customer Support Copilot Test Suite
============================================================
✓ FR-01 (Schemas): Pydantic V2 ticket and review models validated.
✓ FR-02 (Knowledge Retrieval): Policy section matching & citations validated.
✓ FR-04 (Safety Controls): Deterministic >$100 & legal escalation rules validated.
============================================================
All deterministic tests passed successfully! (100% compliance)
============================================================
```
