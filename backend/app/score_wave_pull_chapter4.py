"""Score Wave Pull's full 12-asset universe for Chapter 4 (risk-budgeted
ensemble) eligibility, per docs/adr/0007-risk-budgeted-ensemble-acceptance.md.

Usage (from backend/):
    python -m app.score_wave_pull_chapter4

This is NOT a Stage 9A re-run and does not change Wave Pull v1's closed
`not_material_or_not_consistent` decision under Chapters 1-3's standard --
that decision is immutable.

score_wave_pull_tlt_chapter4.py (2026-08-20) scored only TLT -- the asset
Wave Pull v1's own locked bootstrap happened to report the strongest raw
p-value for. A pasted external critique correctly flagged that reporting
one pre-selected winner's confidence interval alone, without showing how
the other 11 assets in the same universe score, overstates confidence:
a "best of 12" selection is expected to look better than a random single
draw even under a true null. This script closes that gap the same way
score_calendar_dow_chapter4.py already treats Calendar Day-of-Week --
symmetric per-asset scoring across the full locked universe, so TLT's
result is shown in the context of "1 of 12," not standalone.
`calibrate_chapter4_eligibility.py` separately measures, on synthetic null
data, how often a "best of 12" selection shows up eligible by chance alone
(the empirical answer to the critique's underlying concern); this script
supplies the real-data counterpart it needs to be read against.

Uses `case_resample_confidence_interval`, the same CI shape as the TLT-only
script -- Wave Pull's statistic is the mean of a small set of discrete,
cooldown-spaced event occurrences, not a continuous series.
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
from .run_wave_pull import SPEC_PATH, validate_locked_spec
from .store import load_bars

ROOT = Path(__file__).parents[2]
OUTPUT = ROOT / "output/research/chapter4-eligibility/wave-pull-all-assets/score.json"


def score_symbol(symbol: str, spec: dict) -> dict:
    bars = load_bars(symbol)
    closes = bars["close"].to_numpy(dtype=float)
    log_returns_padded = log_returns_from_closes(closes)

    per_event_returns = wave_pull_event_forward_returns_array(
        log_returns_padded,
        warm_up=spec["warm_up_sessions"],
        cooldown=spec["event"]["cooldown_sessions"],
        horizon=spec["forward_return"]["horizon_sessions"],
    )

    min_event_count = spec["event"]["minimum_event_count_per_asset"]
    if per_event_returns.size < min_event_count:
        return {
            "symbol": symbol,
            "event_count": int(per_event_returns.size),
            "insufficient_events": True,
            "eligible": False,
        }

    ci = case_resample_confidence_interval(
        per_event_returns,
        resamples=spec["bootstrap"]["resamples"],
        seed=spec["bootstrap"]["seed"],
    )
    multiplier = chapter4_confidence_multiplier(ci["observed_mean"], ci["lower_bound"])
    return {
        "symbol": symbol,
        "event_count": ci["event_count"],
        "insufficient_events": False,
        "observed_mean_forward_return": ci["observed_mean"],
        "lower_bound_68pct": ci["lower_bound"],
        "upper_bound_68pct": ci["upper_bound"],
        "chapter4_confidence_multiplier": multiplier,
        "eligible": multiplier > 0.0,
    }


def main() -> None:
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    validate_locked_spec(spec)

    universe = sorted(spec["universe"])
    per_asset = {symbol: score_symbol(symbol, spec) for symbol in universe}
    eligible_symbols = [s for s in universe if per_asset[s]["eligible"]]
    scored_symbols = [s for s in universe if not per_asset[s]["insufficient_events"]]

    ranked_by_observed_mean = sorted(
        scored_symbols, key=lambda s: per_asset[s]["observed_mean_forward_return"], reverse=True
    )
    best_symbol = ranked_by_observed_mean[0] if ranked_by_observed_mean else None

    report = {
        "candidate": "wave-pull-v1",
        "chapter_1_3_decision": "not_material_or_not_consistent (unchanged, immutable)",
        "per_asset": per_asset,
        "scored_count": len(scored_symbols),
        "eligible_count": len(eligible_symbols),
        "eligible_symbols": eligible_symbols,
        "best_by_observed_mean": best_symbol,
        "selection_context": (
            "TLT was the asset score_wave_pull_tlt_chapter4.py originally reported alone; "
            f"across all {len(scored_symbols)} scored assets here, "
            + (
                f"TLT is {'also' if best_symbol == 'TLT' else 'NOT'} the single best by observed "
                f"mean forward return (best: {best_symbol})."
                if best_symbol
                else "no asset had enough qualifying events to score."
            )
        ),
        "breadth_reading": (
            f"{len(eligible_symbols)}/{len(scored_symbols)} scored assets individually clear "
            "Chapter 4's 68% bar. Compare against calibrate_chapter4_eligibility.py's synthetic-null "
            "'selected winner of 12' empirical rate before treating a single eligible asset among "
            "many tested as strong evidence on its own."
        ),
        "disclosed_limitations": [
            "Per-asset scores here are NOT yet an ensemble -- ADR 0007 clause 3 (measured "
            "orthogonality) covers only the assets already fed into "
            "score_chapter4_orthogonality.py; if this run changes which Wave Pull assets are "
            "eligible, the orthogonality measurement needs re-running against the updated set.",
            "Each per-asset confidence interval independently uses a 68% band; no family-wise "
            "adjustment across the assets scored here, consistent with Chapter 4's eligibility "
            "clause 4 (no significance claim) but this is exactly the selection-multiplicity "
            "question calibrate_chapter4_eligibility.py's 'winner of 12' measurement addresses.",
            "Small per-asset event counts (Wave Pull's own protocol disclosed this as expected, "
            "given the compound impulse-AND-breakout precondition) -- case-resampling confidence "
            "intervals on a handful of events are inherently wide.",
        ],
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
