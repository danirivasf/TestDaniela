# Meeting Series Model — Coherent Storage for Recurring Meetings

The problem this solves: a weekly standup that runs for a year produces 52 transcripts. If each one lands as a loose file named after its date, the series is *stored* but not *knowable* — you can't answer "what did we decide about pricing in this meeting over the last quarter?" without opening 13 files.

This model makes every recurring meeting resolve to **one stable home** with a **living overview** that carries state forward between occurrences.

---

## 1. Series Identity — how we know two meetings are the same meeting

Every transcript gets a `SeriesId`. It is resolved in strict priority order — first match wins.

| Priority | Signal | Source | Why it's trusted |
|---|---|---|---|
| 1 | `event.seriesMasterId` | Graph `/me/events/{id}` | Authoritative. Every occurrence of a recurring Outlook series shares this GUID. |
| 2 | `onlineMeeting.joinWebUrl` | Graph `/me/onlineMeetings` | Stable across all occurrences of one recurring Teams meeting. Survives subject renames. |
| 3 | `iCalUId` prefix | Graph event | Shared root for series occurrences in most tenants. |
| 4 | `slug(normalizedSubject) + "--" + slug(organizerUpn)` | Computed fallback | Used when no calendar event can be matched (e.g. transcript arrives without event linkage). |

### Subject normalization (for priority 4)

Strip everything that varies between occurrences, then slugify:

```
Input:  "Weekly Revenue Standup - Jul 28 (Occurrence 31) [EXTERNAL]"
Output: "weekly-revenue-standup"
```

Removal rules, applied in order:
1. Strip bracketed tags: `[EXTERNAL]`, `[CONFIDENTIAL]`, `(Canceled)`
2. Strip dates in any format: `Jul 28`, `2026-07-28`, `28/07`, `7/28/26`
3. Strip occurrence markers: `Occurrence N`, `#N`, `Week N`, `Session N`, `Part N`
4. Strip cadence adjectives *only if* other words remain: `Weekly`, `Biweekly`, `Monthly`, `Daily`, `Quarterly`
5. Strip Teams noise: `Meeting with`, `Microsoft Teams Meeting`, trailing `- Copy`
6. Collapse whitespace/punctuation → lowercase → hyphenate

> **Guardrail:** if normalization reduces the subject to fewer than 3 characters, fall back to the raw subject slug. Never let `"Weekly"` alone become a SeriesId — that would merge unrelated meetings.

### Recurrence determination

A meeting is treated as recurring when **any** of these is true:
- Graph event has `recurrence != null`, or `type` is `occurrence` / `exception` / `seriesMaster`
- A prior transcript already exists with the same resolved `SeriesId`
- Two or more meetings with the same normalized subject + organizer occurred more than 4 days apart

That last rule matters: it catches "recurring in practice" meetings that were booked as separate one-offs.

---

## 2. Folder Layout

Root: `https://octaveint.sharepoint.com/sites/DaniandEthan/meeting-transcripts`

```
meeting-transcripts/
│
├── _Series/                                   ← all recurring meetings
│   │
│   ├── weekly-revenue-standup/
│   │   ├── 00_SERIES-OVERVIEW.md              ← LIVING DOC — rewritten every occurrence
│   │   ├── 00_series-state.json               ← machine state: open actions, OKR lock, counters
│   │   ├── 2026/
│   │   │   ├── 2026-07-28_INC_OCC-031_weekly-revenue-standup.md
│   │   │   ├── 2026-07-21_INC_OCC-030_weekly-revenue-standup.md
│   │   │   └── 2026-07-14_INC_OCC-029_weekly-revenue-standup.md
│   │   ├── 2025/
│   │   │   └── ...
│   │   └── _raw/                              ← original .vtt / .docx transcripts
│   │       └── 2026-07-28_transcript.vtt
│   │
│   └── monthly-pricing-review/
│       └── (same structure)
│
└── _OneOff/                                   ← non-recurring meetings
    └── 2026/
        └── 2026-Q3/
            └── 2026-07-14_INC_acme-pricing-negotiation.md
```

### Why this shape

- **`_Series/` and `_OneOff/` split first** — recurring meetings are the ones you return to; they should not be diluted by 200 one-off calls.
- **Year subfolders inside a series** — keeps folders under SharePoint's practical browse limit while preserving a single series root. A 5-year weekly meeting = 5 folders of ~52 files, not one folder of 260.
- **`00_` prefix on the overview** — sorts to the top of every series folder, so the living summary is the first thing you see when you open the folder.
- **`_raw/` separated** — the .vtt files are evidence, not reading material. Keeping them out of the year folders means browsing a series shows only readable summaries.
- **One-offs bucketed by quarter** — no series to return to, so chronological grouping is enough.

### File naming

```
{YYYY-MM-DD}_{OBJ}_OCC-{NNN}_{series-slug}.md      ← recurring
{YYYY-MM-DD}_{OBJ}_{meeting-slug}.md               ← one-off
```

- `{OBJ}` = 3-letter objective code: `INC` (Increase Revenue), `OPS` (Operational Efficiency), `INN` (Product Innovation), `CUS` (Customer Success), `UNC` (unclassified)
- `OCC-{NNN}` = zero-padded occurrence number, so lexical sort = chronological sort

---

## 3. The Living Series Overview

`00_SERIES-OVERVIEW.md` is **regenerated in full** after every occurrence. It is the single page someone reads to catch up on a series they've missed.

```markdown
# Weekly Revenue Standup — Series Overview

| | |
|---|---|
| **Series ID** | `AAMkAGI2...seriesMasterId` |
| **Cadence** | Weekly, Mondays 09:00 CET |
| **Organizer** | daniela.rivas.fernandez-feo@octave.com |
| **Occurrences** | 31 (first: 2026-01-06, latest: 2026-07-28) |
| **OKR** | Increase Revenue → Achieve $5M ARR **[LOCKED]** |
| **Regulars** | Daniela R., Ethan M., 3 rotating |

## Open Action Items (carried forward)

| # | Action | Owner | Opened | Occurrences open | Status |
|---|---|---|---|---|---|
| 1 | Finalize Q3 pricebook tiers | Ethan M. | OCC-028 | 3 | ⚠️ Stale |
| 2 | Send Acme revised quote | Daniela R. | OCC-031 | 1 | Open |

## Recently Closed

| Action | Owner | Opened | Closed |
|---|---|---|---|
| Draft SKU consolidation plan | Ethan M. | OCC-026 | OCC-030 |

## Decision Ledger (most recent first)

| Date | Occurrence | Decision |
|---|---|---|
| 2026-07-28 | OCC-031 | Hold enterprise discount at 15% through Q3 |
| 2026-07-21 | OCC-030 | Consolidate SKU-4xx family into single tier |

## Recurring Themes
`pricing` (28 mentions) · `enterprise deals` (22) · `SKU rationalization` (14) · `churn` (6)

## Occurrence Index
| Date | # | Summary | Link |
|---|---|---|---|
| 2026-07-28 | 031 | Discount policy held; Acme quote pending | [→](2026/2026-07-28_INC_OCC-031_weekly-revenue-standup.md) |
| 2026-07-21 | 030 | SKU consolidation agreed | [→](2026/2026-07-21_INC_OCC-030_weekly-revenue-standup.md) |
```

### `00_series-state.json` — the machine half

The AI reads this before processing a new occurrence and writes it back after. This is what makes carry-forward work.

```json
{
  "series_id": "AAMkAGI2NDk...",
  "series_slug": "weekly-revenue-standup",
  "series_name": "Weekly Revenue Standup",
  "organizer": "daniela.rivas.fernandez-feo@octave.com",
  "cadence": "Weekly",
  "first_occurrence": "2026-01-06",
  "latest_occurrence": "2026-07-28",
  "occurrence_count": 31,
  "okr": {
    "objective": "Increase Revenue",
    "key_result": "Achieve $5M ARR",
    "locked": true,
    "locked_at_occurrence": 3,
    "consistent_classifications": 29
  },
  "open_actions": [
    {
      "id": "a-028-01",
      "action": "Finalize Q3 pricebook tiers",
      "owner": "Ethan M.",
      "opened_occurrence": 28,
      "opened_date": "2026-07-07",
      "occurrences_open": 3,
      "stale": true,
      "last_mentioned_occurrence": 31
    }
  ],
  "closed_actions": [
    {
      "id": "a-026-02",
      "action": "Draft SKU consolidation plan",
      "owner": "Ethan M.",
      "opened_occurrence": 26,
      "closed_occurrence": 30
    }
  ],
  "decision_ledger": [
    { "occurrence": 31, "date": "2026-07-28", "decision": "Hold enterprise discount at 15% through Q3" }
  ],
  "theme_counts": { "pricing": 28, "enterprise deals": 22, "SKU rationalization": 14 },
  "regular_attendees": ["daniela.rivas.fernandez-feo@octave.com", "ethan.m@octave.com"]
}
```

---

## 4. Carry-Forward Processing

This is the sequence that turns isolated transcripts into a coherent thread.

```
New transcript arrives
        │
        ▼
Resolve SeriesId (priority ladder §1)
        │
        ├─── Not recurring ──▶ store in _OneOff/{YYYY}/{YYYY-QQ}/ ──▶ classify normally ──▶ done
        │
        ▼ Recurring
Look up series in KM-Meeting-Series list
        │
        ├─── Not found ──▶ create series folder + registry entry + state.json (occurrence 1)
        │
        ▼ Found
Read 00_series-state.json
        │
        ▼
Call AI with: new transcript + prior summary + open_actions + locked OKR
        │
        ▼
AI returns: summary, decisions, action_items, action_updates[], themes, objective, confidence
        │
        ▼
Apply action reconciliation (§5)
        │
        ▼
Write occurrence file  ──▶  Rewrite 00_SERIES-OVERVIEW.md  ──▶  Write 00_series-state.json
        │
        ▼
Update KM-Meeting-Series registry
        │
        ▼
Post digest to Teams (series link + what changed since last time)
```

### OKR Lock

Once a series has **3 consecutive occurrences** classified to the same Objective, that mapping **locks**:

- New occurrences inherit the locked Objective/KeyResult automatically
- Confidence is set to `max(ai_confidence, 0.92)` — series history is strong evidence
- The AI still reports what it *would* have chosen; if it disagrees with the lock **3 times in a row**, the lock breaks and a Teams card asks a human to re-map the series
- Locking is per-series, stored in `state.json` and mirrored to the `KM-Meeting-Series` list

This kills the biggest source of noise in recurring-meeting classification: the same weekly meeting drifting between two objectives depending on what happened to be discussed that week.

---

## 5. Action Item Reconciliation

Every occurrence, the AI receives the current `open_actions` and must return an `action_updates` array judging each one:

| Verdict | Meaning | Effect |
|---|---|---|
| `completed` | Transcript indicates the action was finished | Move to `closed_actions`, record closing occurrence |
| `in_progress` | Discussed, still open | Increment `occurrences_open`, update `last_mentioned_occurrence` |
| `not_mentioned` | Absent from this transcript | Increment `occurrences_open`, leave `last_mentioned` unchanged |
| `superseded` | Replaced by a new decision or action | Close with reason, link to replacement |
| `reassigned` | Owner changed | Update owner, keep history |

**Staleness:** an action with `occurrences_open >= 3` is flagged `stale: true` and surfaces at the top of the overview and in the Teams digest. An action `not_mentioned` for 6 consecutive occurrences is auto-archived with reason `abandoned` — it stays in history but leaves the open list, so the open list stays honest.

---

## 6. Metadata Columns (added to the base schema)

Applied to the `meeting-transcripts` library:

| Column | Internal name | Type | Purpose |
|---|---|---|---|
| Series ID | `KMSeriesId` | Text (indexed) | Stable series key — the join column for all series views |
| Series Name | `KMSeriesName` | Text | Human-readable series title |
| Series Slug | `KMSeriesSlug` | Text | Folder name |
| Is Recurring | `KMIsRecurring` | Yes/No | Series vs one-off |
| Occurrence Number | `KMOccurrenceNumber` | Number | Position in series |
| Cadence | `KMCadence` | Choice | Daily / Weekly / Biweekly / Monthly / Quarterly / Ad-hoc |
| Series OKR Locked | `KMSeriesOKRLocked` | Yes/No | Whether OKR is inherited from series |
| Previous Occurrence | `KMPreviousOccurrenceUrl` | Hyperlink | Direct link to prior meeting |
| Open Action Count | `KMOpenActionCount` | Number | Open actions as of this occurrence |
| Attendee Count | `KMAttendeeCount` | Number | For engagement trend |

### Views to create on `meeting-transcripts`

| View | Filter / Group | Answers |
|---|---|---|
| **By Series** | Group by `KMSeriesName`, sort `KMOccurrenceNumber` desc | "Show me this meeting's whole history" |
| **Latest per Series** | `KMOccurrenceNumber` = max per group | "What's the current state of every recurring meeting?" |
| **Stale Actions** | `KMOpenActionCount` > 0, sort desc | "Where are things stuck?" |
| **Needs OKR Review** | `KMSeriesOKRLocked` = No AND `KMConfidenceScore` < 0.75 | Review queue |
| **One-Offs This Quarter** | `KMIsRecurring` = No, `KMMeetingDate` within quarter | Ad-hoc meeting audit |

---

## 7. Registry List — `KM-Meeting-Series`

One row per recurring series. This is the index that makes "which recurring meetings do we even have?" a one-click answer.

| Column | Type | Notes |
|---|---|---|
| `SeriesId` | Text | Primary key, indexed, enforced unique by flow |
| `SeriesName` | Text | Title |
| `SeriesSlug` | Text | Folder name |
| `Organizer` | Person | Meeting owner |
| `Cadence` | Choice | Daily / Weekly / Biweekly / Monthly / Quarterly / Ad-hoc |
| `FolderUrl` | Hyperlink | Series root in SharePoint |
| `OverviewUrl` | Hyperlink | Direct link to `00_SERIES-OVERVIEW.md` |
| `LockedObjective` | Choice | Locked OKR objective (blank until locked) |
| `LockedKeyResult` | Text | Locked KR |
| `OKRLocked` | Yes/No | Lock state |
| `OccurrenceCount` | Number | Total processed |
| `FirstSeen` | DateTime | First occurrence date |
| `LastSeen` | DateTime | Most recent occurrence date |
| `OpenActionCount` | Number | Current open actions |
| `StaleActionCount` | Number | Actions open ≥ 3 occurrences |
| `SeriesStateJson` | Note | Full `state.json` mirror, for flows that can't read files |
| `IsActive` | Yes/No | Auto-set No if no occurrence in 3× cadence interval |

---

## 8. AI Prompt — Series-Aware Classification

Used by the Meeting Intelligence flow. The critical difference from a one-shot summarizer is the **prior context block**.

```
You are an enterprise meeting intelligence engine for Octave.

You are processing occurrence {{occurrence_number}} of a recurring meeting series.
Your job is to summarize this occurrence AND reconcile it against the series history,
so that the series overview stays accurate over time.

=== SERIES CONTEXT ===
Series name:        {{series_name}}
Cadence:            {{cadence}}
Occurrence number:  {{occurrence_number}}
Locked OKR:         {{locked_objective}} → {{locked_key_result}}  (locked: {{okr_locked}})

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
  "decisions": [
    { "decision": "...", "rationale": "...", "owner": "name or null" }
  ],
  "new_action_items": [
    { "action": "...", "owner": "name", "due": "YYYY-MM-DD or null" }
  ],
  "action_updates": [
    {
      "id": "id from open_actions_json",
      "verdict": "completed | in_progress | not_mentioned | superseded | reassigned",
      "evidence": "short quote or paraphrase supporting the verdict",
      "new_owner": "name, only if verdict is reassigned",
      "superseded_by": "description, only if verdict is superseded"
    }
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

### First occurrence of a new series

Same prompt with `previous_summary = "(none — first occurrence)"`, `open_actions_json = []`, `okr_locked = false`. The `action_updates` array comes back empty, and `whats_changed` is an empty string.

---

## 9. Teams Digest for Recurring Meetings

After each occurrence, post to Teams — but frame it as *series delta*, not a fresh summary:

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

The point of leading with "what changed" is that for a meeting you attend weekly, the summary is not the useful part — the delta is.

---

## 10. Retrieval — how you actually get information back out

Four access paths, in order of how often they get used:

1. **Series overview page** — open `_Series/{slug}/00_SERIES-OVERVIEW.md`. Catches you up on a whole series in one read.
2. **"By Series" library view** — grouped, collapsible, chronological within group. Browse without knowing folder paths.
3. **SharePoint search with refiners** — search `pricebook`, then refine by `Series Name` and `Objective`. Metadata columns are what make this work.
4. **Ask My Assistant** — "what did we decide about enterprise discounts in the revenue standup?" The assistant queries the `meeting-transcripts` library filtered by `KMSeriesName`, reads the decision ledger from `state.json`, and answers with a citation link.

Path 4 is the one that justifies all the structure above: the decision ledger is machine-readable, so the assistant answers from a ledger instead of re-reading 31 transcripts.
