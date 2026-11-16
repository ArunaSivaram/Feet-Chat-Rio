# PRD: NovaCell AI Telecom Support Assistant (v1)

**Author:** Product · **Status:** Draft v1 · **Last updated:** 2026-11-15

## TL;DR

NovaCell's support operation is overloaded by Tier-1 questions that are already answered somewhere in our FAQ, resolved-ticket history, or PDF user guides — but customers can't find them. We will ship a web- and in-app conversational assistant that answers these questions in plain language, **grounded exclusively** in those three sources, with inline citations and a graceful handoff to a human when it isn't confident. The v1 success bar is a **25% deflection rate** on self-serve Tier-1 contact volume within 90 days of GA, at a **groundedness audit score ≥ 95%** and **p95 answer latency ≤ 4s**, with no regression to CSAT.

---

## 1. Problem & Objective

**Problem.** Support contacts are NovaCell's largest controllable cost center and our lowest-CSAT touchpoint. The majority of inbound volume is Tier-1 — questions whose answers already exist in NovaCell documentation (data usage, bill queries, SIM/eSIM activation, roaming setup, voice issues, basic account tasks). Those answers today live in three disconnected places: a public FAQ, a resolved-tickets database, and PDF user guides. No surface lets a customer ask a plain-language question and get a consolidated, trustworthy answer. The result: customers wait on hold for things an FAQ could resolve, agents burn out on repetitive tickets, and the answers customers do get are inconsistent across channels.

**Hypothesis.** If we expose a single conversational surface, grounded in all three knowledge sources, that cites its sources and escalates when uncertain, a material share of Tier-1 contacts will self-resolve before touching an agent — without eroding trust.

**Objective (v1).** Deflect **≥ 25% of Tier-1 self-serve-eligible contacts** within 90 days of GA, while holding **groundedness ≥ 95%**, **CSAT on bot-handled sessions ≥ 4.0/5**, and **cost-per-deflected-contact ≤ 25% of agent-handled cost**.

---

## 2. Target Users & Key Use Cases

**Primary users:** NovaCell subscribers who would otherwise call 611, open a chat with an agent, or abandon. Secondary skew toward tech-literate users first (web / MyTelecom app), broadening as trust develops.

**Secondary users:**
- **Support Ops (content owners):** maintain the FAQ, curate resolved tickets, upload new guide PDFs — must do so **without an engineering release**.
- **Human agents (downstream):** receive escalations with full conversation context.

### Top use cases (v1)

| # | Use case | Sample question | Primary source(s) |
|---|---|---|---|
| 1 | Diagnose slow / dropped data | "Why is my internet so slow today?" | FAQ, Guide |
| 2 | Explain a bill charge (non-personalized) | "What does the $15/day EU roaming charge cover?" | FAQ, Guide |
| 3 | SIM / eSIM activation help | "I inserted my new SIM an hour ago and it still says No Service." | FAQ, Tickets |
| 4 | Roaming setup before travel | "How do I turn on roaming before I fly to France tomorrow?" | FAQ, Guide |
| 5 | Voice-call troubleshooting | "My calls keep dropping — what should I check?" | FAQ, Tickets |
| 6 | Account & app how-tos | "How do I set up AutoPay?" | FAQ |
| 7 | Feature enablement (VoLTE, Wi-Fi calling, hotspot) | "How do I turn on Wi-Fi calling?" | FAQ, Guide |

**Explicitly out of the primary user set in v1:** enterprise/B2B customers (different plan structures, SLAs), prepaid-only international customers (localization pending).

---

## 3. Scope

### In scope for v1

- Conversational web widget (NovaCell site) and in-app surface (MyTelecom app WebView).
- Retrieval-augmented generation over three sources: `faq.csv`, `tickets.db` (resolved tickets only, PII-scrubbed), `telecom_guide.pdf`.
- Grounded answers with inline citations to source snippets.
- "I don't know" behavior and confidence-gated human escalation.
- Support Ops self-serve console to add/update/retire content and trigger re-index.
- English only.
- Session-level analytics and a weekly groundedness audit sample.

### Out of scope for v1 — with rationale

| Out of scope | Rationale |
|---|---|
| Live billing / CRM reads (e.g., "What's my balance?") | No approved integration path yet; would introduce PII and auth scope we can't secure in the launch window. |
| Transactional actions (change plan, add bundle, pay bill) | Writes require auth, idempotency, and reversibility we can't harden for v1. Read-only keeps blast radius small. |
| Phone / voice channel | Different latency and ASR constraints; validate chat first. |
| Multilingual (ES, FR, etc.) | Groundedness evaluation is harder cross-lingually; add once English audit is stable. |
| Agent copilot (suggesting answers to live agents) | Different UX surface and risk profile; v2. |
| Fine-tuned model | Prompting + RAG hits quality bar at lower operational cost; revisit only if audit fails. |
| Proactive outreach (e.g., "we see your signal is weak") | Requires network telemetry access not in v1 integration scope. |

---

## 4. Functional Requirements

| # | Requirement | Detail |
|---|---|---|
| F1 | Multi-source ingestion | Ingest FAQ (CSV), resolved tickets (SQLite export, status = resolved only, PII-scrubbed), and PDF guides. Each chunk carries `source`, `source_id`, `last_updated`, `owner`. |
| F2 | Indexing | Chunk → embed → store in vector index. Chunk size ≤ 500 tokens with 50-token overlap. Re-embedding triggered by Support Ops publish action. |
| F3 | Retrieval | Hybrid retrieval (BM25 + dense), top-k = 8, re-ranker trims to top-3 for the LLM prompt. |
| F4 | Grounded answering | Model is prompted to answer **only from retrieved chunks**. If retrieval returns no chunk above confidence threshold `τ`, respond with the "I don't know" template and offer escalation. |
| F5 | Citations | Every answer includes 1–3 inline citations rendering as `[FAQ · Billing]`, `[Guide · p.12]`, or `[Ticket · 2025-08]`. Clicking opens the source snippet. |
| F6 | "I don't know" behavior | Templated response: acknowledge the gap, propose the most likely adjacent topic, offer to escalate to a human. Never guess. |
| F7 | Escalation triggers | Any of: retrieval confidence below `τ`; user explicitly asks for a human; user frustration signals (repeat of same question, "this didn't help"); out-of-scope topic (billing specifics, account changes); 3 failed clarification turns. |
| F8 | Escalation handoff payload | Transcript, retrieved sources, detected intent, user-provided identifiers (if any), and the reason code for escalation. Delivered to the existing agent console queue with routing hint (e.g., "roaming", "SIM"). |
| F9 | Multi-turn conversation | Session memory within a single conversation (up to 20 turns). No cross-session memory in v1. |
| F10 | Clarification | If intent is ambiguous (e.g., "my phone isn't working"), ask **one** targeted clarifying question before retrieving. Cap clarification turns at 2. |
| F11 | Guardrails | Refuse requests outside Tier-1 telecom support (coding help, general knowledge, competitors), refuse to discuss other customers' accounts, refuse to invent prices/policies. Toxicity and jailbreak filters on input and output. |
| F12 | Support Ops console | Non-engineering UI to: upload/replace PDFs, edit FAQ rows, approve/retire resolved tickets, preview retrieval output for a test question, trigger re-index, view content freshness age per source. |
| F13 | Content freshness | Each source has a `last_updated` stamp surfaced in Ops console. Any source older than 90 days triggers a weekly review nudge to its owner. |
| F14 | Observability | Per-turn logs: query, retrieved chunks, confidence, answer, citations, escalation flag. Admin UI to inspect any session. |
| F15 | Feedback | Thumbs up / thumbs down per answer + optional free-text. Feeds into weekly audit queue. |

---

## 5. Non-Functional Requirements

| Dimension | Target | Measurement |
|---|---|---|
| Groundedness | ≥ 95% of audited answers rated "fully supported by cited source" | Weekly manual audit of a stratified random sample of 200 sessions |
| Answer accuracy (helpfulness) | ≥ 90% "answered the user's actual question" on audited sample | Same weekly audit, second rubric dimension |
| Latency — first token | p50 ≤ 1.5s, p95 ≤ 2.5s | Server-side telemetry |
| Latency — full answer | p50 ≤ 2.5s, p95 ≤ 4.0s | Server-side telemetry |
| Availability | 99.5% monthly for the chat endpoint | Standard uptime monitoring |
| Cost per conversation | ≤ $0.08 blended (inference + retrieval) `[assumption]` | Per-session cost metering |
| Privacy | No PII leaves NovaCell's VPC; resolved-ticket corpus PII-scrubbed pre-indexing; no cross-session user memory in v1 | Pre-ingest scrubber + DLP scan; audit |
| Security | All retrieval and inference traffic over TLS inside VPC; secrets in KMS; access-logged Support Ops console | SecOps review before GA |
| Accessibility | WCAG 2.1 AA for the chat widget | Pre-GA a11y audit |

---

## 6. Success Metrics

**North Star:** **Tier-1 deflection rate** — share of Tier-1 self-serve-eligible contacts that complete the session in the bot without human escalation **and** receive a thumbs-up or no negative signal. **v1 target: ≥ 25% within 90 days of GA.**

| Metric | Type | Target | Method |
|---|---|---|---|
| Tier-1 deflection rate (North Star) | Lagging | ≥ 25% by day 90 | Session outcome tagging + contact-center volume delta |
| Groundedness audit score | Leading | ≥ 95% | Weekly 200-session manual audit |
| CSAT on bot-handled sessions | Lagging | ≥ 4.0 / 5 | Post-session 1-tap survey |
| Escalation rate | Leading | 20–35% (healthy band; too low = overreach, too high = underpowered) | Session telemetry |
| Containment on escalated conversations | Lagging | Agent "context was useful" ≥ 80% | Agent 1-click rating on handoff payload |
| Cost per deflected contact | Lagging | ≤ 25% of agent-handled cost | Finance monthly reconciliation |
| Answer latency p95 | Leading | ≤ 4s full answer | Server telemetry |
| Content freshness | Leading | 100% of sources ≤ 90 days old at any time | Ops console report |

A green launch requires North Star + all leading indicators at target for two consecutive weeks post-GA.

---

## 7. Risks, Assumptions, Open Questions

### Risks

- **Groundedness regression under long tail.** Rare questions may retrieve weakly-related chunks that the model stitches into a plausible-but-wrong answer. **Mitigation:** strict retrieval threshold `τ`, "I don't know" bias, pre-GA red-team pass, weekly audit.
- **Users treat the bot as billing-aware.** They ask "what's my balance?" and feel misled when the bot can't answer. **Mitigation:** explicit scope statement in opening turn, polished out-of-scope template, one-tap escalation.
- **Support Ops bottleneck.** If Ops can't keep content fresh, groundedness rots silently. **Mitigation:** freshness nudges, ownership per source, pre-GA Ops training.
- **Cost drift.** Per-conversation cost creeps above target as sessions lengthen. **Mitigation:** cost metering alerts at 1.25× target, hard turn cap at 20.
- **Agent handoff friction.** If the payload doesn't integrate cleanly with the agent console, agents reject the channel. **Mitigation:** co-design with 3 agents during build; pilot with a single team before GA.

### Assumptions (if wrong, launch is at risk)

- A materially large share of inbound volume really is Tier-1 and self-resolvable. *(If false, deflection target is unreachable regardless of bot quality.)*
- Current FAQ + guides + resolved tickets collectively cover the top Tier-1 intents. *(If false, we have a content problem, not a bot problem.)*
- A grounded LLM + RAG hits ≥ 95% groundedness without fine-tuning. *(If false, ship slips while we fine-tune or tighten retrieval.)*
- Legal/compliance approves the resolved-ticket corpus as a knowledge source post PII-scrub. *(Hard blocker if no.)*
- Target latency is achievable within target cost on our chosen inference provider. `[assumption]`

### Open questions

- Which inference provider and model tier clears both latency and groundedness bars at target cost?
- What exactly is the Tier-1 contact baseline we're measuring 25% deflection against — do we have a clean denominator?
- Do we need legal sign-off per PDF guide version, or is a one-time approval of the corpus sufficient?
- Is the MyTelecom in-app surface a WebView of the web widget in v1, or a native integration?
- Who owns weekly groundedness audit staffing — Support Ops, QA, or a rotating product/eng pair?

---

## 8. Future Iterations (v2+)

- **Personalized account answers.** Authenticated flows for balance, usage, bill breakdown, plan details — via sanctioned billing/CRM reads with full auth + audit.
- **Transactional actions.** Enable plan change, add-on purchase, bill pay — behind strong auth and reversibility design.
- **Agent copilot.** Surface the same retrieved-and-cited answers to live agents in-session to raise consistency and shorten handle time.
- **Multilingual.** Spanish first, then FR/DE based on roaming traffic — with per-language groundedness audits.
- **Voice channel.** IVR front-door using the same RAG core, pending latency and ASR validation.
- **Proactive outreach.** Pair with network telemetry to proactively explain outages to affected customers.
- **Personalized troubleshooting.** Use (opt-in) device + account signals to tailor "slow data" diagnostics beyond generic steps.
- **Cross-session memory.** Remember prior resolved issues to short-circuit repeat questions.

---

## Decisions Log

| # | Decision | One-line reason |
|---|---|---|
| 1 | Read-only, no billing/CRM in v1 | Keeps blast radius small, dodges auth + PII work we can't harden in the launch window. |
| 2 | RAG with a frontier model, no fine-tuning | Prompting + retrieval should clear the quality bar at a fraction of the fine-tuning ops cost; revisit only if audit fails. |
| 3 | Strict "I don't know" behavior over best-guess | Hallucination is the single fastest way to lose trust; being honest + escalating is a feature, not a failure. |
| 4 | Support Ops owns content, not engineering | Content will change constantly; an engineering-release-gated knowledge base will rot and tank groundedness. |
| 5 | Confidence-gated escalation with full-context handoff | Escalations aren't failures; silent bad answers are. A rich handoff turns escalation into a net-positive customer moment. |
