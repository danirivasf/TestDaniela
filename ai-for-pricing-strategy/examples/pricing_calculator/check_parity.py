"""Parity check: does pricing_model.js agree with value_calculator.py?

The dashboard needs the pricing math in JavaScript so it can recompute as
sliders move. Two implementations of the same policy is a drift risk -- the
kind that surfaces as "the dashboard said 22% was fine but the deal desk
said escalate". This script closes it.

It runs a grid of deals through both implementations and fails on any
disagreement in price or, more importantly, in approval verdict.

    python3 check_parity.py

Requires node on PATH. If node is unavailable the check skips with a warning
rather than failing -- but then you are trusting the JS untested, so don't
ship a policy change without running this somewhere that has node.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import value_calculator as vc

HERE = Path(__file__).parent

# Exported so build_dashboard.py injects the same constants into the page --
# the JS never hardcodes policy.
POLICY = {
    "listPricePerSeatYear": vc.LIST_PRICE_PER_SEAT_YEAR,
    "segmentDiscountLimit": vc.SEGMENT_DISCOUNT_LIMIT,
    "termDiscountHeadroom": {str(k): v for k, v in vc.TERM_DISCOUNT_HEADROOM.items()},
    "absoluteFloorShareOfList": vc.ABSOLUTE_FLOOR_SHARE_OF_LIST,
    "valueCaptureBand": list(vc.VALUE_CAPTURE_BAND),
}

DRIVER_SETS = [
    [("single driver", 500_000, 1.0)],
    [("high conf", 420_000, 0.9), ("low conf", 300_000, 0.3)],
    [("tiny", 1_000, 1.0)],
    [("huge", 8_000_000, 1.0)],
    [("a", 120_000, 0.5), ("b", 90_000, 0.75), ("c", 60_000, 1.0)],
]


def build_cases() -> list[dict]:
    cases = []
    for segment in vc.SEGMENT_DISCOUNT_LIMIT:
        for term in vc.TERM_DISCOUNT_HEADROOM:
            for seats in (10, 100, 250, 2_000):
                for discount in (None, 0.0, 0.15, 0.20, 0.25, 0.30, 0.45, 0.55):
                    for i, drivers in enumerate(DRIVER_SETS):
                        cases.append(
                            {
                                "segment": segment,
                                "termMonths": term,
                                "seats": seats,
                                "proposedDiscount": discount,
                                "driverSet": i,
                                "drivers": [
                                    {"name": n, "annualValue": v, "confidence": c}
                                    for n, v, c in drivers
                                ],
                            }
                        )
    return cases


def run_python(cases: list[dict]) -> list[dict]:
    out = []
    for c in cases:
        deal = vc.Deal(
            customer="parity",
            segment=c["segment"],
            seats=c["seats"],
            term_months=c["termMonths"],
            proposed_discount=c["proposedDiscount"],
            drivers=[
                vc.ValueDriver(d["name"], d["annualValue"], d["confidence"])
                for d in c["drivers"]
            ],
        )
        r = vc.price_deal(deal)
        out.append(
            {
                "recommended": r["price"]["recommended_annual_raw"],
                "verdict": r["proposed"]["verdict"] if r["proposed"] else None,
                "roi": r["customer_economics"]["roi_multiple"],
                "value": r["value"]["risk_adjusted_annual_raw"],
            }
        )
    return out


JS_HARNESS = """
import { priceDeal } from './pricing_model.js';
import { readFileSync } from 'node:fs';
const { policy, cases } = JSON.parse(readFileSync(process.argv[2], 'utf8'));
const out = cases.map((c) => {
  const r = priceDeal(
    { segment: c.segment, seats: c.seats, termMonths: c.termMonths,
      proposedDiscount: c.proposedDiscount, drivers: c.drivers },
    policy,
  );
  if (!r.ok) return { error: r.problems };
  return {
    recommended: r.recommendedAnnual,
    verdict: r.proposed ? r.proposed.verdict : null,
    roi: r.roiMultiple,
    value: r.annualValue,
  };
});
process.stdout.write(JSON.stringify(out));
"""


def run_node(cases: list[dict]) -> list[dict]:
    with tempfile.TemporaryDirectory() as td:
        payload = Path(td) / "payload.json"
        payload.write_text(json.dumps({"policy": POLICY, "cases": cases}))
        harness = HERE / "_parity_harness.mjs"
        harness.write_text(JS_HARNESS)
        try:
            proc = subprocess.run(
                ["node", str(harness), str(payload)],
                capture_output=True,
                text=True,
                check=True,
                cwd=HERE,
            )
        finally:
            harness.unlink(missing_ok=True)
    return json.loads(proc.stdout)


def main() -> int:
    if not shutil.which("node"):
        print("SKIP: node not on PATH; cannot verify pricing_model.js against Python")
        return 0

    cases = build_cases()
    py = run_python(cases)
    js = run_node(cases)

    if len(py) != len(js):
        print(f"FAIL: case count mismatch (python {len(py)}, node {len(js)})")
        return 1

    failures = []
    for c, p, j in zip(cases, py, js):
        where = (
            f"{c['segment']}/{c['termMonths']}mo/{c['seats']}seats/"
            f"discount={c['proposedDiscount']}/drivers={c['driverSet']}"
        )
        if "error" in j:
            failures.append(f"{where}: node reported problems {j['error']}")
            continue
        # Verdict drift is the one that costs margin -- check it first.
        if p["verdict"] != j["verdict"]:
            failures.append(f"{where}: verdict {p['verdict']!r} vs {j['verdict']!r}")
        if abs(p["recommended"] - j["recommended"]) > 0.01:
            failures.append(
                f"{where}: recommended {p['recommended']} vs {j['recommended']}"
            )
        if abs(p["value"] - j["value"]) > 0.01:
            failures.append(f"{where}: value {p['value']} vs {j['value']}")
        if abs(p["roi"] - round(j["roi"], 1)) > 0.051:
            failures.append(f"{where}: roi {p['roi']} vs {round(j['roi'], 1)}")

    print(f"compared {len(cases)} deals across both implementations")
    if failures:
        print(f"\n{len(failures)} DISAGREEMENTS:")
        for f in failures[:20]:
            print(f"  {f}")
        if len(failures) > 20:
            print(f"  ... and {len(failures) - 20} more")
        return 1
    print("python and javascript agree on every case")
    return 0


if __name__ == "__main__":
    sys.exit(main())
