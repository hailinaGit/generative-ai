# Project Requirements & Scope Document: AI Customer Support Copilot

**Project Type:** Intermediate Real-World Task (Arrowstack 1-Month Generative AI Internship, Week 2)  
**Project Folder:** `project-2-support-copilot`  
**Git Branch:** `project-2/support-copilot`  
**Author:** hailinaGit  

---

## 1. Executive Summary & Business Use Case

* **Primary Stakeholder:** Frontline Customer Support Agents, Support Team Leads, and Customer Experience (CX) QA Officers.
* **The Business Problem:** Customer support teams in high-growth companies receive hundreds of inbound inquiries daily across billing, delivery, technical troubleshooting, and account security. Human agents spend excessive time manually parsing ticket context, cross-referencing internal policy documents, and typing repetitive replies from scratch, while fully autonomous bots frequently hallucinate or promise unauthorized refunds.
* **The Solution:** An **AI Customer Support Copilot** that:
  1. Ingests raw ticket text and extracts structured triage data (Sentiment, Urgency, Category).
  2. Retrieves relevant sections from an approved internal knowledge base.
  3. Synthesizes an empathetic, grounded draft reply along with internal reasoning notes.
  4. Provides a **Human-in-the-Loop (HITL) review flow** where human agents inspect, modify, and officially approve the reply before sending.
* **Measurable Benefits:**
  * **First Response Time (FRT):** Reduced by $\ge 60\%$ (agents verify and dispatch grounded replies in under 60 seconds instead of 5–10 minutes).
  * **Draft Edit Distance:** $\ge 80\%$ of AI-generated responses accepted by human agents with minor or no modifications.
  * **Policy Adherence:** $100\%$ compliance with official refund and privacy guidelines.

---

## 2. Problem Statement: Inputs, Outputs & Constraints

* **Inputs:**
  * Inbound customer support ticket (`ticket_id`, `customer_name`, `subscription_tier`, `subject`, `message_body`).
  * Approved internal knowledge base (`data/knowledge_base/support_policies.md`).
* **Outputs:**
  * Validated Pydantic V2 triage JSON (`sentiment`, `category`, `urgency`, `escalate_to_human`, `escalation_reason`).
  * Grounded customer-facing draft reply, internal reasoning notes, and policy section citations.
  * HITL review audit record (`approved_as_is` vs. `edited`, reviewer notes, timestamp).
* **Key Constraints:**
  * **100% Offline / Local Execution:** Runs locally via Ollama (`llama3.2`, temperature `0.0`) with zero external API cost and zero data privacy risk.
  * **Strict Safety & Escalation Controls:** Refund claims $> \$100$, legal threats, and account security breaches must deterministically trigger `escalate_to_human: true`.

---

## 3. Scope Boundaries

### In-Scope (Project 2 Deliverables)
1. **Ticket Ingestion & Parsing:** Extracting customer metadata (Ticket ID, customer name, subscription tier, subject, message body).
2. **Multi-Task Prompting & Structured Output Validation:**
   - Sentiment classification: `Positive`, `Neutral`, `Frustrated`, `Angry`.
   - Category tagging: `Billing`, `Technical Support`, `Account Security`, `Shipping & Delivery`, `Cancellation`.
   - Urgency rating: `Low`, `Medium`, `High`, `Critical`.
   - Strict JSON / Pydantic schema validation for every generated field.
3. **Grounded Draft Generation:** Generating customer-facing drafts derived strictly from approved company policies (e.g. 14-day refund policy, account 2FA resets, SLA delivery times).
4. **Safety & Policy Guardrails:**
   - Escalation trigger if a customer requests cash refunds exceeding the $100 policy threshold.
   - Refusal/fallback when ticket inquiries involve unapproved external topics or legal disputes.
5. **Human-in-the-Loop (HITL) Workflow:**
   - Web-based review desk where agents can preview the AI draft, edit the text in a live editor, and click **"Approve & Dispatch"**.
   - Audit trail capturing original AI draft vs. agent-edited version.
6. **Automated Evaluation Set:** Benchmark suite of 12 test tickets (`data/sample_tickets/benchmark_tickets.json`: billing, refund, security, shipping, cancellation, and legal escalation cases).

### Out-of-Scope (Deferred to Future Iterations)
* Direct bi-directional Zendesk / Salesforce API webhooks.
* Automated voice / phone call transcription.
* Autonomous credit card processing (all monetary actions require human supervisor sign-off).

---

## 4. Functional Requirements (FR)

| ID | Feature Name | Description | Delivered File |
| :--- | :--- | :--- | :--- |
| **FR-01** | **Ticket Ingestion & Triage** | Ingest raw ticket text and produce validated structured metadata: Sentiment (`Positive`, `Neutral`, `Frustrated`, `Angry`), Category, and Urgency. | [`src/models.py`](../src/models.py) |
| **FR-02** | **Grounded Retrieval** | Match incoming ticket inquiries against approved internal policy blocks (Refunds, Account, Technical, Shipping) with source citations. | [`src/copilot.py`](../src/copilot.py) |
| **FR-03** | **Structured Draft Synthesis** | Generate empathetic customer-facing replies following brand tone rules, outputting both the customer response and internal reasoning notes. | [`src/copilot.py`](../src/copilot.py) |
| **FR-04** | **Safety & Escalation Controls** | Automatically flag sensitive edge cases (abusive language, legal threats, refund claims $> \$100$) for mandatory Human Supervisor Escalation. | [`src/copilot.py`](../src/copilot.py) |
| **FR-05** | **Human-in-the-Loop (HITL) Review** | Expose a review interface where agents can view the triage tags, review/edit the draft, and submit final approval. | [`src/static/index.html`](../src/static/index.html) |
| **FR-06** | **Audit Trail & Logging** | Store review timestamps, editor notes, and record whether the draft was approved *as-is* or *edited*. | [`src/api.py`](../src/api.py) |

---

## 5. Technical Stack

* **Programming Language:** Python 3.10+
* **LLM Engine:** Local Ollama (`llama3.2`) via LangChain / ChatOllama (zero external API cost, private local execution).
* **Data Schemas & Validation:** Pydantic V2 (`BaseModel`, `Field`, `Enum`).
* **Web Service:** FastAPI (`GET /health`, `POST /triage`, `POST /draft`, `POST /review/approve`).
* **Agent Dashboard:** Lightweight, clean web UI (HTML5, CSS, responsive ticket inbox with live editor).
* **Test & Verification Harness:** `tests/test_copilot.py` & `tests/evaluate_benchmark.py` asserting schema compliance, triage accuracy, and escalation triggers.
* **Version Control:** Git & GitHub monorepo structure (`project-2/support-copilot`).

---

## 6. Success Metrics & Acceptance Criteria

| Metric Category | Target Standard | Achieved Score | Verification Method |
| :--- | :---: | :---: | :--- |
| **Structured Output Schema Compliance** | **$100\%$** | **$100.0\%$ (12/12)** | Pydantic V2 parse validation on all 12 benchmark test tickets. |
| **Category Classification Accuracy** | $\ge 90\%$ | **$91.7\%$ (11/12)** | Comparison against human-annotated ground truth in `docs/eval_results.md`. |
| **Urgency Classification Accuracy** | $\ge 75\%$ | **$75.0\%$ (9/12)** | Comparison against human-annotated ground truth in `docs/eval_results.md`. |
| **Escalation Trigger Accuracy** | **$100\%$** | **$100.0\%$ (12/12)** | Out-of-policy claims ($> \$100$ refund, legal/security) trigger `escalate_to_human: true`. |
| **Grounding & Citation Compliance** | $\ge 95\%$ | **$100.0\%$ (12/12)** | All 12 ticket drafts cite approved policy sections from `support_policies.md`. |
| **Test Suite Pass Rate** | **$100\%$** | **$100\%$** | Deterministic schema, retrieval, and escalation tests passing in `tests/test_copilot.py`. |

---

## 7. Deliverables & Evidence Mapping (Handbook Section 11)

| Handbook Requirement | Project Deliverable | Location |
| :--- | :--- | :--- |
| **Source Code** | Pydantic schemas, copilot engine, FastAPI service, and HITL UI | [`src/`](../src/) |
| **Policy Knowledge Base** | Approved enterprise customer support policy guidelines | [`data/knowledge_base/support_policies.md`](../data/knowledge_base/support_policies.md) |
| **Benchmark Dataset** | 12 annotated customer support evaluation tickets | [`data/sample_tickets/benchmark_tickets.json`](../data/sample_tickets/benchmark_tickets.json) |
| **Requirements Document** | Formal scope, business problem, and success criteria | [`docs/requirements.md`](./requirements.md) |
| **Evaluation Evidence** | 12-ticket benchmark matrix & before/after optimization report | [`docs/eval_results.md`](./eval_results.md) |
| **Viva / Interview Prep** | Prepared answers to the 7 handbook interview defense questions | [`docs/viva_prep.md`](./viva_prep.md) |
| **Automated Test Suite** | Deterministic schema, retrieval, and safety unit tests | [`tests/test_copilot.py`](../tests/test_copilot.py) |
| **12-Ticket LLM Benchmark** | End-to-end triage, grounding, and escalation evaluation script | [`tests/evaluate_benchmark.py`](../tests/evaluate_benchmark.py) |
| **README Runbook** | Complete installation, execution, and API guide | [`README.md`](../README.md) |

---

## 8. Submission Artifacts Checklist (Handbook Section 11)
- [x] `docs/requirements.md` (This document)
- [x] `data/knowledge_base/support_policies.md` (Approved customer support policy documents)
- [x] `data/sample_tickets/benchmark_tickets.json` (12 annotated benchmark support tickets)
- [x] `src/models.py` (Pydantic V2 schemas for tickets, triage, drafts, and reviews)
- [x] `src/copilot.py` (Triage classifier, grounded drafter, and escalation engine)
- [x] `src/api.py` (FastAPI REST service)
- [x] `src/static/index.html` (Interactive Agent Review Dashboard)
- [x] `tests/test_copilot.py` & `tests/evaluate_benchmark.py` (Automated verification & benchmark harness)
- [x] `docs/eval_results.md` (12-ticket benchmark evaluation matrix)
- [x] `docs/viva_prep.md` (Handbook Section 16 interview defense guide)
- [x] `README.md` (Project overview and quickstart runbook)
