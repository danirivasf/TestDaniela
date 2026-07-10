# Step 5 — Self-Learning Feedback Loop

This is the compounding intelligence layer. Every human correction becomes a training signal that improves future classifications.

---

## How It Works

```
User changes metadata / moves file / overrides classification
              │
              ▼
    Power Automate captures delta
              │
              ▼
    Correction stored in SP list
              │
              ▼
    Weekly: rules updated + LLM prompt enriched
              │
              ▼
    Classification accuracy improves over time
```

---

## 1. SharePoint List: `KM-Correction-Log`

This list captures every human override. It is the training dataset.

### List Schema

| Column                  | Type                  | Required | Description |
|-------------------------|-----------------------|----------|-------------|
| `RunId`                 | Single line of text   | Yes      | Links back to `KM-Classification-Log` |
| `CorrectionDate`        | Date and Time         | Yes      | When the correction was made |
| `CorrectedBy`           | Person or Group       | Yes      | Who made the correction |
| `OriginalObjective`     | Choice (OKR list)     | Yes      | What the AI classified |
| `OriginalKeyResult`     | Single line of text   | Yes      | AI's key result |
| `OriginalConfidence`    | Number (0.00–1.00)    | Yes      | AI's confidence at time of classification |
| `CorrectedObjective`    | Choice (OKR list)     | Yes      | Human's corrected objective |
| `CorrectedKeyResult`    | Single line of text   | Yes      | Human's corrected key result |
| `CorrectedProject`      | Single line of text   | No       | Human's corrected project |
| `CorrectionType`        | Choice                | Yes      | `Objective Change`, `KeyResult Change`, `Both`, `Confirmed Correct` |
| `OverrideReason`        | Multiple lines        | No       | Human's explanation |
| `DocumentKeywords`      | Multiple lines        | Yes      | Keywords from original document (copied from AI extraction) |
| `DocumentSummary`       | Multiple lines        | Yes      | AI summary of the document |
| `ContentType`           | Choice                | Yes      | Email, Transcript, Spreadsheet, etc. |
| `Source`                | Choice                | Yes      | Email, Teams, Upload |
| `SPFileUrl`             | Hyperlink             | Yes      | Link to the corrected document |
| `UsedInTraining`        | Yes/No                | No       | Flag: has this correction been incorporated into rules? |
| `TrainingBatchId`       | Single line of text   | No       | Which training batch used this correction |

### Trigger Flow: `KM | Correction Captured | PROD`

**Trigger:** SharePoint — When an item is created or modified in `classified-documents` or `ai-inbox`

**Condition:** Any of these fields changed:
- `Objective` (OData: `Objective ne triggerOutputs()?['body/Objective']`)
- `KeyResult`
- `Project`
- `ReviewedBy` is not empty (human just reviewed)

**Actions:**
1. Get previous version of item (SharePoint — Get versions)
2. Compare old vs new values
3. If any OKR field changed → create item in `KM-Correction-Log`
4. Post summary to Teams `#ai-learning` channel:
   ```
   📚 Correction captured: [AI said "X"] → [Human said "Y"]
   Document: [link]  |  Corrected by: [name]
   ```

---

## 2. Weekly Rules Update Process

### Flow: `KM | Weekly Rules Refresh | PROD`

**Trigger:** Recurrence — Every Monday at 06:00 UTC

**Step 1 — Get recent corrections**
```
SharePoint — Get items from KM-Correction-Log
Filter: UsedInTraining eq false AND CorrectionType ne 'Confirmed Correct'
Order by: CorrectionDate desc
Top: 100
```

**Step 2 — Aggregate patterns**
```
Compose — Group by ObjectivePair:
{
  "corrections": [
    {
      "from_objective": "Accelerate Product Innovation",
      "to_objective": "Increase Revenue",
      "keywords_present": ["pricebook", "sku", "price list"],
      "count": 12,
      "example_reasoning": "..."
    }
  ]
}
```

**Step 3 — Call LLM to generate updated rules**

```json
{
  "model": "claude-opus-4-8",
  "max_tokens": 2048,
  "messages": [{
    "role": "user",
    "content": "You are maintaining a classification rule system.\n\nHere are recent human corrections to AI classifications:\n{{corrections_json}}\n\nCurrent classification rules are at: {{current_rules_summary}}\n\nBased on these corrections, generate:\n1. Updated keyword mappings (JSON)\n2. Rules that should be strengthened or weakened\n3. New edge cases to handle\n4. Confidence adjustment recommendations\n\nFormat as JSON:\n{\n  \"keyword_updates\": [{\"keyword\": \"...\", \"add_to_objective\": \"...\", \"remove_from_objective\": \"...\", \"weight_delta\": 0.0}],\n  \"rule_changes\": [\"plain text rule description\"],\n  \"new_examples\": [{\"input\": \"...\", \"correct_output\": {...}}],\n  \"confidence_adjustments\": [{\"content_type\": \"...\", \"source\": \"...\", \"delta\": 0.0}]\n}"
  }]
}
```

**Step 4 — Store updated rules**
- Save LLM output to `KM-Classification-Rules` SharePoint list (versioned)
- Mark processed corrections as `UsedInTraining = true` + `TrainingBatchId = [today's date]`
- Send summary to `#knowledge-management` Teams channel

**Step 5 — Update prompt enrichment file**
- Append confirmed correction examples to `classification/okr-mapping-logic.md` (via GitHub/SharePoint)
- These become few-shot examples injected into the brain prompt

---

## 3. Prompt Enrichment: Few-Shot Examples

As corrections accumulate, inject confirmed examples into the brain prompt.
The prompt automatically gets smarter without retraining a model.

Updated brain prompt section (inserted before rules):

```
CONFIRMED EXAMPLES FROM YOUR ORGANIZATION:

Example 1:
Input keywords: pricebook, sku, tier pricing, margin
Correct output: objective=Increase Revenue, key_result=Achieve $5M ARR by Q4, confidence=0.92

Example 2:
Input: Teams meeting about CPQ approval bottleneck
Correct output: objective=Improve Operational Efficiency, key_result=Reduce quote cycle time by 30%, confidence=0.88

[Additional examples appended weekly from KM-Correction-Log]
```

**Flow: `KM | Enrich Prompt with Examples | PROD`**

**Trigger:** After weekly rules refresh completes

**Steps:**
1. Get top 20 high-confidence confirmed corrections (where original AI = human correction, `CorrectionType = Confirmed Correct`)
2. Get top 10 corrections where AI was wrong (to teach edge cases)
3. Format as few-shot examples
4. Update `KM-Prompt-Config` SharePoint list item (stores current active prompt)
5. All 4 classification flows read from `KM-Prompt-Config` at runtime (not hardcoded)

---

## 4. Accuracy Metrics (automated monthly)

### Flow: `KM | Monthly Accuracy Report | PROD`

Computes:
- `classification_accuracy` = (total items - items corrected) / total items
- `accuracy_by_objective` = breakdown per OKR
- `accuracy_by_source` = Email vs Teams vs Upload
- `accuracy_by_confidence_band` = how often each band (High/Medium-High/Low) was correct
- `top_misclassified_patterns` = keyword pairs that most often led to wrong objective

Output: creates a `KM-Accuracy-Report-YYYY-MM` item in a SharePoint list for Power BI to consume.

---

## 5. Retraining Prompts (monthly review)

When accuracy drops below 80% for any objective, generate a retraining prompt:

```
Prompt template stored in KM-Prompt-Config:

"The following objective is being misclassified {{accuracy_pct}}% of the time.
Common errors: {{error_patterns}}

Generate 10 new discriminating rules to distinguish '{{confused_obj_a}}' 
from '{{confused_obj_b}}' when these keywords are present: {{common_keywords}}

Format as keyword weight adjustments JSON."
```

Knowledge Manager reviews the output, approves changes, and they are applied to the next weekly batch.
