"""Score CTA v2's primary variant for Chapter 4 (risk-budgeted ensemble)
eligibility, per docs/adr/0007-risk-budgeted-ensemble-acceptance.md.

Usage (from backend/):
    python -m app.score_cta_v2_chapter4

This is NOT a Stage 9A re-run and does not change CTA v2's closed
`not_material_or_not_consistent` decision under Chapters 1-3's standard --
that decision is immutable. This reconstructs the SAME primary-variant
excess-return series CTA v2's own locked bootstrap already computed, and
asks Chapter 4's different question of it: not "is this proven," but "what
confidence-scaled position size would Loss-based Quantity Determination
assign it." No trade, no cost, no live sizing -- output is an eligibility
score and an illustrative sizing calculation only.
"""

from __future__ import annotations

import json
from pathlib import Path

from .research import (
    CTA_V2_PRIMARY_VARIANT,
    CTA_V2_VARIANTS,
    block_bootstrap_confidence_interval,
    chapter4_confidence_multiplier,
    cta_v2_benchmark_return,
    cta_v2_portfolio_return,
    cta_v2_weight_matrix,
)
from .run_cta_v2 import SPEC_PATH, common_calendar_bars, validate_locked_spec

ROOT = Path(__file__).parents[2]
OUTPUT = ROOT / "output/research/chapter4-eligibility/cta-v2-primary/score.json"

# ADR 0004's existing entry-capacity formula, restated here (not
# reimplemented as portfolio code -- this is an illustrative, no-trade
# calculation only): q = floor(min(0.005E / d, 0.10E / P)). The Chapter 4
# addition is the confidence_multiplier applied on top.
BASE_RISK_FRACTION = 0.005  # 0.5% of equity against the stop distance
BASE_NOTIONAL_CAP_FRACTION = 0.10  # 10% of equity notional cap


def main() -> None:
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    validate_locked_spec(spec)

    bars_by_symbol = common_calendar_bars(spec)
    universe = sorted(spec["universe"])
    closes_by_symbol = {
        symbol: bars_by_symbol[symbol]["close"].to_numpy(dtype=float) for symbol in universe
    }
    warm_up = spec["warm_up_sessions"]

    sma_window = CTA_V2_VARIANTS[CTA_V2_PRIMARY_VARIANT]
    weights = cta_v2_weight_matrix(closes_by_symbol, sma_window=sma_window)
    portfolio = cta_v2_portfolio_return(closes_by_symbol, weights)
    benchmark = cta_v2_benchmark_return(closes_by_symbol)
    excess = (portfolio - benchmark)[warm_up:]

    ci = block_bootstrap_confidence_interval(
        excess,
        block_bars=spec["bootstrap"]["block_bars"],
        resamples=spec["bootstrap"]["resamples"],
        seed=spec["bootstrap"]["seed"],
    )
    multiplier = chapter4_confidence_multiplier(ci["observed_mean"], ci["lower_bound"])

    eligible = multiplier > 0.0
    # Illustrative sizing only: apply the confidence multiplier on top of
    # ADR 0004's existing conservative caps, at a representative $100,000
    # account (ADR 0004's own initial-equity convention) and an
    # illustrative 2% stop distance -- no real position is sized or opened.
    equity = 100_000.0
    illustrative_stop_distance_pct = 0.02
    base_risk_capital = BASE_RISK_FRACTION * equity
    base_notional_cap = BASE_NOTIONAL_CAP_FRACTION * equity
    scaled_risk_capital = multiplier * base_risk_capital
    scaled_notional_cap = multiplier * base_notional_cap

    report = {
        "candidate": "cta-v2-pooled-trend-overlay",
        "variant": CTA_V2_PRIMARY_VARIANT,
        "chapter_1_3_decision": "not_material_or_not_consistent (unchanged, immutable)",
        "confidence_interval": {
            "observed_mean_daily_excess_return": ci["observed_mean"],
            "annualized_point_estimate": ci["observed_mean"] * 252,
            "lower_bound_68pct": ci["lower_bound"],
            "upper_bound_68pct": ci["upper_bound"],
            "annualized_lower_bound_68pct": ci["lower_bound"] * 252,
        },
        "chapter4_confidence_multiplier": multiplier,
        "eligible": eligible,
        "eligibility_reasoning": (
            "68% confidence interval's lower bound stays positive -- some confidence, "
            "not high confidence, that the point estimate is real"
            if eligible
            else "68% confidence interval's lower bound is not positive -- "
            "even at one-sigma coverage, cannot rule out a zero or negative true effect"
        ),
        "illustrative_sizing_at_100k_equity": {
            "note": "No trade authorized. Illustrates ADR 0004's entry-capacity "
            "formula scaled by the confidence multiplier, at an illustrative "
            f"{illustrative_stop_distance_pct:.0%} stop distance -- not a real position.",
            "base_risk_capital_unscaled": base_risk_capital,
            "confidence_scaled_risk_capital": scaled_risk_capital,
            "base_notional_cap_unscaled": base_notional_cap,
            "confidence_scaled_notional_cap": scaled_notional_cap,
        },
        "disclosed_limitations": [
            "Single candidate, not an ensemble -- ADR 0007's minimum-breadth "
            "floor is not met by one signal alone; this score characterizes "
            "eligibility only, it does not authorize deployment.",
            "CTA v2's own disclosed 2008-dependency (regime concentration) is "
            "unresolved by this score and would need direct confrontation "
            "before any real ensemble inclusion.",
        ],
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
