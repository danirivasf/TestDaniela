# The list, triaged

Scored against one criterion: **does this help me automate pricing/strategy work?**
Not "is this good" — most of it is good. A world-class course on training LLMs is a
Skip for you, and that's not a criticism of the course.

⚠️ = link was a `lnkd.in` shortlink that couldn't be resolved from this environment;
the resource was identified by title. Verify before relying on it.

---

## TIER 1 — Read these (roughly 8 hours total)

### Guides

**Anthropic — Building Effective Agents** ⚠️
<https://www.anthropic.com/engineering/building-effective-agents>
The highest value item on the entire list. Names the five workflow patterns
(prompt chaining, routing, parallelisation, orchestrator-workers,
evaluator-optimizer) and argues that you should exhaust all of them before
reaching for an autonomous agent. Every one of your use cases maps to one of
those five. **Read first.**

**Anthropic — Building Effective Agents (video, #5)**
<https://www.youtube.com/watch?v=D7_ipDqhtwk>
Same content as the article, in conversation form. Watch instead of reading if
you prefer, not in addition.

**OpenAI — A Practical Guide to Building Agents** ⚠️
The business-facing counterpart: task-selection criteria, guardrails, escalation
design. Its checklist for "should this be automated" is directly reusable when you
pitch an internal automation to a stakeholder who is nervous about it.

**Google — Agents whitepaper** and **Agents Companion** ⚠️
Good on the *architecture* vocabulary (tools, extensions, function calling,
retrieval) and on agent evaluation in the Companion. Skim; there's redundancy with
the Anthropic piece. The Companion's section on agent evals is the part to actually
read.

**Prompt Engineering Guide** ⚠️ (list item: repos #3)
<https://www.promptingguide.ai/> · <https://github.com/dair-ai/Prompt-Engineering-Guide>
Reference material, not a read-through. You will return to the structured-output
and few-shot sections repeatedly. **The single most practically useful page for
daily work.**

**Claude Code — best practices for agentic coding** ⚠️
<https://www.anthropic.com/engineering/claude-code-best-practices>
Relevant because Claude Code is plausibly the tool you'd *build* these automations
with, given you're already working in a repo. Read once you start week 2.

### Books

**Chip Huyen — AI Engineering**
<https://www.oreilly.com/library/view/ai-engineering/9781098166298/>
The best single book on the list for your purposes. Chapters on evaluation,
RAG, and inference cost/latency tradeoffs are all directly applicable. It assumes
you're building *with* models rather than training them — which is your situation.
Buy this one if you buy one.

**Nicole Koenigstein — AI Agents: The Definitive Guide** ⚠️
**Michael Albada — Building Applications with AI Agents** ⚠️
**Kyle Stratis — AI Agents with MCP** ⚠️
Recent, practitioner-oriented agent books. Pick **one**, not three — they overlap
heavily. Albada's is the most application-shaped; Stratis's is the one to pick if
your automation needs to connect to internal systems (SharePoint, CRM), because
that's the problem MCP exists to solve.

### Papers

Read the abstract, introduction, and the figure of each. Do not read the
experiments sections — they're benchmark results on tasks unlike yours.

**ReAct** — <https://arxiv.org/abs/2210.03629> ⚠️
Reason + act interleaving. This is the mental model behind every tool-using
assistant. Worth understanding because it tells you *why* an agent needs to see
tool results before its next step, which shapes how you design a calculator tool's
output format.

**Chain-of-Thought Prompting** — <https://arxiv.org/abs/2201.11903> ⚠️
Why "show your reasoning step by step" changes output quality. Directly useful for
prompts that classify deals or assess discount justifications — you want the
reasoning visible so a human can audit it.

**Reflexion** — <https://arxiv.org/abs/2303.11366> ⚠️
Self-critique loops. This is the theory behind the evaluator-optimizer pattern,
which is the pattern for "draft this comms update, then check it against our tone
and factual constraints, then revise."

**RAG Survey** — <https://arxiv.org/abs/2312.10997> ⚠️
Skim only. Read it when you get to "answer questions over our pricing policy
documents," which is Blueprint 4. Before that it's premature.

### Courses

**DeepLearning.AI — Evaluating AI Agents** ⚠️
The course most likely to save you from shipping something wrong. Evaluation is
the unglamorous skill that makes an internal automation trustworthy enough to keep
using. If you do one course, do this one.

**Anthropic / DeepLearning.AI — MCP** ⚠️
<https://www.deeplearning.ai/short-courses/>
MCP is how an assistant gets access to your actual systems. If the SharePoint or
CRM integration matters — and for your use cases it does — this is the mechanism.

---

## TIER 2 — Useful when you hit the specific problem

Don't pre-read these. Come back when the blueprint you're building needs them.

| Resource | Come back when... |
|---|---|
| **GenAI Agents** — <https://github.com/NirDiamant/GenAI_Agents> *(list items #1 and #6, duplicated)* | You want a working code example of a specific pattern. Excellent as a copy-paste reference library; poor as a curriculum. Search it by pattern name. |
| **Microsoft — AI Agents for Beginners** — <https://github.com/microsoft/ai-agents-for-beginners> *(items #2 and #5, duplicated)* | You want a structured beginner course *and* you're in a Microsoft shop — which, given SharePoint, you are. Its Azure/Semantic Kernel bias is an advantage for you, not a drawback. Strong Tier 2, borderline Tier 1 for this reason. |
| **Building and Evaluating Agents** — <https://www.youtube.com/watch?v=d5EltXhbcfA> | You've built something and need to prove it works. Pairs with the eval course. |
| **Agentic AI Overview (Stanford)** — <https://www.youtube.com/watch?v=kJLiOGle3Lw> | You want the credible academic framing for a leadership conversation. |
| **Building Agents with MCP** — <https://www.youtube.com/watch?v=kQmXtrmQ5Zg> | You're wiring up a real internal data source. |
| **Awesome Generative AI Guide** ⚠️ — <https://github.com/aishwaryanr/awesome-generative-ai-guide> | You need to find a resource on a narrow topic. It's an index, so use it as one. |
| **Hands-On Large Language Models** ⚠️ — <https://github.com/HandsOnLLM/Hands-On-Large-Language-Models> | You want intuition for embeddings and semantic search, which you'll need for Blueprint 4 (policy Q&A). Good notebooks. |
| **Multi AI Agent Systems / Multi-Agent Use / Agent Design Patterns** (courses 11, 13, 14) ⚠️ | Honestly: probably never, for your use cases. Multi-agent adds coordination cost and non-determinism. Revisit only if you have a genuinely parallel research task. |
| **Vector DB courses (Pinecone, embeddings-to-apps)** ⚠️ | You have >100 documents to search. Below that, stuff them in the prompt — it's cheaper and better. |
| **Agent Memory** ⚠️ | You're building something conversational that must persist state across sessions. Most scheduled automations don't need this. |
| **Building & Evaluating RAG apps** ⚠️ | Blueprint 4, after the RAG survey. |
| **Building Browser Agents** ⚠️ | You need to pull data from a web tool with no API — e.g. competitor pricing pages. Genuinely useful for pricing intel, and a real edge case where browser automation beats an API. |
| **Computer Use with Anthropic** ⚠️ | Same as above, more general and less reliable. Low priority. |
| **Improving LLM Accuracy** ⚠️ | Your outputs are inconsistent and you need systematic fixes rather than prompt-fiddling. |
| **LLMOps** ⚠️ | Something you built is now used by other people and breaks occasionally. Week 10, not week 4. |
| **Philo Agents** — [playlist](https://www.youtube.com/playlist?list=PLacQJwuclt_sV-tfZmpT1Ov6jldHl30NR) | You want to see a full agent system built end to end. Long. Good if video is how you learn. |
| **Building an Agent from Scratch** — <https://www.youtube.com/watch?v=xzXdLRUyjUg> | You want to demystify the agent loop. It's ~50 lines of code, and seeing that is clarifying — it stops you over-estimating what frameworks are doing for you. |
| **HuggingFace Agents Course** ⚠️ — <https://huggingface.co/learn/agents-course> | You want a free structured course with exercises. Solid, somewhat framework-heavy. |

---

## SKIP — good resources, wrong job

These are about *building and training models*. That is a different profession from
yours. Skipping them costs you nothing.

- **LLM Introduction** (<https://www.youtube.com/watch?v=zjkBMFhNj_g>) — Karpathy-style
  intro. Watch on a plane if curious. Zero effect on your output.
- **LLMs from Scratch** (video) and **Raschka — Building an LLM from Scratch** /
  <https://github.com/rasbt/LLMs-from-scratch> ⚠️ — Superb resources for building a
  transformer. You will never build a transformer.
- **Understanding Deep Learning** — <https://udlbook.github.io/udlbook/> — Excellent
  textbook. It's a maths textbook.
- **LLM Course** — <https://github.com/mlabonne/llm-course> — Heavily oriented to
  fine-tuning and quantisation. Not your problem.
- **The LLM Engineering Handbook** ⚠️ — Production LLM systems and MLOps pipelines.
  Overkill unless you become the person who owns this infrastructure.
- **Made With ML** ⚠️ — <https://github.com/GokuMohandas/Made-With-ML> — Classical ML
  engineering practices. Great, and orthogonal.
- **Designing Machine Learning Systems** ⚠️ — <https://github.com/chiphuyen/dmls-book>
  — Chip Huyen's earlier book. Read *AI Engineering* instead; it's the one written
  for your era of this problem.
- **ML for Beginners (Microsoft)** ⚠️ — <https://github.com/microsoft/ML-For-Beginners>
  — Classical ML fundamentals. Not needed for LLM-shell automation.
- **Toolformer** — <https://arxiv.org/abs/2302.04761> ⚠️ — How to *train* a model to
  use tools. Historically important; function calling is a solved product feature now.
- **Generative Agents** — <https://arxiv.org/abs/2304.03442> ⚠️ — The Smallville
  simulation paper. Delightful. Irrelevant.
- **Tree of Thoughts** — <https://arxiv.org/abs/2305.10601> ⚠️ — Search over reasoning
  paths. Research-grade; costly and rarely worth it in practice.

## Newsletters

All five are reasonable. Subscribing to five AI newsletters is how you end up
reading about AI instead of using it. **Pick one** — for your role, a
practitioner-oriented one (e.g. DecodingML) is a better fit than a research-digest
one, because you want implementation patterns rather than paper summaries. Revisit
in three months.
