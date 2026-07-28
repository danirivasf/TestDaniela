# Local Provisioning Runbook

**Purpose:** provision the whole KM structure on `https://octaveint.sharepoint.com/sites/DaniandEthan` from Claude Code running on your own managed laptop, using the `ms365` MCP server.

**Why local:** delegated Microsoft Graph auth from a cloud container is refused by Octave's Conditional Access policy. Your corporate laptop is managed and compliant, so the same login should succeed there.

> **If you are Claude Code reading this file:** this is your task list. Work through the phases in order. Stop at every 🛑 STOP and wait for the user. Do not skip verification steps. Report honestly if a step fails — several known Graph limitations are called out below and are expected.

---

## Phase 0 — Setup

### Fastest path: one command

```powershell
git clone https://github.com/danirivasf/TestDaniela.git
cd TestDaniela
git checkout claude/m365-knowledge-automation-a7ahvl
.\m365-knowledge-architecture\provisioning\Start-KMProvisioning.ps1
```

The script checks Node and installs the Claude Code CLI if missing, walks you through the device-code login while *waiting properly* for you, verifies the result, distinguishes a Conditional Access refusal from an admin-consent block, and then launches Claude Code with this runbook loaded.

Add `-ReadOnly` for an inspection-only first pass with no writes.

If it works, skip to Phase 1. The manual steps below are the fallback.

---

### 0.1 Clone and check out

```bash
git clone https://github.com/danirivasf/TestDaniela.git
cd TestDaniela
git checkout claude/m365-knowledge-automation-a7ahvl
```

### 0.2 Authenticate

```bash
npx -y @softeria/ms-365-mcp-server --org-mode --login
```

Open **https://microsoft.com/devicelogin** and enter the code it prints. Sign in as `daniela.rivas.fernandez-feo@octave.com`.

Confirm:
```bash
npx -y @softeria/ms-365-mcp-server --org-mode --verify-login
```

### 0.3 Start Claude Code

```bash
claude
```

The repo's `.mcp.json` loads the `ms365` server automatically. Approve it when prompted, then run `/mcp` to confirm it shows connected.

Then say: *"Follow m365-knowledge-architecture/provisioning/LOCAL-RUNBOOK.md"*

### 0.4 Troubleshooting authentication

| Symptom | Cause | Fix |
|---|---|---|
| "does not meet the criteria to access this resource" | Conditional Access | You're on an unmanaged device or off-network. Use your corporate laptop on the corporate network or VPN. If it still fails, the policy is app-based → use own app registration (`MCP-SETUP.md`) or the service-principal route (`DEPLOY.md`) |
| "needs admin approval" | Tenant blocks third-party app consent | Register your own app — `MCP-SETUP.md` § "If your tenant blocks the default app registration" |
| "incorrect code" | Expired (~15 min) or wrong URL | Re-run `--login`, use `microsoft.com/devicelogin`, enter promptly |
| Signed into wrong account | Browser session | Private window, or sign out of other Microsoft accounts first |

---

## Phase 1 — Inspect before changing anything

🛑 **Do not create anything in this phase.** This is a live shared site. Establish what's there and show the user before touching it.

### 1.1 Resolve the site

```
get-sharepoint-site-by-path
  hostname: octaveint.sharepoint.com
  serverRelativePath: /sites/DaniandEthan
```

Record the returned **site id** (format `hostname,siteCollectionGuid,webGuid`). Every later call needs it.

### 1.2 Inventory what exists

```
list-sharepoint-site-lists   siteId: <site id>
list-sharepoint-site-drives  siteId: <site id>
```

### 1.3 Report to the user

Present a table: existing lists and libraries, their item counts, and which of the 8 target libraries already exist. Then state plainly what you intend to create.

🛑 **STOP. Wait for the user to approve the plan before Phase 2.**

---

## Phase 2 — Document libraries

Create any of these that don't already exist. **Skip, never overwrite, anything that exists.**

| Display name | Description |
|---|---|
| AI Inbox | Staging library for AI-classified documents pending review |
| Classified Documents | Primary library for reviewed, AI-classified content |
| Email Archives | Raw email exports auto-ingested from Exchange |
| Meeting Transcripts | Teams meeting transcripts and series summaries |
| Spreadsheets | Excel workbooks: pricebooks, SKU catalogs, reports |
| Pricebooks | Master pricebook Excel files |
| SKU Catalog | SKU definition spreadsheets |
| Quotes | Quote PDFs and Word documents |

Use `create-sharepoint-list` with a document-library template:

```json
{
  "displayName": "AI Inbox",
  "description": "Staging library for AI-classified documents pending review",
  "list": { "template": "documentLibrary" }
}
```

After each creation, record the returned **list id**.

### 2.1 Verify

Re-run `list-sharepoint-site-lists` and confirm all 8 are present. Report the count.

---

## Phase 3 — Metadata columns

> ⚠️ **Known Graph limitation — read this before starting.** Graph creates **list-scoped** columns, not tenant-scoped **site columns**. The PnP design in `metadata/schema.md` uses site columns so one definition propagates everywhere. Via Graph you add the same column to each library individually. Functionally equivalent for the flows; the difference is that later schema edits must be repeated per library rather than made once centrally. Tell the user this rather than glossing over it. If central site columns matter to them, the PnP script (`Provision-KMSite.ps1`) is the route.

### 3.1 Base columns — add to all 8 libraries

| Display name | `name` | Graph type |
|---|---|---|
| Objective | `KMObjective` | `choice` — see choices below |
| Key Result | `KMKeyResult` | `text` |
| Project | `KMProject` | `text` |
| Content Type Label | `KMContentTypeLabel` | `choice` |
| Confidence Score | `KMConfidenceScore` | `number` (2 decimals) |
| Source | `KMSource` | `choice` |
| KM Owner | `KMOwner` | `personOrGroup` |
| Classified Date | `KMClassifiedDate` | `dateTime` |
| Reviewed By | `KMReviewedBy` | `personOrGroup` |
| Reviewed Date | `KMReviewedDate` | `dateTime` |
| Override Reason | `KMOverrideReason` | `text` (multiline) |
| Retention Label | `KMRetentionLabel` | `choice` |

Choice values:
- `KMObjective`: `Increase Revenue`, `Improve Operational Efficiency`, `Accelerate Product Innovation`, `Improve Customer Success`
- `KMContentTypeLabel`: `Email`, `Attachment`, `Meeting Transcript`, `Spreadsheet`, `Presentation`, `Report`, `Contract`, `SOP`, `Other`
- `KMSource`: `Email`, `Teams`, `Upload`, `Power BI`, `SharePoint Sync`, `API`
- `KMRetentionLabel`: `Transient-30d`, `Standard-3yr`, `Financial-7yr`, `Legal-Hold`, `Permanent`

Example payload for `create-sharepoint-list-column`:

```json
{
  "name": "KMObjective",
  "displayName": "Objective",
  "description": "The OKR Objective this document supports",
  "choice": {
    "allowTextEntry": false,
    "choices": ["Increase Revenue", "Improve Operational Efficiency",
                "Accelerate Product Innovation", "Improve Customer Success"],
    "displayAs": "dropDownMenu"
  }
}
```

```json
{ "name": "KMConfidenceScore", "displayName": "Confidence Score",
  "number": { "decimalPlaces": "two", "minimum": 0, "maximum": 1 } }
```

```json
{ "name": "KMOverrideReason", "displayName": "Override Reason",
  "text": { "allowMultipleLines": true, "textType": "plain" } }
```

**Efficiency:** 12 columns × 8 libraries = 96 calls. Use **`graph-batch`** to send them in batches of ~20 rather than one at a time. If a batch partially fails, report which columns on which libraries failed — don't silently continue.

### 3.2 Series columns — `Meeting Transcripts` only

Per `meetings/meeting-series-model.md`:

| Display name | `name` | Graph type | Notes |
|---|---|---|---|
| Series ID | `KMSeriesId` | `text` | **`"indexed": true`** — required for series views at scale |
| Series Name | `KMSeriesName` | `text` | |
| Series Slug | `KMSeriesSlug` | `text` | |
| Is Recurring | `KMIsRecurring` | `boolean` | |
| Occurrence Number | `KMOccurrenceNumber` | `number` (0 decimals) | |
| Cadence | `KMCadence` | `choice` | Daily, Weekly, Biweekly, Monthly, Quarterly, Ad-hoc |
| Series OKR Locked | `KMSeriesOKRLocked` | `boolean` | |
| Previous Occurrence URL | `KMPreviousOccurrenceUrl` | `hyperlinkOrPicture` | `isPicture: false` |
| Open Action Count | `KMOpenActionCount` | `number` (0 decimals) | |
| Attendee Count | `KMAttendeeCount` | `number` (0 decimals) | |
| Meeting Date | `KMMeetingDate` | `dateTime` | |

```json
{ "name": "KMSeriesId", "displayName": "Series ID",
  "description": "Stable series key — join column for all series views",
  "indexed": true, "enforceUniqueValues": false, "text": {} }
```

> Correcting an earlier note in this project: `indexed` **is** settable through Graph on `columnDefinition`, so indexing does not require PnP. Verify it took by reading the column back — see 3.4.

### 3.3 Email column — `Email Archives` only

`KMEmailSentDate` — `dateTime`.

### 3.4 Verify

For each library, `list-sharepoint-list-columns` and confirm the expected set. Specifically read back `KMSeriesId` on `Meeting Transcripts` and confirm `indexed: true`. If indexing didn't stick, say so — it's a manual toggle in Library settings → Indexed columns.

---

## Phase 4 — Series folders

Create in the `Meeting Transcripts` library:

```
_Series/
_OneOff/
```

Get the library's drive id from `list-sharepoint-site-drives` (match on the library name), then create folders with `create-onedrive-folder` against that drive, or POST a folder driveItem to the drive root's children:

```json
{ "name": "_Series", "folder": {}, "@microsoft.graph.conflictBehavior": "fail" }
```

`conflictBehavior: fail` means a re-run won't create `_Series 1` duplicates — treat a 409 as "already exists, fine".

Also create `_OneOff/2026/` and `_OneOff/2026/2026-Q3/` so the current quarter's path exists.

Do **not** pre-create per-series folders — the flow creates those on first occurrence of each series.

---

## Phase 5 — Tracking lists

Create these 5 generic lists. Column definitions are in `meetings/meeting-series-model.md` §7 and `automation/copilot-studio-build-prompt.md`.

| List | Purpose |
|---|---|
| `KM-Classification-Log` | Every classification, with AI vs final objective and override flag |
| `KM-Correction-Log` | Human corrections, feeding the self-learning loop |
| `KM-Prompt-Config` | Versioned brain prompt, `IsActive` flag |
| `KM-Metrics-Daily` | Daily rollups for the dashboard |
| `KM-Meeting-Series` | **Recurring meeting registry** — see below |

### 5.1 `KM-Meeting-Series` columns

| Display name | `name` | Type |
|---|---|---|
| Series ID | `SeriesId` | `text`, **`indexed: true`**, `enforceUniqueValues: true` |
| Series Name | `SeriesName` | `text` |
| Series Slug | `SeriesSlug` | `text` |
| Organizer | `Organizer` | `personOrGroup` |
| Cadence | `Cadence` | `choice` (Daily…Ad-hoc) |
| Folder URL | `FolderUrl` | `hyperlinkOrPicture` |
| Overview URL | `OverviewUrl` | `hyperlinkOrPicture` |
| Locked Objective | `LockedObjective` | `choice` (4 objectives) |
| Locked Key Result | `LockedKeyResult` | `text` |
| OKR Locked | `OKRLocked` | `boolean` |
| Occurrence Count | `OccurrenceCount` | `number` (0 dp) |
| First Seen | `FirstSeen` | `dateTime` |
| Last Seen | `LastSeen` | `dateTime` |
| Open Action Count | `OpenActionCount` | `number` (0 dp) |
| Stale Action Count | `StaleActionCount` | `number` (0 dp) |
| Series State JSON | `SeriesStateJson` | `text` multiline |
| Is Active | `IsActive` | `boolean` |

`enforceUniqueValues` on `SeriesId` is the safeguard that stops one meeting series being registered twice by a concurrent flow run.

### 5.2 Seed the brain prompt

Add one item to `KM-Prompt-Config` using `create-sharepoint-list-item`:
- `PromptVersion`: `1.0.0`
- `SystemPrompt` / `UserPrompt`: from `automation/step3-brain-prompt.json`
- `IsActive`: true
- `EffectiveDate`: today

---

## Phase 6 — Views

> ⚠️ **Graph cannot create list views.** There is no supported `columnDefinition`-style API for views. This is a genuine gap, not something to work around.

Report this to the user and offer three options:

1. **Manual, ~10 minutes** — create them in the browser per `meetings/meeting-series-model.md` §6. Four views on `Meeting Transcripts`: By Series (group by `KMSeriesName`, sort `KMOccurrenceNumber` desc), Stale Actions, Needs OKR Review, One-Offs.
2. **PnP script** — `Provision-KMSite.ps1` §3b creates them. Idempotent, safe to run after Graph provisioning.
3. **Defer** — the flows work without views; views are for human browsing.

Recommend option 1. It's quick, and doing it by hand once means they understand the grouping before relying on it.

---

## Phase 7 — Validate against real data

This is the part only a local session can do, and it's where the series model gets proven rather than assumed.

### 7.1 Find real recurring meetings

```
list-calendar-events   (with $select including seriesMasterId, type, recurrence, subject, organizer)
```

Identify events where `type` is `occurrence`/`seriesMaster` or `recurrence != null`. Report the actual recurring meetings on the calendar with their real `seriesMasterId` values.

### 7.2 Test SeriesId resolution

For each recurring meeting found, apply the §1 priority ladder from `meetings/meeting-series-model.md` and show the resolved `SeriesId` and `series-slug`.

**Check the normalization rules against reality.** Real subjects will expose cases the rules don't cover. Report any subject where:
- normalization produces under 3 characters (guardrail triggers)
- two genuinely different meetings collapse to the same slug
- the same meeting would produce different slugs across occurrences

If any of these occur, propose a rule amendment and update `meeting-series-model.md`. **This is the most valuable output of the whole runbook** — the rules were written without access to real data, so treat them as a hypothesis to test, not a spec to defend.

### 7.3 Test against a real transcript

```
list-online-meetings → list-meeting-transcripts → get-meeting-transcript-content
```

Take one real transcript, run the series-aware prompt from `meeting-series-model.md` §8 against it with an empty prior state (simulating occurrence 1), and show the user the JSON output. Check:
- Is the summary actually useful, or generic?
- Are decisions genuinely decisions, or just discussion?
- Are action item owners correctly attributed?
- Is the OKR mapping plausible, and is the confidence honest?

Report findings candidly. If the output is weak, the prompt needs work — say so and propose specific changes rather than declaring success.

### 7.4 Optional: end-to-end dry run

Write one real transcript's summary into `_Series/{slug}/2026/` with a `00_series-state.json` and a `00_SERIES-OVERVIEW.md`, populate the metadata columns, and register the series in `KM-Meeting-Series`. This proves the whole write path before any flow is built.

Use `upload-file-content` (base64, ≤4MB) for the files.

---

## Phase 8 — Report

Summarize:

| | |
|---|---|
| Libraries created / skipped | |
| Columns added (and any failures) | |
| `KMSeriesId` indexed? | |
| Folders created | |
| Lists created | |
| Views | Manual step outstanding? |
| Real recurring meetings found | |
| Series rule amendments proposed | |
| Prompt quality assessment | |

Then commit any changes made to the repo docs (rule amendments especially) to `claude/m365-knowledge-automation-a7ahvl`.

---

## Ground rules

**This is a live shared site.** Skip what exists, never overwrite. `conflictBehavior: fail` on folders, check-before-create on lists and columns.

**Report failures plainly.** Three things are known-uncertain: site columns vs list columns (Phase 3), view creation (Phase 6), and whether the series normalization rules survive real data (Phase 7). Say which of these bit, rather than reporting a clean run.

**Everything here is idempotent.** Safe to re-run after a partial failure.

**Don't build Power Automate flows from this runbook.** Graph has no flow-authoring API. Provision the structure, validate the model, then author flows in the browser per `automation/copilot-studio-build-prompt.md`.
