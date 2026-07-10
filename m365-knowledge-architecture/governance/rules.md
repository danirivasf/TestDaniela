# Governance Rules

---

## 1. Classification Override Rights

| Role                  | Can Override AI Classification | Conditions |
|-----------------------|-------------------------------|------------|
| Document Owner        | Yes                           | Can change their own documents only; must provide `OverrideReason` |
| Knowledge Manager     | Yes                           | Can override any document; audit log required |
| OKR Champion          | Yes (for their Objective only) | Can reassign documents to/from their Objective |
| Site Owner            | Yes (within their site)       | Must notify Knowledge Manager for cross-site moves |
| Regular Member        | No                            | Can flag for review via "Request Reclassification" button |
| AI Pipeline (Service) | Auto-classify only            | Cannot override a human-reviewed document (locked after `ReviewedDate` set) |

### Override Workflow

```
Member flags document → Knowledge Manager notified →
KM reviews within 5 business days →
Override applied with OverrideReason populated →
Audit log entry created in Purview →
Original AI classification preserved in version history
```

---

## 2. Versioning Rules

### Document Libraries

| Library              | Versioning Type     | Versions Kept | Notes |
|----------------------|--------------------|--------------:|-------|
| `AI-Inbox`           | Major only         | 5             | Staging; purged after promotion or 30 days |
| `Classified-Documents` | Major + Minor    | 20            | Minor versions for in-progress edits; major = published |
| `Email-Archives`     | Major only         | Unlimited     | Emails are immutable records |
| `Meeting-Transcripts`| Major only         | Unlimited     | Transcripts are immutable records |
| `Spreadsheets`       | Major + Minor      | 50            | Financial files need full history |
| `Pricebooks`         | Major + Minor      | Unlimited     | Compliance requirement; never purge |
| `Archive`            | Major only         | Unlimited     | Immutable; no edits permitted |

### Version Promotion Rules
- A document moves from Minor → Major version only after explicit **Publish** action
- Only users with `Contribute` or higher permissions can publish
- Publishing triggers metadata validation (required fields checked before save)
- Publishing a Major version sends a notification to the document `Owner`

---

## 3. Retention Rules

| Retention Label  | Trigger                                     | Duration  | Action at Expiry |
|------------------|---------------------------------------------|-----------|------------------|
| `Transient-30d`  | Auto-applied to `AI-Inbox` on ingest        | 30 days   | Auto-delete if not promoted |
| `Standard-3yr`   | Default for general documents               | 3 years   | Review → Archive or delete |
| `Financial-7yr`  | Applied to Spreadsheets, Pricebooks, Quotes | 7 years   | Move to `Archive` site |
| `Legal-Hold`     | Applied by Legal team via Purview           | Indefinite until released | Hold; no deletion |
| `Permanent`      | Applied to foundational OKR documents       | Indefinite | Never delete |

---

## 4. Access Control

### Site Permission Levels

| Group                  | Permission Level  | Sites |
|------------------------|-------------------|-------|
| Knowledge Managers     | Full Control      | All sites |
| OKR Champions          | Site Owner        | Their objective's site |
| Department Leads       | Edit              | Their department's site |
| All Employees          | Read              | `knowledge-hub`, `okr-strategy` |
| External Contributors  | Read (specific libraries only) | Via sharing links, time-limited |
| AI Service Principal   | Contribute        | `AI-Inbox` libraries only |

### Sensitive Content Rules
- Documents with `SensitivityLabel = Highly Confidential` are accessible only to `Owner` + `Knowledge Managers` + explicit grants
- `SensitivityLabel = Confidential` requires MFA re-authentication for download
- Sharing confidential documents externally requires Knowledge Manager approval

---

## 5. Audit & Compliance

- All classification overrides logged to Microsoft Purview audit log
- All document accesses for `Confidential` and above logged
- Monthly report: documents in `Needs Review` older than 14 days (escalated to OKR Champions)
- Quarterly report: classification accuracy review (sample of 100 docs reviewed by KMs)
- Annual: full retention label review by Legal and Knowledge Management team
