# Five things to build

Ordered by value-to-effort. Each names the pattern it uses, what's deterministic
versus generative, and the failure mode to guard against.

Build them in this order. Blueprint 1 teaches the discipline the other four need.

---

## Blueprint 1 — Value / pricing calculator with a generated narrative

**Effort:** 1–2 days · **Pattern:** tool use + prompt chaining
**Starter code:** `examples/pricing_calculator/` — runnable now

### The problem
Value-based pricing conversations need two things: a defensible number and a story a
customer believes. Producing both for every deal is slow, and the story usually gets
rebuilt from scratch each time by whoever has the deck open.

### The build
**Deterministic layer (Python).** Inputs: customer size, current-state baseline cost,
quantified value drivers, term, volume. Outputs: annual value created, a price band
derived from a value-capture ratio, ROI, payback period, discount floor check, and a
sensitivity table over the most uncertain assumption.

**Generative layer (LLM).** Takes the calculator's JSON and produces (a) a
customer-facing value narrative, (b) an internal one-paragraph deal summary, (c) the
list of assumptions stated plainly so the AE can validate them with the customer.

### Why this is first
It's the smallest thing that produces real output, and it forces the
deterministic/generative boundary that everything else depends on. It also produces
a reusable artifact: once the pricing logic is in code, Blueprints 2 and 3 call it
instead of reimplementing it.

### Failure mode to guard
The model quietly editorialising the numbers in prose — "delivers over $2M in value"
when the calculator said $1.6M. Mitigation: pass numbers as pre-formatted strings and
instruct the model to reproduce them verbatim, never to recompute or round. Then spot-
check on your eval set.

---

## Blueprint 2 — Deal-desk triage assistant

**Effort:** 3–5 days · **Pattern:** routing + chain-of-thought classification

### The problem
Non-standard pricing requests arrive in inconsistent formats and need the same three
questions answered every time: is it within policy, what's the precedent, who needs
to approve it. The work is repetitive; the judgement isn't.

### The build
1. **Extract** structured fields from the request (free text, email, or form).
2. **Route** by classification: within-policy standard / exception-needs-justification
   / missing-information / genuinely novel.
3. **Compute** the policy check deterministically — floors, thresholds, approval
   matrix. This is a lookup table, not a judgement.
4. **Draft** the deal-desk summary: request, policy position, comparable precedents,
   recommended approver, open questions.
5. **Never auto-approve.** Output is a prepared brief for a human decision.

### Why it's valuable
It doesn't replace judgement — it removes the 20 minutes of assembly before the
judgement. That's the sweet spot for internal automation and the easiest version to
get approved, because the human decision point is unchanged.

### Failure mode to guard
Confidently mis-classifying an edge case as standard. Mitigations: use the voting
variant of parallelisation (ask three times; disagreement forces escalation), and put
every historical edge case you can find into the eval set. Bias the prompt toward
escalation — a false escalation costs minutes, a false approval costs margin.

---

## Blueprint 3 — Scheduled pricing & competitive intel digest

**Effort:** 2–4 days · **Pattern:** parallelisation (sectioning) + summarisation

### The problem
Competitor pricing pages, packaging changes, and public announcements move
continuously. Checking them is a task everyone agrees is important and nobody does
weekly.

### The build
1. **Collect** on a schedule — public pricing pages, release notes, news. Note that
   *Building Browser Agents* (Tier 2) is genuinely relevant here: pricing pages are
   the canonical case of valuable data with no API.
2. **Diff** against last run's snapshot. This is deterministic and it's the core of
   the value: you want *changes*, not a re-description of the status quo.
3. **Summarise in parallel** — one call per source, then aggregate.
4. **Assess** implications for your positioning, explicitly separating observation
   from inference so a reader can disagree with the inference while trusting the
   observation.
5. **Deliver** to a channel a human reads (see Blueprint 5).

### Why it's valuable
Diff-based monitoring is where scheduled automation genuinely beats a human: no
fatigue, no skipped weeks, and a complete history you can point back to when someone
asks "when did they change that?"

### Failure mode to guard
Hallucinated changes and false alarms — which destroy trust in a digest faster than
missing something. Mitigation: every claimed change must cite the before/after text
from the diff. If there's no diff evidence, it doesn't go in the digest.

Check the terms of service of any site you scrape, and respect `robots.txt`. Prefer
official channels where they exist.

---

## Blueprint 4 — Pricing policy Q&A over your own documents

**Effort:** 2–5 days depending on corpus size · **Pattern:** RAG (only if needed)

### The problem
"What's our policy on X?" is asked constantly, answered inconsistently, and the
answer lives in a document nobody can find.

### The build
**First, count the documents.** Genuinely — this determines the architecture:
- Under ~20: concatenate into one context, ask directly. Build this version first
  even if you'll outgrow it. It takes an afternoon and it might be the final answer.
- 20–100: keyword pre-filter, then paste candidates.
- Over 100: embeddings + vector store. Now the Tier 2 vector DB and RAG courses earn
  their time.

**Always cite.** Every answer quotes the source document and section. An uncited
answer to a policy question is worse than no answer, because someone will act on it.

**Answer "not covered" honestly.** The most valuable output of this system is
discovering which questions your policy doesn't actually address — that's a strategy
finding, not a bug.

### Failure mode to guard
Answering from the model's general knowledge of "typical SaaS discount policy" rather
than from your documents. Mitigation: require a citation for every claim, and include
eval cases whose correct answer is "the policy doesn't address this."

---

## Blueprint 5 — Automated SharePoint communications

**Effort:** 3–7 days, mostly integration · **Pattern:** evaluator–optimizer + scheduled delivery
**Detail:** see `04-sharepoint-and-m365.md`

### The problem
A recurring update — pricing changes, quarterly metrics, competitive notes — that
someone assembles by hand every cycle and that slips whenever they're busy.

### The build
1. **Gather** inputs deterministically: pull the numbers from their source. Numbers
   come from systems, never from the model.
2. **Draft** the update from a template.
3. **Evaluate against a written rubric** — figures match source, no unapproved
   forward-looking statements, correct audience and tone, length limit, required
   sections present.
4. **Revise** once or twice against the rubric.
5. **Route for human approval.** A Teams message with the draft and an approve
   button. This step stays until the eval set earns your trust — for anything
   executives read, that may be a long time, and that's fine.
6. **Publish** to the SharePoint page on approval.

### Why it's last
It's the most integration-heavy and the least about AI. Most of the effort is
plumbing (Power Automate / Graph API permissions), not prompting. Do it after you've
built something that produces content worth publishing — otherwise you've automated
the delivery of nothing.

### Failure mode to guard
Publishing something wrong to a page executives read. Mitigation: the human approval
gate, and a rubric check that every figure in the draft appears in the source data.
Consider making the first version post to a draft page or a Teams channel only, and
graduate it to the live page after a month of clean output.

---

## Sequencing summary

```
Week 2:  Blueprint 1  (calculator — deterministic core)
Week 3:  Blueprint 1  (add LLM narrative layer)
Week 4:  Blueprint 3 or 5  (get something running on a schedule)
Later:   Blueprint 2  (needs policy data + stakeholder buy-in)
Later:   Blueprint 4  (needs a document corpus audit first)
```

Blueprints 2 and 4 are deliberately later: they depend on internal data access and
on stakeholders agreeing to how policy is encoded. That's an organisational task, not
a technical one, and starting there is how these projects stall.
