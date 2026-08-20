"""Score Calendar Day-of-Week's per-asset Monday differential for Chapter 4
(risk-budgeted ensemble) eligibility, per
docs/adr/0007-risk-budgeted-ensemble-acceptance.md.

Usage (from backend/):
    python -m app.score_calendar_dow_chapter4

This is NOT a Stage 9A re-run and does not change Calendar Day-of-Week v1's
closed `not_material_or_not_consistent` decision under Chapters 1-3's
standard -- that decision is immutable. Unlike CTA v2 (one portfolio-level
series) or Wave Pull (one asset's small discrete event set), this
candidate's own closed result was a BREADTH claim -- 9/12 assets negative,
none individually significant after correction -- so this scores all 12
assets individually through Chapter 4, to test directly whether that
directional consistency translates into multiple assets each clearing even
the loosened per-asset bar, or whether none do. No trade, no cost, no live
sizing -- output is a per-asset eligibility table only.

Uses `two_sample_block_bootstrap_confidence_interval`: a third Chapter 4 CI
shape distinct from CTA v2's continuous-series and Wave Pull's discrete-event
case-resampling. Monday and non-Monday returns are each long, potentially
serially-correlated sequences, so each is block-resampled independently and
the difference recomputed each time -- not `dow_bootstrap`'s existing null
test, which fixes calendar positions and resamples values onto them.
"""

from __future__ import annotations

import json
from pathlib import Path

from .research import (
    chapter4_confidence_multiplier,
    dow_event_mask,
    log_returns_from_closes,
    two_sample_block_bootstrap_confidence_interval,
)
from .run_calendar_day_of_week import SPEC_PATH, validate_locked_spec
from .store import load_bars

ROOT = Path(__file__).parents[2]
OUTPUT = ROOT / "output/research/chapter4-eligibility/calendar-day-of-week/score.json"

# ADR 0004's existing entry-capacity formula, restated here (not
# reimplemented as portfolio code -- this is an illustrative, no-trade
# calculation only): q = floor(min(0.005E / d, 0.10E / P)). The Chapter 4
# addition is the confidence_multiplier applied on top.
BASE_RISK_FRACTION = 0.005
BASE_NOTIONAL_CAP_FRACTION = 0.10


def score_symbol(symbol: str, block_bars: int, resamples: int, seed: int) -> dict:
    bars = load_bars(symbol)
    closes = bars["close"].to_numpy(dtype=float)
    dates = bars["date"]
    log_returns_padded = log_returns_from_closes(closes)
    mask = dow_event_mask(dates)

    values = log_returns_padded[1:]
    monday_mask = mask[1:]
    monday_returns = values[monday_mask]
    non_monday_returns = values[~monday_mask]

    # Day-of-Week's own closed claim is negative-direction (underperformance);
    # Chapter 4's eligibility clause requires a POSITIVE point estimate, so
    # the differential is scored as (non-Monday - Monday) -- a positive value
    # here means "Monday underperforms," matching the original claim's own
    # favourable direction, restated so a positive EV is what eligibility
    # actually checks for.
    ci = two_sample_block_bootstrap_confidence_interval(
        non_monday_returns, monday_returns, block_bars=block_bars, resamples=resamples, seed=seed
    )
    multiplier = chapter4_confidence_multiplier(ci["observed_mean"], ci["lower_bound"])
    return {
        "symbol": symbol,
        "monday_count": ci["group_b_count"],
        "non_monday_count": ci["group_a_count"],
        "observed_underperformance_differential": ci["observed_mean"],
        "lower_bound_68pct": ci["lower_bound"],
        "upper_bound_68pct": ci["upper_bound"],
        "chapter4_confidence_multiplier": multiplier,
        "eligible": multiplier > 0.0,
    }


def main() -> None:
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    validate_locked_spec(spec)

    universe = sorted(spec["universe"])
    block_bars = spec["bootstrap"]["block_bars"]
    resamples = spec["bootstrap"]["resamples"]
    seed = spec["bootstrap"]["seed"]

    per_asset = {symbol: score_symbol(symbol, block_bars, resamples, seed) for symbol in universe}
    eligible_symbols = [s for s in universe if per_asset[s]["eligible"]]

    report = {
        "candidate": "calendar-day-of-week-v1",
        "chapter_1_3_decision": "not_material_or_not_consistent (unchanged, immutable)",
        "chapter_1_3_summary": "9/12 assets negative (directionally consistent), 0/12 "
        "individually significant after Holm correction; DBC's raw p=0.048 was the "
        "session's strongest single-asset raw signal but Holm-adjusted p=0.578",
        "per_asset": per_asset,
        "eligible_count": len(eligible_symbols),
        "eligible_symbols": eligible_symbols,
        "breadth_reading": (
            f"{len(eligible_symbols)}/12 assets individually clear Chapter 4's "
            "loosened 68% bar despite none clearing Chapter 1-3's 95% bar -- "
            + (
                "a real, if modest, multi-signal breadth candidate for a future "
                "ensemble, directly relevant to whether this directional tilt is "
                "worth carrying forward."
                if eligible_symbols
                else "zero assets clear it even at the loosened standard, meaning "
                "the 9/12 directional tilt is weaker than it looks even under a "
                "lenient per-asset bar, not just under Chapter 1-3's strict one."
            )
        ),
        "disclosed_limitations": [
            "Per-asset scores here are NOT yet an ensemble -- ADR 0007 clause 3 "
            "(measured orthogonality) is not evaluated in this script; several of "
            "these 12 assets are known to be correlated (e.g. within the US equity "
            "cluster), so a naive count of 'how many are eligible' overstates "
            "effective breadth until pairwise correlation is actually measured.",
            "Each per-asset confidence interval independently uses a 68% band; "
            "no family-wise adjustment is applied across the 12 assets scored "
            "here, consistent with Chapter 4's own eligibility clause 4 (no "
            "significance claim is being made) but worth remembering this is not "
            "the same discipline as Chapters 1-3's Holm correction.",
        ],
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
