# OKR Mapping Logic

The AI classifier runs a multi-stage pipeline to map document content to OKRs.

---

## Pipeline Stages

```
Document Ingested
       │
       ▼
┌─────────────────┐
│  1. Extraction  │  Extract text (OCR for images, transcript parsing, email body strip)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  2. NER / NLP   │  Named entity recognition + keyword extraction
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  3. Keyword     │  Match keywords against OKR term dictionary
│     Matching    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  4. Semantic    │  Embedding similarity against OKR descriptions
│     Similarity  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  5. Score &     │  Combine keyword + semantic scores → ConfidenceScore
│     Route       │  ≥ 0.75: auto-classify → Classified-Documents
└─────────────────┘  < 0.75: route to AI-Inbox (Needs Review)
```

---

## OKR Term Dictionary

### Objective: `Increase Revenue`

| Key Result | Keywords | Semantic Phrases |
|------------|----------|-----------------|
| Achieve $5M ARR by Q4 | `pricebook`, `pricing`, `price list`, `rate card`, `revenue`, `ARR`, `MRR`, `upsell`, `cross-sell`, `deal`, `opportunity` | "annual recurring revenue", "subscription growth", "new logo", "expansion revenue" |
| Improve win rate to 35% | `quote`, `proposal`, `RFP`, `RFQ`, `bid`, `win`, `close`, `deal`, `competitive`, `discount` | "win/loss analysis", "quote approval", "deal desk", "competitive pricing" |
| Expand to 3 new markets | `market`, `region`, `territory`, `segment`, `ICP`, `launch`, `GTM`, `go-to-market`, `expansion` | "new market entry", "territory expansion", "target segment" |

### Objective: `Improve Operational Efficiency`

| Key Result | Keywords | Semantic Phrases |
|------------|----------|-----------------|
| Reduce quote cycle time by 30% | `quote`, `approval`, `workflow`, `cycle time`, `turnaround`, `SLA`, `automation`, `CPQ` | "quote-to-cash", "configure price quote", "approval bottleneck" |
| Cut manual data entry by 50% | `manual`, `entry`, `automation`, `RPA`, `integration`, `sync`, `ETL`, `mapping` | "data integration", "process automation", "eliminate manual steps" |
| Achieve 99.5% system uptime | `uptime`, `SLA`, `incident`, `outage`, `reliability`, `monitoring`, `alert`, `MTTR` | "system availability", "incident response", "service reliability" |

### Objective: `Accelerate Product Innovation`

| Key Result | Keywords | Semantic Phrases |
|------------|----------|-----------------|
| Launch 2 new SKUs by Q3 | `SKU`, `product`, `launch`, `roadmap`, `specification`, `feature`, `release`, `catalog` | "new product introduction", "SKU rationalization", "product catalog", "product launch" |
| Reduce time-to-market to 60 days | `sprint`, `backlog`, `milestone`, `delivery`, `release`, `MVP`, `prototype`, `design` | "time to market", "product development cycle", "agile delivery" |

---

## Detailed Example: Pricebook / SKU / Quote Mapping

### Scenario
An email arrives with subject: **"Updated Pricebook + SKU list for Q3 — please review attached quote"**

### Step-by-step Mapping

**Stage 1 — Extraction**
- Email body text extracted
- Attachment (Excel) detected → text extracted from cell values and named ranges

**Stage 2 — NER**
Entities detected:
- `pricebook` → Product/Pricing entity
- `SKU` → Product entity
- `quote` → Sales entity
- `Q3` → Time period entity

**Stage 3 — Keyword Matching**

| Keyword   | OKR Match                              | Weight |
|-----------|----------------------------------------|--------|
| pricebook | Increase Revenue → Achieve $5M ARR     | 0.90   |
| SKU       | Accelerate Product Innovation → Launch 2 new SKUs | 0.85 |
| quote     | Increase Revenue → Improve win rate    | 0.80   |
| quote     | Improve Operational Efficiency → Reduce quote cycle time | 0.75 |

**Stage 4 — Semantic Similarity**
Email embedding vs OKR description embeddings:
- "Increase Revenue / Achieve $5M ARR" → cosine similarity: **0.87**
- "Accelerate Product Innovation / Launch 2 new SKUs" → cosine similarity: **0.72**
- "Improve Operational Efficiency / Reduce quote cycle time" → cosine similarity: **0.68**

**Stage 5 — Final Score**

Combined score = (keyword_weight × 0.5) + (semantic_similarity × 0.5)

| Objective → Key Result                         | Combined Score |
|------------------------------------------------|----------------|
| Increase Revenue → Achieve $5M ARR             | **0.89** ✓ AUTO |
| Accelerate Product Innovation → Launch 2 SKUs  | **0.79** ✓ AUTO |
| Improve Operational Efficiency → Quote cycle   | **0.72** ⚠ REVIEW |

**Result:**
- Primary: `Objective = Increase Revenue`, `KeyResult = [Achieve $5M ARR by Q4]`
- Secondary: `KeyResult` also tagged with `Launch 2 new SKUs by Q3`
- `ConfidenceScore = 0.89`
- Routed to `Classified-Documents` on `product-pricing` site
- Email tagged as `KM-Email` content type

---

## Conflict Resolution Rules

When two objectives score within 0.05 of each other:
1. Use `ContentTypeLabel` as a tiebreaker (Spreadsheet → Product/Pricing; Email → Revenue)
2. Check `Source` (Teams meeting → operational; Email from sales@ → Revenue)
3. If still tied, assign the higher-scored objective as primary and both as `KeyResult` values
4. Set `ConfidenceScore` to the lower of the two scores (conservative)

---

## Multi-Label Strategy

A document CAN map to multiple `KeyResult` values but MUST have exactly ONE `Objective`.

If keywords span two different objectives with scores both ≥ 0.75:
- Assign to the objective with the higher score
- Create a **cross-reference** record in the secondary objective's library pointing to the primary document
- Do not duplicate the file
