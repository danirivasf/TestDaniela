# M365 AI-Driven Knowledge Automation Architecture

A production-ready, metadata-first knowledge management system built on SharePoint and OneDrive, aligned to OKRs. Designed for automatic classification and storage of emails, attachments, meeting transcripts, and Excel files.

## Structure

```
m365-knowledge-architecture/
├── README.md                          # This file
├── sharepoint/
│   ├── site-collections.md            # Site collection hierarchy
│   └── document-libraries.md          # Library definitions per site
├── metadata/
│   ├── schema.md                      # Full metadata column definitions
│   └── schema.json                    # API-ready JSON Schema
├── classification/
│   ├── okr-mapping-logic.md           # Keyword → OKR mapping rules
│   └── confidence-scoring.md          # How confidence scores are computed
├── governance/
│   ├── rules.md                       # Override rights, versioning, retention
│   └── roles-permissions.md           # RBAC matrix
└── naming-conventions.md              # File and library naming standards
```

## Quick Start

1. Provision site collections per `sharepoint/site-collections.md`
2. Apply metadata schema from `metadata/schema.json` via PnP PowerShell or SPO REST API
3. Deploy classification rules from `classification/okr-mapping-logic.md` into your AI pipeline
4. Enforce governance via `governance/rules.md`

## Key Design Principles

- **Metadata-first**: Content is discoverable through metadata, not folder hierarchy
- **OKR-aligned**: Every document traces to an Objective and Key Result
- **AI-assisted**: Confidence scores enable human-in-the-loop review workflows
- **API-ready**: JSON schema enables integration with Power Automate, Logic Apps, or custom pipelines
