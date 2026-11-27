"""Core Document-to-Workflow Automation Engine (FR-01, FR-02, FR-03, FR-04).

Architecture:
1. Input Validation: Rejects empty or malformed documents before LLM invocation.
2. Grounded Routing Directory: Loads approved team rules & SLAs from `team_directory.md`.
3. Structured Action-Item Extraction: Uses local Ollama (`llama3.2`, temp=0.0) to extract
   typed JSON action items with confidence scores and verbatim source quotes.
4. Deterministic Safety & Confidence Controls:
   - Verifies `source_quote` against the original document text.
   - Routes low-confidence (< 0.70) or unknown-team items to `Manual Review`.
   - Enforces mandatory human validation for Legal & Compliance and Finance spend > $5,000.
"""
from __future__ import annotations

import json
import logging
import re
import sys
from enum import Enum
from pathlib import Path
from typing import Optional, TypeVar

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

SRC_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SRC_DIR.parent
for p in (str(SRC_DIR), str(PROJECT_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from models import (
    TEAM_QUEUE_CHANNELS,
    ActionItem,
    DocumentInput,
    ExtractionStatusEnum,
    PriorityEnum,
    TeamEnum,
    ValidationStatusEnum,
    WorkflowResult,
)

logger = logging.getLogger("document_workflow")
if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

DEFAULT_DIRECTORY_PATH = PROJECT_DIR / "data" / "routing_rules" / "team_directory.md"
CONFIDENCE_THRESHOLD = 0.70
FINANCE_APPROVAL_THRESHOLD = 5000.00
CURRENCY_PATTERN = re.compile(r"\$\s?([\d,]+(?:\.\d{1,2})?)")

E = TypeVar("E", bound=Enum)


def _safe_enum(enum_cls: type[E], value: object, default: E) -> E:
    """Parse an Enum value safely, falling back to default on unrecognized output."""
    if not isinstance(value, str):
        return default
    cleaned = value.strip()
    try:
        return enum_cls(cleaned)
    except ValueError:
        for member in enum_cls:
            if member.value.lower() == cleaned.lower():
                return member
        return default


def _normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def verify_source_quote(quote: str, document_text: str) -> bool:
    """Return True if the extracted source_quote appears verbatim (ignoring whitespace/case) in document_text."""
    norm_quote = _normalize_ws(quote)
    if len(norm_quote) < 6:
        return False
    return norm_quote in _normalize_ws(document_text)


def extract_max_currency(text: str) -> float:
    """Extract the largest USD dollar amount found in text, or 0.0 if none."""
    amounts: list[float] = []
    for raw in CURRENCY_PATTERN.findall(text):
        try:
            amounts.append(float(raw.replace(",", "")))
        except ValueError:
            continue
    return max(amounts, default=0.0)


class RoutingDirectory:
    """Loads and serves the approved team routing directory & SLA policy."""

    def __init__(self, directory_path: Path = DEFAULT_DIRECTORY_PATH) -> None:
        self.directory_path = directory_path
        self._sections: dict[str, str] = {}
        self.raw_text: str = ""
        self._load_directory()

    def _load_directory(self) -> None:
        if not self.directory_path.exists():
            logger.warning("Routing directory not found at %s.", self.directory_path)
            return

        self.raw_text = self.directory_path.read_text(encoding="utf-8")
        current_section = "Overview"
        buffer: list[str] = []

        for line in self.raw_text.splitlines():
            match = re.match(r"^##\s+(.*)", line)
            if match:
                if buffer:
                    self._sections[current_section] = "\n".join(buffer).strip()
                    buffer = []
                current_section = match.group(1).strip()
            else:
                buffer.append(line)

        if buffer:
            self._sections[current_section] = "\n".join(buffer).strip()

        logger.info("Loaded %d team routing sections into memory.", len(self._sections))

    @property
    def section_count(self) -> int:
        return len(self._sections)


EXTRACTION_SYSTEM_PROMPT = """You are an Enterprise Operations Workflow Automation Analyst.
Your job is to read the incoming operational document, extract concrete action items, and route each item strictly according to the Approved Team Routing Directory below.

Approved Team Routing Directory:
{routing_directory}

Return a STRICT JSON object with this exact structure:
{{
  "document_summary": "1-2 sentence summary of the document",
  "action_items": [
    {{
      "title": "Concise actionable task description",
      "owner_role": "Person or role mentioned, or null",
      "target_team": "Engineering" | "Finance" | "HR & People" | "Legal & Compliance" | "Customer Support" | "Operations" | "Manual Review",
      "priority": "Low" | "Medium" | "High" | "Critical",
      "due_date": "Deadline string or null",
      "confidence": 0.0 to 1.0,
      "source_quote": "Exact verbatim substring copied from the document supporting this task"
    }}
  ]
}}

Rules:
1. Zero Hallucination: Only extract action items explicitly supported by the document. Copy `source_quote` verbatim from the document.
2. Non-Actionable Documents: If the document is purely informational (e.g. a cafeteria menu, social announcement, or general greeting with no business task), return `"action_items": []`.
3. Ambiguous / Vague Fragments: If a sentence is too vague to identify a clear task or owner (e.g. "someone should look into that thing"), extract it with `target_team: "Manual Review"` and `confidence <= 0.55`.
4. Team Boundaries:
   - Production bugs, API 500s, database latency -> "Engineering"
   - Vendor invoices, POs, wire transfers, budgets -> "Finance"
   - Benefits, orientation, onboarding paperwork, leave -> "HR & People"
   - Contracts, NDAs, MSAs, GDPR/compliance audits -> "Legal & Compliance"
   - VIP client follow-ups, SLA credits, help-center updates -> "Customer Support"
   - Hardware/equipment procurement, warehouse/office logistics -> "Operations"
5. Output ONLY raw valid JSON. Do not wrap in markdown or commentary.
"""


def _strip_json_fences(raw_content: str) -> str:
    """Strip optional markdown ```json fences from LLM output."""
    text = raw_content.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    return text


class DocumentWorkflowEngine:
    """Orchestrates input validation, LLM action-item extraction, and deterministic routing guardrails."""

    def __init__(
        self,
        model_name: str = "llama3.2",
        temperature: float = 0.0,
        directory_path: Path = DEFAULT_DIRECTORY_PATH,
    ) -> None:
        self.model_name = model_name
        self.temperature = temperature
        self.directory = RoutingDirectory(directory_path)
        self.llm = ChatOllama(model=model_name, temperature=temperature)

    def _validate_single_item(
        self,
        doc: DocumentInput,
        idx: int,
        raw: dict,
        threshold: float,
    ) -> Optional[ActionItem]:
        """Validate one raw extracted item and enforce quote, confidence, and policy guardrails."""
        title = str(raw.get("title") or "").strip()
        if not title:
            return None

        team = _safe_enum(TeamEnum, raw.get("target_team"), TeamEnum.MANUAL_REVIEW)
        priority = _safe_enum(PriorityEnum, raw.get("priority"), PriorityEnum.MEDIUM)

        try:
            confidence = float(raw.get("confidence", 0.5))
        except (TypeError, ValueError):
            confidence = 0.5
        confidence = max(0.0, min(1.0, round(confidence, 2)))

        source_quote = str(raw.get("source_quote") or "").strip()
        quote_verified = verify_source_quote(source_quote, doc.content)

        reasons: list[str] = []
        requires_manual = False

        if not quote_verified:
            confidence = min(confidence, 0.65)
            requires_manual = True
            reasons.append("Source quote could not be verified verbatim in document.")

        if confidence < threshold:
            team = TeamEnum.MANUAL_REVIEW
            requires_manual = True
            reasons.append(f"Confidence {confidence:.2f} below {threshold:.2f} threshold.")

        if team == TeamEnum.MANUAL_REVIEW:
            requires_manual = True
            if not reasons:
                reasons.append("Routed to Manual Review due to ambiguous ownership or scope.")
        elif team == TeamEnum.LEGAL:
            requires_manual = True
            reasons.append("Mandatory human legal review required by POL-ROUTING-003.")
        elif team == TeamEnum.FINANCE:
            max_amt = max(
                extract_max_currency(source_quote),
                extract_max_currency(title),
                extract_max_currency(doc.content),
            )
            if max_amt > FINANCE_APPROVAL_THRESHOLD:
                requires_manual = True
                reasons.append(
                    f"Finance amount ${max_amt:,.2f} exceeds ${FINANCE_APPROVAL_THRESHOLD:,.2f} VP approval threshold."
                )

        validation_status = (
            ValidationStatusEnum.PENDING_VALIDATION
            if requires_manual
            else ValidationStatusEnum.AUTO_ROUTED
        )

        return ActionItem(
            item_id=f"ACT-{doc.doc_id}-{idx}",
            title=title,
            owner_role=raw.get("owner_role"),
            target_team=team,
            queue_channel=TEAM_QUEUE_CHANNELS[team],
            priority=priority,
            due_date=raw.get("due_date"),
            confidence=confidence,
            source_quote=source_quote or "(none)",
            quote_verified=quote_verified,
            requires_manual_review=requires_manual,
            review_reason=" ".join(reasons) if reasons else None,
            validation_status=validation_status,
        )

    def apply_routing_guardrails(
        self,
        doc: DocumentInput,
        raw_items: list[dict],
        confidence_threshold: Optional[float] = None,
    ) -> list[ActionItem]:
        """Validate extracted items, verify source quotes, and enforce confidence/policy guardrails."""
        threshold = CONFIDENCE_THRESHOLD if confidence_threshold is None else confidence_threshold
        validated_items: list[ActionItem] = []
        for idx, raw in enumerate(raw_items, 1):
            item = self._validate_single_item(doc, idx, raw, threshold)
            if item is not None:
                validated_items.append(item)
        return validated_items

    def process_document(self, doc: DocumentInput) -> WorkflowResult:
        """Run full Document-to-Workflow pipeline with input validation & deterministic guardrails."""
        content_clean = doc.content.strip()
        if len(content_clean) < 10:
            return WorkflowResult(
                doc_id=doc.doc_id,
                title=doc.title,
                extraction_status=ExtractionStatusEnum.REJECTED,
                document_summary="Rejected invalid or empty document.",
                action_items=[],
                rejection_reason="Document content is empty or too short (< 10 characters) for workflow extraction.",
            )

        prompt = ChatPromptTemplate.from_messages([
            ("system", EXTRACTION_SYSTEM_PROMPT),
            ("human", "Document ID: {doc_id}\nTitle: {title}\nType: {doc_type}\nContent:\n{content}"),
        ])

        llm = (
            self.llm
            if doc.model_name == self.model_name
            else ChatOllama(model=doc.model_name, temperature=self.temperature)
        )
        chain = prompt | llm
        try:
            res = chain.invoke({
                "routing_directory": self.directory.raw_text,
                "doc_id": doc.doc_id,
                "title": doc.title,
                "doc_type": doc.doc_type,
                "content": content_clean,
            })
            raw_content = _strip_json_fences(str(res.content))
            parsed = json.loads(raw_content)
            summary = str(parsed.get("document_summary") or f"Processed {doc.title}").strip()
            raw_items = parsed.get("action_items") or []
            if not isinstance(raw_items, list):
                raw_items = []

            action_items = self.apply_routing_guardrails(
                doc, raw_items, confidence_threshold=doc.confidence_threshold
            )
            needs_review = any(item.requires_manual_review for item in action_items)
            status = ExtractionStatusEnum.NEEDS_REVIEW if needs_review else ExtractionStatusEnum.COMPLETED

            return WorkflowResult(
                doc_id=doc.doc_id,
                title=doc.title,
                extraction_status=status,
                document_summary=summary,
                action_items=action_items,
            )
        except Exception as exc:
            logger.warning("Workflow extraction fallback triggered for %s: %s", doc.doc_id, exc)
            fallback_item = ActionItem(
                item_id=f"ACT-{doc.doc_id}-1",
                title=f"Manual triage required for: {doc.title}",
                target_team=TeamEnum.MANUAL_REVIEW,
                queue_channel=TEAM_QUEUE_CHANNELS[TeamEnum.MANUAL_REVIEW],
                priority=PriorityEnum.MEDIUM,
                confidence=0.30,
                source_quote=content_clean[:120],
                quote_verified=True,
                requires_manual_review=True,
                review_reason=f"LLM JSON parsing fallback triggered: {exc}",
                validation_status=ValidationStatusEnum.PENDING_VALIDATION,
            )
            return WorkflowResult(
                doc_id=doc.doc_id,
                title=doc.title,
                extraction_status=ExtractionStatusEnum.NEEDS_REVIEW,
                document_summary=f"Fallback manual review queued for {doc.title}.",
                action_items=[fallback_item],
            )
