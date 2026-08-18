"""Value-based pricing calculator.

The deterministic half of Blueprint 1. Every number a customer or an approver
will see is computed here, in plain Python, so it can be tested and audited.
The language model never does arithmetic -- it only narrates the output of this
module (see prompts/narrative.md).

Run the worked example:
    python value_calculator.py
    python value_calculator.py --json
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Commercial policy. Replace these with your real rate card and floors -- this
# is the one block you are expected to edit, and keeping it at the top means
# a policy change is a one-line diff rather than an archaeology exercise.
# ---------------------------------------------------------------------------

LIST_PRICE_PER_SEAT_YEAR = 1_200.00

# Maximum discount off list that does not require deal-desk approval.
SEGMENT_DISCOUNT_LIMIT = {
    "smb": 0.15,
    "mid_market": 0.20,
    "enterprise": 0.25,
}

# Additional discount headroom granted for longer commitments.
TERM_DISCOUNT_HEADROOM = {12: 0.00, 24: 0.05, 36: 0.10}

# Hard floor: no deal may be priced below this share of list, at any approval
# level. Distinct from the limits above, which only trigger an approval.
ABSOLUTE_FLOOR_SHARE_OF_LIST = 0.50

# Share of the value we create that we attempt to capture as price. The band,
# not a point estimate -- a single number here invites false precision.
VALUE_CAPTURE_BAND = (0.10, 0.25)


@dataclass
class ValueDriver:
    """One quantified source of customer value, with an honesty discount.

    confidence expresses how defensible the estimate is in front of the
    customer: 1.0 for a figure they gave us from their own systems, ~0.5 for a
    benchmark, lower for something we inferred. Low-confidence value is still
    worth naming in the narrative, but it should not drive the price.
    """

    name: str
    annual_value: float
    confidence: float = 1.0
    basis: str = ""

    def risk_adjusted(self) -> float:
        return self.annual_value * self.confidence


@dataclass
class Deal:
    customer: str
    segment: str
    seats: int
    term_months: int
    proposed_discount: float | None = None  # e.g. 0.18 for an 18% ask
    drivers: list[ValueDriver] = field(default_factory=list)

    def validate(self) -> list[str]:
        """Return a list of problems. Empty list means the deal is computable.

        Returned as data rather than raised, so a calling agent can read the
        problems and ask the user for the missing input instead of crashing.
        """
        problems = []
        if self.segment not in SEGMENT_DISCOUNT_LIMIT:
            problems.append(
                f"unknown segment {self.segment!r}; "
                f"expected one of {sorted(SEGMENT_DISCOUNT_LIMIT)}"
            )
        if self.term_months not in TERM_DISCOUNT_HEADROOM:
            problems.append(
                f"unsupported term {self.term_months}; "
                f"expected one of {sorted(TERM_DISCOUNT_HEADROOM)}"
            )
        if self.seats <= 0:
            problems.append("seats must be a positive integer")
        if not self.drivers:
            problems.append("no value drivers supplied; cannot compute value-based price")
        for d in self.drivers:
            if not 0.0 <= d.confidence <= 1.0:
                problems.append(f"driver {d.name!r}: confidence must be between 0 and 1")
            if d.annual_value < 0:
                problems.append(f"driver {d.name!r}: annual_value must not be negative")
        if self.proposed_discount is not None and not 0.0 <= self.proposed_discount < 1.0:
            problems.append("proposed_discount must be between 0 and 1")
        return problems


def _money(x: float) -> str:
    """Pre-format currency so the narrating model reproduces, never recomputes."""
    return f"${x:,.0f}"


def price_deal(deal: Deal) -> dict:
    """Compute the full pricing picture for a deal.

    Returns a plain dict: JSON-serialisable, safe to hand to a prompt, and
    shaped so that every figure the narrative needs is already a string.
    """
    problems = deal.validate()
    if problems:
        return {"ok": False, "problems": problems}

    years = deal.term_months / 12

    # --- Value ------------------------------------------------------------
    gross_annual_value = sum(d.annual_value for d in deal.drivers)
    annual_value = sum(d.risk_adjusted() for d in deal.drivers)

    capture_low, capture_high = VALUE_CAPTURE_BAND
    value_band_low = annual_value * capture_low
    value_band_high = annual_value * capture_high

    # --- Policy boundaries ------------------------------------------------
    list_annual = deal.seats * LIST_PRICE_PER_SEAT_YEAR
    approval_free_discount = min(
        SEGMENT_DISCOUNT_LIMIT[deal.segment] + TERM_DISCOUNT_HEADROOM[deal.term_months],
        1.0 - ABSOLUTE_FLOOR_SHARE_OF_LIST,
    )
    approval_free_price = list_annual * (1 - approval_free_discount)
    absolute_floor_price = list_annual * ABSOLUTE_FLOOR_SHARE_OF_LIST

    # --- Recommendation ---------------------------------------------------
    # Anchor on the value band, then constrain to the rate card. A value band
    # above list is a packaging/upsell signal, not licence to exceed list.
    midpoint = (value_band_low + value_band_high) / 2
    recommended_annual = min(max(midpoint, approval_free_price), list_annual)
    recommended_discount = 1 - (recommended_annual / list_annual)

    # --- The ask, if there is one ----------------------------------------
    proposed: dict | None = None
    if deal.proposed_discount is not None:
        proposed_annual = list_annual * (1 - deal.proposed_discount)
        below_absolute_floor = proposed_annual < absolute_floor_price - 0.005
        proposed = {
            "discount_pct": round(deal.proposed_discount * 100, 1),
            "annual_price": _money(proposed_annual),
            "annual_price_raw": round(proposed_annual, 2),
            "within_approval_free_range": deal.proposed_discount <= approval_free_discount + 1e-9,
            "below_absolute_floor": below_absolute_floor,
            "verdict": (
                "reject -- below absolute floor"
                if below_absolute_floor
                else "auto-approvable"
                if deal.proposed_discount <= approval_free_discount + 1e-9
                else "escalate to deal desk"
            ),
        }

    # --- Customer economics, at the recommended price ---------------------
    roi_multiple = annual_value / recommended_annual if recommended_annual else 0.0
    # None rather than float('inf'): json.dumps would emit bare `Infinity`,
    # which is not valid JSON and breaks anything downstream that parses it.
    payback_months = (
        round(recommended_annual / (annual_value / 12), 1) if annual_value > 0 else None
    )

    return {
        "ok": True,
        "customer": deal.customer,
        "segment": deal.segment,
        "seats": deal.seats,
        "term_months": deal.term_months,
        "value": {
            "gross_annual": _money(gross_annual_value),
            "risk_adjusted_annual": _money(annual_value),
            "risk_adjusted_annual_raw": round(annual_value, 2),
            "confidence_haircut": _money(gross_annual_value - annual_value),
            "drivers": [
                {
                    "name": d.name,
                    "annual_value": _money(d.annual_value),
                    "confidence": d.confidence,
                    "risk_adjusted": _money(d.risk_adjusted()),
                    "basis": d.basis,
                }
                for d in deal.drivers
            ],
        },
        "price": {
            "list_annual": _money(list_annual),
            "value_band_annual": f"{_money(value_band_low)} - {_money(value_band_high)}",
            "approval_free_floor_annual": _money(approval_free_price),
            "absolute_floor_annual": _money(absolute_floor_price),
            "recommended_annual": _money(recommended_annual),
            "recommended_annual_raw": round(recommended_annual, 2),
            "recommended_discount_pct": round(recommended_discount * 100, 1),
            "recommended_total_contract": _money(recommended_annual * years),
            "capture_share_of_value_pct": (
                round(recommended_annual / annual_value * 100, 1) if annual_value else None
            ),
        },
        "customer_economics": {
            "roi_multiple": round(roi_multiple, 1),
            "payback_months": payback_months,
            "net_annual_gain": _money(annual_value - recommended_annual),
        },
        "proposed": proposed,
        "sensitivity": sensitivity_table(deal),
        "assumptions_to_validate": [
            f"{d.name}: {_money(d.annual_value)}/yr"
            + (f" -- {d.basis}" if d.basis else "")
            + (f" (confidence {d.confidence:.0%})" if d.confidence < 1.0 else "")
            for d in deal.drivers
        ],
    }


def sensitivity_table(deal: Deal, factors=(0.6, 0.8, 1.0, 1.2)) -> list[dict]:
    """How the picture moves if the value estimate is wrong.

    The most common objection to a value-based price is 'your assumptions are
    optimistic'. Bring the answer to that objection to the meeting.
    """
    base_value = sum(d.risk_adjusted() for d in deal.drivers)
    list_annual = deal.seats * LIST_PRICE_PER_SEAT_YEAR
    approval_free_discount = min(
        SEGMENT_DISCOUNT_LIMIT[deal.segment] + TERM_DISCOUNT_HEADROOM[deal.term_months],
        1.0 - ABSOLUTE_FLOOR_SHARE_OF_LIST,
    )
    approval_free_price = list_annual * (1 - approval_free_discount)
    low, high = VALUE_CAPTURE_BAND

    rows = []
    for f in factors:
        value = base_value * f
        midpoint = value * (low + high) / 2
        price = min(max(midpoint, approval_free_price), list_annual)
        rows.append(
            {
                "value_scenario": f"{f:.0%} of estimate",
                "annual_value": _money(value),
                "recommended_annual": _money(price),
                "roi_multiple": round(value / price, 1) if price else 0.0,
                "still_above_floor": price >= approval_free_price - 0.005,
            }
        )
    return rows


def to_markdown(result: dict) -> str:
    """A one-page internal summary. Rendered from code, not written by a model."""
    if not result["ok"]:
        return "## Cannot price this deal\n\n" + "\n".join(
            f"- {p}" for p in result["problems"]
        )

    v, p, e = result["value"], result["price"], result["customer_economics"]
    lines = [
        f"# Pricing summary -- {result['customer']}",
        "",
        f"**Segment:** {result['segment']} · **Seats:** {result['seats']} · "
        f"**Term:** {result['term_months']} months",
        "",
        "## Value",
        f"- Gross annual value identified: **{v['gross_annual']}**",
        f"- Risk-adjusted annual value: **{v['risk_adjusted_annual']}** "
        f"(confidence haircut {v['confidence_haircut']})",
        "",
        "| Driver | Annual value | Confidence | Risk-adjusted |",
        "|---|---|---|---|",
    ]
    for d in v["drivers"]:
        lines.append(
            f"| {d['name']} | {d['annual_value']} | {d['confidence']:.0%} | {d['risk_adjusted']} |"
        )

    lines += [
        "",
        "## Price",
        f"- List (annual): {p['list_annual']}",
        f"- Value-based band: {p['value_band_annual']}",
        f"- **Recommended: {p['recommended_annual']}/yr "
        f"({p['recommended_discount_pct']}% off list)**",
        f"- Total contract value: {p['recommended_total_contract']}",
        f"- Approval-free floor: {p['approval_free_floor_annual']} · "
        f"Absolute floor: {p['absolute_floor_annual']}",
        f"- Capturing {p['capture_share_of_value_pct']}% of risk-adjusted value",
        "",
        "## Customer economics at recommended price",
        f"- ROI: **{e['roi_multiple']}x** · Payback: **{e['payback_months']} months** · "
        f"Net annual gain: {e['net_annual_gain']}",
    ]

    if result["proposed"]:
        pr = result["proposed"]
        lines += [
            "",
            "## Proposed discount",
            f"- Ask: {pr['discount_pct']}% off list -> {pr['annual_price']}/yr",
            f"- **Verdict: {pr['verdict']}**",
        ]

    lines += ["", "## Sensitivity", "", "| Scenario | Annual value | Price | ROI | Above floor |", "|---|---|---|---|---|"]
    for r in result["sensitivity"]:
        lines.append(
            f"| {r['value_scenario']} | {r['annual_value']} | {r['recommended_annual']} "
            f"| {r['roi_multiple']}x | {'yes' if r['still_above_floor'] else 'NO'} |"
        )

    lines += ["", "## Assumptions to validate with the customer"]
    lines += [f"- {a}" for a in result["assumptions_to_validate"]]
    return "\n".join(lines)


EXAMPLE_DEAL = Deal(
    customer="Northwind Logistics",
    segment="mid_market",
    seats=250,
    term_months=36,
    proposed_discount=0.28,
    drivers=[
        ValueDriver(
            name="Analyst time recovered",
            annual_value=420_000,
            confidence=0.9,
            basis="14 analysts x 6 hrs/week saved x fully-loaded rate, from their own time study",
        ),
        ValueDriver(
            name="Reduced billing error rework",
            annual_value=180_000,
            confidence=0.6,
            basis="error rate 2.1% -> 0.4%, benchmark from three comparable accounts",
        ),
        ValueDriver(
            name="Retired legacy tooling",
            annual_value=95_000,
            confidence=1.0,
            basis="contract value of the two tools this replaces, confirmed in writing",
        ),
        ValueDriver(
            name="Faster quote turnaround -> win-rate uplift",
            annual_value=300_000,
            confidence=0.3,
            basis="inferred; not defensible without their win-rate data",
        ),
    ],
)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true", help="emit JSON for the narrative prompt")
    args = ap.parse_args()

    result = price_deal(EXAMPLE_DEAL)
    print(json.dumps(result, indent=2) if args.json else to_markdown(result))


if __name__ == "__main__":
    main()
