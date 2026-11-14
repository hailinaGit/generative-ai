# Cambodia HR & Labor Law RAG Knowledge Assistant

An internal Retrieval-Augmented Generation (RAG) assistant designed for HR officers, legal compliance teams, and employees in Cambodia. It provides verified, grounded answers strictly derived from Cambodian Labor Law and internal company regulations with explicit section citations.

---

## Key Features

- **Jurisdiction-Specific:** Grounded strictly in Cambodian Labor Law (Internal Regulations, MLVT guidelines, NSSF, overtime rates, maternity, and seniority pay).
- **100% Local & Offline Stack:**
  - **Vector DB:** ChromaDB with local embeddings.
  - **LLM:** Local LLM via LangChain + Ollama (`llama3.2`, `mistral`, etc.) — zero third-party API dependencies and zero API costs.
- **Strict Grounding (FR-03):** Temperature set to `0.0` with explicit system prompt rules preventing hallucinations. Uncovered topics automatically trigger a clear fallback message.
- **Citations & Auditing (FR-04):** Every statement links to the source markdown/document and section header.
- **FastAPI Deployment:** Ready-to-serve REST API with interactive Swagger UI.

---

## Repository Structure

```text
project-1-rag-assistant/
├── data/
│   ├── raw/
│   │   └── cambodia_hr_regulations.md  # Ground truth Cambodian policy doc
├── docs/
│   ├── eval_results.md                # 10-query benchmark matrix & test evidence
│   ├── requirements.md                # Project requirements & acceptance criteria
│   └── viva_prep.md                   # Viva & interview defense answers (Handbook Sec 16)
├── src/
│   ├── api.py                         # FastAPI web service
│   ├── generate.py                    # Local LangChain Ollama RAG generation
│   ├── ingest.py                      # Text cleaning, chunking & ChromaDB loader
│   └── retrieve.py                    # Semantic search & citation retrieval
├── tests/
│   ├── evaluate_rag.py                # 10-query end-to-end LLM benchmark script
│   └── test_rag.py                    # Automated test & assertion harness
├── requirements.txt                   # Project dependencies
└── README.md
```

---

## Quickstart Guide

### 1. Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com/) installed and running on your machine:
  ```bash
  ollama serve
  ollama pull llama3.2
  ```

### 2. Environment Setup
```bash
# From the repository root
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Step 1: Document Ingestion (Phase 2)
Ingest and chunk the Cambodian labor documents into ChromaDB:
```bash
cd project-1-rag-assistant
python src/ingest.py --reset
```
*Output: `Ingested 1 files -> 5 chunks (collection total: 5)`*

### 4. Step 2: Semantic Retrieval Test (Phase 3)
Test cosine similarity retrieval from the terminal:
```bash
python src/retrieve.py "How many days of annual leave do employees get?"
python src/retrieve.py "What are the overtime pay rates for working on Sundays?"
```

### 5. Step 3: Grounded Local Generation (Phase 4)
Ask questions to the local LLM with citations:
```bash
python src/generate.py "What is the policy for maternity leave duration and pay?"
```

### 6. Step 4: Run the FastAPI Service
Launch the internal API:
```bash
uvicorn src.api:app --reload --port 8000
```
Open **[http://localhost:8000/docs](http://localhost:8000/docs)** to test the interactive Swagger documentation.

#### Example API Request:
```bash
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"question": "What is the overtime rate for working on public holidays?"}'
```

---

## Testing & Evaluation (Phase 5)

Run the automated test harness:
```bash
python tests/test_rag.py
```
This validates:
- ChromaDB collection readiness.
- Retrieval accuracy for key labor queries (annual leave, overtime, maternity).
- 100% citation completeness.

Run the 10-query end-to-end LLM benchmark (requires Ollama running):
```bash
python tests/evaluate_rag.py
```
This evaluates Q01–Q10 from [docs/eval_results.md](docs/eval_results.md) and reports Grounding & Faithfulness (100.0%), Hallucination Rate (0.0%), Citation Completeness (100.0%), and Fallback & Safety Accuracy (100.0%).

