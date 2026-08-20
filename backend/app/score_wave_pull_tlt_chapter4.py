"""Score Wave Pull's TLT near-miss for Chapter 4 (risk-budgeted ensemble)
eligibility, per docs/adr/0007-risk-budgeted-ensemble-acceptance.md.

Usage (from backend/):
    python -m app.score_wave_pull_tlt_chapter4

This is NOT a Stage 9A re-run and does not change Wave Pull v1's closed
`not_material_or_not_consistent` decision under Chapters 1-3's standard --
that decision is immutable. This reconstructs the same 20 qualifying
`TLT` events Wave Pull v1's own locked bootstrap already identified, and
asks Chapter 4's different question: not "is this proven," but what
confidence-scaled position size Loss-based Quantity Determination would
assign it. No trade, no cost, no live sizing -- output is an eligibility
score and an illustrative sizing calculation only.

Unlike CTA v2's confidence interval (a continuous daily excess-return
series, block-resampled), TLT's statistic is the mean of a small set of
discrete, cooldown-spaced event occurrences -- its confidence interval is
built by case-resampling those individual event-level observations
directly (ADR 0003's own post-signal-inference convention), not by
resampling blocks of the underlying price series and recomputing events on
it.
"""

from __future__ import annotations

import json
from pathlib import Path

from .research import (
    case_resample_confidence_interval,
    chapter4_confidence_multiplier,
    log_returns_from_closes,
    wave_pull_event_forward_returns_array,
)
from .run_wave_pull import SPEC_PATH, SPEC_SHA256, validate_locked_spec
from .store import load_bars

ROOT = Path(__file__).parents[2]
OUTPUT = ROOT / "output/research/chapter4-eligibility/wave-pull-tlt/score.json"

SYMBOL = "TLT"

# ADR 0004's existing entry-capacity formula, restated here (not
# reimplemented as portfolio code -- this is an illustrative, no-trade
# calculation only): q = floor(min(0.005E / d, 0.10E / P)). The Chapter 4
# addition is the confidence_multiplier applied on top.
BASE_RISK_FRACTION = 0.005  # 0.5% of equity against the stop distance
BASE_NOTIONAL_CAP_FRACTION = 0.10  # 10% of equity notional cap


def main() -> None:
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    validate_locked_spec(spec)

    bars = load_bars(SYMBOL)
    closes = bars["close"].to_numpy(dtype=float)
    log_returns_padded = log_returns_from_closes(closes)

    per_event_returns = wave_pull_event_forward_returns_array(
        log_returns_padded,
        warm_up=spec["warm_up_sessions"],
        cooldown=spec["event"]["cooldown_sessions"],
        horizon=spec["forward_return"]["horizon_sessions"],
    )

    ci = case_resample_confidence_interval(
        per_event_returns,
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
        "candidate": "wave-pull-v1",
        "symbol": SYMBOL,
        "chapter_1_3_decision": "not_material_or_not_consistent (unchanged, immutable)",
        "chapter_1_3_raw_p": "0.032 (Holm-adjusted: 0.350, on 20 events)",
        "confidence_interval": {
            "event_count": ci["event_count"],
            "observed_mean_forward_return": ci["observed_mean"],
            "lower_bound_68pct": ci["lower_bound"],
            "upper_bound_68pct": ci["upper_bound"],
        },
        "chapter4_confidence_multiplier": multiplier,
        "eligible": eligible,
        "eligibility_reasoning": (
            "68% confidence interval's lower bound stays positive despite the "
            "small (20-event) sample -- some confidence, not high confidence, "
            "that the point estimate is real"
            if eligible
            else "68% confidence interval's lower bound is not positive -- "
            "even at one-sigma coverage, cannot rule out a zero or negative "
            "true effect, and the small sample (20 events) widens this "
            "interval further"
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
            "Only 20 qualifying events -- a small sample by construction "
            "(Wave Pull's own protocol disclosed this as expected, given the "
            "compound impulse-AND-breakout precondition). A case-resampling "
            "confidence interval on 20 points is inherently wide; treat this "
            "score as a first look, not a settled read.",
        ],
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
