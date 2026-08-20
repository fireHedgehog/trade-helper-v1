"""Correlation-aware significance test for Calendar Day-of-Week's Chapter 4
breadth result (`6/12` assets independently eligible), per
docs/research-program.md Chapter 4 §4.

Usage (from backend/):
    python -m app.run_calendar_dow_breadth_significance

calibrate_chapter4_eligibility.py calibrated the per-asset eligibility rule's
false-positive rate using INDEPENDENT synthetic null assets (16.25%) --
adversarial verification of that calibration against the real `6/12` result
found the naive independent-trials reading unresolved: the 12 real assets
are correlated with each other (score_chapter4_orthogonality.py,
score_calendar_dow_full_correlation.py), and correlation among trials
inflates the variance of an extreme count under a true null, working AGAINST
the naive "still significant" reading, not for it. This settles the question
directly with `research.dow_breadth_correlation_aware_null`: a joint
circular-block-resampling null that preserves the REAL cross-asset
correlation structure (one shared block-shift applied to all 12 assets at
once, the same principle etf12_rotation_bootstrap and overnight_gap_bootstrap
already use), rather than a hand-adjusted design-effect approximation from
the correlation matrix alone.

Hardened by an independent pre-lock adversarial review before running
against real data -- see research.py's `dow_breadth_correlation_aware_null`
docstring/comment for the one real finding (trading-week/block_bars
resonance) and its fix. As a disclosed robustness check on that fix, this
script reruns the same null at two additional outer block sizes coprime
with the 5-day trading week (17, 23) alongside the default (19) and reports
all three, plus a Wilson 95% CI on each resulting p-value (the review's own
adversarial-coverage concern: 300 replications alone leaves real Monte
Carlo noise near conventional significance thresholds).

This is NOT a Stage 9A re-run and does not change Calendar Day-of-Week v1's
closed `not_material_or_not_consistent` decision under Chapters 1-3's
standard, nor score_calendar_dow_chapter4.py's own per-asset eligibility
results -- it answers a different, narrower question: is the COUNT of `6`
eligible assets itself distinguishable from what real, correlated market
data would produce with no true Monday effect anywhere. No trade, no cost,
no live sizing.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from .research import dow_breadth_correlation_aware_null, dow_event_mask, log_returns_from_closes
from .run_calendar_day_of_week import SPEC_PATH, validate_locked_spec
from .store import load_bars

ROOT = Path(__file__).parents[2]
OUTPUT = ROOT / "output/research/chapter4-eligibility/calendar-day-of-week/breadth-significance.json"

OUTER_BLOCK_BARS_TO_CHECK = [19, 17, 23]  # default first, then two more
# coprime-with-5 values as a disclosed robustness check on the pre-lock
# review's own recommendation.


def load_aligned_closes(spec: dict) -> tuple[dict, dict]:
    """Mirrors run_etf12_rotation.py's own helper exactly: restrict every
    symbol's bars to the shared date range every symbol covers."""
    symbols = sorted(spec["universe"])
    bars = {symbol: load_bars(symbol) for symbol in symbols}
    common_start = max(bars[symbol]["date"].iloc[0] for symbol in symbols)
    common_end = min(bars[symbol]["date"].iloc[-1] for symbol in symbols)
    aligned_bars = {
        symbol: bars[symbol][
            (bars[symbol]["date"] >= common_start) & (bars[symbol]["date"] <= common_end)
        ].reset_index(drop=True)
        for symbol in symbols
    }
    lengths = {len(aligned_bars[symbol]) for symbol in symbols}
    if len(lengths) != 1:
        raise RuntimeError(f"aligned bars are not equal length: {lengths}")
    closes = {symbol: aligned_bars[symbol]["close"].to_numpy(dtype=float) for symbol in symbols}
    return closes, aligned_bars


def _wilson_interval(successes: int, n: int, z: float = 1.959963985) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    phat = successes / n
    denom = 1 + z**2 / n
    center = (phat + z**2 / (2 * n)) / denom
    half = z * math.sqrt(phat * (1 - phat) / n + z**2 / (4 * n**2)) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def main() -> None:
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    validate_locked_spec(spec)

    closes, aligned_bars = load_aligned_closes(spec)
    symbols = sorted(spec["universe"])
    dates = aligned_bars[symbols[0]]["date"]
    mask = dow_event_mask(dates)
    log_returns_by_symbol = {s: log_returns_from_closes(closes[s]) for s in symbols}

    runs = []
    for outer_block_bars in OUTER_BLOCK_BARS_TO_CHECK:
        result = dow_breadth_correlation_aware_null(
            log_returns_by_symbol, mask, outer_block_bars=outer_block_bars
        )
        p_lo, p_hi = _wilson_interval(
            round(result["p_value"] * (result["outer_replications"] + 1)) - 1,
            result["outer_replications"],
        )
        runs.append({
            "outer_block_bars": outer_block_bars,
            "observed_count": result["observed_count"],
            "observed_eligible_symbols": result["observed_eligible_symbols"],
            "null_count_mean": result["null_count_mean"],
            "null_count_std": result["null_count_std"],
            "p_value": result["p_value"],
            "p_value_wilson_95_ci": [p_lo, p_hi],
            "outer_replications": result["outer_replications"],
            "inner_resamples": result["inner_resamples"],
        })

    p_values = [r["p_value"] for r in runs]
    stable = (max(p_values) - min(p_values)) < 0.10

    report = {
        "candidate": "calendar-day-of-week-v1",
        "question": "Is the real 6/12 Chapter 4 breadth count distinguishable from a null "
        "that preserves the true joint cross-asset correlation structure of the real 12-asset "
        "universe, rather than assuming independence?",
        "aligned_common_start": str(dates.iloc[0]),
        "aligned_common_end": str(dates.iloc[-1]),
        "runs_by_outer_block_bars": runs,
        "p_value_range": [min(p_values), max(p_values)],
        "p_value_stable_across_block_bars": stable,
        "reading": (
            f"Observed count {runs[0]['observed_count']}/12 (symbols: "
            f"{runs[0]['observed_eligible_symbols']}). Across {len(runs)} outer block sizes "
            f"({OUTER_BLOCK_BARS_TO_CHECK}), p ranges {min(p_values):.4f}-{max(p_values):.4f}. "
            + (
                "Stable across block sizes -- the result is not an artifact of one particular "
                "resampling grid."
                if stable
                else "NOT stable across block sizes -- treat any single point estimate here "
                "with caution; the specific block size materially changes the read."
            )
        ),
        "disclosed_limitations": [
            "Aligned to the common date range across all 12 assets (bounded by DBC's shorter "
            "history), not each asset's own full individual history used in "
            "score_calendar_dow_chapter4.py -- the observed_count here may differ slightly from "
            "the originally-reported 6/12 if the shorter shared window changes any borderline "
            "asset's eligibility; both counts are disclosed for direct comparison.",
            "inner_resamples reduced from Chapter 4's locked 5,000 to 500 per replication "
            "(calibrate_chapter4_eligibility.py's own disclosed deviation, for the same reason: "
            "an outer empirical distribution across many replications does not need the same "
            "per-replication inner precision as one standalone score).",
            "outer_replications=300 carries real Monte Carlo noise near conventional "
            "significance thresholds -- the Wilson 95% CI on each p-value should be read "
            "alongside the point estimate, not instead of it.",
            "Pre-lock adversarially reviewed (2 of 3 lenses completed via independent review; "
            "the third, adversarial-coverage, was completed directly after the reviewing agent "
            "hit a session limit) -- see research.py's dow_breadth_correlation_aware_null "
            "comment for the one real finding (trading-week/block_bars resonance) and its fix; "
            "the multi-block-size run above is the disclosed robustness check that finding "
            "recommended.",
        ],
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
