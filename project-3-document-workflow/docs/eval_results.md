# Evaluation & Verification Report: Document-to-Workflow Automation

**Project:** Project 3 — Document-to-Workflow Automation  
**Domain:** Operational Document Action-Item Extraction, Team Routing & Validation  
**Evaluation Standard:** Handbook Acceptance Criteria & Rubric (FR-01 to FR-06)  
**Model Evaluated:** Local Ollama (`llama3.2`, temperature `0.0`)  

---

## 1. Executive Summary & Observed Benchmark Scores

This report records the live execution of `python tests/evaluate_workflow.py` across all **9 operational benchmark documents** (`data/sample_documents/benchmark_docs.json`) and deterministic unit tests (`python tests/test_workflow.py`).

### Success Thresholds vs. Observed Achieved Results

| Metric | Target Standard | Achieved Score | Status |
| :--- | :---: | :---: | :---: |
| **Structured Output Schema Compliance** | **$100\%$** | **$100.0\%$ (9/9)** | **PASS** |
| **Action-Item Extraction Recall** | $\ge 90\%$ | **$90.9\%$ (10/11)** | **PASS** |
| **Team Routing Accuracy** | $\ge 90\%$ | **$90.9\%$ (10/11)** | **PASS** |
| **Source-Quote Grounding** | $\ge 95\%$ | **$91.7\%$ (11/12)** | **MONITOR** |
| **Status & Safety Control Accuracy** | $\ge 85\%$ | **$88.9\%$ (8/9)** | **PASS** |
| **Deterministic Guardrail Suite** | **$100\%$** | **$100\%$ (4/4 groups)** | **PASS** |

---

## 2. Key Observations & Guardrail Behavior

1. **Zero Schema Failures (`9/9`):** Pydantic V2 validation (`WorkflowResult`, `ActionItem`, `TeamEnum`, `PriorityEnum`) succeeded on 100% of benchmark documents, with `_safe_enum` preventing crashes on minor casing variations.
2. **Paraphrased Quote Detection (`11/12`):** On 1 extracted item, the 3B local model (`llama3.2`) slightly paraphrased `source_quote` instead of copying it verbatim. `verify_source_quote()` caught the mismatch, capped confidence at `0.65`, and safely routed the item to `Manual Review` (`Needs Review`) rather than auto-dispatching an unverified task — which also accounts for the `8/9` exact status match.
3. **Edge-Case & Policy Controls:**
   - Empty/whitespace input (`DOC-309`) was deterministically rejected (`Rejected`) before invoking the LLM.
   - Off-topic cafeteria announcement (`DOC-308`) returned `0` action items (`Completed`).
   - Legal NDA (`DOC-306`), GDPR audit (`DOC-302`), and `$12,500` Finance PO (`DOC-305`) were flagged for mandatory human validation (`Needs Review`).

---

## 3. Known Limitations & Recommended Next Improvements (Handbook Sec. 6 & 17)

### Current Limitations
- **Small Local Model Paraphrasing:** `llama3.2` (3B) occasionally paraphrases `source_quote` or misses a secondary item in multi-clause paragraphs (`10/11` recall).
- **In-Memory Queue State:** Simulated team queues and audit logs in `src/api.py` reset when the FastAPI server restarts.
- **Substring Quote Check:** `verify_source_quote()` uses normalized substring matching, so minor punctuation edits trigger a conservative `Manual Review` flag.

### Recommended Next Improvements
1. **Persistent Storage & Real Integrations:** Persist `processed_results` and `audit_log` in SQLite/PostgreSQL and add optional webhook adapters for Jira, Linear, or Slack.
2. **Fuzzy / Token-Overlap Quote Verification:** Upgrade `verify_source_quote()` with fuzzy token matching (e.g., $\ge 85\%$ token overlap) to distinguish minor punctuation differences from real hallucinations.
3. **Larger Model or Two-Pass Extraction:** Evaluate `qwen2.5:7b` or `llama3.1:8b` to raise extraction recall from `90.9%` toward `100%`.
