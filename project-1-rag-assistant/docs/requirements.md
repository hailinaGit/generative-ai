# Project Requirements & Scope Document: RAG Knowledge Assistant (Cambodia HR Compliance)

**Project Type:** Foundation / Core Industry Task (Arrowstack 1-Month Generative AI Internship, Week 1)  
**Project Folder:** `project-1-rag-assistant`  
**Git Branch:** `project-1/rag-assistant`  
**Author:** hailinaGit  

---

## 1. Executive Summary & Business Use Case
* **Project Name:** RAG Knowledge Assistant[cite: 3]
* **Primary Stakeholder:** HR Personnel and Legal Compliance Officers in Cambodia[cite: 3]
* **Business Problem:** HR teams frequently need to reference complex labor regulations and internal company policies to answer employee queries quickly and accurately, reducing compliance risks and administrative bottlenecks.
* **Decision Enabled:** Empowers staff to instantly retrieve verified rules regarding leave, working hours, and benefits aligned with local company standards[cite: 3].

---

## 2. Scope Boundaries
* **In-Scope:**
  * Ingestion of localized company HR handbooks or policy documents (Markdown/Text format).
  * Local embedding generation and storage using ChromaDB[cite: 3].
  * Top-$k$ semantic retrieval and grounded response generation with strict citation tracking[cite: 3].
  * FastAPI deployment for internal querying[cite: 3].
* **Out-of-Scope (for Project 1):**
  * Live integration with enterprise payroll or government databases.
  * Multi-language translation models (focusing on structured English corporate policies/local guidelines first).
  
---

## 3. Functional Requirements
* **FR-01 (Document Ingestion):** The system must ingest approved text/PDF documents, clean the text, and split them into manageable chunks with overlap.
* **FR-02 (Vector Search):** Given a natural language query, the retrieval engine must fetch the top-k relevant chunks using cosine similarity[cite: 1].
* **FR-03 (Grounded Generation):** The LLM must synthesize an answer strictly derived from the retrieved context chunks, appending a fallback message ("I cannot find this information in the approved policy documents") if the context is insufficient.
* **FR-04 (Citations):** Every generated response must include explicit citations pointing to the source document and section[cite: 1].

---

## 4. Technical Requirements & Suggested Stack
* **Language:** Python 3.10+[cite: 1]
* **Orchestration / Framework:** LangChain or LlamaIndex (or lightweight custom Python scripts)
* **Embeddings & LLM:** OpenAI API or local models (e.g., Hugging Face / Ollama)[cite: 1]
* **Vector Database:** ChromaDB or FAISS[cite: 1]
* **API Framework:** FastAPI[cite: 1]
* **Version Control:** Git / GitHub repository with a structured `docs/` and `src/` directory[cite: 1]

---

## 5. Success Metrics & Acceptance Criteria
| Metric Category | Target Standard / Threshold | Verification Method |
| :--- | :--- | :--- |
| **Grounding & Faithfulness** | $\ge 95\%$ of generated statements must be directly supported by retrieved context. | Manual spot-check of a 10-query test set. |
| **Hallucination Rate** | $< 5\%$ unsupported claims or fabricated policy details[cite: 1]. | Test set evaluation against edge-case queries not present in the docs. |
| **Citation Accuracy** | $100\%$ of answers derived from documents must include correct source file references[cite: 1]. | Automated assertion checks in test scripts. |
| **Reproducibility** | A mentor or reviewer must be able to spin up the service using the `README.md` instructions within 10 minutes[cite: 1]. | Clean-environment clone and test run. |
