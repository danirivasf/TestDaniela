# Example requests — anonymized test set

Five request patterns drawn from real intake traffic Cassie's team shared,
then **fully anonymized** for this prototype: invented customers, part
numbers, prices, and people. What is preserved is the *shape* of each
request and the failure it exposes — those are the requirements findings,
and they are what the clay model must handle.

> The raw source threads contain real customer and pricing data and are
> **not** stored in this repo, per the guardrail in `CLAUDE.md` (the model
> must never contain real data). This anonymized set is the committable
> version.

Each example is also encoded in `anonymized-examples.json` for seeding, and
three of them ship as seed requests in the clay model (PLR-0007/0008/0009).

---

## EX-01 · Lease part against a limited-status product
- **Type / expected route:** Create part number · **full review**
- **Why that route:** the base product is on limited/discontinued status, so
  an exception applies — management review is required before creation.
- **Shape:** sales-driven, a partner evaluation likely to convert to a lease.
- **Failure it exposed:** the limited-status check was done from memory; two
  conflicting derived prices appeared in one email thread with no
  reconciliation; the approval existed only as a mailbox reply.
- **Model must:** raise an exception flag on limited-status creates and route
  them to review; treat the derived price as one computed field, not free text.

## EX-02 · Monthly flavor of an existing annual part
- **Type / expected route:** Create part number · **fast track**
- **Why that route:** a clone of an existing part with one attribute changed
  (billing frequency), no new variables — the canonical fast-track case.
- **Failure it exposed:** routing happened by manual email forwarding; the
  justification lived in a nested forwarded thread; nothing structured
  survived for audit.
- **Model must:** let a clone reference its parent part and route straight to
  the Operations queue.

## EX-03 · Third-party add-on wrongly swept into an annual increase
- **Type / expected route:** Change price (correction) · **fast track**
- **Why that route:** revert to previously agreed values.
- **Failure it exposed:** the annual increase run had no exclusion flag for
  third-party / royalty products; the error was found by accident; the
  blast-radius question ("were others affected?") was answered from memory.
- **Model must:** carry a third-party / royalty flag on parts, and a
  correction type that records which run caused the error.

## EX-04 · New offering structure (editions and bundling)
- **Type / expected route:** Structure change · **full review**
- **Why that route:** new editions, bundling, and license-model decisions.
- **Failure it exposed:** the decision, the pricebook pages, and a field
  advisory had no shared home; one approval email sat unsent in an outbox for
  a week and silently blocked the whole chain; nobody could see it was stuck.
- **Model must:** trigger the review path and relevance questions, and show a
  visible status so a stalled step is seen, not discovered later.

## EX-05 · Urgent hosting-fee part blocking a renewal invoice
- **Type / expected route:** Create part number (urgent) · **fast track**
- **Why that route:** a straightforward new fee part, but a live invoice is
  blocked because the quote line points at the wrong part and the correct one
  does not exist.
- **Failure it exposed:** the part was created reactively during billing; a
  material attribute (license model) was settled by a one-word email; the
  customer invoice was the only thing acting as an SLA.
- **Model must:** carry an urgent flag that *requires* naming the blocked
  downstream artifact (invoice / quote / order), so priority is data.

---

## What the five prove (cross-cutting)

1. **There was no single front door** — at least five intake aliases plus
   direct personal email. Some auto-created a tracked case, but the case only
   threaded mail: no routing, structured fields, status, or queue.
2. **Approval was one person, one line, in a mailbox** — the single-point
   bottleneck the two-step approval and delegated authority replace.
3. **Four of five requests were born inside a live deal, order, or renewal** —
   "requests arrive late" is the observed default, not an anecdote.
4. **Pricing logic was tribal** — conventions lived in people's heads; one
   thread produced two conflicting prices unnoticed.
5. **Data rode attachments and nested threads** — nothing queryable afterward.
6. **Schema validation:** all five map cleanly onto the five request types
   (three creates, one price change, one structure change) and surfaced three
   fields the intake form was missing — now added to the clay model:
   a **limited-status / EOL exception flag**, a **third-party / royalty flag**,
   and an **urgent flag tied to the blocked downstream artifact**.
