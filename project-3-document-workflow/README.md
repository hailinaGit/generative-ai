# Document-to-Workflow Automation Engine

An enterprise **Document-to-Workflow Automation** system that ingests unstructured operational documents (meeting notes, incident postmortems, vendor memos, HR requests, and legal notices), extracts structured action items with verbatim source quotes and confidence scores, routes them to simulated team queues, and enforces deterministic validation guardrails.

---

## Key Features

- **Grounded Team Routing (FR-02):** Routes extracted tasks strictly against [`data/routing_rules/team_directory.md`](./data/routing_rules/team_directory.md) across `Engineering`, `Finance`, `HR & People`, `Legal & Compliance`, `Customer Support`, `Operations`, and `Manual Review`.
- **Structured Extraction & Quote Verification (FR-01 & FR-03):** Validates all outputs with Pydantic V2 (`ActionItem`, `WorkflowResult`) and verifies every `source_quote` verbatim against the input document (`verify_source_quote`).
- **Deterministic Safety & Uncertainty Guardrails (FR-04):**
  - Rejects empty/invalid documents before LLM invocation (`Rejected`).
  - Routes low-confidence (`< 0.70`) or unverified-quote items to `Manual Review` (`#workflow-exceptions`).
  - Flags all `Legal & Compliance` tasks and `Finance` requests `> $5,000.00 USD` for mandatory human validation.
- **Validation Desk & Simulated Team Queues (FR-05 & FR-06):** FastAPI REST API and interactive dark-themed dashboard where coordinators can inspect quotes, override teams, approve/reject tasks, and audit every routing decision.
- **100% Local & Offline Stack:** Powered by Python, FastAPI, Pydantic V2, LangChain, and local Ollama (`llama3.2`).

---

## Repository Structure

```text
project-3-document-workflow/
├── data/
│   ├── routing_rules/
│   │   └── team_directory.md          # Approved team responsibilities, channels & SLAs
│   └── sample_documents/
│       └── benchmark_docs.json        # 9 operational benchmark docs + edge cases
├── docs/
│   ├── requirements.md                # Project scope, FRs, and acceptance criteria
│   ├── eval_results.md                # 9-doc benchmark scores, limitations & next steps
│   └── viva_prep.md                   # Interview & oral defense guide (Handbook Sec 16)
├── src/
│   ├── __init__.py
│   ├── models.py                      # Pydantic V2 schemas & simulated queue channels
│   ├── workflow.py                    # Grounded extractor, router & safety guardrails
│   ├── api.py                         # FastAPI service, team queues & audit log
│   └── static/
│       └── index.html                 # Interactive Workflow Validation & Queue UI
├── tests/
│   ├── test_workflow.py               # Deterministic unit & guardrail tests
│   └── evaluate_workflow.py           # 9-document end-to-end LLM benchmark runner
├── pyrefly.toml
└── README.md
```

---

## Quickstart Guide

### 1. Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com/) installed and running locally:
  ```bash
  ollama serve
  ollama pull llama3.2
  ```

### 2. Environment Setup
From the root `Internship/` workspace:
```bash
source .venv/bin/activate
cd project-3-document-workflow
```

### 3. Launch the FastAPI Service & Workflow Desk UI
```bash
uvicorn src.api:app --reload --port 8000
```
- **Workflow Desk UI:** Open **[http://localhost:8000/](http://localhost:8000/)**
- **Swagger API Docs:** Open **[http://localhost:8000/docs](http://localhost:8000/docs)**

### 4. API Endpoints
- `GET /health` — Service readiness, model name, and loaded routing sections.
- `GET /api/documents` — Lists the 9 sample operational documents with live status.
- `POST /api/workflow/process` — Extracts action items, verifies source quotes, and routes to team queues.
- `POST /api/workflow/validate` — Approves, overrides, or rejects an extracted action item.
- `GET /api/team-queues` — Returns simulated team queues (`#eng-triage`, `#ap-finance`, etc.).
- `GET /api/audit-log` — Returns the full extraction and validation audit trail.

---

## Testing & Benchmark Evaluation

### 1. Deterministic Unit & Guardrail Tests (`< 1 sec`, no LLM required)
```bash
python tests/test_workflow.py
```

### 2. Full 9-Document LLM Benchmark (`llama3.2`)
```bash
python tests/evaluate_workflow.py
```

**Observed Benchmark Results:**
- **Structured Output Schema Compliance:** `9/9 (100.0%)`
- **Action-Item Extraction Recall:** `10/11 (90.9%)`
- **Team Routing Accuracy:** `10/11 (90.9%)`
- **Source-Quote Grounding:** `11/12 (91.7%)`
- **Status & Safety Control Accuracy:** `8/9 (88.9%)`
