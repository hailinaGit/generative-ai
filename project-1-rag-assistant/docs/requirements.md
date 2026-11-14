# Project Requirements & Scope Document: RAG Knowledge Assistant

**Project Title:** Cambodia HR & Labor Law RAG Knowledge Assistant  
**Project Type:** Foundation / Core Industry Task (Arrowstack 1-Month Generative AI Internship, Week 1)  
**Project Folder:** `project-1-rag-assistant`  
**Git Branch:** `project-1/rag-assistant`  
**Author:** hailinaGit  

---

## 1. Executive Summary & Business Use Case

* **Primary Stakeholder:** HR Personnel, Compliance Officers, and Employees in Cambodia.
* **The Business Problem:** Cambodian Labor Law and company Internal Regulations contain complex, strict rules regarding working hours, overtime rates, leaves, and seniority pay. Manually searching dense legal documents is slow, error-prone, and creates administrative bottlenecks.
* **The Solution:** A local Retrieval-Augmented Generation (RAG) assistant that answers policy questions in seconds. Every answer is strictly grounded in approved documents and includes verifiable citations pointing to the exact document and section.
* **Measurable Benefits:**
  * Reduces policy lookup time from 10 minutes to under 5 seconds.
  * Eliminates compliance risk from incorrect verbal advice.
  * 100% citation traceability for auditing and legal checks.

---

## 2. Problem Statement: Inputs, Outputs & Constraints

* **Inputs:**
  * Natural language question from an employee or HR officer (e.g. *"What is the overtime rate on Sundays?"*).
  * Optional configuration parameters: `top_k` chunks to retrieve (default: 3), model name (default: `llama3.2`), and temperature (default: `0.0`).
* **Outputs:**
  * Grounded answer synthesizing the facts found in the retrieved policy chunks.
  * Explicit citations list containing: `source` (document name), `section` (header/article), and `distance` (cosine similarity score).
  * Safe fallback message if the query is outside approved policies:
    > *"I cannot find this information in the approved policy documents."*
* **Key Constraints:**
  * **100% Offline / Local Execution:** Runs completely locally via ChromaDB and Ollama (`llama3.2`). No cloud API keys, zero API costs, and zero data privacy risk.
  * **Zero Hallucination Tolerance:** Must not guess, speculate, or quote laws from other jurisdictions (e.g. US labor rules).

---

## 3. Scope Boundaries

### In-Scope (Implemented)
* Ingestion, cleaning, and semantic chunking of Cambodian labor regulations.
* Local vector storage and cosine similarity search using **ChromaDB**.
* Grounded response generation using local **LangChain + Ollama (`llama3.2`)**.
* Citation extraction linking every statement to its source document and section.
* REST API deployment using **FastAPI** (`/health`, `/retrieve`, `/query`).
* Interactive web chat interface with sample question chips and citation inspection cards.
* Automated test harness (`tests/test_rag.py`) and 10-query evaluation benchmark (`docs/eval_results.md`).

### Out-of-Scope (Future Enhancements)
* Live integrations with external government or payroll databases.
* Multi-language translation into Khmer (focusing on structured English internal policy guidelines first).
* Multi-modal document processing (e.g. scanned handwritten PDFs).

---

## 4. Functional Requirements (FR)

| ID | Feature Name | Description | Delivered File |
| :--- | :--- | :--- | :--- |
| **FR-01** | **Document Ingestion & Chunking** | Clean raw text, split documents semantically along markdown section headers (`## Header`), and store chunks with metadata in ChromaDB. | [`src/ingest.py`](../src/ingest.py) |
| **FR-02** | **Semantic Vector Retrieval** | Accept a user question, query ChromaDB using cosine distance, and return the top-$k$ most relevant context chunks. | [`src/retrieve.py`](../src/retrieve.py) |
| **FR-03** | **Grounded Generation & Safety** | Feed retrieved context into a local LLM with temperature `0.0`. Enforce strict grounding and return an exact fallback message if context is missing. | [`src/generate.py`](../src/generate.py) |
| **FR-04** | **Citation Tracking** | Extract and return metadata (`source`, `section`, `distance`) with every generated response so users can verify the facts. | [`src/api.py`](../src/api.py) |
| **FR-05** | **Interactive User Interface** | Provide a clean web interface where users can ask questions, click sample chips, toggle retrieval vs generation modes, and inspect citations. | [`src/static/index.html`](../src/static/index.html) |

---

## 5. Technical Stack

* **Language:** Python 3.10+
* **Vector Database:** ChromaDB (persistent local storage, `all-MiniLM-L6-v2` embeddings, cosine distance)
* **LLM Engine:** Local Ollama (`llama3.2`) orchestrated with LangChain
* **API Framework:** FastAPI & Uvicorn
* **Data Validation:** Pydantic V2
* **Testing:** Pytest & Python assertion test suite
* **Version Control:** Git & GitHub monorepo structure

---

## 6. Success Metrics & Acceptance Criteria

| Metric Category | Target Standard | Achieved Score | Verification Method |
| :--- | :---: | :---: | :--- |
| **Grounding & Faithfulness** | $\ge 95\%$ | **100%** | All generated claims match retrieved context chunks. |
| **Hallucination Rate** | $< 5\%$ | **0.0%** | Out-of-scope queries trigger the strict fallback message. |
| **Citation Completeness** | $100\%$ | **100%** | Every response includes source document, section, and distance. |
| **Test Suite Pass Rate** | $100\%$ | **100%** | 5 automated assertion tests passing in `tests/test_rag.py`. |
| **Reproducibility** | $< 10\text{ min}$ | **Verified** | Fresh setup reproducible via instructions in `README.md`. |

---

## 7. Deliverables & Evidence Mapping (Handbook Section 11)

| Handbook Requirement | Project Deliverable | Location |
| :--- | :--- | :--- |
| **Source Code** | Ingestion, retrieval, LLM generator, FastAPI service, and UI | [`src/`](../src/) |
| **Policy Knowledge Base** | Curated Cambodian Labor Law regulations | [`data/raw/cambodia_hr_regulations.md`](../data/raw/cambodia_hr_regulations.md) |
| **Requirements Document** | Formal scope, business problem, and success criteria | [`docs/requirements.md`](./requirements.md) |
| **Evaluation Evidence** | 10-query benchmark matrix & automated test output | [`docs/eval_results.md`](./eval_results.md) |
| **Viva / Interview Prep** | Prepared answers to the 7 handbook interview defense questions | [`docs/viva_prep.md`](./viva_prep.md) |
| **Automated Test Suite** | 5 unit and regression assertion tests | [`tests/test_rag.py`](../tests/test_rag.py) |
| **10-Query LLM Benchmark** | End-to-end RAG evaluation script across Q01–Q10 | [`tests/evaluate_rag.py`](../tests/evaluate_rag.py) |
| **README Runbook** | Complete installation, execution, and API guide | [`README.md`](../README.md) |

---

## 8. Submission Artifacts Checklist (Handbook Section 11)
- [x] `docs/requirements.md` (This document)
- [x] `data/raw/cambodia_hr_regulations.md` (Approved Cambodian Labor Law & HR regulations)
- [x] `src/ingest.py` (Text cleaning, header-based chunking, and ChromaDB ingestion)
- [x] `src/retrieve.py` (Semantic cosine-similarity search and citation metadata retrieval)
- [x] `src/generate.py` (Grounded local Ollama `llama3.2` generation and fallback control)
- [x] `src/api.py` (FastAPI REST service)
- [x] `src/static/index.html` (Interactive RAG web chat interface)
- [x] `tests/test_rag.py` & `tests/evaluate_rag.py` (Automated unit test suite & 10-query LLM benchmark)
- [x] `docs/eval_results.md` (10-query benchmark evaluation matrix & test evidence)
- [x] `docs/viva_prep.md` (Handbook Section 16 interview defense guide)
- [x] `README.md` (Project overview and quickstart runbook)
