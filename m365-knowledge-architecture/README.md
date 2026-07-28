# M365 AI-Driven Knowledge Automation Architecture

A metadata-first knowledge management system on SharePoint and OneDrive, aligned to OKRs. Automatically classifies and files emails, attachments, meeting transcripts, and spreadsheets — and keeps recurring meetings as coherent, browsable threads rather than piles of dated files.

Target site: `https://octaveint.sharepoint.com/sites/DaniandEthan`

---

## Start here

| If you want to… | Read |
|---|---|
| Understand how it all deploys and gets shared with teammates | **[`DEPLOY.md`](DEPLOY.md)** |
| Connect Claude to your M365 tenant | **[`MCP-SETUP.md`](MCP-SETUP.md)** |
| Understand recurring-meeting storage | **[`meetings/meeting-series-model.md`](meetings/meeting-series-model.md)** |
| Get an AI to build the automations for you | **[`automation/copilot-studio-build-prompt.md`](automation/copilot-studio-build-prompt.md)** |
| Provision SharePoint right now | [`provisioning/QUICKSTART.md`](provisioning/QUICKSTART.md) |

---

## Structure

```
m365-knowledge-architecture/
├── DEPLOY.md                          # ★ How to deploy and share with the team
├── MCP-SETUP.md                       # ★ Connecting Claude to M365 via MCP
├── meetings/
│   └── meeting-series-model.md        # ★ Recurring meeting coherence model
├── sharepoint/
│   ├── site-collections.md            # Site hierarchy
│   └── document-libraries.md          # Library definitions + views
├── metadata/
│   ├── schema.md                      # Metadata column definitions
│   └── schema.json                    # API-ready JSON Schema
├── classification/
│   ├── okr-mapping-logic.md           # Keyword → OKR mapping rules
│   └── confidence-scoring.md          # How confidence scores are computed
├── automation/
│   ├── copilot-studio-build-prompt.md # ★ Full build prompt for all 3 agents
│   ├── step2-librarian-agent-flow.md  # Email flow, step by step
│   ├── step3-brain-prompt.json        # Reusable classification prompt
│   ├── step4-cloned-flows.md          # Teams / OneDrive / Excel variants
│   ├── step5-feedback-loop.md         # Self-learning correction capture
│   └── step6-dashboard.md             # SharePoint + Power BI dashboards
├── governance/
│   ├── rules.md                       # Override rights, versioning, retention
│   └── roles-permissions.md           # RBAC matrix
├── provisioning/
│   ├── Provision-KMSite.ps1           # PnP script — builds the whole site
│   └── QUICKSTART.md                  # Week-by-week rollout timeline
└── naming-conventions.md              # File and library naming standards
```

Repo root also contains:
```
.mcp.json                              # MCP servers: ms365 + Microsoft Learn
.github/workflows/
  ├── deploy-sharepoint.yml            # Provision any SharePoint site
  └── deploy-power-platform.yml        # Install flows + agents into any environment
power-platform/
  ├── deployment-settings.json         # Per-environment bindings, no secrets
  └── solution-source/                 # Exported solution, version controlled
```

---

## The three automations

**1. My Assistant** — a Teams chat agent that delivers a prioritized daily brief every morning: today's meetings, email highlights, action items due, important attachments received. Also answers retrieval questions like *"what did we decide about enterprise discounts in the revenue standup?"*

**2. Meeting Intelligence** — captures every Teams transcript, summarizes it, and files it. Recurring meetings resolve to a single stable folder with a living overview that carries open action items and a decision ledger forward between occurrences. See the series model for why this matters.

**3. Email Triage** — every email with an attachment gets its files saved to SharePoint, classified against OKRs, and routed to the right library (pricebooks, quotes, SKU catalog…). Low-confidence classifications go to a Teams approval card instead of being guessed.

---

## Key design principles

- **Metadata-first** — content is discoverable through metadata, not folder hierarchy. The one exception is recurring meetings, where a stable folder per series is what makes the history navigable.
- **OKR-aligned** — every document traces to an Objective and Key Result.
- **Confidence-gated** — nothing low-confidence is filed silently. Below 0.75 a human sees it.
- **Series state is machine-readable** — the decision ledger is JSON, so the assistant answers from a ledger rather than re-reading 31 transcripts.
- **Deployable from git** — flows and agents live in a Power Platform solution under version control, so teammates install rather than rebuild.
