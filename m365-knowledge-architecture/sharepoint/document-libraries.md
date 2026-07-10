# Document Libraries

All libraries use **metadata columns** (defined in `metadata/schema.md`) as the primary navigation mechanism. Folder structures are optional and flat (max 1 level deep) to avoid deep nesting.

---

## Standard Libraries (present on every spoke site)

### `AI-Inbox`
Staging library where the AI classifier deposits unreviewed items before promotion.

| Property        | Value |
|-----------------|-------|
| Versioning      | Major only, keep last 5 |
| Require checkout | No |
| Default view    | Grouped by `ConfidenceScore` band |
| Retention label | `Transient-30d` (auto-deleted after 30 days if not promoted) |

### `Classified-Documents`
Primary working library for all human-reviewed, AI-classified content.

| Property        | Value |
|-----------------|-------|
| Versioning      | Major + minor, keep last 20 |
| Require checkout | Yes (for documents marked `Sensitive`) |
| Default view    | Grouped by `Objective`, sorted by `ModifiedDate` desc |
| Content types   | Email, Attachment, Transcript, Spreadsheet, Presentation, Report |

### `Email-Archives`
Raw email exports (.eml / .msg) auto-ingested from Exchange.

| Property        | Value |
|-----------------|-------|
| Source          | Power Automate flow from shared mailboxes |
| Versioning      | Major only, no limit (immutable email record) |
| Default view    | Grouped by `KeyResult` |

### `Meeting-Transcripts`
Teams meeting transcripts (VTT/DOCX) auto-ingested from Teams recording pipeline.

| Property        | Value |
|-----------------|-------|
| Source          | Graph API subscription on `callRecords` |
| Versioning      | Major only |
| Default view    | Sorted by `MeetingDate` desc |

### `Spreadsheets`
Excel workbooks — financial models, pricebooks, SKU catalogs, reports.

| Property        | Value |
|-----------------|-------|
| Versioning      | Major + minor, keep last 50 |
| Require checkout | Yes |
| Default view    | Grouped by `Project` |

---

## Site-Specific Libraries

### `product-pricing` site

| Library         | Content | Notes |
|-----------------|---------|-------|
| `Pricebooks`    | Master pricebook Excel files | Checkout required; approval workflow on publish |
| `SKU-Catalog`   | SKU definition spreadsheets | Version-controlled; linked to Pricebooks via metadata |
| `Quotes`        | Quote PDFs / Word docs | Auto-tagged with customer account metadata |

### `ops-excellence` site

| Library         | Content | Notes |
|-----------------|---------|-------|
| `SOPs`          | Process documentation | Approval workflow; review reminder every 180 days |
| `Reports`       | Weekly/monthly operational reports | Auto-ingested from Power BI export pipeline |

---

## View Definitions (all libraries)

| View Name           | Filter / Group                                     |
|---------------------|----------------------------------------------------|
| By Objective        | Group by `Objective`                               |
| By Key Result       | Group by `KeyResult`                               |
| Needs Review        | `ConfidenceScore < 0.75` AND `ReviewedBy` is empty |
| High Confidence     | `ConfidenceScore >= 0.90`                          |
| My Documents        | `Owner` = [Me]                                     |
| This Week           | `ClassifiedDate` >= [Today]-7                      |
