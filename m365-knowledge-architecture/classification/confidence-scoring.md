# Confidence Scoring Model

## Score Bands

| Band        | Score Range  | Action |
|-------------|--------------|--------|
| High        | 0.90 – 1.00  | Auto-classify, no review required |
| Medium-High | 0.75 – 0.89  | Auto-classify, owner notified for 5-day review window |
| Medium-Low  | 0.50 – 0.74  | Routed to `AI-Inbox` → assigned to Owner for review |
| Low         | 0.25 – 0.49  | Routed to `AI-Inbox` → escalated to Knowledge Manager |
| Very Low    | 0.00 – 0.24  | Routed to `AI-Inbox` → manual classification required, AI suggestion shown as hint only |

## Score Composition

```
ConfidenceScore = (keyword_score × 0.40)
               + (semantic_score × 0.40)
               + (source_signal × 0.10)
               + (metadata_completeness × 0.10)
```

**source_signal** bonuses:
- Email from a domain-specific alias (e.g. pricing@, sales@) → +0.05
- Teams meeting with ≥3 attendees from sales/product → +0.05
- Manual upload by the document Owner → +0.03

**metadata_completeness**: ratio of optional metadata fields populated (0–1 mapped to 0–0.10)

## Score Decay

Scores decay over time to prompt periodic review:
- Documents not reviewed after 180 days: `ConfidenceScore × 0.95`
- After 365 days without review: routed back to `Needs Review` view regardless of score
- After human review: score resets to `1.00` and decay timer restarts
