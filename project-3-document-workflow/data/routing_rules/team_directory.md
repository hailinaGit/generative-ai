# Approved Team Routing Directory & Operational SLA Policy

**Document ID:** `POL-ROUTING-003`  
**Owner:** Business Operations & PMO  
**Effective Date:** 2026-11-01  

---

## 1. Engineering (`#eng-triage` | Owner: Engineering Lead)
* **Business Function:** Software reliability, production incident remediation, bug fixes, API/webhook maintenance, database performance, and CI/CD infrastructure.
* **Routing Keywords:** `bug`, `outage`, `API`, `database`, `deploy`, `latency`, `hotfix`, `server`, `500 error`, `pipeline`, `timeout`, `read-replica`.
* **Approval & Guardrails:** Production hotfixes and database changes require peer review before deployment; no customer-facing financial promises.
* **Target SLA:** Critical = 2 hours | High = 4 hours | Medium = 1 business day | Low = 3 business days.

## 2. Finance (`#ap-finance` | Owner: Finance Controller)
* **Business Function:** Corporate Accounts Payable (AP), vendor invoices, purchase orders (POs), wire transfers, employee expense reimbursements, and departmental budget approvals. *(Note: Customer-facing SLA credits or subscription disputes belong to Customer Support, not AP.)*
* **Routing Keywords:** `invoice`, `vendor`, `wire`, `purchase order`, `PO`, `reimbursement`, `expense`, `budget`, `accounts payable`, `tax`.
* **Approval & Escalation Thresholds:**
  * $\le \$5,000.00\text{ USD}$: Standard AP processing queue.
  * $> \$5,000.00\text{ USD}$: Mandatory VP Finance sign-off (`requires_manual_review: true`).
* **Target SLA:** High = 1 business day | Medium = 2 business days | Low = 5 business days.

## 3. HR & People (`#people-ops` | Owner: HR Operations Manager)
* **Business Function:** Employee onboarding paperwork, benefits enrollment, new-hire orientation scheduling, leave/attendance compliance, performance cycles, and offboarding coordination. *(Hardware/IT provisioning is handled by Operations.)*
* **Routing Keywords:** `onboarding`, `offboarding`, `new hire`, `employee`, `orientation`, `benefits`, `leave`, `training`, `performance review`.
* **Target SLA:** High = 1 business day | Medium = 2 business days | Low = 5 business days.

## 4. Legal & Compliance (`#legal-review` | Owner: General Counsel)
* **Business Function:** Commercial contract redlines (NDA, MSA, DPA), regulatory & GDPR privacy audits, vendor compliance reviews, subpoenas, and intellectual property or liability disputes.
* **Routing Keywords:** `contract`, `NDA`, `MSA`, `GDPR`, `compliance`, `audit`, `legal`, `subpoena`, `privacy`, `regulation`, `liability`, `lawsuit`.
* **Mandatory Guardrail:** All Legal & Compliance action items require human legal review (`requires_manual_review: true`) before any external commitment.
* **Target SLA:** Critical = 4 hours | High = 1 business day | Medium = 3 business days.

## 5. Customer Support (`#cx-escalations` | Owner: Support Team Lead)
* **Business Function:** Enterprise/VIP account follow-ups, customer SLA credit notifications, help-center documentation updates, and escalated customer ticket resolution.
* **Routing Keywords:** `customer`, `client`, `VIP`, `support ticket`, `SLA credit`, `help center`, `account manager`, `escalation`.
* **Target SLA:** High = 4 hours | Medium = 1 business day | Low = 3 business days.

## 6. Operations (`#ops-desk` | Owner: Operations Manager)
* **Business Function:** IT hardware & workspace provisioning, warehouse/office logistics, equipment procurement, facility requests, and cross-departmental scheduling.
* **Routing Keywords:** `facilities`, `office`, `warehouse`, `logistics`, `equipment`, `scanner`, `laptop`, `procurement`, `workspace`, `inventory`, `schedule`.
* **Target SLA:** High = 1 business day | Medium = 2 business days | Low = 5 business days.

## 7. Manual Review (`#workflow-exceptions` | Owner: Operations Coordinator)
* **Trigger Conditions:**
  1. Extracted `confidence < 0.70` due to vague ownership, missing actionability, or ambiguous scope.
  2. Target team does not match an approved business unit above.
  3. High-risk overrides: Legal & Compliance items or Finance spend $> \$5,000.00\text{ USD}$.
  4. Invalid, corrupted, or contradictory input documents.
* **Non-Actionable Documents:** Purely informational announcements (e.g., social events, cafeteria menus) must return `0` action items rather than inventing tasks.
