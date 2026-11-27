# Generative AI Internship — Portfolio Repository

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Vector DB](https://img.shields.io/badge/Vector%20DB-ChromaDB-purple.svg)](https://www.trychroma.com/)
[![Local LLM](https://img.shields.io/badge/LLM-Ollama%20(llama3.2)-orange.svg)](https://ollama.com/)

> **Program:** Arrowstack 1-Month Generative AI Internship  
> **Difficulty:** Intermediate • **Duration:** 4 Weeks  
> **Working Mode:** Individual, Mentor-Reviewed, Evidence-Based Delivery  
> **Author:** hailinaGit  

---

## 📖 Internship Summary & Roadmap

This repository contains the end-to-end deliverables, source code, evaluation evidence, and documentation for **3 progressive industry-aligned generative AI projects** as defined in the Arrowstack Internship Handbook:

```text
Internship/
├── project-1-rag-assistant/          # Project 1: RAG Knowledge Assistant (✅ Completed)
├── project-2-support-copilot/        # Project 2: AI Customer Support Copilot (✅ Completed)
└── project-3-document-workflow/      # Project 3: Document-to-Workflow Automation (✅ Completed)
```

| Project | Type | Tech Stack | Status | Documentation & Evidence |
| :--- | :--- | :--- | :---: | :--- |
| **1. RAG Knowledge Assistant** | Core / Foundation | Python, ChromaDB, Ollama (`llama3.2`), FastAPI | **✅ Complete** | [Project 1 README](./project-1-rag-assistant/README.md) • [Eval Results](./project-1-rag-assistant/docs/eval_results.md) • [Viva Prep](./project-1-rag-assistant/docs/viva_prep.md) |
| **2. AI Customer Support Copilot** | Intermediate Real-World | Python, Pydantic V2, LangChain, Ollama (`llama3.2`), FastAPI, HITL UI | **✅ Complete** | [Project 2 README](./project-2-support-copilot/README.md) • [Eval Results](./project-2-support-copilot/docs/eval_results.md) • [Viva Prep](./project-2-support-copilot/docs/viva_prep.md) |
| **3. Document-to-Workflow Automation** | Capstone Portfolio | Python, Pydantic V2, LangChain, Ollama (`llama3.2`), FastAPI, Workflow UI | **✅ Complete** | [Project 3 README](./project-3-document-workflow/README.md) • [Eval Results](./project-3-document-workflow/docs/eval_results.md) • [Viva Prep](./project-3-document-workflow/docs/viva_prep.md) |

---

## 🚀 Project 1: RAG Knowledge Assistant (Cambodia HR Compliance)

### 📌 Problem Statement & Real-World Use Case
HR personnel and legal compliance officers in Cambodia spend substantial administrative hours cross-referencing statutory labor requirements (working hours, overtime rates, maternity benefits, and bi-annual seniority pay). Errors risk labor disputes or compliance fines. This solution delivers an internal AI assistant grounded strictly in approved Cambodian labor regulations with 100% citation traceability.

### 🌟 Key Technical Implementations
- **Document Ingestion (FR-01):** Section-aware semantic chunking keeping statutory articles unified.
- **Vector Search (FR-02):** Cosine distance semantic retrieval via local **ChromaDB**.
- **Grounded Generation (FR-03):** Local inference via **LangChain + Ollama (`llama3.2`)** with temperature `0.0`. Strict boundary control ensures off-topic or unapproved queries return the exact fallback message: `"I cannot find this information in the approved policy documents."`
- **Citation Tracking (FR-04):** Every statement links to the source markdown, section header, and cosine distance score.
- **API & UI Delivery:** Production-grade **FastAPI** service (`/health`, `/retrieve`, `/query`) paired with an interactive dark-themed web chat interface.
- **Verification Harness:** Automated 5-test assertion suite with 100% compliance.

### 🧪 Verification Evidence
- **Benchmark Evaluation:** 10-query test matrix documented in [`docs/eval_results.md`](./project-1-rag-assistant/docs/eval_results.md) demonstrating $\ge 95\%$ grounding and $0.0\%$ hallucination.
- **Viva Defense Prep:** Comprehensive answers to all 7 handbook interview questions in [`docs/viva_prep.md`](./project-1-rag-assistant/docs/viva_prep.md).

---

## ⚡ Quickstart Guide (Running Project 1)

### 1. Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com/) running locally:
  ```bash
  ollama serve
  ollama pull llama3.2
  ```

### 2. Setup Environment
```bash
git clone https://github.com/hailinaGit/generative-ai.git
cd generative-ai
python3 -m venv .venv
source .venv/bin/activate
pip install -r project-1-rag-assistant/requirements.txt
```

### 3. Run Ingestion & Test Suite
```bash
cd project-1-rag-assistant
python src/ingest.py --reset
python tests/test_rag.py
```

### 4. Launch the Web Service & UI
```bash
uvicorn src.api:app --reload --port 8000
```
- **Web UI:** Open [http://localhost:8000/](http://localhost:8000/) in your browser.
- **Swagger API Docs:** Open [http://localhost:8000/docs](http://localhost:8000/docs).

---

## 🤖 Project 2: AI Customer Support Copilot

### 📌 Problem Statement & Real-World Use Case
Support teams handle high volumes of inbound tickets across billing, technical support, account security, shipping, and cancellations. Manual drafting is slow, while unguarded bots risk hallucinating or promising unauthorized refunds. This project delivers a **Human-in-the-Loop (HITL) Copilot** that triages tickets, retrieves approved policy rules, drafts grounded replies, and enforces deterministic supervisor escalation before dispatch.

### 🌟 Key Technical Implementations
- **Structured Triage (FR-01):** Pydantic V2 schemas (`CustomerTicket`, `TriageClassification`, `CopilotDraftResponse`, `ReviewSubmission`) enforcing validated Sentiment, Category, and Urgency enums.
- **Policy Grounding (FR-02 & FR-03):** Section-indexed lookup against [`support_policies.md`](./project-2-support-copilot/data/knowledge_base/support_policies.md) with explicit `PolicyCitation` metadata.
- **Deterministic Safety Guardrails (FR-04):** Pre-guards automatically flag legal/chargeback threats, security breaches, and refund requests $> \$100$ for mandatory supervisor escalation.
- **HITL Review Desk & Audit Trail (FR-05 & FR-06):** FastAPI service and interactive Agent Review Desk UI (`/api/tickets`, `/api/copilot/draft`, `/api/review/submit`, `/api/audit-log`).

### 🧪 Verification Evidence & Quickstart
- **Deterministic Tests:** `cd project-2-support-copilot && python tests/test_copilot.py` (`100%` pass)
- **12-Ticket LLM Benchmark:** `python tests/evaluate_benchmark.py` (`100.0%` schema compliance, `91.7%` category, `75.0%` urgency, `100.0%` escalation, `100.0%` grounding — see [`docs/eval_results.md`](./project-2-support-copilot/docs/eval_results.md))
- **Launch UI & API:** `uvicorn src.api:app --reload --port 8000` -> [http://localhost:8000/](http://localhost:8000/)

---

## ⚙️ Project 3: Document-to-Workflow Automation

### 📌 Problem Statement & Real-World Use Case
Operations coordinators manually parse meeting transcripts, incident postmortems, vendor memos, and legal notices to extract action items and route them to the right teams. This capstone delivers a **Document-to-Workflow Automation Engine** that extracts structured tasks, verifies verbatim source quotes, routes them to simulated team queues, and enforces deterministic validation guardrails.

### 🌟 Key Technical Implementations
- **Structured Extraction & Schemas (FR-01 & FR-03):** Pydantic V2 schemas (`DocumentInput`, `ActionItem`, `WorkflowResult`, `ValidationSubmission`) with `confidence`, `source_quote`, and `quote_verified`.
- **Grounded Team Routing (FR-02):** Routes tasks strictly against [`team_directory.md`](./project-3-document-workflow/data/routing_rules/team_directory.md) (`Engineering`, `Finance`, `HR & People`, `Legal & Compliance`, `Customer Support`, `Operations`, `Manual Review`).
- **Deterministic Safety & Uncertainty Guardrails (FR-04):** Rejects empty/invalid inputs (`Rejected`), routes `< 0.70` confidence or unverified quotes to `Manual Review`, and flags Legal items and Finance spend $> \$5,000$ for human validation.
- **Validation Desk & Simulated Queues (FR-05 & FR-06):** FastAPI service and interactive dashboard (`/api/documents`, `/api/workflow/process`, `/api/workflow/validate`, `/api/team-queues`, `/api/audit-log`).

### 🧪 Verification Evidence & Quickstart
- **Deterministic Tests:** `cd project-3-document-workflow && python tests/test_workflow.py` (`100%` pass)
- **9-Document LLM Benchmark:** `python tests/evaluate_workflow.py` (`100.0%` schema compliance, `90.9%` extraction recall, `90.9%` team routing, `91.7%` quote grounding, `88.9%` status accuracy — see [`docs/eval_results.md`](./project-3-document-workflow/docs/eval_results.md))
- **Launch UI & API:** `uvicorn src.api:app --reload --port 8000` -> [http://localhost:8000/](http://localhost:8000/)

---

## 🌿 Git Branch Organization

This repository uses a structured branch workflow:
- **`main`** — Production-ready master branch containing all reviewed projects and top-level documentation.
- **`project-1/rag-assistant`** — Dedicated branch preserving the complete history and implementation of Project 1.
- **`project-2/support-copilot`** — Dedicated branch preserving the complete history and implementation of Project 2.
- **`project-3/workflow-automation`** — Dedicated branch preserving the complete history and implementation of Project 3.

---

## 📄 Evaluation & Submission Mapping

| Handbook Deliverable (Sec 11) | Project 1 Mapping | Project 2 Mapping | Project 3 Mapping | Status |
| :--- | :--- | :--- | :--- | :---: |
| Project Source Files | [`project-1-rag-assistant/src/`](./project-1-rag-assistant/src/) | [`project-2-support-copilot/src/`](./project-2-support-copilot/src/) | [`project-3-document-workflow/src/`](./project-3-document-workflow/src/) | ✅ |
| Requirements & Research Doc | [`project-1-rag-assistant/docs/requirements.md`](./project-1-rag-assistant/docs/requirements.md) | [`project-2-support-copilot/docs/requirements.md`](./project-2-support-copilot/docs/requirements.md) | [`project-3-document-workflow/docs/requirements.md`](./project-3-document-workflow/docs/requirements.md) | ✅ |
| Test / Validation Evidence | [`project-1-rag-assistant/docs/eval_results.md`](./project-1-rag-assistant/docs/eval_results.md) | [`project-2-support-copilot/docs/eval_results.md`](./project-2-support-copilot/docs/eval_results.md) | [`project-3-document-workflow/docs/eval_results.md`](./project-3-document-workflow/docs/eval_results.md) | ✅ |
| README / Technical Guide | [`project-1-rag-assistant/README.md`](./project-1-rag-assistant/README.md) | [`project-2-support-copilot/README.md`](./project-2-support-copilot/README.md) | [`project-3-document-workflow/README.md`](./project-3-document-workflow/README.md) | ✅ |
| Viva / Interview Prep | [`project-1-rag-assistant/docs/viva_prep.md`](./project-1-rag-assistant/docs/viva_prep.md) | [`project-2-support-copilot/docs/viva_prep.md`](./project-2-support-copilot/docs/viva_prep.md) | [`project-3-document-workflow/docs/viva_prep.md`](./project-3-document-workflow/docs/viva_prep.md) | ✅ |
| Version-Controlled Repository | GitHub: `hailinaGit/generative-ai` | GitHub: `hailinaGit/generative-ai` | GitHub: `hailinaGit/generative-ai` | ✅ |
