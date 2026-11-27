# Project Requirements & Scope Document: Document-to-Workflow Automation

**Project Title:** Document-to-Workflow Automation Engine  
**Project Type:** Capstone / Portfolio Task (Arrowstack 1-Month Generative AI Internship, Week 3–4)  
**Project Folder:** `project-3-document-workflow`  
**Git Branch:** `project-3/workflow-automation`  
**Author:** hailinaGit  

---

## 1. Executive Summary & Business Use Case

* **Primary Stakeholder:** Operations Managers, Team Leads (Engineering, Finance, HR, Legal, Support), and Project Coordinators.
* **The Business Problem:** Organizations receive unstructured operational documents daily — meeting transcripts, incident postmortems, vendor notices, and client change requests. Coordinators spend hours manually reading documents, extracting action items, assigning owners and deadlines, and routing tasks to the right team queues. Missed or misrouted tasks cause SLA breaches, duplicated effort, and poor operational visibility.
* **The Solution:** A **Document-to-Workflow Automation Engine** that:
  1. Ingests unstructured operational documents (`.txt`, `.md`, `.json`, or raw text) and validates input integrity.
  2. Grounds extraction and routing decisions in an approved **Team Routing & SLA Policy Directory**.
  3. Extracts structured action items (`task_title`, `owner_role`, `target_team`, `priority`, `due_date`, `confidence_score`, `source_quote`) validated against strict Pydantic V2 / JSON schemas.
  4. Routes each action item to simulated team queues, flags low-confidence or ambiguous items for human validation, and retains a traceable audit log.
* **Measurable Benefits:**
  * **Triage & Routing Time:** Reduces manual document-to-task breakdown from 15–20 minutes per document to under 10 seconds.
  * **Operational Visibility:** 100% of extracted tasks include source-quote traceability, target team, and confidence score.
  * **Routing Reliability:** Eliminates unvalidated or hallucinated task assignments via deterministic schema + confidence guardrails.

---

## 2. Problem Statement: Inputs, Outputs & Constraints

* **Inputs:**
  * Unstructured or semi-structured operational document (`doc_id`, `title`, `doc_type`, `content`).
  * Approved routing rules & team directory (`data/routing_rules/team_directory.md`).
* **Outputs:**
  * Strict Pydantic V2 workflow payload containing:
    * `doc_id`, `document_summary`, and `extraction_status` (`Completed`, `Needs Review`, `Rejected`).
    * List of extracted `ActionItem` objects (`item_id`, `title`, `target_team`, `priority`, `due_date`, `confidence`, `source_quote`, `validation_status`).
    * Simulated team routing dispatch records (`Engineering`, `Finance`, `HR & People`, `Legal & Compliance`, `Customer Support`, `Operations`, or `Unassigned / Manual Review`).
    * Retained validation & audit evidence log (`data/audit_logs/` or in-memory + exported JSON).
* **Key Constraints:**
  * **100% Offline / Local Execution:** Runs locally via Ollama (`llama3.2`, temperature `0.0`) with zero external API cost and full data privacy.
  * **Zero Hallucinated Action Items:** Every extracted action item must reference a verbatim `source_quote` from the input document.
  * **Uncertainty & Edge-Case Controls:** Empty, corrupted, off-topic, or contradictory documents must be safely rejected or flagged (`Needs Review`), and items with `confidence < 0.70` or unknown target teams must route to `Manual Review` rather than auto-dispatching.

---

## 3. Scope Boundaries

### In-Scope (Project 3 Deliverables)
1. **Document Ingestion & Input Validation:** Reject empty, malformed, or non-actionable inputs with clear error/status codes.
2. **Grounded Team & SLA Routing:** Load approved team responsibilities, escalation rules, and SLA priorities from `data/routing_rules/team_directory.md`.
3. **Structured Action-Item Extraction:** Extract typed JSON / Pydantic V2 action items with `confidence` (`0.0`–`1.0`) and verbatim `source_quote` grounding.
4. **Workflow Routing & Confidence Guardrails:**
   - Deterministic routing verification against approved team names.
   - Low-confidence (`< 0.70`) or sensitive (legal/security/budget threshold) items held for human validation.
5. **Human Validation & Audit Evidence:** FastAPI service + interactive Workflow Review UI where reviewers can inspect extracted items, override team/priority, approve/reject, and inspect the dispatch audit log.
6. **Evaluation Set & Verification Harness:** Benchmark suite of realistic operational documents (meeting notes, incident reports, finance requests, legal notices, and edge-case/empty/ambiguous inputs).

### Out-of-Scope (Future Enhancements)
* Live external webhooks to Jira, Asana, Slack, or Linear (simulated team queues used for reproducible offline evaluation).
* Automated OCR on scanned image PDFs.
* Multi-user OAuth / enterprise SSO authentication.

---

## 4. Functional Requirements (FR)

| ID | Feature Name | Description | Delivered File |
| :--- | :--- | :--- | :--- |
| **FR-01** | **Document Ingestion & Validation** | Accept raw documents or files, validate non-empty/readable content, and normalize metadata. | `src/models.py` |
| **FR-02** | **Grounded Team & Policy Lookup** | Load approved team definitions, ownership keywords, and SLA rules from the routing directory. | `src/workflow.py` |
| **FR-03** | **Structured Action-Item Extraction** | Use local LLM (`llama3.2`, temperature `0.0`) to extract typed action items with `source_quote` and `confidence`. | `src/workflow.py` |
| **FR-04** | **Routing & Safety Controls** | Validate target teams deterministically, enforce confidence thresholds (`< 0.70` -> `Needs Review`), and handle edge/invalid inputs safely. | `src/workflow.py` |
| **FR-05** | **Validation & Team Dispatch UI** | Provide FastAPI endpoints and a web dashboard to review extracted tasks, edit/approve/reject items, and inspect simulated team queues. | `src/api.py`, `src/static/index.html` |
| **FR-06** | **Audit Trail & Evidence Retention** | Record routing decisions, confidence scores, reviewer overrides, and timestamps for every workflow run. | `src/api.py` |

---

## 5. Technical Stack

* **Programming Language:** Python 3.10+
* **LLM Engine:** Local Ollama (`llama3.2`) via LangChain / ChatOllama (zero external API cost, private local execution)
* **Data Schemas & Validation:** Pydantic V2 (`BaseModel`, `Field`, `Enum`)
* **Web Service:** FastAPI & Uvicorn
* **Workflow Dashboard:** Lightweight HTML5/CSS/JS review & simulated team-queue UI
* **Testing & Evaluation:** Deterministic unit tests (`tests/test_workflow.py`) + end-to-end document benchmark (`tests/evaluate_workflow.py`)
* **Version Control:** Git & GitHub monorepo (`project-3/workflow-automation`)

---

## 6. Success Metrics & Acceptance Criteria

| Metric Category | Target Standard | Achieved Score | Verification Method |
| :--- | :---: | :---: | :--- |
| **Structured Output Schema Compliance** | **$100\%$** | **$100.0\%$ (9/9)** | Pydantic V2 validation across all 9 benchmark documents. |
| **Action-Item Extraction Recall** | $\ge 90\%$ | **$90.9\%$ (10/11)** | Comparison against ground-truth action items in `docs/eval_results.md`. |
| **Team Routing Accuracy** | $\ge 90\%$ | **$90.9\%$ (10/11)** | Predicted `target_team` vs. expected team per ground truth. |
| **Source Quote Grounding** | $\ge 95\%$ | **$91.7\%$ (11/12)** | Verbatim `source_quote` verification (1 paraphrased quote caught & flagged). |
| **Status & Safety Control Accuracy** | $\ge 85\%$ | **$88.9\%$ (8/9)** | Empty inputs rejected; low-confidence/legal/high-spend items flagged. |
| **Deterministic Test Pass Rate** | **$100\%$** | **$100\%$** | Schema, routing, and guardrail tests passing in `tests/test_workflow.py`. |

---

## 7. Deliverables & Evidence Mapping (Handbook Section 11)

| Handbook Requirement | Project Deliverable | Location |
| :--- | :--- | :--- |
| **Source Code** | Schemas, extraction/routing workflow engine, FastAPI service, and UI | [`src/`](../src/) |
| **Routing Rules & Sample Docs** | Approved team directory and 9 benchmark operational documents | [`data/`](../data/) |
| **Requirements Document** | Formal scope, business problem, and success criteria | [`docs/requirements.md`](./requirements.md) |
| **Evaluation Evidence** | Benchmark evaluation matrix, limitations, and next improvements | [`docs/eval_results.md`](./eval_results.md) |
| **Viva / Interview Prep** | Prepared answers to the 7 handbook interview defense questions | [`docs/viva_prep.md`](./viva_prep.md) |
| **Automated Test Suite** | Deterministic schema, routing, and edge-case unit tests | [`tests/test_workflow.py`](../tests/test_workflow.py) |
| **End-to-End LLM Benchmark** | Document-to-workflow evaluation script across benchmark docs | [`tests/evaluate_workflow.py`](../tests/evaluate_workflow.py) |
| **README Runbook** | Complete installation, execution, and API guide | [`README.md`](../README.md) |

---

## 8. Submission Artifacts Checklist (Handbook Section 11)
- [x] `docs/requirements.md` (This document)
- [x] `data/routing_rules/team_directory.md` (Approved team responsibilities & SLA rules)
- [x] `data/sample_documents/benchmark_docs.json` (Evaluation set of 9 operational documents + ground truth)
- [x] `src/models.py` (Pydantic V2 schemas for documents, action items, routing, and validation)
- [x] `src/workflow.py` (Grounded extractor, team router, confidence & edge-case guardrails)
- [x] `src/api.py` (FastAPI REST service & simulated team queues / audit log)
- [x] `src/static/index.html` (Interactive Workflow Validation & Team Queue UI)
- [x] `tests/test_workflow.py` & `tests/evaluate_workflow.py` (Deterministic tests & LLM benchmark)
- [x] `docs/eval_results.md` (Benchmark evaluation matrix, limitations & next improvements)
- [x] `docs/viva_prep.md` (Handbook Section 16 interview defense guide)
- [x] `README.md` (Project overview and quickstart runbook)
