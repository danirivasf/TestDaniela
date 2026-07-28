# Step 2 — Librarian Agent: Email + Attachment Flow

## Overview

This Power Automate flow is the core ingestion engine. It triggers on every inbound email with an attachment, classifies it via LLM, stores the file in SharePoint, and routes low-confidence items to Teams for human review.

---

## Flow: `KM | Email → Classify & Store | PROD`

### Trigger
**When a new email arrives (V3)** — Office 365 Outlook connector

```
Trigger settings:
  Folder:        Inbox
  Include Attachments: Yes
  Only with Attachments: Yes
  From: (optional — scope to specific senders or leave blank for all)
```

---

### Step 1 — Initialize Variables

| Variable Name        | Type    | Initial Value |
|----------------------|---------|---------------|
| `varConfidenceScore` | Float   | 0             |
| `varClassification`  | Object  | {}            |
| `varSPFileUrl`       | String  | ""            |
| `varRunId`           | String  | `@{guid()}`   |

---

### Step 2 — Extract Email Content

**Compose — Build content payload**

```json
{
  "run_id": "@{variables('varRunId')}",
  "source": "Email",
  "email_subject": "@{triggerOutputs()?['body/subject']}",
  "email_body": "@{triggerOutputs()?['body/body']}",
  "email_from": "@{triggerOutputs()?['body/from']}",
  "email_sent_date": "@{triggerOutputs()?['body/receivedDateTime']}",
  "has_attachments": true,
  "attachment_names": "@{triggerOutputs()?['body/attachments']}"
}
```

---

### Step 3 — Extract Attachment Text

**Apply to each** — loop over `triggerOutputs()?['body/attachments']`

Inside loop:

**Condition: Is it an Office/PDF file?**
```
item()?['contentType'] contains 'spreadsheet'
OR item()?['contentType'] contains 'wordprocessing'
OR item()?['contentType'] contains 'pdf'
```

**If Yes → Get attachment content**
Use **Office 365 Outlook — Get Attachment (V2)**:
```
Message ID: @{triggerOutputs()?['body/id']}
Attachment ID: @{items('Apply_to_each')?['id']}
```

Append to `varAttachmentText` variable (string):
```
@{items('Apply_to_each')?['name']}: [binary content — pass to LLM via base64 or extract first 2000 chars of text if parseable]
```

> Note: For Excel files, use the **Excel Online (Business)** connector or a custom Azure Function to extract cell text before passing to LLM.

---

### Step 4 — Call LLM Classification Engine

**HTTP — POST to Claude API** (or Azure OpenAI — swap endpoint/auth accordingly)

```
Method:  POST
URI:     https://api.anthropic.com/v1/messages
Headers:
  x-api-key:         @{parameters('AnthropicApiKey')}
  anthropic-version: 2023-06-01
  Content-Type:      application/json
```

**Body** (paste the full prompt — see `step3-brain-prompt.json`):

```json
{
  "model": "claude-opus-4-8",
  "max_tokens": 1024,
  "messages": [
    {
      "role": "user",
      "content": "You are an enterprise knowledge classification engine.\n\nYour job:\nAnalyze the input and map it to company OKRs.\n\nINPUT:\n@{outputs('Compose_-_Build_content_payload')}\n\nATTACHMENT TEXT (first 2000 chars):\n@{variables('varAttachmentText')}\n\nOUTPUT (strict JSON only, no other text):\n{\n  \"summary\": \"...\",\n  \"keywords\": [\"...\"],\n  \"objective\": \"...\",\n  \"key_result\": \"...\",\n  \"project\": \"...\",\n  \"content_type\": \"...\",\n  \"confidence\": 0.0,\n  \"reasoning\": \"...\"\n}\n\nRules:\n- Prefer high precision over guessing\n- If uncertain, lower confidence score\n- Use business language\n- Keep outputs consistent\n- Objectives must be one of: Increase Revenue, Improve Operational Efficiency, Accelerate Product Innovation, Improve Customer Success"
    }
  ]
}
```

**Parse JSON** — parse `body/content[0]/text` from HTTP response into `varClassification`

Schema (use `step3-brain-prompt.json` output schema):
```json
{
  "type": "object",
  "properties": {
    "summary":      { "type": "string" },
    "keywords":     { "type": "array", "items": { "type": "string" } },
    "objective":    { "type": "string" },
    "key_result":   { "type": "string" },
    "project":      { "type": "string" },
    "content_type": { "type": "string" },
    "confidence":   { "type": "number" },
    "reasoning":    { "type": "string" }
  }
}
```

Set `varConfidenceScore`:
```
@{body('Parse_JSON')?['confidence']}
```

---

### Step 5 — Save Attachment to SharePoint

**Apply to each** attachment (second loop):

**SharePoint — Create file**
```
Site Address:   https://octaveint.sharepoint.com/sites/DaniandEthan
                (or dynamic based on objective → see routing table below)
Folder Path:    /ai-inbox
File Name:      @{formatDateTime(utcNow(), 'yyyy-MM-dd')}_@{substring(body('Parse_JSON')?['objective'],0,3)}_EMAIL_@{replace(items()?['name'],' ','_')}
File Content:   @{items()?['contentBytes']}
```

**Objective → Site routing table:**

| Objective                         | Site URL slug       |
|-----------------------------------|---------------------|
| Increase Revenue                  | `product-pricing`   |
| Improve Operational Efficiency    | `ops-excellence`    |
| Accelerate Product Innovation     | `product-pricing`   |
| Improve Customer Success          | `customer-success`  |
| (unmatched)                       | `knowledge-hub`     |

Set `varSPFileUrl` = `@{outputs('Create_file')?['body/{Link}']}` 

---

### Step 6 — Populate SharePoint Metadata

**SharePoint — Update file properties**
```
Site Address:  [same as above]
Library:       ai-inbox
Id:            @{outputs('Create_file')?['body/ItemId']}
```

Fields to set:

| Column              | Value |
|---------------------|-------|
| `Objective`         | `@{body('Parse_JSON')?['objective']}` |
| `KeyResult`         | `@{body('Parse_JSON')?['key_result']}` |
| `Project`           | `@{body('Parse_JSON')?['project']}` |
| `ContentTypeLabel`  | `@{body('Parse_JSON')?['content_type']}` |
| `ConfidenceScore`   | `@{variables('varConfidenceScore')}` |
| `Source`            | `Email` |
| `Owner`             | `@{triggerOutputs()?['body/from']}` |
| `ClassifiedDate`    | `@{utcNow()}` |
| `EmailSentDate`     | `@{triggerOutputs()?['body/receivedDateTime']}` |

---

### Step 7 — Confidence Gate → Teams Approval

**Condition:** `@{variables('varConfidenceScore')}` is less than `0.75`

**If Yes → Post adaptive card to Teams**

**Microsoft Teams — Post an Adaptive Card and wait for a response**
```
Post in:  Channel
Team:     Knowledge Management
Channel:  #ai-review-queue
```

Adaptive Card body:
```json
{
  "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
  "type": "AdaptiveCard",
  "version": "1.4",
  "body": [
    { "type": "TextBlock", "text": "🔍 Low-Confidence Classification — Review Required", "weight": "Bolder", "size": "Medium" },
    { "type": "FactSet", "facts": [
      { "title": "Subject:",      "value": "@{triggerOutputs()?['body/subject']}" },
      { "title": "From:",         "value": "@{triggerOutputs()?['body/from']}" },
      { "title": "AI Objective:", "value": "@{body('Parse_JSON')?['objective']}" },
      { "title": "Key Result:",   "value": "@{body('Parse_JSON')?['key_result']}" },
      { "title": "Confidence:",   "value": "@{variables('varConfidenceScore')}" },
      { "title": "Reasoning:",    "value": "@{body('Parse_JSON')?['reasoning']}" },
      { "title": "File:",         "value": "@{variables('varSPFileUrl')}" }
    ]},
    { "type": "Input.ChoiceSet", "id": "approved_objective", "label": "Correct Objective:", "choices": [
      { "title": "Increase Revenue",               "value": "Increase Revenue" },
      { "title": "Improve Operational Efficiency", "value": "Improve Operational Efficiency" },
      { "title": "Accelerate Product Innovation",  "value": "Accelerate Product Innovation" },
      { "title": "Improve Customer Success",       "value": "Improve Customer Success" }
    ]},
    { "type": "Input.Text", "id": "override_reason", "label": "Override reason (if changing):", "isMultiline": true }
  ],
  "actions": [
    { "type": "Action.Submit", "title": "Approve & Promote", "data": { "action": "approve" } },
    { "type": "Action.Submit", "title": "Reject & Discard",  "data": { "action": "reject" } }
  ]
}
```

**If action = approve:**
- Update `Objective` with `approved_objective` from card response
- Update `ReviewedBy` with approver's email
- Update `ReviewedDate` with `@{utcNow()}`
- If `approved_objective` ≠ `@{body('Parse_JSON')?['objective']}`: set `OverrideReason`
- Move file from `ai-inbox` to `classified-documents`

**If action = reject:**
- Delete file from SharePoint
- Log rejection in tracking list

**If No (confidence ≥ 0.75):**
- Move file directly from `ai-inbox` to `classified-documents`

---

### Step 8 — Log to Tracking Table

**SharePoint — Create item** in list `KM-Classification-Log`

| Column               | Value |
|----------------------|-------|
| `RunId`              | `@{variables('varRunId')}` |
| `Source`             | `Email` |
| `OriginalSubject`    | `@{triggerOutputs()?['body/subject']}` |
| `AIObjective`        | `@{body('Parse_JSON')?['objective']}` |
| `AIKeyResult`        | `@{body('Parse_JSON')?['key_result']}` |
| `ConfidenceScore`    | `@{variables('varConfidenceScore')}` |
| `WasOverridden`      | `@{if(equals(body('Parse_JSON')?['objective'], outputs('Teams_response')?['approved_objective']), false, true)}` |
| `FinalObjective`     | `[final value after approval]` |
| `SPFileUrl`          | `@{variables('varSPFileUrl')}` |
| `ProcessedDate`      | `@{utcNow()}` |
| `FlowRunUrl`         | `@{concat('https://flow.microsoft.com/manage/environments/', parameters('EnvironmentId'), '/flows/', workflow()?['name'], '/runs/', workflow()?['run']['name'])}` |

---

## Parameters (store in flow or Azure Key Vault)

| Parameter          | Description |
|--------------------|-------------|
| `AnthropicApiKey`  | Claude API key (store in Key Vault, reference via `@parameters()`) |
| `TenantSPUrl`      | Base SharePoint URL |
| `EnvironmentId`    | Power Platform environment GUID |
| `ReviewChannelId`  | Teams channel ID for review queue |
