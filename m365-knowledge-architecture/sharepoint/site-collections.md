# SharePoint Site Collections

## Hierarchy Overview

```
Tenant Root
└── /sites/knowledge-hub                    [Hub Site]
    ├── /sites/okr-strategy                 [OKR Strategy]
    ├── /sites/ops-excellence               [Operations Excellence]
    ├── /sites/product-pricing              [Product & Pricing]
    ├── /sites/customer-success             [Customer Success]
    └── /sites/archive                      [Archive / Records]
```

---

## 1. Hub Site — `knowledge-hub`

| Property         | Value                                      |
|------------------|--------------------------------------------|
| URL              | `https://tenant.sharepoint.com/sites/knowledge-hub` |
| Purpose          | Central discovery portal; search scope for all spoke sites |
| Template         | Communication Site                         |
| Hub registration | Yes — all spoke sites associate to this hub |
| Owners           | Knowledge Management Team                  |

**Key pages:**
- Home dashboard (OKR progress widgets, recently classified content)
- Search center with metadata-driven refiners (Objective, Key Result, Content Type)
- Governance & classification guidelines

---

## 2. OKR Strategy — `okr-strategy`

| Property | Value |
|----------|-------|
| URL      | `https://tenant.sharepoint.com/sites/okr-strategy` |
| Purpose  | Canonical OKR definitions, strategic documents, exec presentations |
| Template | Team Site |
| Hub      | Associated to `knowledge-hub` |

**Libraries:** OKR Definitions, Strategic Presentations, Board Materials

---

## 3. Operations Excellence — `ops-excellence`

| Property | Value |
|----------|-------|
| URL      | `https://tenant.sharepoint.com/sites/ops-excellence` |
| Purpose  | Process docs, SOPs, meeting transcripts, operational email archives |
| Template | Team Site |
| Hub      | Associated to `knowledge-hub` |

**Libraries:** SOPs, Meeting Transcripts, Email Archives, Reports

---

## 4. Product & Pricing — `product-pricing`

| Property | Value |
|----------|-------|
| URL      | `https://tenant.sharepoint.com/sites/product-pricing` |
| Purpose  | Pricebooks, SKU catalogs, quotes, product specs |
| Template | Team Site |
| Hub      | Associated to `knowledge-hub` |

**Libraries:** Pricebooks, SKU Catalog, Quotes, Product Specs

---

## 5. Customer Success — `customer-success`

| Property | Value |
|----------|-------|
| URL      | `https://tenant.sharepoint.com/sites/customer-success` |
| Purpose  | Customer-facing materials, case studies, onboarding docs |
| Template | Team Site |
| Hub      | Associated to `knowledge-hub` |

**Libraries:** Onboarding, Case Studies, Customer Comms, Health Reports

---

## 6. Archive — `archive`

| Property | Value |
|----------|-------|
| URL      | `https://tenant.sharepoint.com/sites/archive` |
| Purpose  | Immutable records, retention-managed content, legal hold |
| Template | Team Site (locked down) |
| Hub      | Associated to `knowledge-hub` |
| Access   | Read-only for most users; write-only via automated retention policy |
