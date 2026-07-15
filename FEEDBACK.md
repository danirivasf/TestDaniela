# Feedback log — clay model working sessions

Corrections from Michele, Cassie, and other reviewers are the requirements
document for the Salesforce build. Log every reaction here, even small ones.

Format: date · who · what they said · what changed (or why nothing did).

| Date | Who | Feedback | Resolution |
|------|-----|----------|------------|
| 2026-07-15 | Cassie's team (real traffic) | Five real request threads shared and normalized to the schema. All five map cleanly onto the five request types (3 create, 1 price, 1 structure), which validates the routing model. They surfaced three fields the intake form was missing. | Added three flags to the clay-model form: limited-status / EOL exception, third-party / royalty, and an urgent flag that **requires** naming the blocked downstream artifact. Limited-status creates now route to full review by policy. Anonymized the five examples into `spec/example-requests/anonymized-examples.{md,json}`; seeded three (PLR-0007/0008/0009). Raw real-data files kept out of the repo per the CLAUDE.md guardrail. |
| 2026-07-15 | Scoping doc revision | Updated "Today" narrative from "one generic inbox" to the real picture: 5+ intake aliases plus direct personal email, GoSell case tracking that only threads mail, single-approver bottleneck. Added a scoping question about the existing case flow. | Replaced `spec/product-licensing-intake-scoping.html` with the revised version. |
