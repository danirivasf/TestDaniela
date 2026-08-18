# Worked example: value calculator + generated narrative

A runnable version of Blueprint 1. No dependencies, no API key, Python 3.10+.

```bash
python3 value_calculator.py           # internal one-page summary (markdown)
python3 value_calculator.py --json    # structured output for the narrative prompt
python3 eval_cases.py                 # 28 eval cases -- run after any policy change
python3 check_parity.py               # proves the JS mirror matches the Python
python3 build_dashboard.py            # regenerate dashboard.html, then open it
```

All 28 eval cases pass, `--json` validates as strict JSON, and the parity check
agrees across 1,440 deals.

## Files

| File | Role |
|---|---|
| `value_calculator.py` | Deterministic core. Every customer-visible number lives here |
| `eval_cases.py` | The eval set. Edge cases, especially "must escalate" ones |
| `prompts/narrative.md` | The LLM layer: turns the JSON into a value narrative and deal summary |
| `pricing_model.js` | Browser mirror of the math, so the dashboard recomputes live |
| `check_parity.py` | Runs both implementations over 1,440 deals; fails on any disagreement |
| `build_dashboard.py` | Generates `dashboard.html` from the Python policy + the JS model |
| `dashboard.html` | Generated. Single file, no dependencies — open it in a browser |

## The dashboard

`dashboard.html` is a self-contained interactive view: sliders for segment, term,
seats, discount asked, and the value estimate, with a hero price, KPI tiles, an
approval verdict chip, and three charts that recompute live. Light and dark mode,
keyboard-accessible tooltips, and a table view of every chart.

Single-file HTML was chosen because it is the only format you can put on a
SharePoint page, email to a stakeholder, or open in three years without a build
step. See `../../05-visualizing-calculators.md` for the alternatives (Excel,
Streamlit, Power BI) and when each is the better call.

**The duplication risk is real and is handled.** Live interactivity means the
pricing math must also exist in JavaScript. Two copies of a discount floor is how
you end up telling an AE that 22% is fine while the deal desk says escalate. So:
policy constants are injected from `value_calculator.py` at build time (the JS
never hardcodes a floor), and `check_parity.py` fails the build if the two
implementations disagree on any price or — especially — any approval verdict.

## The point of the structure

The split is the lesson, not the pricing model:

```
messy inputs ──▶ [ Python: math, floors, approvals ] ──▶ JSON ──▶ [ LLM: prose ] ──▶ draft
                          testable, auditable                      fast, fluent
```

Concretely:

- **Money is pre-formatted into strings** (`"$210,000"`) before the model sees it.
  The correct behaviour — copying — becomes the easiest behaviour.
- **Invalid input returns `{"ok": false, "problems": [...]}`** rather than raising.
  A calling agent can read the problems and ask for the missing input. Errors as
  data, not as exceptions.
- **Approval verdicts are computed, not judged.** `auto-approvable` /
  `escalate to deal desk` / `reject -- below absolute floor` comes from comparing
  numbers, so it can't be talked out of by a persuasive prompt.
- **Policy constants sit at the top of the file**, so changing a discount limit is a
  one-line diff you can review, and `eval_cases.py` tells you immediately what that
  change did to your routing.

## What the worked example demonstrates

Run it and look at the Northwind deal. Two things worth noticing, both deliberate:

**1. The confidence haircut does real work.** $995k of gross identified value becomes
$671k risk-adjusted. The largest single haircut is on the driver with no customer
data behind it — a $300k win-rate uplift at 30% confidence. That driver is exactly
what gets a value case torn apart in a QBR, so the model is built to name it as
unvalidated rather than bury it in a total.

**2. The rate-card floor binds, not the value band.** The value band is
$67k–$168k, but the approval-free floor is $210k, so the recommendation is $210k.
That's not a bug — it's the calculator telling you something useful: **for this deal
the rate card is setting the price, not the value case.** Either the value drivers
are understated, or this account is priced by the card and the value story is
supporting material rather than the basis of the price. Knowing which is a strategy
question, and the tool surfaces it instead of hiding it inside a blended number.

That second behaviour is the argument for building the deterministic layer first.
A prompt asked to "recommend a price" would have produced a confident number
somewhere in the middle and told you nothing about the tension.

## Making it yours

1. Replace `LIST_PRICE_PER_SEAT_YEAR`, `SEGMENT_DISCOUNT_LIMIT`,
   `TERM_DISCOUNT_HEADROOM`, and `ABSOLUTE_FLOOR_SHARE_OF_LIST` with your real
   policy. If your model isn't per-seat, change the `list_annual` calculation —
   it's one line.
2. Set `VALUE_CAPTURE_BAND` to what you actually target. The band matters more than
   the midpoint; a single number invites false precision.
3. **Rewrite `eval_cases.py` around your own historical edge cases.** Pull ten real
   deals — especially ones where the desk overrode the obvious answer — and encode
   the correct verdict. This is where the value is. The rest of the code is a day's
   work; the eval set is the asset.
4. Only then wire up `prompts/narrative.md` against a real model.

## Deliberately not included

No LLM API call, no framework, no vector store, no agent loop. Adding them before
step 3 above is the most common way this kind of project goes wrong: you end up
debugging an agent loop when the actual problem was that nobody agreed on the
discount floor.
