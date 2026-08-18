/**
 * Browser-side mirror of price_deal() in value_calculator.py.
 *
 * This file exists only so the dashboard can recompute live as sliders move.
 * Python remains the source of truth: the policy constants are injected from
 * value_calculator.py at build time (never hardcoded here), and check_parity.py
 * runs both implementations over the same cases and fails if they disagree.
 *
 * If you change the pricing math, change it in BOTH files and run:
 *     python3 check_parity.py
 */

export function validate(deal, policy) {
  const problems = [];
  if (!(deal.segment in policy.segmentDiscountLimit)) {
    problems.push(`unknown segment '${deal.segment}'`);
  }
  if (!(String(deal.termMonths) in policy.termDiscountHeadroom)) {
    problems.push(`unsupported term ${deal.termMonths}`);
  }
  if (!(deal.seats > 0)) problems.push('seats must be a positive integer');
  if (!deal.drivers || deal.drivers.length === 0) {
    problems.push('no value drivers supplied; cannot compute value-based price');
  }
  for (const d of deal.drivers || []) {
    if (!(d.confidence >= 0 && d.confidence <= 1)) {
      problems.push(`driver '${d.name}': confidence must be between 0 and 1`);
    }
    if (d.annualValue < 0) {
      problems.push(`driver '${d.name}': annualValue must not be negative`);
    }
  }
  if (deal.proposedDiscount != null && !(deal.proposedDiscount >= 0 && deal.proposedDiscount < 1)) {
    problems.push('proposedDiscount must be between 0 and 1');
  }
  return problems;
}

export function priceDeal(deal, policy) {
  const problems = validate(deal, policy);
  if (problems.length) return { ok: false, problems };

  const [captureLow, captureHigh] = policy.valueCaptureBand;
  const grossAnnualValue = deal.drivers.reduce((s, d) => s + d.annualValue, 0);
  const annualValue = deal.drivers.reduce((s, d) => s + d.annualValue * d.confidence, 0);

  const valueBandLow = annualValue * captureLow;
  const valueBandHigh = annualValue * captureHigh;

  const listAnnual = deal.seats * policy.listPricePerSeatYear;
  const approvalFreeDiscount = Math.min(
    policy.segmentDiscountLimit[deal.segment] + policy.termDiscountHeadroom[String(deal.termMonths)],
    1 - policy.absoluteFloorShareOfList,
  );
  const approvalFreePrice = listAnnual * (1 - approvalFreeDiscount);
  const absoluteFloorPrice = listAnnual * policy.absoluteFloorShareOfList;

  const midpoint = (valueBandLow + valueBandHigh) / 2;
  const recommendedAnnual = Math.min(Math.max(midpoint, approvalFreePrice), listAnnual);
  const recommendedDiscount = 1 - recommendedAnnual / listAnnual;

  let proposed = null;
  if (deal.proposedDiscount != null) {
    const proposedAnnual = listAnnual * (1 - deal.proposedDiscount);
    const belowAbsoluteFloor = proposedAnnual < absoluteFloorPrice - 0.005;
    const withinApprovalFree = deal.proposedDiscount <= approvalFreeDiscount + 1e-9;
    proposed = {
      discountPct: deal.proposedDiscount * 100,
      annualPrice: proposedAnnual,
      withinApprovalFreeRange: withinApprovalFree,
      belowAbsoluteFloor,
      verdict: belowAbsoluteFloor
        ? 'reject -- below absolute floor'
        : withinApprovalFree
          ? 'auto-approvable'
          : 'escalate to deal desk',
    };
  }

  return {
    ok: true,
    grossAnnualValue,
    annualValue,
    confidenceHaircut: grossAnnualValue - annualValue,
    valueBandLow,
    valueBandHigh,
    listAnnual,
    approvalFreeDiscount,
    approvalFreePrice,
    absoluteFloorPrice,
    recommendedAnnual,
    recommendedDiscountPct: recommendedDiscount * 100,
    recommendedTotalContract: recommendedAnnual * (deal.termMonths / 12),
    captureShareOfValuePct: annualValue ? (recommendedAnnual / annualValue) * 100 : null,
    roiMultiple: recommendedAnnual ? annualValue / recommendedAnnual : 0,
    paybackMonths: annualValue > 0 ? recommendedAnnual / (annualValue / 12) : null,
    netAnnualGain: annualValue - recommendedAnnual,
    proposed,
    drivers: deal.drivers.map((d) => ({
      name: d.name,
      annualValue: d.annualValue,
      confidence: d.confidence,
      riskAdjusted: d.annualValue * d.confidence,
      basis: d.basis || '',
    })),
    sensitivity: sensitivityTable(deal, policy),
  };
}

export function sensitivityTable(deal, policy, factors = [0.6, 0.8, 1.0, 1.2]) {
  const baseValue = deal.drivers.reduce((s, d) => s + d.annualValue * d.confidence, 0);
  const listAnnual = deal.seats * policy.listPricePerSeatYear;
  const approvalFreeDiscount = Math.min(
    policy.segmentDiscountLimit[deal.segment] + policy.termDiscountHeadroom[String(deal.termMonths)],
    1 - policy.absoluteFloorShareOfList,
  );
  const approvalFreePrice = listAnnual * (1 - approvalFreeDiscount);
  const [low, high] = policy.valueCaptureBand;

  return factors.map((f) => {
    const value = baseValue * f;
    const midpoint = (value * (low + high)) / 2;
    const price = Math.min(Math.max(midpoint, approvalFreePrice), listAnnual);
    return {
      factor: f,
      label: `${Math.round(f * 100)}% of estimate`,
      annualValue: value,
      recommendedAnnual: price,
      roiMultiple: price ? value / price : 0,
      stillAboveFloor: price >= approvalFreePrice - 0.005,
    };
  });
}
