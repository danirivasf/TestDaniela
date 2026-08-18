# AI & Agents for a Pricing / Strategy Role

A triaged read of a large AI-learning link dump, filtered for one question:
**what actually helps someone doing pricing and strategy work automate their own job?**

The original list is ~60 items covering everything from transformer internals to
multi-agent frameworks. Most of it is aimed at people *building AI products*. You
are not building an AI product — you are trying to (a) automate internal process,
(b) build value/pricing calculators, (c) automate communications on a SharePoint
page. That changes which 15% of the list is worth your time.

## Files here

| File | What it's for |
|---|---|
| `01-curated-resources.md` | The full list, triaged Tier 1 / Tier 2 / Skip, with a one-line "why this matters for pricing" on each |
| `02-patterns-cheatsheet.md` | The concepts distilled — no video required. Read this before you read anything on the list |
| `03-project-blueprints.md` | Five concrete things to build, in order of value-to-effort, with the pattern each one uses |
| `04-sharepoint-and-m365.md` | The specific "automate comms on a SharePoint page" path, honestly assessed |
| `examples/pricing_calculator/` | A working, dependency-free value/pricing calculator you can run today |

## The 20% that matters

If you read four things off that entire list, read these:

1. **Anthropic — Building Effective Agents.** <https://www.anthropic.com/engineering/building-effective-agents>
   Short. Its central argument is the single most useful idea for your work:
   *most problems don't need an agent.* A fixed workflow with an LLM step in it is
   cheaper, faster, and far more predictable. Pricing work is full of problems that
   look agentic and are actually workflows.
2. **OpenAI — A Practical Guide to Building Agents.** The complementary business-side
   framing: when to automate, guardrails, human-in-the-loop. Useful vocabulary for
   pitching this internally.
3. **Prompt Engineering Guide.** <https://www.promptingguide.ai/>
   You will spend more time writing prompts than writing code. Read the sections on
   few-shot, structured output, and chain-of-thought; skip the rest.
4. **Chip Huyen — AI Engineering** (book, O'Reilly). The chapter on evaluation is
   the one that separates "demo that impressed my manager" from "thing the deal desk
   actually trusts." If you build anything that touches a customer-facing number,
   you need an eval set.

Everything else on the list is either a deeper version of these, or irrelevant to you.

## The one architectural rule for pricing work

> **Never let a language model do arithmetic that a customer will see.**

Put every number in deterministic code — Python, or even an Excel formula. Use the
LLM only for the layer around it: reading messy inputs, summarising, drafting the
narrative, explaining the output in prose, routing an approval.

This is the pattern in `examples/pricing_calculator/`. Discount math, floor checks,
and ROI live in `value_calculator.py`, which is testable and auditable. The LLM gets
the finished JSON and writes the customer-facing story. If someone challenges a
number in a QBR, you can point at a line of code, not at a prompt.

Every blueprint in `03-project-blueprints.md` follows this rule. It is also why
roughly half the resource list — the model-internals half — doesn't help you: you
don't need to know how attention works to be good at this. You need to know where
to put the boundary between deterministic and generative.

## A four-week path

**Week 1 — Vocabulary.** Read *Building Effective Agents* and skim the OpenAI guide.
Read `02-patterns-cheatsheet.md`. Goal: be able to say "that's a routing problem,
not an agent problem" and mean it.

**Week 2 — One deterministic tool.** Run the calculator in `examples/`, then rewrite
it around a real pricing model you own. No LLM yet. Goal: a script that turns inputs
into a defensible price band.

**Week 3 — Add the LLM shell.** Wrap the calculator with a prompt that drafts the
value narrative and the internal deal summary. Compare against three real proposals
you've written. Goal: output you'd send with light editing.

**Week 4 — Automate the delivery.** Pick one blueprint from
`03-project-blueprints.md` and get it running end-to-end, on a schedule, posting
somewhere a human reads. Goal: something that runs without you.

Do not spend week 1 on transformer architecture. It's genuinely interesting and it
will not move any of this forward.

## Honest caveats

- **The `lnkd.in` shortlinks in the source list could not be resolved** from this
  environment (LinkedIn is blocked by network policy). Titles were matched to
  canonical sources by name. Items marked ⚠️ in `01-curated-resources.md` are
  best-guess identifications — verify the link before relying on it.
- **The list has duplicates.** "GenAI Agents" appears twice (repos #1 and #6) and
  "AI Agents for Beginners" appears twice (#2 and #5). Noted in the triage.
- **Course URLs move.** DeepLearning.AI short courses are best found by searching
  the title at <https://www.deeplearning.ai/short-courses/> rather than via a
  saved link.
- **Nothing here is Octave-specific.** The blueprints are shaped for a generic B2B
  pricing/strategy function. Sanity-check them against your actual deal process,
  approval thresholds, and data sources before building.
- **Check internal policy before pointing any AI tool at commercial data.**
  Customer pricing, discount floors, and win-loss data are usually the most
  sensitive non-financial data a company has. That's a conversation to have before
  week 3, not after.
