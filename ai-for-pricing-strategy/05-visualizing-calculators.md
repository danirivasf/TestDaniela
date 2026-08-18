# Visualising the calculators

A markdown table is fine for you. It's useless in a deal review, and it can't be
put on a SharePoint page. Here are the four realistic options, and which to use when.

**A working example is already built:** `examples/pricing_calculator/dashboard.html`.
Generate it with `python3 build_dashboard.py` and open it in a browser — no server,
no install, no network.

---

## Option 1 — Single-file HTML (recommended, and what's built here)

One `.html` file with the charts and interactive controls inlined. No CDN, no build
step, no dependencies.

**Why this wins for your situation:**
- **It's the only format you can actually deploy.** Drop it in a SharePoint document
  library, or embed it on a page with the *Embed* web part. Email it. Put it in
  Teams. No IT ticket, no licence.
- **It works offline and forever.** No CDN link to rot, no `pip install` for the
  person you send it to.
- **Interactive.** Sliders for seats, term, discount, and the value estimate, with
  everything recomputing live. That is what turns a static number into a
  conversation: "what if we go to 36 months?" gets answered in the meeting.
- **Version-controllable.** It's generated from Python, so the chart code is
  reviewable and the output is reproducible.

**The one real risk, and how it's handled here.** Interactivity means the pricing
math has to run in the browser, so it exists twice — Python and JavaScript. Two
implementations of a discount floor is exactly how you end up telling an AE that 22%
is fine when the deal desk says escalate. Two mitigations, both in the example:

1. **Policy constants are injected from `value_calculator.py` at build time.** The
   JavaScript never hardcodes a floor. Change the Python, rebuild, and the page
   cannot disagree.
2. **`check_parity.py` runs both implementations over 1,440 deals** and fails the
   build if any price, value, or — most importantly — approval verdict differs.

If you take one idea from this file, take that one: **when a number has to live in
two places, write the test that proves they agree.**

## Option 2 — Excel

Not a joke, and not a downgrade. For a pricing audience it's often the right answer.

- Everyone can open it, and more importantly everyone can *audit* it — a stakeholder
  who distrusts your dashboard will trust a cell they can click into.
- Native charts, no code.
- It's where your rate card probably already lives.

Use Excel when the deliverable is a model someone else needs to modify. Use HTML when
the deliverable is a *view* that must not be modified. That distinction is usually the
whole decision.

The weakness is version sprawl: six copies of `pricing_model_v3_FINAL.xlsx` with
different floors in them is the failure mode this whole repo is trying to avoid. A
reasonable hybrid is to generate the workbook from the same Python (`openpyxl`), so
the spreadsheet is an *output*, not the source of truth.

## Option 3 — Streamlit / Gradio

`pip install streamlit`, ~30 lines, and you get sliders and charts calling your Python
directly — so **no duplicated math at all**, which is a genuine advantage over Option 1.

The catch is deployment: it needs a running Python process. That means a server,
which means an internal hosting story and an IT conversation. Great for prototyping
on your own machine and for a live demo; awkward as something a stakeholder opens next
Tuesday.

## Option 4 — Power BI

Right answer when the data is *already* in your Microsoft estate and the audience
expects a corporate dashboard, especially for Blueprint 3-style recurring reporting.

Wrong answer for a deal-level calculator: it's built for exploring datasets, not for
"recompute this one deal as I move a slider." Also a licensing and gateway
conversation you don't need in week 4.

---

## Getting it onto a SharePoint page

Building on `04-sharepoint-and-m365.md`:

1. **Upload `dashboard.html` to a document library.** Simplest path; people open it
   from the library.
2. **Embed it on a page.** The *Embed* web part or *File viewer* web part can render
   it inline. Note that many tenants restrict the Embed web part to allow-listed
   domains — for a file in your own library it usually works, but confirm before you
   promise it.
3. **If embedding is blocked**, fall back to a SharePoint *list* holding the computed
   figures plus a link to the HTML file. Less pretty, more robust, and it keeps the
   numbers queryable.

Regenerate and re-upload when the rate card changes. If that becomes a chore, that's
your cue to automate it via Power Automate — which is Blueprint 5.

---

## What made this chart set work

Not aesthetics — decisions. Worth reusing on your next chart:

- **The form came before the colour.** Recommended price is one number, so it's a
  hero figure, not a one-bar chart. The price ladder is an *emphasis* chart: the
  recommendation is in colour, every policy reference is grey. That's what makes the
  finding visible instead of buried in a rainbow.
- **The palette was validated, not eyeballed.** Run through the dataviz validator:
  the blue/grey pair passes CVD separation (ΔE 15.9), normal-vision separation
  (17.8), and 3:1 contrast in both modes; the four-step blue ramp on the sensitivity
  chart passes all ordinal checks in both light and dark. The one check the pair
  "fails" is the chroma floor, because grey reads as grey — which is the entire point
  of a de-emphasis colour.
- **Every chart has a table twin.** *Show data tables* reveals the same numbers in
  WCAG-clean tables, so nothing is reachable only by hovering.
- **The tooltip never gates a value**, and keyboard focus shows the same readout as
  hover.
- **Labels are selective.** Two of four columns on the sensitivity chart are labelled
  — the base case and the worst case. A number on every mark goes unread.
- **Rendering it caught bugs that reading the code did not.** The table view was
  visible when it should have been hidden (`display: grid` silently overrides
  `[hidden]`), the sensitivity axis clipped the tallest column because the tick
  domain stopped below the data, and the in-fill label picked white on a blue where
  dark ink had better contrast. All three were invisible until a screenshot existed.
  **Always render and look at it.**

One gap, stated plainly: **texture fills for full-colour-blindness and forced-colours
mode are not implemented.** The mitigations in place are the always-present legend,
direct labels, and the table view. If you need genuine print/CVD robustness, that's
the piece to add.
