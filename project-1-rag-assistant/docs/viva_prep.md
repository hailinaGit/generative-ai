# Viva & Interview Preparation Guide: Cambodia HR RAG Assistant

**Project:** Project 1 — RAG Knowledge Assistant  
**Reference:** Internship Handbook Section 16 (Viva / Interview Questions) & Section 13 (Acceptance Criteria)  

---

### Q1: What business or user problem does the project solve, and how did you define success?
* **Problem:** HR officers, line managers, and employees in Cambodia spend significant time cross-referencing complex statutory labor provisions (MLVT guidelines, Internal Regulations, overtime premiums, and seniority pay). Mistakes lead to compliance liabilities or labor disputes.
* **Success Definition:**
  - $\ge 95\%$ grounding accuracy against approved texts.
  - $< 5\%$ hallucination rate.
  - $100\%$ citation traceability (source document, section header, distance score).

---

### Q2: Which design, technical, analytical or research decision had the biggest impact on the result?
* **Decision:** Implementing **Markdown section-level semantic chunking** rather than fixed token slicing (e.g. arbitrary 500-token windows).
* **Impact:** In legal and compliance documents, statutory clauses belong together. Splitting strictly along `## Header` boundaries preserved clause integrity (e.g., keeping overtime rate conditions unified) and eliminated chunk-boundary truncation errors.

---

### Q3: How did you validate the quality or correctness of your work?
* Through a two-tier verification harness:
  1. **Automated Unit Testing (`tests/test_rag.py`):** Programmatic assertions verifying chunk counts, cosine similarity rankings, citation schemas, and negative fallback triggers.
  2. **10-Query Benchmark Evaluation Set (`docs/eval_results.md`):** Testing positive retrievals, numerical thresholds, edge cases, and out-of-domain negative assertions.

---

### Q4: What edge cases, limitations or risks did you identify?
* **Out-of-Scope Queries:** Mitigated via strict prompt engineering enforcing zero external knowledge and a deterministic fallback message.
* **Language Limitations:** The current pilot ingests approved English-language corporate summaries; formal labor dispute cases in Cambodia require certified Khmer-language documents.
* **Dynamic Legal Updates:** Minimum wages and NSSF caps are updated annually by ministerial Prakas; the ingestion pipeline requires an automated version-refresh trigger.

---

### Q5: What would you change if this solution had to support 10× the users/data/workload?
* **Vector Store:** Migrate from embedded local ChromaDB to an enterprise distributed vector cluster (Qdrant, Milvus, or Pgvector).
* **Caching Layer:** Implement Redis semantic caching for high-frequency queries (e.g., standard annual leave questions), bypassing vector search and LLM calls.
* **Model Inference:** Decouple local Ollama execution by hosting quantized models on dedicated GPU endpoints via vLLM / Triton or serverless LLM APIs.
* **Worker Concurrency:** Scale FastAPI with multiple Uvicorn workers behind an NGINX load balancer.

---

### Q6: How would you explain the project to a non-technical stakeholder?
> *"It is an automated compliance assistant that acts like an expert digital librarian. Instead of guessing or searching through 30-page PDF handbooks, you ask a natural question, and it provides an exact answer strictly quoted from our approved labor regulations, complete with the legal chapter and section so you can double-check its work."*

---

### Q7: Which part of the project required the most independent problem-solving?
* Resolving vector similarity boundary edge cases. Irrelevant queries still return the nearest mathematical vector in vector space; solving this required combining cosine distance checks with a strict negative fallback prompt (`"If not found, reply EXACTLY: I cannot find this information in the approved policy documents."`) to ensure 0% hallucination.

