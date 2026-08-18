"""The eval set. This is the file that makes the calculator trustworthy.

Twenty-odd cases covering the edges, run on every change to the pricing policy
or the code. No test framework needed:

    python eval_cases.py

The cases that matter most are the ones whose correct answer is "escalate" or
"refuse" -- those are where an automation quietly costs margin.
"""

from __future__ import annotations

from value_calculator import (
    Deal,
    ValueDriver,
    price_deal,
    LIST_PRICE_PER_SEAT_YEAR,
    ABSOLUTE_FLOOR_SHARE_OF_LIST,
)

failures: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"  pass  {name}")
    else:
        print(f"  FAIL  {name}" + (f" -- {detail}" if detail else ""))
        failures.append(name)


def deal(**kw) -> Deal:
    base = dict(
        customer="Test Co",
        segment="mid_market",
        seats=100,
        term_months=12,
        drivers=[ValueDriver("value", 500_000, 1.0)],
    )
    base.update(kw)
    return Deal(**base)


print("\n-- input validation: bad input must return problems, not crash --")

r = price_deal(deal(seats=0))
check("zero seats rejected", r["ok"] is False and any("seats" in p for p in r["problems"]))

r = price_deal(deal(segment="public_sector"))
check("unknown segment rejected", r["ok"] is False and any("segment" in p for p in r["problems"]))

r = price_deal(deal(term_months=18))
check("unsupported term rejected", r["ok"] is False and any("term" in p for p in r["problems"]))

r = price_deal(deal(drivers=[]))
check("no value drivers rejected", r["ok"] is False)

r = price_deal(deal(drivers=[ValueDriver("bad", 100_000, 1.4)]))
check("confidence above 1.0 rejected", r["ok"] is False)

r = price_deal(deal(drivers=[ValueDriver("bad", -50_000, 1.0)]))
check("negative value rejected", r["ok"] is False)

r = price_deal(deal(proposed_discount=1.5))
check("discount above 100% rejected", r["ok"] is False)


print("\n-- approval routing: the cases that cost money if wrong --")

# mid_market limit 20% + 12mo headroom 0% = 20% approval-free
r = price_deal(deal(proposed_discount=0.18))
check("18% ask on mid_market/12mo is auto-approvable", r["proposed"]["verdict"] == "auto-approvable")

r = price_deal(deal(proposed_discount=0.20))
check("exactly at the limit is auto-approvable", r["proposed"]["verdict"] == "auto-approvable",
      f"got {r['proposed']['verdict']}")

r = price_deal(deal(proposed_discount=0.21))
check("one point over the limit escalates", r["proposed"]["verdict"] == "escalate to deal desk")

r = price_deal(deal(proposed_discount=0.35))
check("35% ask escalates", r["proposed"]["verdict"] == "escalate to deal desk")

r = price_deal(deal(proposed_discount=0.60))
check("60% ask is rejected outright, not escalated",
      r["proposed"]["verdict"] == "reject -- below absolute floor")

r = price_deal(deal(proposed_discount=1 - ABSOLUTE_FLOOR_SHARE_OF_LIST))
check("exactly at the absolute floor is not rejected",
      r["proposed"]["below_absolute_floor"] is False)

# 36-month term grants 10 points of extra headroom -> 30% approval-free
r = price_deal(deal(term_months=36, proposed_discount=0.28))
check("28% on a 36-month mid_market deal is auto-approvable",
      r["proposed"]["verdict"] == "auto-approvable")

r = price_deal(deal(term_months=12, proposed_discount=0.28))
check("the same 28% on a 12-month deal escalates",
      r["proposed"]["verdict"] == "escalate to deal desk")

r = price_deal(deal(segment="smb", proposed_discount=0.18))
check("18% on SMB escalates (tighter limit than mid_market)",
      r["proposed"]["verdict"] == "escalate to deal desk")

r = price_deal(deal(segment="enterprise", proposed_discount=0.18))
check("18% on enterprise is auto-approvable", r["proposed"]["verdict"] == "auto-approvable")


print("\n-- pricing logic --")

r = price_deal(deal())
list_annual = 100 * LIST_PRICE_PER_SEAT_YEAR
check("recommended price never exceeds list",
      r["price"]["recommended_annual_raw"] <= list_annual + 0.005,
      f"{r['price']['recommended_annual_raw']} vs list {list_annual}")

# Huge value, small seat count: value band would blow past list.
r = price_deal(deal(seats=10, drivers=[ValueDriver("massive", 10_000_000, 1.0)]))
check("enormous value is capped at list, not priced above it",
      r["price"]["recommended_annual_raw"] == 10 * LIST_PRICE_PER_SEAT_YEAR)

# Tiny value: floor must hold rather than following value down.
r = price_deal(deal(seats=500, drivers=[ValueDriver("negligible", 1_000, 1.0)]))
check("negligible value does not price below the approval-free floor",
      r["price"]["recommended_annual_raw"] >= 500 * LIST_PRICE_PER_SEAT_YEAR * 0.80 - 0.005)

r = price_deal(deal(drivers=[ValueDriver("zero", 0, 1.0)]))
check("zero value still returns a computable price", r["ok"] is True)
check("zero value yields null payback (JSON-safe), not inf or a crash",
      r["customer_economics"]["payback_months"] is None)

r = price_deal(deal(drivers=[ValueDriver("a", 400_000, 0.5), ValueDriver("b", 200_000, 1.0)]))
check("confidence haircut is applied (400k*0.5 + 200k = 400k)",
      r["value"]["risk_adjusted_annual_raw"] == 400_000,
      r["value"]["risk_adjusted_annual"])


print("\n-- output contract: what the narrative prompt depends on --")

r = price_deal(deal(proposed_discount=0.18))
check("money fields are pre-formatted strings",
      r["price"]["recommended_annual"].startswith("$"))
check("sensitivity table has all scenarios", len(r["sensitivity"]) == 4)
check("assumptions list is populated", len(r["assumptions_to_validate"]) >= 1)
for key in ("value", "price", "customer_economics", "sensitivity"):
    check(f"result contains {key!r}", key in r)


print()
if failures:
    print(f"{len(failures)} FAILED: {', '.join(failures)}")
    raise SystemExit(1)
print("all eval cases passed")
