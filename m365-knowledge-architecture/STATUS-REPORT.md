# Knowledge Automation Initiative - Status Report

**Prepared by:** Daniela Rivas Fernandez-Feo
**Date:** 28 July 2026
**Status:** Design and build complete. Blocked awaiting IT approval.

---

## Summary

I have designed and built an AI-driven knowledge automation system for Microsoft 365 that captures, classifies, and files our meeting records and email attachments automatically, tagged against our OKRs.

The design work and all deployment automation are complete and version controlled. Implementation is blocked at the first step: the tooling needs IT approval to access Microsoft 365. **One approval decision unblocks roughly two weeks of delivery.**

---

## The problem being solved

Three recurring costs, all currently absorbed manually:

1. **Meeting knowledge evaporates.** A weekly meeting running a year produces 52 transcripts with no connective tissue. Answering "what did we decide about pricing last quarter?" means opening a dozen files. Action items agreed in one meeting are commonly forgotten by the next.
2. **Attachments are unfindable.** Pricebooks, SKU catalogs, and quotes arrive by email and land wherever the recipient happens to put them. There is no shared, searchable index.
3. **Nothing traces to strategy.** We cannot currently answer "show me everything we produced against our revenue objective this quarter" without a manual trawl.

---

## What the system does

**1. Meeting Intelligence.** Captures every Teams transcript automatically, summarizes it, and files it. Recurring meetings resolve to a single stable location with a running overview that carries open action items and a decision log forward between occurrences. Action items are tracked across meetings and flagged when they have been open too long, so commitments stop quietly lapsing.

**2. Email Triage.** Every email attachment is saved to SharePoint, classified, and routed to the correct library. Where the AI is not confident, it asks a human rather than guessing.

**3. Daily Assistant.** A Teams chat agent delivering each morning: today's meetings, prioritized email, action items due, and important attachments received. It also answers retrieval questions such as "what did we decide about enterprise discounts in the revenue standup?"

Everything is tagged to an Objective and Key Result, with an explicit AI confidence score. Anything below the confidence threshold routes to a person for review; classifications are never silently guessed.

---

## What is complete

| Deliverable | Status |
|---|---|
| Full information architecture: libraries, metadata schema, naming, governance, RBAC | Complete |
| OKR classification logic and confidence-scoring model | Complete |
| Recurring-meeting model with carry-forward action tracking and decision log | Complete |
| Provisioning automation (two independent routes) | Complete |
| Deployment pipeline for installing the system for other team members | Complete |
| Build specifications for all three agents | Complete |
| Self-learning feedback loop design (corrections improve future accuracy) | Complete |

All of it is in version control with a reviewable history. Nothing depends on knowledge held only by me, which was a deliberate design goal.

---

## What is blocked, and the ask

To create the SharePoint structure and read meeting transcripts, the tooling needs delegated Microsoft Graph access. Our tenant correctly requires IT approval, and an approval request has been raised.

**Two ways forward. I recommend Option B.**

**Option A - Approve the third-party application ("MS 365 MCP Server", softeria.com).** Fastest. Uses delegated permissions, meaning it acts strictly as me with exactly my existing access and nothing more. It cannot reach anything I cannot already reach.

**Option B - IT registers an internal application we control.** Roughly 20 minutes of IT time. Same functionality, but the app registration is ours: IT sets the permission scope, can audit usage, and can revoke it at any time. No third-party app in the tenant. This is the better answer for an organization with our governance posture, and it is also the route that lets the system be deployed to the rest of the team without each person needing an individual approval.

Technical detail for whoever picks this up is in `MCP-SETUP.md` and `DEPLOY.md` in the repository.

---

## Point requiring a decision: AI processing location

Being explicit about this because it needs a deliberate answer, not a discovered one.

Classification is performed by a large language model. In the current design, meeting transcript text and attachment content are sent to Anthropic's API for analysis. **That means this content leaves the Microsoft 365 boundary.**

Three options:

1. **Anthropic API** - best classification quality. Requires a commercial agreement and a data-processing review. Note that an earlier attempt to create an organizational account was blocked at the parent-organization level, so this needs a procurement conversation rather than a self-service signup.
2. **Azure OpenAI in our own tenant** - content never leaves our Azure boundary. Likely the correct answer for our governance posture. The system is designed so this is an endpoint swap, not a redesign.
3. **Microsoft 365 Copilot** - stays entirely within M365 but offers less control over classification behaviour.

I would recommend option 2 unless procurement is straightforward. **This should be settled before we process real content**, not after.

---

## Timeline once unblocked

| Phase | Duration | Outcome |
|---|---|---|
| Provision SharePoint structure | Half a day | Libraries, metadata, tracking lists live |
| Validate the model against real meetings | Half a day | Classification rules tested on actual transcripts before committing to them |
| Build the three automations | 2-3 days | Email triage, meeting intelligence, daily assistant running |
| Package for team distribution | Half a day | Any team member installs in about 10 minutes |
| Tuning period | 2-4 weeks | Accuracy improves from roughly 70% to 85-95% as the feedback loop accumulates corrections |

**Approximately two weeks to a working system for me, then about 10 minutes per additional team member.** That ratio is the main design achievement: the system is built to be handed over, not to be a personal tool.

---

## Requests

1. **Approve Option B** (internal app registration) with IT, or Option A if faster is preferred.
2. **Decide the AI processing question** above - Azure OpenAI is my recommendation.
3. **Confirm the OKR list** the system classifies against. It currently uses: Increase Revenue, Improve Operational Efficiency, Accelerate Product Innovation, Improve Customer Success. If these are not our actual objectives, correcting them now is trivial and later is not.

---

## Honest assessment of risk

Worth stating plainly rather than presenting this as risk-free:

- **Classification accuracy will not start high.** Expect around 70% initially, improving with corrections. The confidence threshold means low-confidence items go to a human rather than being filed wrongly, so errors surface as review requests rather than as silently misplaced documents.
- **The recurring-meeting rules are untested against our real data.** They were written without tenant access. Validating them is an explicit early step, and I expect to amend them once I can see real meeting titles.
- **The one-time build of the automations cannot be scripted.** Microsoft provides no API for authoring Power Automate flows, so the first version is built by hand. Everything after that is automated, which is why distribution to the team is fast.
