# Step 6 — Visibility Dashboard

---

## Option A: SharePoint List-Based Dashboard (Zero cost, works today)

Build directly on your existing `DaniandEthan` site using SharePoint list views + web parts.

### Required SharePoint Lists

#### `KM-Classification-Log` (already defined in Step 2)
Feeds all metrics.

#### `KM-Metrics-Daily` (aggregated by Power Automate)

| Column             | Type   | Description |
|--------------------|--------|-------------|
| `Date`             | Date   | Report date |
| `TotalClassified`  | Number | Documents classified that day |
| `AutoApproved`     | Number | Confidence ≥ 0.75, no human review |
| `SentForReview`    | Number | Confidence < 0.75 |
| `Overridden`       | Number | Human changed AI classification |
| `Rejected`         | Number | Discarded by reviewer |
| `AvgConfidence`    | Number | Average confidence score |
| `ByObjective`      | Multi-line text | JSON: {"Increase Revenue": 12, ...} |
| `BySource`         | Multi-line text | JSON: {"Email": 8, "Teams": 3, ...} |

**Flow: `KM | Daily Metrics Aggregation | PROD`**
Trigger: Recurrence — daily at 23:00 UTC
Aggregates previous day's `KM-Classification-Log` into `KM-Metrics-Daily`

---

### SharePoint Dashboard Page Layout

**Page name:** `KM Intelligence Dashboard`
**URL:** `https://octaveint.sharepoint.com/sites/DaniandEthan/SitePages/KM-Dashboard.aspx`

#### Section 1 — Hero KPIs (4 quick stats tiles)

| Tile                  | Data source                                | Formula |
|-----------------------|--------------------------------------------|---------|
| Documents This Week   | `KM-Classification-Log` — count last 7d    | COUNT |
| Automation Rate       | `KM-Metrics-Daily` — AutoApproved / Total  | AVG last 7d |
| Avg Confidence Score  | `KM-Metrics-Daily` — AvgConfidence         | AVG last 7d |
| Pending Review        | `KM-Classification-Log` — ReviewedBy empty | COUNT |

Use **Quick Chart web part** or **Highlighted Content web part** + custom CSS for tiles.

#### Section 2 — Files per OKR (Bar chart)

**Data:** `KM-Classification-Log` grouped by `AIObjective`

```
Quick Chart web part:
  Type: Column chart
  Data: [Manual labels]
    Increase Revenue: [dynamic count]
    Improve Ops Efficiency: [dynamic count]
    Accelerate Product Innovation: [dynamic count]
    Improve Customer Success: [dynamic count]
```

For live data, use **Power Apps** embed or **Power BI** tile.

#### Section 3 — Activity per Key Result (List view)

**SharePoint List View web part** on `KM-Classification-Log`:
```
Columns shown: AIKeyResult, Count (grouped), AvgConfidence
Group by: AIKeyResult
Sort: Count desc
Filter: ClassifiedDate >= [Today]-30
```

#### Section 4 — Misclassification Rate Trend

**Source:** `KM-Correction-Log` — CorrectionType ≠ 'Confirmed Correct', grouped by week

Displayed as a **Quick Chart** line chart with weeks on X axis, correction count on Y axis.

#### Section 5 — Needs Review Queue

**SharePoint List View web part** on `KM-Classification-Log`:
```
Filter: ReviewedBy is empty AND ConfidenceScore < 0.75
Sort: ConfidenceScore asc (lowest confidence first)
Columns: OriginalSubject/FileName, AIObjective, ConfidenceScore, Source, ClassifiedDate, [Review button]
```

#### Section 6 — Top Content Sources (Donut)

Pie/donut chart: Email vs Teams vs Upload vs API vs SharePoint Sync
Source: `KM-Metrics-Daily` → `BySource` JSON

---

## Option B: Power BI Dashboard (Recommended for scale)

### Data Sources

| Dataset               | Source                                     | Refresh |
|-----------------------|--------------------------------------------|---------|
| Classifications       | `KM-Classification-Log` SharePoint list    | Hourly  |
| Corrections           | `KM-Correction-Log` SharePoint list        | Hourly  |
| Daily Metrics         | `KM-Metrics-Daily` SharePoint list         | Daily   |
| OKR Definitions       | `OKR-Definitions` SharePoint list          | Weekly  |

### Report Pages

#### Page 1: Executive Summary
- KPI cards: Total classified (MTD), Automation rate %, Avg confidence, Pending reviews
- Trend line: Daily classification volume (last 30 days)
- Pie: Split by Source (Email / Teams / Upload)

#### Page 2: OKR Alignment
- Stacked bar: Documents per Objective (weekly trend)
- Heat map: Objective × Key Result (density of documents)
- Table: Key Results with document count + avg confidence

#### Page 3: Quality & Accuracy
- Gauge: Overall automation rate (target: 85%)
- Line chart: Weekly misclassification rate trend
- Scatter: Confidence score distribution
- Table: Top 10 misclassified patterns (keyword → wrong OKR)

#### Page 4: Activity Feed
- Table: Last 50 classified documents with drill-through to SharePoint
- Filter: By source, by objective, by date range, by reviewer

#### Page 5: Feedback Loop Health
- Bar: Corrections by objective (which OKR needs the most improvement)
- KPI: Training batches run, examples in prompt
- Table: Recent corrections with before/after

### Power BI Connection Setup

```
Get Data → SharePoint Online List
Site URL: https://octaveint.sharepoint.com/sites/DaniandEthan
Select lists: KM-Classification-Log, KM-Correction-Log, KM-Metrics-Daily
```

Publish to: **Power BI workspace** → embed tiles back into SharePoint dashboard page via **Power BI web part**.

---

## Alerts & Proactive Notifications

### Flow: `KM | Dashboard Alerts | PROD`
**Trigger:** Recurrence — daily at 08:00

**Alert 1 — Stale review queue:**
If COUNT of items in Needs Review > 10 AND oldest item > 3 days:
→ Teams message to `#ai-review-queue` tagging OKR Champions

**Alert 2 — Accuracy drop:**
If weekly accuracy < 80%:
→ Teams message to `#knowledge-management` with details

**Alert 3 — Volume spike:**
If today's classification count > 2× 7-day average:
→ Informational Teams post (capacity awareness)

**Alert 4 — Unprocessed corrections:**
If `KM-Correction-Log` has items where `UsedInTraining = false` AND age > 7 days:
→ Reminder to Knowledge Manager to run rules refresh
