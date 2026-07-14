# Product Licensing Intake — Clay Model

## Purpose

This project is a **clay model** of Octave's product licensing ticketing
workflow: a rough but working interactive prototype of the intake system —
real form, real routing rules, real approval steps — running locally with
fake data. Its job is to be reacted to and reshaped by Pricing Operations
and Pricing Strategy, **not** to be used in production. The validated model
becomes the requirements specification for the Salesforce build by
Business IT.

**This is a prototype only. It must never contain real pricing data, real
part numbers, real customer names, or real request content.** All data is
invented.

## The reference spec

`spec/product-licensing-intake-scoping.html` is the scoping artifact and the
source of truth for the process design. When the prototype and the spec
disagree, the spec wins until a stakeholder decision says otherwise.
`spec/example-requests/` is where the two current intake forms (Word
price-per-page, multi-part Excel) and 5–10 anonymized example requests go
when Cassie sends them — the model should be tested against actual traffic.

## Design constraints (do not change without a stakeholder decision)

1. **Five request types**: create part number · change price · change
   attributes · retire / EOL · structure change.
2. **Routing rule**: *fast track* for a copy of an existing product with no
   new variables (clone, in-policy price update, straightforward
   retirement) → straight to the Operations execution queue. *Full review*
   for anything introducing a new pricing model, tier model, offering
   structure, or license model → Pricing Strategy review plus the
   cross-functional relevance check.
3. **Nine-function relevance check** (full review only): Legal, Finance,
   Sales Operations, Order Management, Software Delivery, Revenue
   Recognition, Cloud Operations, IT and Provisioning, Support. Only
   functions whose relevance question flags engage.
4. **Two-step approval**: Pricing Strategy signs off on the commercial
   design, then Pricing Operations accepts the request as executable.
5. **Four standing guardrails**: no part number, no quote · dedupe before
   create · one authoring point (prices change in Conga on the PLI only) ·
   everything logged (no request, approval, or load exists outside the
   system).

## Technical constraints

- Single-file vanilla HTML/CSS/JS in `clay-model/index.html`. No build
  step, no framework, no external services or network calls.
- Persistence via `localStorage`; single user; a persona switcher simulates
  Requester / Pricing Operations / Pricing Strategy.
- Every state change writes a timestamped history entry — the simulated
  audit trail is a first-class feature, not decoration.
- Runs by opening the file in a browser (or `python3 -m http.server`).

## Iteration protocol

Michele and Cassie react to the running model; their corrections **are**
the requirements document. Log every correction and decision in
`FEEDBACK.md` with a date and who said it. When a correction changes a
design constraint above, update this file and the spec note together.
