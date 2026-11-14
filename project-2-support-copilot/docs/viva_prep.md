# Viva & Interview Preparation Guide: AI Customer Support Copilot

**Project:** Project 2 — AI Customer Support Copilot  
**Reference:** Internship Handbook Section 16 (Viva / Interview Questions) & Section 13 (Acceptance Criteria)  

---

### Q1: What business or user problem does the project solve, and how did you define success?
* **Problem:** Frontline customer support agents spend significant time reading raw tickets, classifying urgency, searching internal policy handbooks, and drafting repetitive replies from scratch. On the other hand, fully autonomous bots risk hallucinating unauthorized refunds or mishandling angry/legal-threat tickets.
* **Solution:** A **Human-in-the-Loop (HITL) Copilot** that triages tickets into structured JSON, retrieves approved support policies, drafts an empathetic reply, and lets a human agent review, edit, and approve before dispatching.
* **Success Definition:**
  - $100\%$ Pydantic V2 structured output schema compliance.
  - $\ge 90\%$ category classification accuracy (achieved **91.7%**).
  - $100\%$ escalation accuracy for high-risk tickets (refunds $> \$100$, legal threats, security breaches).
  - $100\%$ grounding against approved policy sections.

---

### Q2: Which design, technical, analytical or research decision had the biggest impact on the result?
* **Decision:** Separating **LLM semantic reasoning** (tone, empathy, category, summarization) from **deterministic policy guardrails** (`_check_deterministic_escalation` using regex + monetary thresholds).
* **Impact:** In our initial benchmark run (`llama3.2`), the 3B model over-escalated 5 routine tickets, resulting in **58.3%** escalation accuracy. By making deterministic policy checks authoritative for strict business rules (legal disputes, unauthorized logins, refunds $> \$100$) and refining the prompt, **Escalation Trigger Accuracy jumped from 58.3% to 100.0% (12/12)** and **Category Accuracy improved from 83.3% to 91.7%**.

---

### Q3: How did you validate the quality or correctness of your work?
* Through a two-tier verification suite:
  1. **Fast Deterministic Unit Tests (`tests/test_copilot.py`):** Validates Pydantic V2 schemas (`CustomerTicket`, `ReviewSubmission`), policy section retrieval, and boundary escalation rules in $<1$ second without needing an LLM call.
  2. **12-Ticket Live LLM Benchmark (`tests/evaluate_benchmark.py`):** Runs all 12 realistic enterprise tickets (`benchmark_tickets.json`) through `llama3.2`, comparing predicted category, urgency, escalation, and citations against ground truth, with all observed results logged in `docs/eval_results.md`.

---

### Q4: What edge cases, limitations or risks did you identify?
* **Excessive Refund Claims & Legal Threats:** Mitigated by deterministic pre-guards (`REFUND_SUPERVISOR_THRESHOLD = $100.00`, `LEGAL_DISPUTE_PATTERN`) that force `escalate_to_human=True` and lock dispatch behind supervisor sign-off.
* **Security Breaches:** Unknown IP / unauthorized login tickets (`TCK-107`) trigger immediate Critical escalation.
* **Out-of-Scope Requests:** Unrelated inquiries (e.g., crypto trading in `TCK-106`) trigger a polite fallback routing to a specialist instead of hallucinating.
* **Model Size Limitation:** A 3B local model (`llama3.2`) occasionally misclassifies nuanced urgency levels (e.g. **75.0%** urgency accuracy on `TCK-102`, `TCK-108`, `TCK-109`), which is why **Human-in-the-Loop review** remains mandatory before sending.

---

### Q5: What would you change if this solution had to support 10× the users/data/workload?
* **Async Queue & Workers:** Offload LLM drafting to background task workers (Celery / Redis Queue) so ticket ingestion and UI rendering stay non-blocking.
* **Persistent Database:** Replace the in-memory `ticket_status_map` and `audit_log` list with PostgreSQL for durable audit trails and multi-agent concurrency.
* **Vector Retrieval for Large KBs:** Upgrade `PolicyKnowledgeBase` from keyword-section matching to a hybrid vector + BM25 retriever (e.g. Qdrant or Pgvector) when the knowledge base scales from 5 sections to hundreds of articles.
* **Model Scaling:** Serve larger instruction-tuned models (e.g. 8B–70B or quantized vLLM endpoints) for higher urgency classification accuracy.

---

### Q6: How would you explain the project to a non-technical stakeholder?
> *"Think of this as an intelligent assistant sitting right next to our customer support agents. When a customer email arrives, the assistant reads it, tags whether the customer is angry or has a billing issue, finds the exact company rule we need to follow, and writes a polite draft reply. Crucially, it never sends anything on its own—and if a customer demands a large refund or mentions a lawyer, it flashes a red warning so a supervisor steps in."*

---

### Q7: Which part of the project required the most independent problem-solving?
* Diagnosing and fixing the **58.3% false-positive escalation rate** in `llama3.2`. Rather than blindly accepting the LLM's output or tweaking temperature alone, running the 12-ticket benchmark exposed that small local models over-escalate stressful language. Designing a **hybrid architecture** (combining LLM flexibility with deterministic regex/threshold guardrails) solved the problem cleanly and pushed escalation accuracy to **100%**.

