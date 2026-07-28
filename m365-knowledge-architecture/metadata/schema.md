# Metadata Schema

All columns are defined as **Site Columns** in the Content Type Hub so they propagate consistently across all site collections.

---

## Column Definitions

### 1. `Objective`
| Property      | Value |
|---------------|-------|
| Type          | Managed Metadata (Term Set: `OKR/Objectives`) |
| Required      | Yes |
| Description   | The top-level OKR Objective this document supports |
| Example       | `Increase Revenue`, `Improve Operational Efficiency` |
| Allow multiple | No |

### 2. `KeyResult`
| Property      | Value |
|---------------|-------|
| Type          | Managed Metadata (Term Set: `OKR/KeyResults`) |
| Required      | Yes |
| Description   | The specific Key Result under the Objective |
| Example       | `Achieve $5M ARR by Q4`, `Reduce quote cycle time by 30%` |
| Allow multiple | Yes (a document can support multiple KRs) |
| Cascade       | Must be a child of the selected `Objective` term |

### 3. `Project`
| Property      | Value |
|---------------|-------|
| Type          | Managed Metadata (Term Set: `Projects`) |
| Required      | No |
| Description   | Project or initiative the document belongs to |
| Example       | `Pricebook Refresh 2026`, `ERP Migration` |
| Allow multiple | Yes |

### 4. `ContentTypeLabel`
| Property      | Value |
|---------------|-------|
| Type          | Choice |
| Required      | Yes |
| Choices       | `Email`, `Attachment`, `Meeting Transcript`, `Spreadsheet`, `Presentation`, `Report`, `Contract`, `SOP`, `Other` |
| Description   | Semantic content type (distinct from SPO content type) |
| Default       | `Other` |

### 5. `ConfidenceScore`
| Property      | Value |
|---------------|-------|
| Type          | Number (decimal, 0.00–1.00) |
| Required      | Yes (set by AI pipeline; defaults to 0.00 for manual uploads) |
| Description   | AI classification confidence. Values below 0.75 trigger human review |
| Display format | Percentage (×100) |
| Threshold     | `< 0.75` → routed to `Needs Review` view; `< 0.50` → flagged for override |

### 6. `Source`
| Property      | Value |
|---------------|-------|
| Type          | Choice |
| Required      | Yes |
| Choices       | `Email`, `Teams`, `Upload`, `Power BI`, `SharePoint Sync`, `API` |
| Description   | System or channel that originated the document |

### 7. `Owner`
| Property      | Value |
|---------------|-------|
| Type          | Person or Group |
| Required      | Yes |
| Description   | Business owner responsible for document accuracy |
| Allow multiple | No |
| Scope         | People only (no groups) |

### 8. `ClassifiedDate`
| Property      | Value |
|---------------|-------|
| Type          | Date and Time |
| Required      | Yes (auto-set by pipeline) |
| Description   | UTC timestamp when AI classification was applied |

### 9. `ReviewedBy`
| Property      | Value |
|---------------|-------|
| Type          | Person or Group |
| Required      | No |
| Description   | Person who reviewed and approved AI classification |

### 10. `ReviewedDate`
| Property      | Value |
|---------------|-------|
| Type          | Date and Time |
| Required      | No |
| Description   | UTC timestamp of human review |

### 11. `OverrideReason`
| Property      | Value |
|---------------|-------|
| Type          | Multiple lines of text (plain text) |
| Required      | No (required if `ReviewedBy` overrides AI classification) |
| Description   | Justification when a reviewer changes the AI-assigned Objective/KeyResult |

### 12. `RetentionLabel`
| Property      | Value |
|---------------|-------|
| Type          | Choice (synced from M365 Compliance center) |
| Required      | No (auto-applied by retention policy) |
| Choices       | `Transient-30d`, `Standard-3yr`, `Financial-7yr`, `Legal-Hold`, `Permanent` |

### 13. `SensitivityLabel`
| Property      | Value |
|---------------|-------|
| Type          | Choice (synced from Purview) |
| Required      | No (auto-applied by Purview) |
| Choices       | `Public`, `Internal`, `Confidential`, `Highly Confidential` |

### 14. `MeetingDate`
| Property      | Value |
|---------------|-------|
| Type          | Date and Time |
| Required      | No (required for `ContentTypeLabel = Meeting Transcript`) |
| Description   | Date the meeting took place |

### 15. `EmailSentDate`
| Property      | Value |
|---------------|-------|
| Type          | Date and Time |
| Required      | No (required for `ContentTypeLabel = Email`) |
| Description   | Original sent date of the email |

---

## Content Types

| Content Type        | Inherits From    | Additional Required Columns |
|---------------------|------------------|-----------------------------|
| `KM-Email`          | Document         | `EmailSentDate`, `Source=Email` |
| `KM-Attachment`     | Document         | `Source` |
| `KM-Transcript`     | Document         | `MeetingDate`, `Source=Teams` |
| `KM-Spreadsheet`    | Document         | `Project` |
| `KM-Presentation`   | Document         | `Objective`, `KeyResult` |
| `KM-Report`         | Document         | `Project`, `Owner` |

All content types inherit `Objective`, `KeyResult`, `ConfidenceScore`, `Source`, `Owner`, `ClassifiedDate`.
