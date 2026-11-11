# Generative AI Internship — Portfolio Repository

> **Program:** Arrowstack 1-Month Generative AI Internship  
> **Structure:** 3 Progressive, Portfolio-Oriented Industry Projects  
> **Working Mode:** Individual, Mentor-Reviewed, Evidence-Based Delivery  

---

## 📁 Repository Overview

This repository contains the end-to-end deliverables, code, tests, and documentation for the three core internship projects:

```text
.
├── generative-ai/                    # Project 1: RAG Knowledge Assistant (Completed)
├── customer-support-copilot/         # Project 2: AI Customer Support Copilot (In Progress)
└── workflow-automation/              # Project 3: Document-to-Workflow Automation (Upcoming)
```

---

## 🚀 Projects Summary

### [Project 1: RAG Knowledge Assistant (Cambodia HR Compliance)](./generative-ai)
- **Domain:** Cambodian Labor Law & Internal Corporate HR Policies.
- **Key Features:**
  - Semantic section chunking & local ChromaDB vector store.
  - Strict grounding ($\ge 95\%$) with temperature `0.0` and fallback safety controls for out-of-scope topics.
  - Full citation traceability (`source`, `section`, `distance`).
  - FastAPI deployment (`/health`, `/retrieve`, `/query`) + Interactive Web Chat UI.
  - Automated 5-test assertion suite + 10-query benchmark evaluation report.
- **Status:** **Completed & Verified**

---

### [Project 2: AI Customer Support Copilot](./customer-support-copilot)
- **Domain:** Support Ticket Triage, Grounded Draft Synthesis & Human-in-the-Loop Review.
- **Key Features:**
  - Automated ticket context extraction, sentiment analysis & priority tagging.
  - Retrieval-grounded response generation from approved internal knowledge.
  - Human review approval/edit mechanism before final message dispatch.
  - Structured output schemas (Pydantic / JSON schema).
  - Evaluation suite testing response helpfulness, safety, and edit ratios.
- **Status:** **In Progress**

---

### [Project 3: Document-to-Workflow Automation](./workflow-automation)
- **Domain:** Action item extraction, routing, confidence validation & workflow dispatch.
- **Status:** **Upcoming**

---

## 🌿 Git Branch Organization

Each project is developed on its own dedicated branch:
- `main` — Consolidated master branch containing all reviewed projects.
- `project-1/rag-assistant` — Dedicated branch for Project 1.
- `project-2/support-copilot` — Active branch for Project 2 development.
- `project-3/workflow-automation` — Upcoming branch for Project 3.
