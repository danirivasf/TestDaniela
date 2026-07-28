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

### AGENT 2 — Meeting Intelligence (Auto-Summarize Teams Meetings)

**What it does:**
After every Teams meeting ends (recurring or one-off), automatically:
1. Capture the meeting transcript (Teams auto-generates .vtt transcript files)
2. Send transcript to AI → generate structured summary:
   - Meeting title, date, attendees
   - Key decisions made
   - Action items with owner names
   - Topics discussed mapped to company OKRs (see OKR list below)
   - Confidence score (0–1) that the mapping is correct
3. Save the summary as a SharePoint page or document in the Meeting Transcripts library at: `https://octaveint.sharepoint.com/sites/DaniandEthan/meeting-transcripts`
4. Tag the document with metadata: Objective, KeyResult, MeetingDate, Attendees, ContentType = "Meeting Transcript"
5. If confidence < 0.75, post a Teams message to the meeting organizer asking them to confirm the OKR mapping

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

**Tracking lists to create:**
- `KM-Classification-Log` — columns: RunId, Source, OriginalName, AIObjective, FinalObjective, ConfidenceScore, WasOverridden, ProcessedDate, SPFileUrl
- `KM-Correction-Log` — columns: FileId, OriginalObjective, CorrectedObjective, CorrectedBy, CorrectionDate, Reason
- `KM-Prompt-Config` — columns: PromptVersion, SystemPrompt, IsActive, EffectiveDate
- `KM-Metrics-Daily` — columns: Date, FilesProcessed, AutoClassified, HumanReviewed, AvgConfidence

---

### HOW TO MAKE THIS REPRODUCIBLE FOR TEAMMATES

1. Export the Copilot Studio agent as a solution (.zip) from Power Platform Admin → Solutions
2. Share the solution file so teammates can import it into their own Power Platform environment
3. When they import, they authorize their own connections (Outlook, Teams, SharePoint)
4. The SharePoint libraries are shared (same site), but each person's Outlook/calendar data is private
5. The Claude API key is stored as an environment variable in Power Platform — each person can use the same shared org key or their own personal key

Please give me exact step-by-step instructions for all of the above, starting with:
1. How to create the SharePoint libraries and columns (manual steps in SharePoint UI if PnP PowerShell is not available)
2. How to build Agent 1 (My Assistant) in Copilot Studio
3. How to build the Power Automate flow for Agent 3 (Email Triage) at make.powerautomate.com
4. How to connect the Claude HTTP action with an environment variable for the API key
5. How to publish My Assistant to Teams so it appears as a chat
6. How to export the solution and share with teammates

---
