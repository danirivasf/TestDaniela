# Naming Conventions

Consistent naming reduces ambiguity, supports search, and enables automation. All names use **kebab-case** for URLs/IDs and **Title Case** for display names.

---

## 1. Site Collections

Pattern: `{domain-area}` (short, lowercase, hyphenated)

| Display Name              | URL Slug          |
|---------------------------|-------------------|
| Knowledge Hub             | `knowledge-hub`   |
| OKR Strategy              | `okr-strategy`    |
| Operations Excellence     | `ops-excellence`  |
| Product & Pricing         | `product-pricing` |
| Customer Success          | `customer-success`|
| Archive                   | `archive`         |

---

## 2. Document Libraries

Pattern: `{ContentArea}` (PascalCase display name; kebab-case internal name)

| Display Name         | Internal Name         |
|----------------------|-----------------------|
| AI Inbox             | `ai-inbox`            |
| Classified Documents | `classified-documents`|
| Email Archives       | `email-archives`      |
| Meeting Transcripts  | `meeting-transcripts` |
| Spreadsheets         | `spreadsheets`        |
| Pricebooks           | `pricebooks`          |
| SKU Catalog          | `sku-catalog`         |
| Quotes               | `quotes`              |

---

## 3. Files

### General Pattern
```
{YYYY-MM-DD}_{ObjectiveCode}_{ContentType}_{DescriptiveName}[_v{N}]
```

| Token           | Rules |
|-----------------|-------|
| `YYYY-MM-DD`    | ISO date of creation or original document date |
| `ObjectiveCode` | 3–4 letter abbreviation: `REV` (Revenue), `OPS` (Operations), `PROD` (Product), `CS` (Customer Success) |
| `ContentType`   | `EMAIL`, `ATTACH`, `TRANSCRIPT`, `SHEET`, `DECK`, `REPORT`, `CONTRACT`, `SOP` |
| `DescriptiveName` | Title Case, max 40 chars, spaces replaced with underscores |
| `_vN`           | Optional manual version suffix for non-SPO-versioned exports |

### Examples

| Scenario | Filename |
|----------|----------|
| Pricebook spreadsheet | `2026-07-10_REV_SHEET_Pricebook_Q3_2026.xlsx` |
| SKU catalog update email | `2026-07-08_PROD_EMAIL_SKU_Catalog_Q3_Launch.eml` |
| Sales meeting transcript | `2026-07-09_REV_TRANSCRIPT_Q3_Pipeline_Review.docx` |
| Quote for Acme Corp | `2026-07-10_REV_ATTACH_Quote_Acme_Corp_v2.pdf` |
| SOP for quote approval | `2026-06-01_OPS_SOP_Quote_Approval_Workflow.docx` |

---

## 4. Term Sets (Managed Metadata)

Pattern: `{Namespace}/{TermSet}/{Term}`

```
OKR
├── Objectives
│   ├── Increase Revenue
│   ├── Improve Operational Efficiency
│   ├── Accelerate Product Innovation
│   └── Improve Customer Success
└── KeyResults
    ├── Increase Revenue
    │   ├── Achieve $5M ARR by Q4
    │   ├── Improve win rate to 35%
    │   └── Expand to 3 new markets
    ├── Improve Operational Efficiency
    │   ├── Reduce quote cycle time by 30%
    │   ├── Cut manual data entry by 50%
    │   └── Achieve 99.5% system uptime
    └── ...

Projects
├── Pricebook Refresh 2026
├── ERP Migration
├── Pricing Optimization
└── ...
```

Term naming rules:
- Use sentence case for term labels
- Include the measurement/target in Key Result terms (e.g., "by Q4", "by 30%")
- Deprecated terms: mark as `[DEPRECATED]` prefix, never delete (preserves historical metadata)

---

## 5. Content Types

Pattern: `KM-{SemanticType}` (prefix `KM-` ensures no collision with built-in types)

| Content Type     |
|------------------|
| `KM-Email`       |
| `KM-Attachment`  |
| `KM-Transcript`  |
| `KM-Spreadsheet` |
| `KM-Presentation`|
| `KM-Report`      |
| `KM-Contract`    |
| `KM-SOP`         |

---

## 6. Power Automate Flows

Pattern: `KM | {Source} → {Action} | {Environment}`

Examples:
- `KM | Email → Classify & Store | PROD`
- `KM | Teams Transcript → Ingest | PROD`
- `KM | Spreadsheet Upload → Tag & Route | PROD`
- `KM | AI-Inbox → Review Reminder | PROD`

---

## 7. Azure AD Groups

Pattern: `km-{role}[-{scope}]` (lowercase, hyphenated)

| Group Name                        | Purpose |
|-----------------------------------|---------|
| `km-knowledge-managers`           | Full governance rights |
| `km-okr-champions-revenue`        | OKR Champion for Revenue objective |
| `km-okr-champions-ops`            | OKR Champion for Operations objective |
| `km-okr-champions-product`        | OKR Champion for Product objective |
| `km-dept-leads`                   | Department leads |
| `km-contributors`                 | Content contributors |
| `km-readers`                      | Read-only |
| `km-compliance`                   | Compliance officers |
| `svc-km-classifier`               | AI pipeline service principal |
