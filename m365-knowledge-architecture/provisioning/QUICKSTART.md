# Quickstart — Deploy to DaniandEthan Site

Your target site: **https://octaveint.sharepoint.com/sites/DaniandEthan**

---

## Prerequisites (one-time, 5 min)

```powershell
# Install PnP PowerShell (run as your user, not admin)
Install-Module PnP.PowerShell -Scope CurrentUser -Force
```

---

## Step 1 — Run the Provisioning Script (10 min)

```powershell
# Clone or download this repo, then:
cd m365-knowledge-architecture/provisioning

.\Provision-KMSite.ps1 -SiteUrl "https://octaveint.sharepoint.com/sites/DaniandEthan"
```

A browser window will open for M365 login. Sign in with your Octave account.

**What gets created on your site:**

| Type | Items created |
|------|--------------|
| Document Libraries | AI Inbox, Classified Documents, Email Archives, Meeting Transcripts, Spreadsheets, Pricebooks, SKU Catalog, Quotes |
| Site Columns | 14 metadata columns (Objective, Key Result, Confidence Score, Source, Owner, etc.) |
| Tracking Lists | KM Classification Log, KM Correction Log, KM Prompt Config, KM Metrics Daily |
| Versioning | Configured per library (see governance/rules.md) |

---

## Step 2 — Seed the Brain Prompt (2 min)

After provisioning, go to your site → **KM Prompt Config** list → **New item**:

| Field | Value |
|-------|-------|
| Prompt Version | `1.0.0` |
| System Prompt | *(copy from `automation/step3-brain-prompt.json` → `llm_request.system`)* |
| User Prompt | *(copy from `automation/step3-brain-prompt.json` → `llm_request.messages[0].content`)* |
| Is Active | Yes |
| Effective Date | Today |

---

## Step 3 — Build Flow 1: Email Classifier (30 min)

Go to **Power Automate** (make.powerautomate.com) → Create → Automated cloud flow

Follow `automation/step2-librarian-agent-flow.md` step by step.

You need:
- An Anthropic API key (get one at console.anthropic.com)
- Outlook connection (your Octave M365 account)
- SharePoint connection (same account)
- Teams connection (same account)

Store API key: Azure Key Vault → add secret `AnthropicApiKey` → reference in flow via `@parameters('AnthropicApiKey')`

---

## Step 4 — Clone for Other Sources (15 min each)

Follow `automation/step4-cloned-flows.md` to create:
- Teams Transcript flow
- OneDrive file flow
- Excel upload flow

Only the trigger and extraction step change. Brain prompt is identical.

---

## Step 5 — Build the Dashboard Page (20 min)

On your SharePoint site:
1. **Pages** → New → Page
2. Name it `KM Intelligence Dashboard`
3. Add web parts per `automation/step6-dashboard.md` → Option A section
4. Save and publish

---

## Step 6 — Enable Feedback Loop (10 min)

Create one more Power Automate flow following `automation/step5-feedback-loop.md`:
- **Trigger:** When item is modified in `classified-documents`
- **Action:** Detect field changes → write to `KM-Correction-Log`

This starts the self-learning loop immediately.

---

## Realistic Timeline

| Week | What's live | Automation level |
|------|-------------|-----------------|
| End of Day 1 | Libraries + metadata columns provisioned | Manual only |
| End of Week 1 | Email classifier flow live | ~50% |
| End of Week 2 | All 4 flows live + dashboard | ~70% |
| Week 4+ | Feedback loop accumulating + prompt enriched | 85–95% |

---

## Files Reference

| File | Purpose |
|------|---------|
| `sharepoint/site-collections.md` | Site hierarchy design |
| `sharepoint/document-libraries.md` | Library specs + views |
| `metadata/schema.md` | All 15 metadata columns defined |
| `metadata/schema.json` | API-ready JSON Schema |
| `classification/okr-mapping-logic.md` | How pricebook/SKU/quote → OKR |
| `classification/confidence-scoring.md` | Score bands + decay rules |
| `governance/rules.md` | Override rights + versioning + retention |
| `governance/roles-permissions.md` | RBAC matrix |
| `naming-conventions.md` | File/library/flow naming |
| `automation/step2-librarian-agent-flow.md` | Email flow — full step by step |
| `automation/step3-brain-prompt.json` | The reusable AI classification prompt |
| `automation/step4-cloned-flows.md` | 3 cloned flows (Teams, OneDrive, Excel) |
| `automation/step5-feedback-loop.md` | Self-learning correction capture |
| `automation/step6-dashboard.md` | SP + Power BI dashboard design |
| `provisioning/Provision-KMSite.ps1` | **Run this first** — builds everything on your site |
