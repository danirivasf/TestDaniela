# Narrative prompt

The generative half of Blueprint 1. Paste the JSON from
`python value_calculator.py --json` where indicated.

The one rule this prompt exists to enforce: **the model reproduces figures, it
never produces them.** Every number is already computed and pre-formatted in the
JSON.

---

## Prompt

You are helping a pricing and strategy lead turn a completed pricing analysis into
written output. The analysis is finished — your job is language, not arithmetic.

**Absolute constraints:**

1. Use **only** the figures present in the JSON below, copied **exactly** as they
   appear, including currency symbols and separators. Do not recompute, re-round,
   re-scale, or restate any number in different units.
2. Do not introduce any quantity that is not in the JSON. No "over", "up to", or
   "as much as" attached to a figure. If a claim needs a number you don't have,
   drop the claim.
3. Treat `confidence` values as instructions about emphasis. Drivers below 50%
   confidence must be described as unvalidated and must not appear in the headline
   value claim.
4. If `ok` is `false`, do not write a narrative. List the problems and stop.
5. If `proposed.verdict` is anything other than `auto-approvable`, say so plainly
   in the internal summary. Never soften an escalation or a rejection.

**Produce three sections:**

### 1. Customer-facing value narrative (150–200 words)
Lead with the business outcome, not the product. State the risk-adjusted annual
value and the recommended annual price, then ROI and payback. Name the two
highest-confidence drivers specifically, with their basis. Reference the
sensitivity table to show the case holds even if the estimate is conservative —
this pre-empts the "your assumptions are optimistic" objection rather than waiting
for it. Plain, declarative sentences. No superlatives, no "unlock", no "transform".

### 2. Internal deal summary (max 80 words)
For the deal desk. Recommended price and discount, the approval verdict, the single
biggest risk to the value case, and what the AE must validate before this number is
committed to.

### 3. Open questions for the customer
Convert `assumptions_to_validate` into questions the AE can ask in the next call.
One line each. Put the lowest-confidence assumptions first — those are where the
value case is most likely to move.

**Analysis JSON:**

```json
{{ PASTE OUTPUT OF `python value_calculator.py --json` HERE }}
```

---

## Why the prompt is shaped this way

- **Constraint 1** is the guardrail against the main failure mode of LLM-assisted
  pricing: prose that drifts from the model of record. Pre-formatted strings make
  the correct behaviour (copy) easier than the incorrect one (compute).
- **Constraint 3** encodes judgement you'd otherwise have to apply by hand every
  time. A 30%-confidence driver belongs in the appendix, not the headline, and the
  prompt now knows that.
- **Constraint 4** means malformed input produces a refusal rather than a
  confident fabrication. Pair it with the validation tests in `eval_cases.py`.
- **Constraint 5** exists because the natural failure of a helpful assistant is to
  frame an escalation as a formality. Escalations must survive contact with the
  drafting step.
- **Section 3** exists because the most useful output here is often not the
  narrative — it's a clean list of what you don't yet know. That's the thing that
  moves the deal.

## Extending this with the evaluator–optimizer pattern

Add a second call that scores the draft against an explicit rubric:

1. Does every figure in the draft appear verbatim in the source JSON? *(Mechanical
   check — you can do this one in code with a regex over the money strings, and you
   should. Don't ask a model to do what `re.findall` does perfectly.)*
2. Are sub-50%-confidence drivers excluded from the headline claim?
3. Is the escalation verdict stated without hedging?
4. Is the customer section within 150–200 words?
5. Are there any superlatives or unsupported forward-looking claims?

Feed the failures back for one revision pass. Two rounds is almost always enough;
beyond that you're paying for diminishing returns.

Check 1 being code rather than prompt is the general lesson: **move every check you
can into deterministic code, and use the model only for the ones that genuinely
need judgement.**
