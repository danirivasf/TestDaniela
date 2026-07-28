# Copilot Studio Build Prompt — My Assistant + Knowledge Automation

> **How to use:** Paste the block below into Perplexity, ChatGPT, or any AI to get step-by-step Copilot Studio build instructions tailored to this exact setup.

---

## PASTE THIS INTO PERPLEXITY ↓

---

I need to build a complete AI knowledge automation system inside Microsoft 365 using **Copilot Studio** with MCP connectors (Microsoft Graph, Outlook, Teams, SharePoint). My environment:

- **Tenant:** octaveint.sharepoint.com
- **SharePoint hub site:** https://octaveint.sharepoint.com/sites/DaniandEthan
- **Teams workspace:** Octave (same M365 tenant)
- **M365 plan:** Business Premium (Copilot Studio, Power Automate, Teams, SharePoint, Outlook all available)
- **AI API:** Anthropic Claude (personal API key stored securely — do NOT include key in any config shown)

Please give me complete, step-by-step instructions to build the following three agents and automation flows in Copilot Studio. Include: which connectors to add, what actions to configure, what prompts to use, how to publish to Teams, and how to share the setup with teammates so they can install the same thing.

---

### AGENT 1 — "My Assistant" (Daily Briefing Agent in Teams)

**What it does:**
Every weekday morning at 8:00 AM, this agent sends me a proactive message in Microsoft Teams (personal chat or a dedicated channel) with:
1. **Today's calendar** — list of meetings from Outlook Calendar for the day, with time, title, attendees
2. **Unread email summary** — top 5 emails by importance/recency from Outlook Inbox, with sender, subject, one-line summary
3. **Action items** — any emails flagged for follow-up or tasks in To Do / Planner assigned to me that are due today or overdue
4. **Important attachments received yesterday** — list of attachments from the last 24 hours with file name, sender, and a one-line description of what the file contains (use AI to summarize)
5. **Priority score** — AI ranks each item as High / Medium / Low based on subject keywords, sender VIP list, and due dates

**Copilot Studio setup needed:**
- Agent name: `My Assistant`
- Connectors required: Microsoft Graph (calendar, mail, tasks), Office 365 Outlook, Microsoft Teams
- Trigger: Scheduled (Power Automate scheduled flow calling the agent or a Power Automate flow that posts an Adaptive Card to Teams)
- AI instructions (system prompt for the agent): "You are My Assistant, a personal productivity agent for an Octave team member. Every morning you analyze the user's calendar, inbox, and tasks and deliver a concise, prioritized daily brief. Use a warm, professional tone. Format output as a structured Teams Adaptive Card with sections: Today's Meetings, Email Highlights, Action Items, Important Attachments. Rank everything High/Medium/Low priority."
- Output format: Microsoft Teams Adaptive Card with collapsible sections

**How it should work when a teammate installs it:**
- They authorize their own Outlook + Teams + Graph connection
- The agent runs against their own calendar and inbox (not mine)
- No shared data between users

---

### AGENT 2 — Meeting Intelligence (Auto-Summarize Teams Meetings, Series-Aware)

**What it does:**
After every Teams meeting ends, automatically capture the transcript, summarize it, and file it. The critical requirement: **recurring meetings must all land in the same place and build on each other** — a weekly standup that runs a year should produce one coherent, browsable thread, not 52 loose files.

#### 2.1 — Detect whether the meeting is recurring

Resolve a stable `SeriesId` using this priority ladder (first match wins):

| Priority | Signal | Where to get it |
|---|---|---|
| 1 | `seriesMasterId` | Microsoft Graph `GET /me/events/{id}` — all occurrences of a recurring series share this GUID |
| 2 | `onlineMeeting.joinWebUrl` | Graph `/me/onlineMeetings` — stable across occurrences, survives subject renames |
| 3 | `iCalUId` root | Graph event |
| 4 | `slug(normalizedSubject) + "--" + slug(organizerEmail)` | Computed fallback when no calendar event can be matched |

**Subject normalization for priority 4** — strip everything that varies between occurrences, then slugify:
```
"Weekly Revenue Standup - Jul 28 (Occurrence 31) [EXTERNAL]"  →  "weekly-revenue-standup"
```
Removal order: bracketed tags → dates in any format → occurrence markers (`Occurrence N`, `#N`, `Week N`) → cadence words (`Weekly`, `Monthly`, …) *only if other words remain* → Teams noise (`Meeting with`, `- Copy`) → collapse and hyphenate.
**Guardrail:** if the result is under 3 characters, use the raw subject slug instead. Never let `"weekly"` alone become a SeriesId — that would merge unrelated meetings.

**Treat as recurring if any of these is true:** the Graph event has `recurrence != null` or type `occurrence`/`exception`/`seriesMaster`; OR a transcript already exists with the same resolved SeriesId; OR two meetings with the same normalized subject + organizer occurred more than 4 days apart (this catches meetings that recur in practice but were booked as separate one-offs).

#### 2.2 — File it in the right place

All under `https://octaveint.sharepoint.com/sites/DaniandEthan/meeting-transcripts`:

```
meeting-transcripts/
├── _Series/
│   └── weekly-revenue-standup/
│       ├── 00_SERIES-OVERVIEW.md      ← living doc, rewritten every occurrence
│       ├── 00_series-state.json       ← machine state: open actions, OKR lock, counters
│       ├── 2026/
│       │   ├── 2026-07-28_INC_OCC-031_weekly-revenue-standup.md
│       │   └── 2026-07-21_INC_OCC-030_weekly-revenue-standup.md
│       └── _raw/                      ← original .vtt files
└── _OneOff/
    └── 2026/2026-Q3/
        └── 2026-07-14_INC_acme-pricing-negotiation.md
```

Naming: `{YYYY-MM-DD}_{OBJ}_OCC-{NNN}_{series-slug}.md` for recurring, `{YYYY-MM-DD}_{OBJ}_{slug}.md` for one-offs. `{OBJ}` is a 3-letter objective code: `INC`, `OPS`, `INN`, `CUS`, or `UNC`.

Year subfolders keep each folder browsable; `00_` prefix sorts the overview to the top; `_raw/` keeps .vtt evidence out of the reading path.

#### 2.3 — Carry state forward between occurrences (the important part)

Before classifying a new occurrence, **read `00_series-state.json` from the series folder** and pass its contents into the AI call. After classifying, **write it back**. This is what makes the series coherent instead of 52 disconnected summaries.

State file contents:
```json
{
  "series_id": "AAMkAGI2NDk...",
  "series_slug": "weekly-revenue-standup",
  "series_name": "Weekly Revenue Standup",
  "cadence": "Weekly",
  "occurrence_count": 31,
  "okr": {
    "objective": "Increase Revenue",
    "key_result": "Achieve $5M ARR",
    "locked": true,
    "locked_at_occurrence": 3,
    "consistent_classifications": 29
  },
  "open_actions": [
    { "id": "a-028-01", "action": "Finalize Q3 pricebook tiers", "owner": "Ethan M.",
      "opened_occurrence": 28, "occurrences_open": 3, "stale": true }
  ],
  "closed_actions": [
    { "id": "a-026-02", "action": "Draft SKU consolidation plan", "owner": "Ethan M.",
      "opened_occurrence": 26, "closed_occurrence": 30 }
  ],
  "decision_ledger": [
    { "occurrence": 31, "date": "2026-07-28", "decision": "Hold enterprise discount at 15% through Q3" }
  ],
  "theme_counts": { "pricing": 28, "enterprise deals": 22 },
  "regular_attendees": ["daniela.rivas.fernandez-feo@octave.com"]
}
```

**OKR Lock rule:** once 3 consecutive occurrences classify to the same Objective, lock it. Later occurrences inherit the locked Objective and get confidence `max(ai_confidence, 0.92)`. The AI still reports what it *would* have chosen; if it disagrees with the lock 3 times in a row, break the lock and post a Teams card asking a human to re-map the series. This prevents a weekly meeting from drifting between objectives based on whatever happened to come up that week — the single biggest source of noise in recurring-meeting classification.

**Action reconciliation:** every occurrence, the AI must return a verdict for every currently-open action — `completed`, `in_progress`, `not_mentioned`, `superseded`, or `reassigned`. An action open ≥3 occurrences is flagged stale and surfaces at the top of the overview. An action not mentioned for 6 consecutive occurrences is auto-archived as `abandoned`, so the open list stays honest.

#### 2.4 — Rewrite the living overview

After each occurrence, regenerate `00_SERIES-OVERVIEW.md` in full. It must contain, in this order: series metadata table (ID, cadence, organizer, occurrence count, locked OKR, regular attendees) → **Open Action Items** table with staleness flags → Recently Closed → **Decision Ledger** (most recent first) → Recurring Themes with mention counts → Occurrence Index (date, number, one-line summary, link).

This is the page someone opens to catch up on a series they've missed. It must be readable standalone.

#### 2.5 — Post a series-delta digest to Teams

For a meeting you attend weekly, the summary is not the useful part — the delta is. Post:
```
📊 Weekly Revenue Standup — Occurrence 31
Series: 31 meetings since Jan 6 · OKR: Increase Revenue (locked)

What changed since last week:
Discount policy resolved; SKU consolidation now in execution.

✅ Closed: Draft SKU consolidation plan (Ethan)
🆕 New: Send Acme revised quote (Daniela, due Aug 1)
⚠️ Stale (3 weeks open): Finalize Q3 pricebook tiers (Ethan)

📄 This occurrence  ·  📚 Full series overview
```

#### 2.6 — Series-aware metadata columns

On the `meeting-transcripts` library, in addition to the base columns:

| Column | Internal name | Type |
|---|---|---|
| Series ID | `KMSeriesId` | Text (**indexed** — this is the join column for all series views) |
| Series Name | `KMSeriesName` | Text |
| Series Slug | `KMSeriesSlug` | Text |
| Is Recurring | `KMIsRecurring` | Yes/No |
| Occurrence Number | `KMOccurrenceNumber` | Number |
| Cadence | `KMCadence` | Choice (Daily/Weekly/Biweekly/Monthly/Quarterly/Ad-hoc) |
| Series OKR Locked | `KMSeriesOKRLocked` | Yes/No |
| Previous Occurrence | `KMPreviousOccurrenceUrl` | Hyperlink |
| Open Action Count | `KMOpenActionCount` | Number |
| Attendee Count | `KMAttendeeCount` | Number |

**Library views to create:**
- **By Series** — group by `KMSeriesName`, sort `KMOccurrenceNumber` descending → "show me this meeting's whole history"
- **Latest per Series** — max occurrence per series → "current state of every recurring meeting"
- **Stale Actions** — `KMOpenActionCount` > 0 → "where are things stuck"
- **Needs OKR Review** — not locked AND confidence < 0.75
- **One-Offs This Quarter** — `KMIsRecurring` = No

#### 2.7 — Series registry list

Create a SharePoint list `KM-Meeting-Series`, one row per recurring series, so "which recurring meetings do we even have?" is one click. Columns: `SeriesId` (indexed, unique), `SeriesName`, `SeriesSlug`, `Organizer` (Person), `Cadence`, `FolderUrl`, `OverviewUrl`, `LockedObjective`, `LockedKeyResult`, `OKRLocked`, `OccurrenceCount`, `FirstSeen`, `LastSeen`, `OpenActionCount`, `StaleActionCount`, `SeriesStateJson` (Note — mirror of state.json for flows that can't read files), `IsActive`.

#### 2.8 — Copilot Studio / Power Automate setup

- Agent name: `KM Meeting Intelligence`
- Connectors: Microsoft Teams, SharePoint, Microsoft Graph (meeting metadata + transcripts), Office 365 Outlook (calendar, for recurrence detection), HTTP (Claude API)
- Trigger: Power Automate — "When a file is created in SharePoint library `/Recordings`" (Teams saves transcripts here), OR Graph subscription on `/me/onlineMeetings/{id}/transcripts`
- Flow order: get transcript → resolve SeriesId → look up `KM-Meeting-Series` → read `state.json` (or `SeriesStateJson`) → call AI with prior context → reconcile actions → write occurrence file → rewrite overview → write state back → update registry → post Teams digest

**Series-aware AI prompt to use:**
```
You are an enterprise meeting intelligence engine for Octave.

You are processing occurrence {{occurrence_number}} of a recurring meeting series.
Summarize this occurrence AND reconcile it against the series history.

=== SERIES CONTEXT ===
Series name:        {{series_name}}
Cadence:            {{cadence}}
Occurrence number:  {{occurrence_number}}
Locked OKR:         {{locked_objective}} → {{locked_key_result}} (locked: {{okr_locked}})

Previous occurrence summary:
{{previous_summary}}

Currently open action items (you MUST return a verdict for every one):
{{open_actions_json}}

Established recurring themes:
{{theme_counts_json}}

=== THIS OCCURRENCE ===
Date:      {{meeting_date}}
Attendees: {{attendees}}
Transcript:
{{transcript_text}}

=== OUTPUT (strict JSON only, no prose, no markdown fences) ===
{
  "summary": "2-4 sentences on what happened THIS occurrence. Do not re-summarize the series.",
  "whats_changed": "1-2 sentences: what is different from last occurrence. Empty string if occurrence 1.",
  "decisions": [{ "decision": "...", "rationale": "...", "owner": "name or null" }],
  "new_action_items": [{ "action": "...", "owner": "name", "due": "YYYY-MM-DD or null" }],
  "action_updates": [
    { "id": "id from open_actions_json",
      "verdict": "completed | in_progress | not_mentioned | superseded | reassigned",
      "evidence": "short quote or paraphrase supporting the verdict",
      "new_owner": "only if reassigned",
      "superseded_by": "only if superseded" }
  ],
  "themes": ["theme1", "theme2"],
  "objective": "one of the four allowed objectives",
  "key_result": "most relevant key result",
  "confidence": 0.0,
  "agrees_with_lock": true,
  "reasoning": "why this objective; if it disagrees with the locked OKR, say so explicitly"
}

RULES
- Return a verdict for EVERY id in open_actions_json. Omitting one is an error.
- If an action is not discussed at all, verdict is "not_mentioned" — do not guess "in_progress".
- "decisions" means things actually settled. Discussion without resolution is not a decision.
- Attribute owners by name only when the transcript makes it clear. Otherwise null.
- If the OKR is locked and you agree, return the locked values and set agrees_with_lock true.
- If the OKR is locked and you genuinely disagree, return YOUR choice and set agrees_with_lock false.
- Prefer precision over completeness. Lower confidence when the transcript is fragmentary.

Allowed objectives: Increase Revenue, Improve Operational Efficiency,
Accelerate Product Innovation, Improve Customer Success
```

For the **first occurrence** of a new series, pass `previous_summary = "(none — first occurrence)"`, `open_actions_json = []`, `okr_locked = false`.

**Company OKRs to map to (use exactly these values):**
- Objective: "Increase Revenue" → Key Results: Achieve $5M ARR, Close 20 enterprise deals, Launch 3 new SKUs
- Objective: "Improve Operational Efficiency" → Key Results: Reduce manual processing by 40%, Automate 5 recurring workflows, Cut meeting overhead by 25%
- Objective: "Accelerate Product Innovation" → Key Results: Ship 2 major features per quarter, Reduce time-to-market by 30%, Complete 10 customer pilots
- Objective: "Improve Customer Success" → Key Results: Achieve NPS > 50, Reduce churn below 5%, Onboard 15 new enterprise accounts

**Copilot Studio setup needed:**
- Agent name: `KM Meeting Intelligence`
- Connectors: Microsoft Teams, SharePoint, Microsoft Graph (for meeting metadata and transcripts)
- Trigger: Power Automate flow — "When a file is created in SharePoint library /Recordings" (Teams saves recordings/transcripts here automatically)
- AI classification prompt to use inside the flow:
```
You are an enterprise knowledge classification engine.

Analyze this meeting transcript and extract structured information.

TRANSCRIPT:
{{transcript_text}}

OUTPUT (strict JSON only, no other text):
{
  "summary": "2-3 sentence meeting summary",
  "decisions": ["decision 1", "decision 2"],
  "action_items": [{"owner": "name", "task": "description", "due": "date or null"}],
  "topics": ["topic 1", "topic 2"],
  "objective": "one of the four allowed objectives",
  "key_result": "the most relevant key result",
  "confidence": 0.0,
  "reasoning": "why you chose this objective"
}

Allowed objectives: Increase Revenue, Improve Operational Efficiency, Accelerate Product Innovation, Improve Customer Success
Rules: prefer precision over guessing; if unsure, lower confidence score; use business language.
```
- SharePoint metadata columns to populate: Objective (Choice), KeyResult (Text), ConfidenceScore (Number), MeetingDate (DateTime), Source = "Teams", ContentTypeLabel = "Meeting Transcript"

---

### AGENT 3 — Email Triage + Attachment Organizer

**What it does:**
When a new email arrives in my Outlook Inbox with an attachment:
1. Save every attachment to SharePoint at: `https://octaveint.sharepoint.com/sites/DaniandEthan/ai-inbox`
   - File naming convention: `YYYY-MM-DD_[OBJ]_EMAIL_[original-filename]` (e.g., `2026-07-28_INC_EMAIL_Q3-Pricebook.xlsx`)
2. Use AI to classify the attachment content:
   - Read first 2000 characters of file content (use AI Builder document extraction or Excel connector for spreadsheets)
   - Call Claude API or Copilot Studio AI prompt to classify
3. Tag with metadata: Objective, KeyResult, Source = "Email", Owner = sender email, ClassifiedDate
4. Move classified file from ai-inbox to appropriate library:
   - Pricebooks/price lists → `/pricebooks`
   - SKU data → `/sku-catalog`
   - Quotes/proposals → `/quotes`
   - Meeting notes from email → `/meeting-transcripts`
   - Everything else → `/classified-documents`
5. If confidence ≥ 0.75: auto-classify and move silently
6. If confidence < 0.75: post a Teams Adaptive Card to #ai-review-queue channel asking me to confirm or correct the classification
7. Log every classification (correct or overridden) to a SharePoint list called `KM-Classification-Log`

**AI prompt for email/attachment classification:**
```
You are an enterprise knowledge classification engine.

Analyze the input and map it to company OKRs.

EMAIL SUBJECT: {{email_subject}}
EMAIL FROM: {{email_from}}
ATTACHMENT NAME: {{attachment_name}}
ATTACHMENT CONTENT (first 2000 chars): {{attachment_text}}

OUTPUT (strict JSON only, no other text):
{
  "summary": "one sentence describing what this document is",
  "keywords": ["keyword1", "keyword2"],
  "objective": "one of the four allowed objectives",
  "key_result": "the most relevant key result",
  "project": "project name if identifiable, else null",
  "content_type": "Pricebook | SKU Catalog | Quote | Meeting Notes | Report | Contract | Other",
  "confidence": 0.0,
  "reasoning": "why you chose this classification"
}

Allowed objectives: Increase Revenue, Improve Operational Efficiency, Accelerate Product Innovation, Improve Customer Success
```

**Copilot Studio / Power Automate setup needed:**
- Flow name: `KM | Email → Classify & Store | PROD`
- Trigger: Office 365 Outlook — "When a new email arrives (V3)" with Only with Attachments = Yes
- Connectors: Office 365 Outlook, SharePoint, Microsoft Teams, HTTP (for Claude API call), Excel Online (for spreadsheet extraction)
- API call to Claude:
  - URL: `https://api.anthropic.com/v1/messages`
  - Method: POST
  - Headers: `x-api-key: [store in environment variable, NEVER hardcode]`, `anthropic-version: 2023-06-01`, `Content-Type: application/json`
  - Body: use the prompt above with `model: "claude-opus-4-8"`, `max_tokens: 1024`

---

### SHAREPOINT LIBRARIES REQUIRED

All at site: `https://octaveint.sharepoint.com/sites/DaniandEthan`

| Library name | URL slug | Purpose |
|---|---|---|
| AI Inbox | `/ai-inbox` | Landing zone for all new files before classification |
| Classified Documents | `/classified-documents` | General classified content |
| Email Archives | `/email-archives` | Emails saved as .msg or .eml |
| Meeting Transcripts | `/meeting-transcripts` | Teams meeting summaries |
| Spreadsheets | `/spreadsheets` | Excel uploads |
| Pricebooks | `/pricebooks` | Pricing documents |
| SKU Catalog | `/sku-catalog` | Product/SKU data |
| Quotes | `/quotes` | Sales quotes and proposals |

**Site columns to create (apply to all libraries):**
- `Objective` — Choice (Increase Revenue, Improve Operational Efficiency, Accelerate Product Innovation, Improve Customer Success)
- `KeyResult` — Single line of text
- `Project` — Single line of text
- `ConfidenceScore` — Number (0–1, 2 decimal places)
- `Source` — Choice (Email, Teams, Upload, Manual)
- `ContentTypeLabel` — Single line of text
- `Owner` — Person or Group
- `ClassifiedDate` — Date and Time
- `ReviewedBy` — Person or Group
- `OverrideReason` — Multiple lines of text
- `MeetingDate` — Date and Time (for transcripts)
- `EmailSentDate` — Date and Time (for email attachments)

**Series-specific columns for `meeting-transcripts` only** — see section 2.6 above (`KMSeriesId` indexed, `KMSeriesName`, `KMSeriesSlug`, `KMIsRecurring`, `KMOccurrenceNumber`, `KMCadence`, `KMSeriesOKRLocked`, `KMPreviousOccurrenceUrl`, `KMOpenActionCount`, `KMAttendeeCount`)

**Folder structure to pre-create inside `meeting-transcripts`:**
- `_Series/` — one subfolder per recurring meeting, created automatically by the flow
- `_OneOff/` — year → quarter subfolders for non-recurring meetings

**Tracking lists to create:**
- `KM-Classification-Log` — columns: RunId, Source, OriginalName, AIObjective, FinalObjective, ConfidenceScore, WasOverridden, ProcessedDate, SPFileUrl
- `KM-Correction-Log` — columns: FileId, OriginalObjective, CorrectedObjective, CorrectedBy, CorrectionDate, Reason
- `KM-Prompt-Config` — columns: PromptVersion, SystemPrompt, IsActive, EffectiveDate
- `KM-Metrics-Daily` — columns: Date, FilesProcessed, AutoClassified, HumanReviewed, AvgConfidence
- `KM-Meeting-Series` — the recurring-meeting registry, see section 2.7 above

---

### RETRIEVAL — how information comes back out

This is the payoff for all the structure above. Four access paths, most-used first:

1. **Series overview page** — open `_Series/{slug}/00_SERIES-OVERVIEW.md` and you're caught up on a whole series in one read
2. **"By Series" library view** — grouped and collapsible, browse without knowing folder paths
3. **SharePoint search with metadata refiners** — search `pricebook`, refine by Series Name and Objective
4. **Ask My Assistant in Teams** — "what did we decide about enterprise discounts in the revenue standup?" The assistant filters `meeting-transcripts` by `KMSeriesName`, reads the decision ledger out of `00_series-state.json`, and answers with a citation link

Path 4 is why the decision ledger is stored as machine-readable JSON: the assistant answers from a ledger instead of re-reading 31 transcripts. **Please include the setup for this retrieval capability in Agent 1 (My Assistant)** — add SharePoint as a knowledge source scoped to the `meeting-transcripts` library, and give the agent a topic that handles "what did we decide/discuss about X" by querying series state.

---

### HOW TO MAKE THIS REPRODUCIBLE FOR TEAMMATES

1. Export the Copilot Studio agent as a solution (.zip) from Power Platform Admin → Solutions
2. Share the solution file so teammates can import it into their own Power Platform environment
3. When they import, they authorize their own connections (Outlook, Teams, SharePoint)
4. The SharePoint libraries are shared (same site), but each person's Outlook/calendar data is private
5. The Claude API key is stored as an environment variable in Power Platform — each person can use the same shared org key or their own personal key

Please give me exact step-by-step instructions for all of the above, starting with:
1. How to create the SharePoint libraries and columns (manual steps in SharePoint UI if PnP PowerShell is not available), including the indexed `KMSeriesId` column and the `_Series` / `_OneOff` folders
2. How to build Agent 1 (My Assistant) in Copilot Studio, including the SharePoint knowledge source for series retrieval
3. How to build the Power Automate flow for Agent 2 (Meeting Intelligence) — **especially the series detection, reading and writing `00_series-state.json`, and the OKR lock logic**, since that's the part that makes recurring meetings coherent
4. How to build the Power Automate flow for Agent 3 (Email Triage) at make.powerautomate.com
5. How to connect the Claude HTTP action with an environment variable for the API key
6. How to publish My Assistant to Teams so it appears as a chat
7. How to export the solution and share with teammates

For step 3, be concrete about the SharePoint connector actions needed to read a JSON file from a folder, parse it, mutate it, and write it back — that round-trip is the piece I most need to get right.

---
