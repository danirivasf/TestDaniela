# Example requests — test set

- **`anonymized-examples.md` / `anonymized-examples.json`** — five request
  patterns drawn from real intake traffic Cassie's team shared, fully
  anonymized (invented customers, parts, prices, people). These are the
  committable test set; three are seeded in the clay model as PLR-0007/0008/0009.

Still to add when available:

1. The two current intake forms (the Word price-per-page export and the
   multi-part Excel sheet), so the clay model's required fields can be
   checked against what people actually fill in today.

**Guardrail:** raw source threads contain real customer and pricing data and
must **not** be committed here (see `CLAUDE.md`). Anonymize first — strip
customer names, real prices, and real part numbers. If a real request can't
be expressed in the form, that's a requirements finding, not a user error.

Log what breaks in `../../FEEDBACK.md`.
