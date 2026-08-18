"""Generate dashboard.html -- a single-file, interactive view of the calculator.

    python3 build_dashboard.py && open dashboard.html

The output is one self-contained HTML file: no build step, no CDN, no network
access. That matters because it is the only format you can actually get onto a
SharePoint page or email to a stakeholder without asking anyone's permission.

Policy constants are injected from value_calculator.py, so the page can never
disagree with the Python about what the discount floors are. The pricing
formulas are mirrored in pricing_model.js; check_parity.py proves the two
implementations agree.
"""

from __future__ import annotations

import json
from pathlib import Path

import value_calculator as vc
from check_parity import POLICY

HERE = Path(__file__).parent

DEAL = {
    "customer": vc.EXAMPLE_DEAL.customer,
    "segment": vc.EXAMPLE_DEAL.segment,
    "seats": vc.EXAMPLE_DEAL.seats,
    "termMonths": vc.EXAMPLE_DEAL.term_months,
    "proposedDiscount": vc.EXAMPLE_DEAL.proposed_discount,
    "drivers": [
        {
            "name": d.name,
            "annualValue": d.annual_value,
            "confidence": d.confidence,
            "basis": d.basis,
        }
        for d in vc.EXAMPLE_DEAL.drivers
    ],
}

# Validated with dataviz/scripts/validate_palette.js -- see README for the
# recorded results. Do not hand-tune these; re-run the validator.
PALETTE = "#2a78d6,#898781"

TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pricing calculator -- __CUSTOMER__</title>
<style>
  .viz-root {
    color-scheme: light;
    --surface-1:      #fcfcfb;
    --page:           #f9f9f7;
    --text-primary:   #0b0b0b;
    --text-secondary: #52514e;
    --muted:          #898781;
    --gridline:       #e1e0d9;
    --baseline:       #c3c2b7;
    --border:         rgba(11,11,11,0.10);
    --series-1:       #2a78d6;
    --deemph:         #898781;
    --ord-1:          #86b6ef;
    --ord-2:          #5598e7;
    --ord-3:          #2a78d6;
    --ord-4:          #1c5cab;
    --good:           #0ca30c;
    --warning:        #fab219;
    --critical:       #d03b3b;
  }
  @media (prefers-color-scheme: dark) {
    :root:where(:not([data-theme="light"])) .viz-root {
      color-scheme: dark;
      --surface-1:      #1a1a19;
      --page:           #0d0d0d;
      --text-primary:   #ffffff;
      --text-secondary: #c3c2b7;
      --muted:          #898781;
      --gridline:       #2c2c2a;
      --baseline:       #383835;
      --border:         rgba(255,255,255,0.10);
      --series-1:       #3987e5;
      --deemph:         #898781;
      --ord-1:          #9ec5f4;
      --ord-2:          #6da7ec;
      --ord-3:          #3987e5;
      --ord-4:          #256abf;
    }
  }
  :root[data-theme="dark"] .viz-root {
    color-scheme: dark;
    --surface-1:      #1a1a19;
    --page:           #0d0d0d;
    --text-primary:   #ffffff;
    --text-secondary: #c3c2b7;
    --muted:          #898781;
    --gridline:       #2c2c2a;
    --baseline:       #383835;
    --border:         rgba(255,255,255,0.10);
    --series-1:       #3987e5;
    --deemph:         #898781;
    --ord-1:          #9ec5f4;
    --ord-2:          #6da7ec;
    --ord-3:          #3987e5;
    --ord-4:          #256abf;
  }

  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
    background: var(--page, #f9f9f7);
  }
  .viz-root {
    background: var(--page);
    color: var(--text-primary);
    min-height: 100vh;
    padding: 28px 24px 56px;
  }
  .wrap { max-width: 1080px; margin: 0 auto; }

  header { display: flex; align-items: flex-start; gap: 20px; flex-wrap: wrap; }
  header .titles { flex: 1 1 320px; }
  h1 { font-size: 19px; font-weight: 600; margin: 0 0 4px; letter-spacing: -0.01em; }
  .sub { font-size: 13px; color: var(--text-secondary); margin: 0; }
  .head-controls { display: flex; gap: 8px; align-items: center; }

  button, select, input[type="range"] { font: inherit; }
  .btn {
    background: var(--surface-1); color: var(--text-primary);
    border: 1px solid var(--border); border-radius: 7px;
    padding: 6px 11px; font-size: 12.5px; cursor: pointer;
  }
  .btn:hover { border-color: var(--baseline); }
  .btn[aria-pressed="true"] { border-color: var(--series-1); }

  /* One filter row, above everything it scopes. */
  .filters {
    display: flex; flex-wrap: wrap; gap: 18px 26px; align-items: flex-end;
    background: var(--surface-1); border: 1px solid var(--border);
    border-radius: 10px; padding: 14px 18px; margin: 18px 0 20px;
  }
  .field { display: flex; flex-direction: column; gap: 5px; }
  .field > label {
    font-size: 11px; text-transform: uppercase; letter-spacing: 0.04em;
    color: var(--muted); font-weight: 600;
  }
  .field select {
    background: var(--surface-1); color: var(--text-primary);
    border: 1px solid var(--border); border-radius: 6px; padding: 5px 8px; font-size: 13px;
  }
  .field .rowctl { display: flex; align-items: center; gap: 9px; }
  .field input[type="range"] { width: 132px; accent-color: var(--series-1); }
  .readout {
    font-size: 13px; font-variant-numeric: tabular-nums;
    color: var(--text-primary); min-width: 56px;
  }

  .hero-card {
    background: var(--surface-1); border: 1px solid var(--border); border-radius: 10px;
    padding: 20px 22px; display: flex; align-items: center; gap: 28px; flex-wrap: wrap;
  }
  .hero-label { font-size: 12px; color: var(--muted); text-transform: uppercase;
                letter-spacing: 0.04em; font-weight: 600; margin-bottom: 2px; }
  .hero-figure { font-size: 50px; line-height: 1.02; font-weight: 600; letter-spacing: -0.02em; }
  .hero-note { font-size: 12.5px; color: var(--text-secondary); margin-top: 5px; }

  .chip {
    display: inline-flex; align-items: center; gap: 8px;
    border-radius: 8px; padding: 8px 13px; font-size: 13px; font-weight: 500;
    color: var(--text-primary); border: 1px solid; background: var(--surface-1);
  }
  .chip .glyph { font-size: 13px; line-height: 1; font-weight: 700; }
  .chip.good     { border-color: var(--good); }
  .chip.good .glyph { color: var(--good); }
  .chip.warning  { border-color: var(--warning); }
  .chip.warning .glyph { color: var(--warning); }
  .chip.critical { border-color: var(--critical); }
  .chip.critical .glyph { color: var(--critical); }

  .kpi-row {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(168px, 1fr));
    gap: 12px; margin: 12px 0 20px;
  }
  .tile {
    background: var(--surface-1); border: 1px solid var(--border);
    border-radius: 10px; padding: 13px 15px;
  }
  .tile .t-label { font-size: 12px; color: var(--muted); margin-bottom: 5px; }
  .tile .t-value { font-size: 25px; font-weight: 600; letter-spacing: -0.01em; }
  .tile .t-note { font-size: 11.5px; color: var(--text-secondary); margin-top: 3px; }

  .grid { display: grid; gap: 14px; grid-template-columns: 1fr; }
  @media (min-width: 900px) { .grid.two { grid-template-columns: 1fr 1fr; } }

  figure.card {
    margin: 0; background: var(--surface-1); border: 1px solid var(--border);
    border-radius: 10px; padding: 16px 18px 12px;
  }
  figcaption { margin-bottom: 2px; }
  .c-title { font-size: 14px; font-weight: 600; }
  .c-sub { font-size: 12px; color: var(--text-secondary); margin-top: 2px; }
  svg { display: block; width: 100%; height: auto; overflow: visible; }
  svg text { font-family: inherit; }

  .legend { display: flex; flex-wrap: wrap; gap: 6px 16px; margin: 10px 0 2px; }
  .legend .item { display: inline-flex; align-items: center; gap: 6px;
                  font-size: 12px; color: var(--text-secondary); }
  .legend .key { width: 11px; height: 11px; border-radius: 2px; flex: none; }
  .legend .key.wash { opacity: 0.18; }

  .hit { fill: transparent; cursor: default; }
  .hit:focus-visible { outline: 2px solid var(--text-primary); outline-offset: -2px; }

  .tooltip {
    position: fixed; z-index: 20; pointer-events: none; opacity: 0;
    transition: opacity 90ms linear;
    background: var(--surface-1); color: var(--text-primary);
    border: 1px solid var(--border); border-radius: 8px;
    padding: 9px 11px; font-size: 12.5px; min-width: 148px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.13);
  }
  .tooltip[data-show="1"] { opacity: 1; }
  .tooltip .tt-title { font-size: 11.5px; color: var(--muted); margin-bottom: 5px; }
  .tooltip .tt-row { display: flex; align-items: baseline; gap: 8px; margin-top: 3px; }
  .tooltip .tt-key { width: 12px; height: 2px; border-radius: 1px; flex: none;
                     align-self: center; }
  .tooltip .tt-val { font-weight: 600; font-variant-numeric: tabular-nums; }
  .tooltip .tt-name { color: var(--text-secondary); font-size: 12px; }

  .tables { margin-top: 20px; display: grid; gap: 14px; }
  /* display:grid would otherwise override [hidden]'s display:none */
  .tables[hidden] { display: none; }
  table { border-collapse: collapse; width: 100%; font-size: 12.5px; }
  caption { text-align: left; font-size: 13px; font-weight: 600; padding-bottom: 7px; }
  th, td { text-align: right; padding: 6px 9px; border-bottom: 1px solid var(--gridline);
           font-variant-numeric: tabular-nums; }
  th:first-child, td:first-child { text-align: left; font-variant-numeric: normal; }
  thead th { color: var(--muted); font-weight: 600; font-size: 11.5px;
             text-transform: uppercase; letter-spacing: 0.03em; }

  .footnote { font-size: 12px; color: var(--text-secondary); margin-top: 22px;
              max-width: 68ch; line-height: 1.5; }
  @media (prefers-reduced-motion: reduce) { .tooltip { transition: none; } }
</style>
</head>
<body data-palette="__PALETTE__">
<div class="viz-root"><div class="wrap">

<header>
  <div class="titles">
    <h1>Pricing analysis &mdash; <span id="hCustomer"></span></h1>
    <p class="sub">Value-based price band, policy floors, and approval position.
       Every figure is computed by the same model the deal desk runs.</p>
  </div>
  <div class="head-controls">
    <button class="btn" id="tableToggle" aria-pressed="false">Show data tables</button>
    <button class="btn" id="themeToggle">Dark mode</button>
  </div>
</header>

<div class="filters" role="group" aria-label="Deal inputs">
  <div class="field">
    <label for="fSegment">Segment</label>
    <select id="fSegment"></select>
  </div>
  <div class="field">
    <label for="fTerm">Term</label>
    <select id="fTerm"></select>
  </div>
  <div class="field">
    <label for="fSeats">Seats</label>
    <div class="rowctl">
      <input type="range" id="fSeats" min="10" max="2000" step="10">
      <span class="readout" id="rSeats"></span>
    </div>
  </div>
  <div class="field">
    <label for="fDiscount">Discount asked</label>
    <div class="rowctl">
      <input type="range" id="fDiscount" min="0" max="55" step="1">
      <span class="readout" id="rDiscount"></span>
    </div>
  </div>
  <div class="field">
    <label for="fFactor">Value estimate</label>
    <div class="rowctl">
      <input type="range" id="fFactor" min="40" max="140" step="5">
      <span class="readout" id="rFactor"></span>
    </div>
  </div>
</div>

<section class="hero-card">
  <div>
    <div class="hero-label">Recommended price</div>
    <div class="hero-figure" id="heroPrice"></div>
    <div class="hero-note" id="heroNote"></div>
  </div>
  <div id="verdictChip"></div>
</section>

<div class="kpi-row" id="kpiRow"></div>

<div class="grid">
  <figure class="card">
    <figcaption>
      <div class="c-title">Where the price sits against value and policy</div>
      <div class="c-sub" id="ladderSub"></div>
    </figcaption>
    <svg id="ladder" viewBox="0 0 760 236" role="group" aria-label="Price against value band and policy floors"></svg>
    <div class="legend" id="ladderLegend"></div>
  </figure>
</div>

<div class="grid" style="margin-top:14px">
  <figure class="card">
    <figcaption>
      <div class="c-title">Value drivers, before and after the confidence haircut</div>
      <div class="c-sub">Bar length is the gross estimate. Blue is the part defensible in front of the customer.</div>
    </figcaption>
    <svg id="drivers" viewBox="0 0 760 250" role="group" aria-label="Value drivers split into risk-adjusted value and confidence haircut"></svg>
    <div class="legend" id="driversLegend"></div>
  </figure>

  <figure class="card">
    <figcaption>
      <div class="c-title">Does the case survive a worse estimate?</div>
      <div class="c-sub">Customer ROI at the recommended price if the value estimate is off.</div>
    </figcaption>
    <svg id="sens" viewBox="0 0 760 250" role="group" aria-label="Customer ROI across value estimate scenarios"></svg>
  </figure>
</div>

<div class="tables" id="tables" hidden></div>

<p class="footnote">
  Policy constants are injected from <code>value_calculator.py</code> at build time, so
  this page cannot disagree with the Python about discount limits or floors.
  The pricing formulas are mirrored in <code>pricing_model.js</code>;
  <code>check_parity.py</code> runs both implementations over 1,440 deals and fails on
  any disagreement. Figures here are illustrative &mdash; replace the policy block
  with your own rate card before showing this to anyone.
</p>

</div></div>
<div class="tooltip" id="tip" role="status" aria-live="polite"></div>

<script type="module">
__PRICING_MODEL_JS__

const POLICY = __POLICY_JSON__;
const BASE_DEAL = __DEAL_JSON__;
const SVGNS = 'http://www.w3.org/2000/svg';

/* ---------- formatting ---------- */
const money = (n) => '$' + Math.round(n).toLocaleString('en-US');
const moneyCompact = (n) => {
  if (n >= 1e6) return '$' + (n / 1e6).toFixed(n >= 1e7 ? 0 : 1) + 'M';
  if (n >= 1000) return '$' + Math.round(n / 1000) + 'k';
  return '$' + Math.round(n);
};
const pct = (n) => n.toFixed(n < 10 ? 1 : 0) + '%';
const mult = (n) => n.toFixed(1) + '×';
const titleCase = (s) => s.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
// Rough advance width for the UI sans; used only to decide whether a label fits.
const textWidth = (s, size) => s.length * size * 0.56;

/* A label set inside a colored fill is the one place text may sit on a series
   color -- so pick white or ink by the fill's luminance, per mode, instead of
   assuming white always clears. */
const chan = (c) => (c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4));
function relLum(rgb) {
  const [r, g, b] = rgb.map((v) => chan(v / 255));
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}
function parseColor(str) {
  const s = str.trim();
  // Hex must be handled BEFORE the numeric fallback: '#2a78d6' contains digit
  // runs ('2','78','6') that a bare \d+ match happily mistakes for RGB.
  if (s.startsWith('#')) {
    let h = s.slice(1);
    if (h.length === 3) h = h.split('').map((c) => c + c).join('');
    if (h.length >= 6) return [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16));
  }
  const m = s.match(/(\d+(?:\.\d+)?)/g);
  if (m && m.length >= 3) return m.slice(0, 3).map(Number);
  return [128, 128, 128];
}
function inkOn(cssVar) {
  const root = document.querySelector('.viz-root');
  const resolved = getComputedStyle(root).getPropertyValue(cssVar.slice(4, -1)).trim();
  const L = relLum(parseColor(resolved));
  const onWhite = 1.05 / (L + 0.05);
  const onInk = (L + 0.05) / 0.05;
  return onWhite >= onInk ? '#ffffff' : '#0b0b0b';
}

/* ---------- tiny SVG helper: attributes set, text via textContent ---------- */
function el(tag, attrs, text) {
  const n = document.createElementNS(SVGNS, tag);
  if (attrs) for (const k in attrs) if (attrs[k] != null) n.setAttribute(k, attrs[k]);
  if (text != null) n.textContent = text;
  return n;
}
/* Horizontal bar: 4px rounded data-end, square at the baseline. */
function hBarPath(x, y, w, h, r = 4) {
  if (w <= 0.5) return `M${x},${y} h0`;
  const rr = Math.min(r, w, h / 2);
  return `M${x},${y} H${x + w - rr} A${rr},${rr} 0 0 1 ${x + w},${y + rr}`
       + ` V${y + h - rr} A${rr},${rr} 0 0 1 ${x + w - rr},${y + h} H${x} Z`;
}
/* Column: rounded cap, square at the baseline. */
function vBarPath(x, yTop, w, h, r = 4) {
  if (h <= 0.5) return `M${x},${yTop + h} h0`;
  const rr = Math.min(r, h, w / 2);
  return `M${x},${yTop + h} V${yTop + rr} A${rr},${rr} 0 0 1 ${x + rr},${yTop}`
       + ` H${x + w - rr} A${rr},${rr} 0 0 1 ${x + w},${yTop + rr} V${yTop + h} Z`;
}
/* Ticks that always COVER max -- a domain short of the data clips the tallest
   mark, which is how a chart silently lies. The last tick is the domain. */
function niceTicks(max, count = 4) {
  if (!(max > 0)) return [0, 1];
  const mag = Math.pow(10, Math.floor(Math.log10(max)));
  for (const m of [0.1, 0.2, 0.25, 0.5, 1, 2, 2.5, 5, 10]) {
    const step = m * mag;
    const n = Math.ceil(max / step - 1e-9);
    if (n >= 2 && n <= count + 1) {
      return Array.from({ length: n + 1 }, (_, i) => step * i);
    }
  }
  return [0, max];
}

/* ---------- tooltip ---------- */
const tip = document.getElementById('tip');
function showTip(evt, title, rows) {
  tip.textContent = '';
  const h = document.createElement('div');
  h.className = 'tt-title';
  h.textContent = title;
  tip.appendChild(h);
  for (const r of rows) {
    const line = document.createElement('div');
    line.className = 'tt-row';
    if (r.color) {
      const k = document.createElement('span');
      k.className = 'tt-key';
      k.style.background = r.color;
      line.appendChild(k);
    }
    const v = document.createElement('span');
    v.className = 'tt-val';
    v.textContent = r.value;              // values lead
    line.appendChild(v);
    const n = document.createElement('span');
    n.className = 'tt-name';
    n.textContent = r.name;               // labels follow
    line.appendChild(n);
    tip.appendChild(line);
  }
  tip.dataset.show = '1';
  place(evt);
}
function place(evt) {
  const pad = 14;
  let x, y;
  if (evt && evt.clientX != null && evt.clientX !== 0) {
    x = evt.clientX + pad; y = evt.clientY + pad;
  } else {
    const r = (evt.target.getBoundingClientRect && evt.target.getBoundingClientRect()) || { right: 0, top: 0 };
    x = r.right + pad; y = r.top;
  }
  const b = tip.getBoundingClientRect();
  if (x + b.width > window.innerWidth - 8) x = Math.max(8, x - b.width - pad * 2);
  if (y + b.height > window.innerHeight - 8) y = Math.max(8, y - b.height - pad * 2);
  tip.style.left = x + 'px';
  tip.style.top = y + 'px';
}
function hideTip() { tip.dataset.show = '0'; }

/* A hit target that covers the mark plus its gap, never only painted pixels. */
function addHit(svg, { x, y, w, h, label, title, rows, marks = [] }) {
  const hit = el('rect', {
    x, y, width: Math.max(w, 1), height: Math.max(h, 24),
    class: 'hit', tabindex: '0', role: 'img', 'aria-label': label,
  });
  // The hovered mark visibly responds, so the reader knows what they're reading.
  const lift = (on) => marks.forEach((m) => m && m.setAttribute('opacity', on ? 0.78 : 1));
  const enter = (e) => { lift(true); showTip(e, title, rows); };
  const leave = () => { lift(false); hideTip(); };
  hit.addEventListener('pointerenter', enter);
  hit.addEventListener('pointermove', place);
  hit.addEventListener('pointerleave', leave);
  hit.addEventListener('focus', enter);
  hit.addEventListener('blur', leave);
  svg.appendChild(hit);
}

function legend(node, items) {
  node.textContent = '';
  for (const it of items) {
    const w = document.createElement('span');
    w.className = 'item';
    const k = document.createElement('span');
    k.className = 'key' + (it.wash ? ' wash' : '');
    k.style.background = it.color;
    w.appendChild(k);
    const t = document.createElement('span');
    t.textContent = it.label;
    w.appendChild(t);
    node.appendChild(w);
  }
}

/* ---------- chart 1: price ladder (emphasis form) ---------- */
function drawLadder(r) {
  const svg = document.getElementById('ladder');
  svg.textContent = '';
  const W = 760, GUT = 176, PAD_R = 96, TOP = 30, ROW = 38, BAR = 20;

  const rows = [
    { name: 'Recommended', v: r.recommendedAnnual, emph: true,
      note: pct(r.recommendedDiscountPct) + ' off list' },
    { name: 'List price', v: r.listAnnual, emph: false, note: 'no discount' },
    { name: 'Approval-free floor', v: r.approvalFreePrice, emph: false,
      note: pct(r.approvalFreeDiscount * 100) + ' off list' },
    { name: 'Absolute floor', v: r.absoluteFloorPrice, emph: false, note: 'never price below' },
  ];
  const plotW = W - GUT - PAD_R;
  const maxV = Math.max(r.listAnnual, r.valueBandHigh, r.recommendedAnnual);
  const ticks = niceTicks(maxV, 4);
  const domain = ticks[ticks.length - 1];
  const sx = (v) => GUT + (v / domain) * plotW;
  const plotBottom = TOP + rows.length * ROW;

  // gridlines + x axis (solid hairlines, recessive)
  for (const t of ticks) {
    svg.appendChild(el('line', { x1: sx(t), y1: TOP - 8, x2: sx(t), y2: plotBottom,
      stroke: 'var(--gridline)', 'stroke-width': 1 }));
    svg.appendChild(el('text', { x: sx(t), y: plotBottom + 17, 'text-anchor': 'middle',
      'font-size': 11, fill: 'var(--muted)' }, moneyCompact(t)));
  }
  svg.appendChild(el('line', { x1: GUT, y1: plotBottom, x2: W - PAD_R, y2: plotBottom,
    stroke: 'var(--baseline)', 'stroke-width': 1 }));

  // value-based band: a 10% wash behind the marks
  const bw = sx(r.valueBandHigh) - sx(r.valueBandLow);
  if (bw > 0.5) {
    svg.appendChild(el('rect', { x: sx(r.valueBandLow), y: TOP - 8, width: bw,
      height: plotBottom - TOP + 8, fill: 'var(--series-1)', opacity: 0.1 }));
    const lbl = 'Value band ' + moneyCompact(r.valueBandLow) + '–' + moneyCompact(r.valueBandHigh);
    const fits = textWidth(lbl, 11) < bw - 8;
    svg.appendChild(el('text', {
      x: fits ? sx(r.valueBandLow) + bw / 2 : sx(r.valueBandHigh) + 6,
      y: TOP - 14, 'text-anchor': fits ? 'middle' : 'start',
      'font-size': 11, fill: 'var(--muted)' }, lbl));
  }

  rows.forEach((row, i) => {
    const y = TOP + i * ROW + (ROW - BAR) / 2;
    const w = sx(row.v) - GUT;
    const mark = el('path', {
      d: hBarPath(GUT, y, w, BAR),
      fill: row.emph ? 'var(--series-1)' : 'var(--deemph)',
    });
    svg.appendChild(mark);
    svg.appendChild(el('text', { x: GUT - 12, y: y + BAR / 2 + 4, 'text-anchor': 'end',
      'font-size': 12, fill: row.emph ? 'var(--text-primary)' : 'var(--text-secondary)',
      'font-weight': row.emph ? 600 : 400 }, row.name));
    // value at the tip, outside the bar
    svg.appendChild(el('text', { x: GUT + w + 8, y: y + BAR / 2 + 4, 'text-anchor': 'start',
      'font-size': 12, fill: 'var(--text-primary)',
      'font-weight': row.emph ? 600 : 400 }, moneyCompact(row.v)));
    addHit(svg, {
      x: GUT, y: TOP + i * ROW, w: Math.max(w, 2), h: ROW,
      label: row.name + ': ' + money(row.v) + ' per year, ' + row.note,
      title: row.name,
      marks: [mark],
      rows: [
        { value: money(row.v), name: 'per year',
          color: row.emph ? 'var(--series-1)' : 'var(--deemph)' },
        { value: row.note, name: '' },
      ],
    });
  });

  legend(document.getElementById('ladderLegend'), [
    { color: 'var(--series-1)', label: 'Recommended price' },
    { color: 'var(--deemph)', label: 'Policy reference' },
    { color: 'var(--series-1)', label: 'Value-based band', wash: true },
  ]);

  const binding = r.recommendedAnnual > r.valueBandHigh + 0.5
    ? 'The rate-card floor is setting this price, not the value case.'
    : r.recommendedAnnual >= r.listAnnual - 0.5
      ? 'Value supports list price; the cap is the rate card.'
      : 'The value band is setting this price.';
  document.getElementById('ladderSub').textContent = binding;
}

/* ---------- chart 2: value drivers (stacked, 2 series) ---------- */
function drawDrivers(r) {
  const svg = document.getElementById('drivers');
  svg.textContent = '';
  const W = 760, GUT = 188, PAD_R = 92, TOP = 14, ROW = 40, BAR = 20, GAP = 2;

  const rows = r.drivers.slice().sort((a, b) => b.annualValue - a.annualValue);
  const plotW = W - GUT - PAD_R;
  const ticks = niceTicks(Math.max(...rows.map((d) => d.annualValue), 1), 4);
  const domain = ticks[ticks.length - 1];
  const sx = (v) => (v / domain) * plotW;
  const plotBottom = TOP + rows.length * ROW;
  svg.setAttribute('viewBox', `0 0 ${W} ${plotBottom + 30}`);

  for (const t of ticks) {
    svg.appendChild(el('line', { x1: GUT + sx(t), y1: TOP, x2: GUT + sx(t), y2: plotBottom,
      stroke: 'var(--gridline)', 'stroke-width': 1 }));
    svg.appendChild(el('text', { x: GUT + sx(t), y: plotBottom + 17, 'text-anchor': 'middle',
      'font-size': 11, fill: 'var(--muted)' }, moneyCompact(t)));
  }
  svg.appendChild(el('line', { x1: GUT, y1: plotBottom, x2: W - PAD_R, y2: plotBottom,
    stroke: 'var(--baseline)', 'stroke-width': 1 }));

  rows.forEach((d, i) => {
    const y = TOP + i * ROW + (ROW - BAR) / 2;
    const wAdj = sx(d.riskAdjusted);
    const haircut = d.annualValue - d.riskAdjusted;
    const wCut = sx(haircut);
    const hasCut = wCut > 0.5;

    // Blue segment: square end when a haircut follows it, rounded when it is the end.
    const mAdj = el('path', {
      d: hasCut
        ? `M${GUT},${y} h${Math.max(wAdj, 0)} v${BAR} h${-Math.max(wAdj, 0)} Z`
        : hBarPath(GUT, y, wAdj, BAR),
      fill: 'var(--series-1)',
    });
    svg.appendChild(mAdj);
    let mCut = null;
    if (hasCut) {
      // 2px surface gap does the separating -- no stroke around the marks.
      mCut = el('path', {
        d: hBarPath(GUT + wAdj + GAP, y, Math.max(wCut - GAP, 0.6), BAR),
        fill: 'var(--deemph)',
      });
      svg.appendChild(mCut);
    }

    svg.appendChild(el('text', { x: GUT - 12, y: y + BAR / 2 + 4, 'text-anchor': 'end',
      'font-size': 12, fill: 'var(--text-secondary)' }, d.name));

    // Label inside the blue fill only when it actually fits with padding.
    const inLabel = moneyCompact(d.riskAdjusted);
    if (textWidth(inLabel, 11) + 16 < wAdj) {
      svg.appendChild(el('text', { x: GUT + wAdj - 8, y: y + BAR / 2 + 4, 'text-anchor': 'end',
        'font-size': 11, fill: inkOn('var(--series-1)'), 'font-weight': 600 }, inLabel));
    }
    svg.appendChild(el('text', { x: GUT + sx(d.annualValue) + 8, y: y + BAR / 2 + 4,
      'text-anchor': 'start', 'font-size': 11, fill: 'var(--muted)' },
      Math.round(d.confidence * 100) + '% conf'));

    addHit(svg, {
      x: GUT, y: TOP + i * ROW, w: Math.max(sx(d.annualValue), 2), h: ROW,
      label: `${d.name}: ${money(d.annualValue)} gross, ${money(d.riskAdjusted)} risk-adjusted at ${Math.round(d.confidence * 100)}% confidence`,
      title: d.name,
      marks: [mAdj, mCut],
      rows: [
        { value: money(d.riskAdjusted), name: 'risk-adjusted', color: 'var(--series-1)' },
        { value: money(haircut), name: 'confidence haircut', color: 'var(--deemph)' },
        { value: money(d.annualValue), name: 'gross estimate' },
      ],
    });
  });

  legend(document.getElementById('driversLegend'), [
    { color: 'var(--series-1)', label: 'Risk-adjusted value' },
    { color: 'var(--deemph)', label: 'Confidence haircut' },
  ]);
}

/* ---------- chart 3: sensitivity (ordinal ramp) ---------- */
function drawSensitivity(r) {
  const svg = document.getElementById('sens');
  svg.textContent = '';
  const W = 760, H = 250, GUT = 118, PAD_R = 24, TOP = 22, BOTTOM = 46;
  const plotW = W - GUT - PAD_R, plotH = H - TOP - BOTTOM;
  const rows = r.sensitivity;
  const ramp = ['var(--ord-1)', 'var(--ord-2)', 'var(--ord-3)', 'var(--ord-4)'];

  const ticks = niceTicks(Math.max(...rows.map((s) => s.roiMultiple), 1.2), 4);
  const domain = ticks[ticks.length - 1];
  const sy = (v) => TOP + plotH - (v / domain) * plotH;
  const isBreakeven = (t) => Math.abs(t - 1) < 1e-9;

  for (const t of ticks) {
    svg.appendChild(el('line', { x1: GUT, y1: sy(t), x2: W - PAD_R, y2: sy(t),
      // the breakeven line is the one reference that isn't just a grid
      stroke: isBreakeven(t) ? 'var(--baseline)' : 'var(--gridline)', 'stroke-width': 1 }));
    // Label the reference on the AXIS, not inside the plot -- an in-plot
    // annotation collides with the tallest column exactly when it matters.
    svg.appendChild(el('text', { x: GUT - 10, y: sy(t) + 4, 'text-anchor': 'end',
      'font-size': 11, fill: 'var(--muted)' },
      isBreakeven(t) ? '1.0× breakeven' : mult(t)));
  }
  svg.appendChild(el('line', { x1: GUT, y1: TOP + plotH, x2: W - PAD_R, y2: TOP + plotH,
    stroke: 'var(--baseline)', 'stroke-width': 1 }));

  const band = plotW / rows.length;
  const BARW = Math.min(24, band * 0.42);
  rows.forEach((s, i) => {
    const cx = GUT + band * (i + 0.5);
    const x = cx - BARW / 2;
    const h = Math.max((s.roiMultiple / domain) * plotH, 0);
    const mark = el('path', { d: vBarPath(x, TOP + plotH - h, BARW, h), fill: ramp[i] });
    svg.appendChild(mark);
    svg.appendChild(el('text', { x: cx, y: TOP + plotH + 18, 'text-anchor': 'middle',
      'font-size': 11.5, fill: 'var(--text-secondary)' }, s.label));
    // Label the base case and the worst case only -- never every column.
    if (s.factor === 1.0 || i === 0) {
      svg.appendChild(el('text', { x: cx, y: TOP + plotH - h - 8, 'text-anchor': 'middle',
        'font-size': 12, fill: 'var(--text-primary)', 'font-weight': 600 },
        mult(s.roiMultiple)));
    }
    addHit(svg, {
      x: cx - band / 2, y: TOP, w: band, h: plotH,
      label: `${s.label}: value ${money(s.annualValue)}, price ${money(s.recommendedAnnual)}, ROI ${mult(s.roiMultiple)}`,
      title: s.label,
      marks: [mark],
      rows: [
        { value: mult(s.roiMultiple), name: 'customer ROI', color: ramp[i] },
        { value: money(s.annualValue), name: 'annual value' },
        { value: money(s.recommendedAnnual), name: 'price' },
      ],
    });
  });
}

/* ---------- figures ---------- */
function drawFigures(r, deal) {
  document.getElementById('hCustomer').textContent = deal.customer;
  document.getElementById('heroPrice').textContent = money(r.recommendedAnnual);
  document.getElementById('heroNote').textContent =
    `per year · ${pct(r.recommendedDiscountPct)} off list · `
    + `${money(r.recommendedTotalContract)} total over ${deal.termMonths} months`;

  const v = r.proposed ? r.proposed.verdict : null;
  const chip = document.getElementById('verdictChip');
  chip.textContent = '';
  if (v) {
    const cls = v === 'auto-approvable' ? 'good'
      : v.startsWith('reject') ? 'critical' : 'warning';
    const glyphs = { good: '✓', warning: '▲', critical: '✕' };
    const labels = {
      good: 'Auto-approvable',
      warning: 'Escalate to deal desk',
      critical: 'Reject — below absolute floor',
    };
    const box = document.createElement('span');
    box.className = 'chip ' + cls;
    const g = document.createElement('span');
    g.className = 'glyph';
    g.textContent = glyphs[cls];            // icon + label: never colour alone
    box.appendChild(g);
    const t = document.createElement('span');
    t.textContent = `${pct(r.proposed.discountPct)} ask — ${labels[cls]}`;
    box.appendChild(t);
    chip.appendChild(box);
  }

  const tiles = [
    { label: 'Risk-adjusted annual value', value: money(r.annualValue),
      note: money(r.confidenceHaircut) + ' removed by confidence haircut' },
    { label: 'Customer ROI', value: mult(r.roiMultiple),
      note: money(r.netAnnualGain) + ' net annual gain' },
    { label: 'Payback', value: r.paybackMonths == null ? '—' : r.paybackMonths.toFixed(1) + ' mo',
      note: r.paybackMonths == null ? 'no quantified value' : 'to recover the annual fee' },
    { label: 'Share of value captured',
      value: r.captureShareOfValuePct == null ? '—' : pct(r.captureShareOfValuePct),
      note: 'target band ' + pct(POLICY.valueCaptureBand[0] * 100) + '–' + pct(POLICY.valueCaptureBand[1] * 100) },
  ];
  const row = document.getElementById('kpiRow');
  row.textContent = '';
  for (const t of tiles) {
    const d = document.createElement('div');
    d.className = 'tile';
    const a = document.createElement('div'); a.className = 't-label'; a.textContent = t.label;
    const b = document.createElement('div'); b.className = 't-value'; b.textContent = t.value;
    const c = document.createElement('div'); c.className = 't-note'; c.textContent = t.note;
    d.append(a, b, c);
    row.appendChild(d);
  }
}

/* ---------- table view (the WCAG-clean twin of every chart) ---------- */
function drawTables(r) {
  const host = document.getElementById('tables');
  host.textContent = '';
  const table = (caption, head, body) => {
    const t = document.createElement('table');
    const cap = document.createElement('caption'); cap.textContent = caption;
    t.appendChild(cap);
    const thead = document.createElement('thead');
    const hr = document.createElement('tr');
    for (const h of head) { const th = document.createElement('th'); th.textContent = h; hr.appendChild(th); }
    thead.appendChild(hr); t.appendChild(thead);
    const tb = document.createElement('tbody');
    for (const row of body) {
      const tr = document.createElement('tr');
      for (const cell of row) { const td = document.createElement('td'); td.textContent = cell; tr.appendChild(td); }
      tb.appendChild(tr);
    }
    t.appendChild(tb);
    const card = document.createElement('figure');
    card.className = 'card';
    card.appendChild(t);
    host.appendChild(card);
  };

  table('Price against value and policy', ['Reference', 'Annual', 'Off list'], [
    ['Recommended', money(r.recommendedAnnual), pct(r.recommendedDiscountPct)],
    ['List price', money(r.listAnnual), '0%'],
    ['Value band low', money(r.valueBandLow), '—'],
    ['Value band high', money(r.valueBandHigh), '—'],
    ['Approval-free floor', money(r.approvalFreePrice), pct(r.approvalFreeDiscount * 100)],
    ['Absolute floor', money(r.absoluteFloorPrice), pct((1 - POLICY.absoluteFloorShareOfList) * 100)],
  ]);

  table('Value drivers', ['Driver', 'Gross', 'Confidence', 'Risk-adjusted', 'Haircut'],
    r.drivers.slice().sort((a, b) => b.annualValue - a.annualValue).map((d) => [
      d.name, money(d.annualValue), Math.round(d.confidence * 100) + '%',
      money(d.riskAdjusted), money(d.annualValue - d.riskAdjusted),
    ]));

  table('Sensitivity', ['Scenario', 'Annual value', 'Price', 'ROI', 'Above floor'],
    r.sensitivity.map((s) => [
      s.label, money(s.annualValue), money(s.recommendedAnnual),
      mult(s.roiMultiple), s.stillAboveFloor ? 'yes' : 'no',
    ]));
}

/* ---------- state ---------- */
const ui = {
  segment: document.getElementById('fSegment'),
  term: document.getElementById('fTerm'),
  seats: document.getElementById('fSeats'),
  discount: document.getElementById('fDiscount'),
  factor: document.getElementById('fFactor'),
};

for (const s of Object.keys(POLICY.segmentDiscountLimit)) {
  ui.segment.appendChild(new Option(titleCase(s), s));
}
for (const t of Object.keys(POLICY.termDiscountHeadroom).sort((a, b) => a - b)) {
  ui.term.appendChild(new Option(t + ' months', t));
}
ui.segment.value = BASE_DEAL.segment;
ui.term.value = String(BASE_DEAL.termMonths);
ui.seats.value = BASE_DEAL.seats;
ui.discount.value = Math.round((BASE_DEAL.proposedDiscount ?? 0) * 100);
ui.factor.value = 100;

function currentDeal() {
  const factor = Number(ui.factor.value) / 100;
  return {
    customer: BASE_DEAL.customer,
    segment: ui.segment.value,
    seats: Number(ui.seats.value),
    termMonths: Number(ui.term.value),
    proposedDiscount: Number(ui.discount.value) / 100,
    drivers: BASE_DEAL.drivers.map((d) => ({
      name: d.name,
      annualValue: d.annualValue * factor,   // matches the Python sensitivity semantics
      confidence: d.confidence,
      basis: d.basis,
    })),
  };
}

function render() {
  document.getElementById('rSeats').textContent = Number(ui.seats.value).toLocaleString('en-US');
  document.getElementById('rDiscount').textContent = ui.discount.value + '%';
  document.getElementById('rFactor').textContent = ui.factor.value + '%';

  const deal = currentDeal();
  const r = priceDeal(deal, POLICY);
  if (!r.ok) { console.warn('not priceable', r.problems); return; }
  drawFigures(r, deal);
  drawLadder(r);
  drawDrivers(r);
  drawSensitivity(r);
  drawTables(r);
}

for (const c of Object.values(ui)) c.addEventListener('input', render);

const tableBtn = document.getElementById('tableToggle');
tableBtn.addEventListener('click', () => {
  const open = tableBtn.getAttribute('aria-pressed') === 'true';
  tableBtn.setAttribute('aria-pressed', String(!open));
  tableBtn.textContent = open ? 'Show data tables' : 'Hide data tables';
  document.getElementById('tables').hidden = open;
});

const themeBtn = document.getElementById('themeToggle');
themeBtn.addEventListener('click', () => {
  const dark = document.documentElement.dataset.theme === 'dark'
    || (!document.documentElement.dataset.theme
        && window.matchMedia('(prefers-color-scheme: dark)').matches);
  document.documentElement.dataset.theme = dark ? 'light' : 'dark';
  themeBtn.textContent = dark ? 'Dark mode' : 'Light mode';
});

render();
</script>
</body>
</html>
"""


def main() -> None:
    model_js = (HERE / "pricing_model.js").read_text()
    # Inline the module: strip `export` so it becomes plain in-scope code.
    model_inline = model_js.replace("\nexport function", "\nfunction")

    html = (
        TEMPLATE.replace("__PRICING_MODEL_JS__", model_inline)
        .replace("__POLICY_JSON__", json.dumps(POLICY, indent=2))
        .replace("__DEAL_JSON__", json.dumps(DEAL, indent=2))
        .replace("__CUSTOMER__", DEAL["customer"])
        .replace("__PALETTE__", PALETTE)
    )
    out = HERE / "dashboard.html"
    out.write_text(html)
    print(f"wrote {out} ({len(html):,} bytes)")
    print("open it directly in a browser -- no server, no dependencies")


if __name__ == "__main__":
    main()
