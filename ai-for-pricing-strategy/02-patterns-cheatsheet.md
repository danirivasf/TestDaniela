# Patterns cheatsheet, translated into pricing work

The concepts from ~60 resources, compressed, each mapped to something you'd
plausibly do. Read this once; it replaces about 20 hours of the source list.

---

## First: workflow or agent?

This distinction is the whole game, and it's the thing Anthropic's *Building
Effective Agents* is about.

- **Workflow** — you decide the steps in advance; the LLM fills in specific slots.
  Predictable, cheap, debuggable, testable.
- **Agent** — the model decides the steps and which tools to call, in a loop, until
  it thinks it's done. Flexible, expensive, non-deterministic, hard to audit.

**For pricing and strategy work, you want workflows almost every time.** Your
outputs are numbers and commitments that other people rely on. Non-determinism is
a liability, not a feature. Use an agent only when the *path* genuinely can't be
known in advance — open-ended research is the honest example.

A useful test: if you can draw the process as a flowchart, build the flowchart.
Don't hand a flowchart to an agent and hope.

---

## The five workflow patterns

### 1. Prompt chaining
Decompose into fixed sequential steps; each output feeds the next.

> **Pricing use:** Deal summary generation. Step 1: extract structured fields from
> the CRM record. Step 2: run the deterministic calculator on those fields. Step 3:
> draft the narrative from the calculator output. Step 4: check it against approval
> policy and flag exceptions.

Why it works: each step is small enough to verify. When output is wrong you know
which step broke.

### 2. Routing
Classify the input, then send it down a specialised path.

> **Pricing use:** Inbound pricing requests. Standard-config renewal → auto-generate
> quote from rate card. Non-standard discount → route to the deal-desk exception
> template. Net-new segment with no comparable → route to a human with a prepared
> brief.

Why it works: you stop trying to write one prompt that handles every case. Most
"the AI gave a weird answer" problems are really missing routing.

### 3. Parallelisation
Fan out independent subtasks, then aggregate.

Two flavours: *sectioning* (split the work) and *voting* (same task several times,
take consensus).

> **Pricing use (sectioning):** Competitor pricing scan — one call per competitor,
> aggregate into a comparison table.
> **Pricing use (voting):** Ask three times whether a discount request meets policy;
> disagreement is a signal that it's a genuine edge case needing a human. That's a
> cheap and surprisingly effective confidence measure.

### 4. Orchestrator–workers
A central call decomposes a task dynamically and delegates subtasks.

> **Pricing use:** Quarterly competitive review where you don't know in advance which
> segments moved. Orchestrator decides what to investigate; workers do each dig.

Use sparingly. This is where cost and unpredictability start climbing.

### 5. Evaluator–optimizer
Generate, critique against explicit criteria, revise. Loop 1–3 times.

> **Pricing use:** The highest-value pattern for your **communications** work.
> Generate the SharePoint update, then evaluate against a written rubric — correct
> figures, no forward-looking commitments, right tone, under 300 words — then revise.
> Two passes gets most of the way to publishable.

The critical detail: **the evaluation criteria must be written down explicitly.**
"Make it better" does nothing. A rubric with five named checks does a lot.

---

## Tool use / function calling

You give the model a set of functions with described inputs; it decides when to call
them and reads the results back.

**This is the mechanism that makes your calculator safe.** The model doesn't compute
the price — it calls `calculate_price(seats=250, term=36, segment="mid-market")` and
receives an audited number. The arithmetic is Python. The model handles the messy
input and the prose output.

Design notes that matter more than they look:
- Return **structured, labelled** output. `{"floor_price": 42000, "reason": "segment
  floor"}` is far more usable than `"42000"`.
- Return errors as data, not exceptions: `{"error": "term must be 12/24/36"}` lets
  the model correct itself.
- Describe each parameter's units and valid range in the tool description. Most
  tool-calling failures are actually documentation failures.

---

## MCP (Model Context Protocol)

An open standard for connecting assistants to data sources and tools, so each
integration is written once rather than per-application.

**Why you specifically care:** your data lives in SharePoint, Excel, a CRM, and
probably Aha. MCP is the plumbing that lets an assistant reach those without you
writing bespoke glue per tool. See `04-sharepoint-and-m365.md` for what's actually
available today versus what needs building.

---

## RAG (Retrieval-Augmented Generation)

Retrieve relevant documents, put them in the prompt, answer from them.

> **Pricing use:** "What's our discount policy for multi-year public sector deals?"
> answered over your actual policy documents rather than from the model's guesswork.

**Don't over-build this.** The honest decision rule:
- Under ~20 documents → paste the relevant ones into the prompt. Done. No vector
  database, no chunking strategy, no embedding pipeline.
- 20–100 → keyword search to select candidates, then paste.
- Over 100, or genuinely semantic queries → now you need embeddings and a vector
  store, and the vector DB courses on the list become relevant.

Most internal pricing-policy corpora are smaller than people assume. Check the actual
document count before you architect anything.

---

## Chain-of-thought and structured reasoning

Asking for explicit reasoning before the answer improves quality on judgement tasks
and — more importantly for you — makes the output **auditable**.

> **Pricing use:** For any discount-justification or approval-classification step,
> require the model to output its reasoning *and* the criteria it applied, then the
> verdict. When the deal desk disagrees, you can see exactly where the logic diverged,
> and fix the prompt rather than argue about vibes.

---

## Evaluation — the part people skip

You cannot tell whether an automation works by looking at three outputs and feeling
good. Build a small eval set before you build the automation.

A pricing eval set is not exotic. It's a spreadsheet:

| Input case | Expected output | Notes |
|---|---|---|
| 250 seats, 36mo, mid-market, 18% ask | Approved, within floor | standard |
| 40 seats, 12mo, SMB, 35% ask | Escalate — below floor | must not auto-approve |
| Missing seat count | Ask for input, don't guess | failure mode |

Twenty rows covering your real edge cases. Run it every time you change a prompt.
This is the difference between an automation people trust and one quietly abandoned
after it embarrassed someone once.

Include, deliberately, the cases where the correct answer is *"escalate to a human."*
Those are the ones that create risk when they're missed.

---

## Cost and latency intuition

Rough shape, not precise figures — check current pricing before you budget:
- A short classification call costs a fraction of a cent. Batch thousands freely.
- Long-document analysis is meaningfully more; watch it in loops.
- Agent loops multiply calls by iterations. An agent that "just checks a few things"
  can be 50× the cost of the workflow that does the same thing.
- Prompt caching cuts cost substantially when you resend the same large context (a
  policy document, a rate card) across many calls. Very applicable to your patterns.

Practical implication: **cost is almost never the reason not to automate an internal
pricing process.** The reason is trust, and trust comes from evals.

---

## Anti-patterns to avoid

1. **Letting the model do arithmetic a customer will see.** Stated in the README and
   worth repeating. Deterministic code, always.
2. **Multi-agent systems for linear problems.** Coordination overhead and
   compounding non-determinism for no benefit.
3. **Building RAG for 12 documents.** Paste them.
4. **No eval set.** You're guessing.
5. **Automating a process you don't already understand.** If the manual process is
   inconsistent, you'll automate the inconsistency at scale. Document the process
   first — you'll often find the documentation was the real win.
6. **Full autonomy on outbound communications.** Anything that leaves the building,
   or lands on a page executives read, gets a human approval step. Not forever —
   but at least until an eval set says otherwise.
