# Project Requirements & Scope Document: AI Customer Support Copilot

**Project Type:** Intermediate Real-World Task (Arrowstack 1-Month Generative AI Internship, Week 2)  
**Project Folder:** `project-2-support-copilot`  
**Git Branch:** `project-2/support-copilot`  
**Author:** hailinaGit  

---

## 1. Executive Summary & Real-World Scenario
Customer support teams in high-growth companies receive hundreds of inbound inquiries daily across billing, delivery, technical troubleshooting, and account security. Human agents spend excessive time manually parsing ticket context, cross-referencing internal policy documents, and typing repetitive replies from scratch. Fully autonomous bots, however, frequently hallucinate or promise unauthorized refunds.

**The Solution:**  
Build an **AI Customer Support Copilot** that:
1. Ingests raw ticket text and extracts structured triage data (Sentiment, Urgency, Category).
2. Retrieves relevant sections from an approved internal knowledge base.
3. Synthesizes an empathetic, grounded draft reply along with internal reasoning notes.
4. Provides a **Human-in-the-Loop (HITL) review flow** where human agents inspect, modify, and officially approve the reply before sending.

---

## 2. Business Use Case & Stakeholders
* **Primary Stakeholder:** Frontline Customer Support Agents, Support Team Leads, and Customer Experience (CX) QA Officers.
* **Decision Enabled:** Empowers agents to verify and dispatch grounded replies in under 60 seconds instead of 5–10 minutes of manual drafting.
* **Measurable Benefits:**
  * **First Response Time (FRT):** Reduced by $\ge 60\%$.
  * **Draft Edit Distance:** $\ge 80\%$ of AI-generated responses accepted by human agents with minor or no modifications.
  * **Policy Adherence:** $100\%$ compliance with official refund and privacy guidelines.

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
6. **Automated Evaluation Set:** Benchmark suite of 10 test tickets (positive, angry, billing edge case, out-of-scope).

### Out-of-Scope (Deferred to Future Iterations)
* Direct bi-directional Zendesk / Salesforce API webhooks.
* Automated voice / phone call transcription.
* Autonomous credit card processing (all monetary actions require human supervisor sign-off).

---

## 4. Functional Requirements (FR)

| ID | Requirement | Description |
| :--- | :--- | :--- |
| **FR-01** | **Ticket Ingestion & Triage** | Ingest raw ticket text and produce validated structured metadata: Sentiment (`Positive`, `Neutral`, `Frustrated`, `Angry`), Category, and Urgency. |
| **FR-02** | **Grounded Retrieval** | Match incoming ticket inquiries against approved internal policy blocks (Refunds, Account, Technical, Shipping) with source citations. |
| **FR-03** | **Structured Draft Synthesis** | Generate empathetic customer-facing replies following brand tone rules, outputting both the customer response and internal reasoning notes. |
| **FR-04** | **Safety & Escalation Controls** | Automatically flag sensitive edge cases (abusive language, legal threats, refund claims > $100) for mandatory Human Supervisor Escalation. |
| **FR-05** | **Human-in-the-Loop (HITL) Review** | Expose a review interface where agents can view the triage tags, review/edit the draft, and submit final approval. |
| **FR-06** | **Audit Trail & Logging** | Store review timestamps, editor notes, and record whether the draft was approved *as-is* or *edited*. |

---

## 5. Technical Requirements & Suggested Stack

* **Programming Language:** Python 3.10+
* **LLM Engine:** Local Ollama (`llama3.2`) via LangChain / ChatOllama (zero external API cost, private local execution).
* **Data Schemas & Validation:** Pydantic V2 (`BaseModel`, `Field`, `Enum`).
* **Web Service:** FastAPI (`GET /health`, `POST /triage`, `POST /draft`, `POST /review/approve`).
* **Agent Dashboard:** Lightweight, clean web UI (HTML5, Tailwind/CSS, responsive ticket inbox with live editor).
* **Test & Verification Harness:** `pytest` / Python script asserting schema compliance, triage accuracy, and escalation triggers.

---

## 6. Success Metrics & Quality Criteria

| Metric | Target Standard | Verification Method |
| :--- | :---: | :--- |
| **Structured Output Schema Compliance** | **$100\%$** | Pydantic V2 parse validation on all 10 benchmark test tickets. |
| **Triage Accuracy (Category & Urgency)** | $\ge 90\%$ | Comparison against human-annotated ground truth. |
| **Grounding Faithfulness** | $\ge 95\%$ | Verification that claims adhere strictly to approved knowledge base articles. |
| **Escalation Trigger Accuracy** | **$100\%$** | Out-of-policy claims (> $100 refund, chargebacks) must trigger `escalate_to_human: true`. |
| **Review Usability** | $< 60\text{ sec}$ | Human agent can review, tweak, and approve draft in under 1 minute via the UI. |

---

## 7. Submission Artifacts Checklist (Handbook Section 11)
- [ ] `docs/requirements.md` (This document)
- [ ] `data/knowledge_base/` (Approved customer support policy documents)
- [ ] `src/models.py` (Pydantic V2 schemas for tickets, triage, drafts, and reviews)
- [ ] `src/copilot.py` (Triage classifier, grounded drafter, and escalation engine)
- [ ] `src/api.py` (FastAPI REST service)
- [ ] `src/static/index.html` (Interactive Agent Review Dashboard)
- [ ] `tests/test_copilot.py` (Automated verification harness)
- [ ] `docs/eval_results.md` (10-ticket benchmark evaluation matrix)
- [ ] `docs/viva_prep.md` (Handbook Section 16 interview defense guide)
- [ ] `README.md` (Project overview and quickstart runbook)
