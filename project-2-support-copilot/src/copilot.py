"""Core Copilot Engine for AI Customer Support Copilot (FR-01, FR-02, FR-03, FR-04).

Enterprise-grade architecture featuring:
1. Multi-task Structured Triage (Sentiment, Category, Urgency, Escalation Triggers).
2. Grounded Policy Knowledge Retrieval (Semantic section-matching).
3. Two-pass Verification: Deterministic Guardrails + Empathetic LLM Synthesis.
4. Fail-Safe Parsing: Fallback recovery with strict Pydantic V2 validation.
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

# Ensure project root and src are in python search path
SRC_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SRC_DIR.parent
for p in (str(SRC_DIR), str(PROJECT_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from models import (
    CategoryEnum,
    CopilotDraftResponse,
    CustomerTicket,
    PolicyCitation,
    SentimentEnum,
    TriageClassification,
    UrgencyEnum,
)

logger = logging.getLogger("support_copilot")
if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

E = TypeVar("E", bound=Enum)


def _safe_enum(enum_cls: type[E], value: object, default: E) -> E:
    """Parse an Enum value safely, falling back to default on unrecognized LLM output."""
    if not isinstance(value, str):
        return default
    try:
        return enum_cls(value.strip())
    except ValueError:
        return default

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_POLICY_PATH = BASE_DIR / "data" / "knowledge_base" / "support_policies.md"

# Safety Rule Regex Thresholds (Deterministic Pre-guards)
LEGAL_DISPUTE_PATTERN = re.compile(
    r"\b(lawyer|lawsuit|legal department|attorney|court|litigation|chargeback|subpoena)\b",
    re.IGNORECASE,
)
SECURITY_BREACH_PATTERN = re.compile(
    r"\b(unauthorized logins?|suspicious logins?|hacked|account breach|unknown ip)\b",
    re.IGNORECASE,
)
CURRENCY_AMOUNT_PATTERN = re.compile(r"\$\s?(\d+(?:\.\d{1,2})?)")
REFUND_SUPERVISOR_THRESHOLD = 100.00


class PolicyKnowledgeBase:
    """Manages section-indexed policy lookup from approved support documentation."""

    def __init__(self, policy_path: Path = DEFAULT_POLICY_PATH) -> None:
        self.policy_path = policy_path
        self._sections: dict[str, str] = {}
        self._load_policies()

    @property
    def section_count(self) -> int:
        """Number of loaded policy sections."""
        return len(self._sections)

    def _load_policies(self) -> None:
        if not self.policy_path.exists():
            logger.warning("Policy handbook not found at %s. Initializing empty KB.", self.policy_path)
            return

        raw_text = self.policy_path.read_text(encoding="utf-8")
        current_section = "General Support Overview"
        buffer: list[str] = []

        for line in raw_text.splitlines():
            header_match = re.match(r"^##\s+(.*)", line)
            if header_match:
                if buffer:
                    self._sections[current_section] = "\n".join(buffer).strip()
                    buffer = []
                current_section = header_match.group(1).strip()
            else:
                buffer.append(line)

        if buffer:
            self._sections[current_section] = "\n".join(buffer).strip()
        logger.info("Loaded %d policy sections into memory.", len(self._sections))

    def retrieve_relevant_policy(self, query: str) -> tuple[str, list[PolicyCitation]]:
        """Match query context to relevant sections using keyword & semantic priority."""
        q_lower = query.lower()
        matched_blocks: list[str] = []
        citations: list[PolicyCitation] = []

        mapping = [
            (["refund", "charged", "billing", "invoice", "payment", "$"], "1. Refund & Billing Policy", "14-day refund window & $100 frontline limit"),
            (["2fa", "password", "locked", "authenticator", "login", "account"], "2. Account Security & Access Recovery", "Identity verification & emergency 2FA reset"),
            (["shipping", "delivery", "carrier", "tracking", "package", "lost", "transit"], "3. Shipping, Delivery & Missing Orders", "Domestic SLA & free lost-package reshipment"),
            (["cancel", "downgrade", "subscription", "plan", "retention"], "4. Subscription Cancellation & Downgrades", "Cycle-end effective date & 60-day data retention"),
        ]

        for keywords, section_name, rule_desc in mapping:
            if any(k in q_lower for k in keywords) and section_name in self._sections:
                matched_blocks.append(f"### {section_name}\n{self._sections[section_name]}")
                citations.append(
                    PolicyCitation(
                        policy_name="support_policies.md",
                        section=section_name,
                        rule_applied=rule_desc,
                    )
                )

        # Fallback to general tone guidelines if no specific section triggered
        if not matched_blocks:
            tone_section = "5. Tone Guidelines & Safety Controls"
            if tone_section in self._sections:
                matched_blocks.append(f"### {tone_section}\n{self._sections[tone_section]}")

        return "\n\n".join(matched_blocks), citations


# --- System Prompts with Few-Shot Framing ---
TRIAGE_SYSTEM_PROMPT = """You are an expert Customer Support Operations Analyst.
Analyze the inbound ticket text and return a STRICT JSON object with these exact keys:
{{
  "sentiment": "Positive" | "Neutral" | "Frustrated" | "Angry",
  "category": "Billing" | "Technical Support" | "Account Security" | "Shipping & Delivery" | "Cancellation" | "Other / Uncategorized",
  "urgency": "Low" | "Medium" | "High" | "Critical",
  "key_issues": ["brief issue 1", "brief issue 2"],
  "escalate_to_human": true | false,
  "escalation_reason": "string or null"
}}

Rules:
1. Escalation (escalate_to_human):
   - Set escalate_to_human=true ONLY IF:
     (a) The customer threatens legal action, lawsuits, or bank chargebacks, OR
     (b) The customer demands a refund strictly greater than $100, OR
     (c) The customer reports an active unauthorized account hack / unknown IP login breach.
   - For ALL other tickets (routine refunds <= $100, lost 2FA phone, late/damaged shipping, cancellations, API/webhook errors, invoice updates, out-of-scope questions), you MUST set escalate_to_human=false and escalation_reason=null.
2. Category:
   - Refunds, double charges, invoices, and payment disputes -> "Billing".
   - Out-of-scope / unrelated topics (e.g. cryptocurrency trading) -> "Other / Uncategorized".
3. Urgency:
   - Legal threats, active security breaches -> "Critical".
   - Production outages, double charges, lost packages, 2FA lockouts -> "High".
   - Damaged non-critical items -> "Medium".
   - Routine cancellations, invoice edits, general questions -> "Low".
4. Output ONLY the raw valid JSON string. Do not wrap in markdown or commentary.
"""

DRAFT_SYSTEM_PROMPT = """You are an empathetic, professional Senior Customer Support Specialist.
Your task is to draft an official, grounded response to the customer ticket using ONLY the approved policy context below.

Brand Guidelines:
1. Tone: Empathetic, calm, solution-oriented, and reassuring.
2. Grounding: Rely strictly on the provided policy context. Never invent procedures or promise unauthorized cash payouts.
3. Off-Topic / Out of Scope: If the ticket is unrelated to company services or policies (e.g. crypto, stock advice, competitor software), state clearly and politely:
   "I cannot find this information in our approved support policies. I have routed your ticket to a specialist for review."
4. Structure:
   - Warm greeting using customer name
   - Empathetic acknowledgment of the exact problem
   - Clear, step-by-step resolution or next actions based on policy
   - Professional sign-off

Approved Policy Context:
{policy_context}
"""


class SupportCopilotEngine:
    """End-to-end Support Copilot orchestrator (Triage + Retrieval + Grounded Drafting)."""

    def __init__(
        self,
        model_name: str = "llama3.2",
        temperature: float = 0.0,
        policy_path: Path = DEFAULT_POLICY_PATH,
    ) -> None:
        self.model_name = model_name
        self.temperature = temperature
        self.kb = PolicyKnowledgeBase(policy_path)
        self.llm = ChatOllama(model=model_name, temperature=temperature)

    def _check_deterministic_escalation(self, text: str) -> tuple[bool, Optional[str]]:
        """Deterministic safety layer detecting legal threats, security breaches, and >$100 refund requests."""
        if LEGAL_DISPUTE_PATTERN.search(text):
            return True, "Triggered legal dispute or chargeback safety rule."

        if SECURITY_BREACH_PATTERN.search(text):
            return True, "Triggered compromised account / unauthorized login security rule."

        amounts = [float(a) for a in CURRENCY_AMOUNT_PATTERN.findall(text)]
        if any(amt > REFUND_SUPERVISOR_THRESHOLD for amt in amounts):
            return True, f"Requested refund amount exceeds frontline ${REFUND_SUPERVISOR_THRESHOLD:.2f} threshold."

        return False, None

    def triage_ticket(self, ticket: CustomerTicket) -> TriageClassification:
        """Classify sentiment, category, urgency, and human escalation need."""
        full_ticket_text = f"Subject: {ticket.subject}\nCustomer: {ticket.customer_name} ({ticket.customer_tier} tier)\nMessage: {ticket.message}"

        # 1. Deterministic safety check (authoritative policy guardrail)
        deterministic_escalate, deterministic_reason = self._check_deterministic_escalation(full_ticket_text)

        prompt = ChatPromptTemplate.from_messages([
            ("system", TRIAGE_SYSTEM_PROMPT),
            ("human", "{ticket_text}"),
        ])

        chain = prompt | self.llm
        try:
            res = chain.invoke({"ticket_text": full_ticket_text})
            raw_content = str(res.content).strip()
            # Clean markdown code blocks if returned
            if raw_content.startswith("```"):
                raw_content = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_content)

            parsed = json.loads(raw_content)

            # Enforce deterministic policy escalation (prevents both missed escalations and false positives)
            parsed["escalate_to_human"] = deterministic_escalate
            parsed["escalation_reason"] = deterministic_reason
            if LEGAL_DISPUTE_PATTERN.search(full_ticket_text) or SECURITY_BREACH_PATTERN.search(full_ticket_text):
                parsed["urgency"] = "Critical"

            return TriageClassification(
                sentiment=_safe_enum(SentimentEnum, parsed.get("sentiment"), SentimentEnum.NEUTRAL),
                category=_safe_enum(CategoryEnum, parsed.get("category"), CategoryEnum.OTHER),
                urgency=_safe_enum(UrgencyEnum, parsed.get("urgency"), UrgencyEnum.MEDIUM),
                key_issues=parsed.get("key_issues") or [ticket.subject],
                escalate_to_human=bool(parsed.get("escalate_to_human", False)),
                escalation_reason=parsed.get("escalation_reason"),
            )
        except Exception as exc:
            logger.warning("LLM triage parsing fallback triggered: %s", exc)
            return TriageClassification(
                sentiment=SentimentEnum.FRUSTRATED if "urgent" in full_ticket_text.lower() else SentimentEnum.NEUTRAL,
                category=CategoryEnum.BILLING if "$" in full_ticket_text else CategoryEnum.TECHNICAL,
                urgency=UrgencyEnum.CRITICAL if deterministic_escalate else UrgencyEnum.MEDIUM,
                key_issues=[ticket.subject],
                escalate_to_human=deterministic_escalate,
                escalation_reason=deterministic_reason,
            )

    def generate_draft(self, ticket: CustomerTicket) -> CopilotDraftResponse:
        """Run full Copilot pipeline: Triage -> Policy Retrieval -> Grounded Synthesis."""
        # Step 1: Triage
        triage = self.triage_ticket(ticket)

        # Step 2: Policy Retrieval
        combined_query = f"{ticket.subject} {ticket.message}"
        policy_context, citations = self.kb.retrieve_relevant_policy(combined_query)

        # Step 3: Synthesis
        prompt = ChatPromptTemplate.from_messages([
            ("system", DRAFT_SYSTEM_PROMPT),
            (
                "human",
                "Customer: {customer_name}\nTier: {customer_tier}\nSubject: {subject}\nMessage:\n{message}",
            ),
        ])

        chain = prompt | self.llm
        res = chain.invoke({
            "policy_context": policy_context,
            "customer_name": ticket.customer_name,
            "customer_tier": ticket.customer_tier,
            "subject": ticket.subject,
            "message": ticket.message,
        })

        clean_draft = str(res.content).strip()
        # Clean out any stray markdown bold asterisks for clean UI rendering
        clean_draft = re.sub(r"\*\*(.*?)\*\*", r"\1", clean_draft).replace("**", "")

        # Step 4: Build internal reasoning notes
        if triage.escalate_to_human:
            internal_notes = (
                f"[ESCALATION REQUIRED]: {triage.escalation_reason} "
                f"Do not dispatch without supervisor sign-off."
            )
        else:
            internal_notes = (
                f"Triage: {triage.category.value} | Sentiment: {triage.sentiment.value} | "
                f"Urgency: {triage.urgency.value}. Derived from {len(citations)} policy sections."
            )

        return CopilotDraftResponse(
            ticket_id=ticket.ticket_id,
            triage=triage,
            draft_reply=clean_draft,
            internal_notes=internal_notes,
            citations=citations,
            requires_supervisor_approval=triage.escalate_to_human,
        )


if __name__ == "__main__":
    # Self-test harness
    engine = SupportCopilotEngine()
    sample = CustomerTicket(
        ticket_id="TCK-TEST",
        customer_name="Sarah Jenkins",
        customer_tier="Pro",
        subject="Double charged for Pro plan",
        message="I was charged twice ($49.00 each) on Nov 10th. Please refund the extra charge!",
    )
    draft_res = engine.generate_draft(sample)
    print("\n--- TRIAGE ---")
    print(draft_res.triage.model_dump_json(indent=2))
    print("\n--- DRAFT REPLY ---")
    print(draft_res.draft_reply)
    print("\n--- INTERNAL NOTES ---")
    print(draft_res.internal_notes)

