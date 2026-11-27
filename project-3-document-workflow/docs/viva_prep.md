# Viva & Interview Defense Guide (Handbook Section 16)

**Project:** Project 3 — Document-to-Workflow Automation (`project-3-document-workflow`)  
**Role:** Capstone / Portfolio Task  

---

### 1. What business or user problem does the project solve, and how did you define success?
Operations coordinators and team leads spend significant time manually reading meeting transcripts, incident postmortems, vendor memos, and legal notices to extract tasks and route them to the right teams. Unchecked LLM automation risks inventing tasks or misrouting high-stakes finance/legal items.  
Success was defined using measurable targets in `docs/requirements.md`: **$100\%$ Pydantic V2 schema compliance**, **$\ge 90\%$ action-item extraction recall and team routing accuracy**, **verbatim `source_quote` verification**, and **deterministic safety guardrails** for empty inputs, low-confidence items (`< 0.70`), Legal reviews, and Finance spend $> \$5,000$.

### 2. Which design, technical, analytical or research decision had the biggest impact on the result?
Combining **grounded prompt engineering** (injecting `data/routing_rules/team_directory.md` directly into the system prompt) with **deterministic post-extraction guardrails** (`apply_routing_guardrails` in `src/workflow.py`). Even when the 3B local model (`llama3.2`) is overly confident or paraphrases a quote, `verify_source_quote()`, `< 0.70` confidence routing, and the `$5,000` Finance / Legal rules enforce policy compliance deterministically.

### 3. How did you validate the quality or correctness of your work?
Using a two-layer verification harness:
1. **Deterministic Unit & Guardrail Suite (`tests/test_workflow.py`):** Tests schema loading, empty-input rejection, ungrounded-quote detection, `< 0.70` confidence routing to `Manual Review`, and `$5,000` Finance / Legal escalation (`100%` pass).
2. **9-Document End-to-End LLM Benchmark (`tests/evaluate_workflow.py`):** Evaluates `DOC-301` through `DOC-309` live against `llama3.2`, achieving `100.0%` schema compliance, `90.9%` extraction recall, `90.9%` team routing accuracy, `91.7%` source-quote grounding, and `88.9%` exact status accuracy.

### 4. What edge cases, limitations or risks did you identify?
- **Edge cases handled:** Empty/whitespace documents (`Rejected` before LLM call), non-actionable announcements (`DOC-308` returns `0` tasks), ambiguous fragments (`Manual Review`), and high-value Finance / Legal items (`Needs Review`).
- **Limitations:** `llama3.2` (3B) occasionally paraphrases a `source_quote` (`11/12` verbatim) or misses 1 of 2 tasks in dense documents (`10/11`), and simulated queues/audit logs are stored in memory.

### 5. What would you change if this solution had to support 10× the users/data/workload?
1. Move FastAPI state (`processed_results`, `team_queues`, `audit_log`) to **PostgreSQL** with an async task queue (**Celery / Redis**) for document ingestion.
2. Add **document chunking** for long multi-page transcripts/PDFs and **batch/async Ollama inference** (or vLLM serving) for higher throughput.
3. Replace simulated queues with idempotent **webhook connectors** (Jira, Slack, Linear) and add role-based access control (RBAC) for Finance/Legal approvers.

### 6. How would you explain the project to a non-technical stakeholder?
"Think of it as an AI operations coordinator: you paste in meeting notes, an incident report, or a vendor memo, and within seconds it pulls out every action item, quotes the exact sentence it came from, and routes it to the right team queue (Engineering, Finance, HR, Legal, Support, or Operations). Whenever something looks uncertain, involves a legal contract, or exceeds `$5,000`, it automatically holds the item for human approval first."

### 7. Which part of the project required the most independent problem-solving?
Designing the **verbatim `source_quote` verification and confidence-downgrade loop** alongside realistic **departmental boundaries** in `team_directory.md` (such as separating corporate AP Finance from Customer Support SLA credits, and IT/hardware provisioning from HR onboarding) so the local 3B model routes accurately without hallucinating tasks.
