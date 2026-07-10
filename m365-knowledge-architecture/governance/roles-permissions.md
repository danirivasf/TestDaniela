# Roles & Permissions Matrix

## Role Definitions

| Role                | Azure AD Group                 | Description |
|---------------------|-------------------------------|-------------|
| Knowledge Manager   | `km-knowledge-managers`       | Owns the classification taxonomy, resolves disputes, manages term sets |
| OKR Champion        | `km-okr-champions-{objective}`| Responsible for one Objective's alignment; reviews documents for their OKR |
| Department Lead     | `km-dept-leads`               | Manages content within their department's site |
| Content Contributor | `km-contributors`             | Creates and edits documents; can flag misclassifications |
| Reader              | `km-readers` / All Employees  | Read-only access to published content |
| AI Service Account  | `svc-km-classifier`           | Service principal for the AI pipeline; restricted to ingest operations |
| Compliance Officer  | `km-compliance`               | Manages retention labels, legal holds, DLP policies |

## Permissions Matrix

| Action                             | Knowledge Manager | OKR Champion | Dept Lead | Contributor | Reader | AI Service |
|------------------------------------|:-----------------:|:------------:|:---------:|:-----------:|:------:|:----------:|
| Read classified documents          | ✓                 | ✓            | ✓         | ✓           | ✓      | —          |
| Create / upload documents          | ✓                 | ✓            | ✓         | ✓           | —      | ✓ (AI-Inbox only) |
| Edit metadata (own documents)      | ✓                 | ✓            | ✓         | ✓           | —      | ✓ (AI-Inbox only) |
| Override AI classification         | ✓                 | ✓ (own OKR)  | —         | —           | —      | —          |
| Publish major version              | ✓                 | ✓            | ✓         | ✓           | —      | —          |
| Delete documents                   | ✓                 | —            | ✓ (own site) | —        | —      | —          |
| Manage term sets / taxonomy        | ✓                 | —            | —         | —           | —      | —          |
| Apply / change retention labels    | ✓ + Compliance    | —            | —         | —           | —      | —          |
| Apply legal hold                   | Compliance only   | —            | —         | —           | —      | —          |
| View audit logs                    | ✓ + Compliance    | —            | —         | —           | —      | —          |
| Manage site permissions            | ✓                 | ✓ (own site) | —         | —           | —      | —          |
| Access Archive site                | ✓ + Compliance    | Read only    | Read only | Read only   | —      | —          |
| Share externally                   | ✓                 | With KM approval | —     | —           | —      | —          |
