"""Monte Carlo false-positive calibration for Chapter 4's eligibility rule
(confidence_multiplier > 0), per docs/adr/0007-risk-budgeted-ensemble-acceptance.md.

Usage (from backend/):
    python -m app.calibrate_chapter4_eligibility [--replications N]

Motivated by a pasted external critique (2026-08-20) arguing that
"6/12 eligible" for Calendar Day-of-Week is close to what pure chance would
produce at a 68% confidence band, and that Wave Pull's TLT-only report
suffers "winner's curse" -- TLT was the best of 12 assets by raw p-value,
so reporting only its own confidence interval overstates what a
pre-specified, non-selected test would show. Both are checkable claims
about the FALSE-POSITIVE RATE of the eligibility rule itself, not about
opinion -- this measures them directly, the same way
calibrate_event_bootstraps.py already measured Chapters 1-3's Type-I rate.

This is methodology validation, not a market hypothesis test: no real
data is touched, no research-candidate scorecard applies, this is not a
Stage 9A protocol, and it does not change any closed Chapter 1-3 decision
or either already-reported Chapter 4 score. Synthetic null data only
(zero true mean by construction, realistic GARCH(1,1) volatility
clustering) -- any eligibility "hit" here is, by construction, a false
positive.

Two things measured:
  A. Two-sample (Calendar Day-of-Week shape): per-asset empirical
     eligibility rate under a true null, compared against the naive ~16%
     one-sided-tail approximation and the critique's own ~32% figure.
  B. Case-resample (Wave Pull shape): per-asset empirical eligibility
     rate under a true null, AND the "winner's curse" rate -- across 12
     independent null assets per replication, how often does the single
     asset with the best observed effect turn out eligible, versus the
     average single-asset rate.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np
import pandas as pd

from . import research
from .calibrate_event_bootstraps import garch_log_returns, closes_from_returns, _wilson_interval
from .run_experiment import _atomic_json

ROOT = Path(__file__).parents[2]
OUTPUT_DIR = ROOT / "output/research/chapter4-eligibility-calibration-v1"

SERIES_LENGTH = 3_000
CALIBRATION_RESAMPLES = 500  # Chapter 4's own locked default is 5,000; reduced
# here for the same reason calibrate_event_bootstraps.py reduces its own inner
# resample count -- measuring the empirical hit RATE across many replications
# does not need the same inner precision as one real eligibility score.
DEFAULT_REPLICATIONS = 300
DOW_ASSETS_PER_REPLICATION = 12  # matches the real Calendar Day-of-Week universe size
WAVE_PULL_ASSETS_PER_REPLICATION = 12  # matches the real 12-ETF universe size


def dow_style_trial(seed: int) -> bool:
    """One synthetic asset's Monday-vs-non-Monday eligibility check under a
    true null (zero mean by construction) -- mirrors
    score_calendar_dow_chapter4.py's per-asset pipeline exactly, on
    synthetic instead of real data."""
    r = garch_log_returns(SERIES_LENGTH, seed=seed)
    dates = pd.bdate_range("2000-01-03", periods=SERIES_LENGTH)
    mask = research.dow_event_mask(dates)
    values = r[1:]
    monday_mask = mask[1:]
    non_monday = values[~monday_mask]
    monday = values[monday_mask]
    ci = research.two_sample_block_bootstrap_confidence_interval(
        non_monday, monday, resamples=CALIBRATION_RESAMPLES, seed=seed
    )
    multiplier = research.chapter4_confidence_multiplier(ci["observed_mean"], ci["lower_bound"])
    return multiplier > 0.0


def wave_pull_style_trial(seed: int) -> tuple[bool, float, int] | None:
    """One synthetic asset's Wave Pull eligibility check under a true null.
    Returns (eligible, observed_mean, event_count), or None if the asset
    has too few qualifying events (mirrors production's insufficient-event
    handling)."""
    r = garch_log_returns(SERIES_LENGTH, seed=seed)
    closes = closes_from_returns(r)
    log_returns_padded = research.log_returns_from_closes(closes)
    array = research.wave_pull_event_forward_returns_array(log_returns_padded)
    if array.size < research.WAVE_PULL_MIN_EVENT_COUNT:
        return None
    ci = research.case_resample_confidence_interval(array, resamples=CALIBRATION_RESAMPLES, seed=seed)
    multiplier = research.chapter4_confidence_multiplier(ci["observed_mean"], ci["lower_bound"])
    return multiplier > 0.0, ci["observed_mean"], int(array.size)


def run(replications: int) -> dict:
    dow_hits = 0
    dow_trials = 0

    wave_pull_single_hits = 0
    wave_pull_single_trials = 0
    wave_pull_winner_hits = 0
    wave_pull_winner_trials = 0

    start = time.time()
    for i in range(replications):
        base_seed = 950_000 + i * 1000

        for a in range(DOW_ASSETS_PER_REPLICATION):
            if dow_style_trial(base_seed + a):
                dow_hits += 1
            dow_trials += 1

        candidates = []
        for a in range(WAVE_PULL_ASSETS_PER_REPLICATION):
            result = wave_pull_style_trial(base_seed + 500 + a)
            if result is None:
                continue
            eligible, observed_mean, _ = result
            candidates.append((eligible, observed_mean))
            if eligible:
                wave_pull_single_hits += 1
            wave_pull_single_trials += 1

        if candidates:
            # The "selected winner" mimics how TLT was chosen: the asset
            # with the single best observed effect among the 12 tested.
            winner_eligible, _ = max(candidates, key=lambda c: c[1])
            if winner_eligible:
                wave_pull_winner_hits += 1
            wave_pull_winner_trials += 1

        if (i + 1) % 10 == 0:
            elapsed = time.time() - start
            print(f"{i + 1}/{replications} replications, {elapsed:.0f}s elapsed", flush=True)

    dow_rate = dow_hits / dow_trials if dow_trials else None
    dow_lo, dow_hi = _wilson_interval(dow_hits, dow_trials) if dow_trials else (None, None)

    wp_single_rate = wave_pull_single_hits / wave_pull_single_trials if wave_pull_single_trials else None
    wp_single_lo, wp_single_hi = (
        _wilson_interval(wave_pull_single_hits, wave_pull_single_trials) if wave_pull_single_trials else (None, None)
    )

    wp_winner_rate = wave_pull_winner_hits / wave_pull_winner_trials if wave_pull_winner_trials else None
    wp_winner_lo, wp_winner_hi = (
        _wilson_interval(wave_pull_winner_hits, wave_pull_winner_trials) if wave_pull_winner_trials else (None, None)
    )

    return {
        "replications_attempted": replications,
        "series_length": SERIES_LENGTH,
        "calibration_resamples": CALIBRATION_RESAMPLES,
        "null_generator": "GARCH(1,1), zero mean, same generator as event-bootstrap-calibration-v1",
        "wall_clock_seconds": time.time() - start,
        "two_sample_dow_style": {
            "trials": dow_trials,
            "eligible_hits": dow_hits,
            "empirical_eligibility_rate": dow_rate,
            "wilson_95_ci": [dow_lo, dow_hi],
            "naive_one_sided_16pct_approximation_note": (
                "A one-sided normal tail at ~1 SE (matching a 68%-coverage "
                "two-sided interval's lower bound) predicts ~15.9% under a "
                "true null, not the 32% two-sided-mass figure the critique "
                "used -- this measurement settles it empirically rather than "
                "by competing approximations."
            ),
            "real_result_for_comparison": "6/12 = 50.0% observed for Calendar Day-of-Week",
        },
        "case_resample_wave_pull_style": {
            "single_asset": {
                "trials": wave_pull_single_trials,
                "eligible_hits": wave_pull_single_hits,
                "empirical_eligibility_rate": wp_single_rate,
                "wilson_95_ci": [wp_single_lo, wp_single_hi],
            },
            "selected_winner_of_12": {
                "trials": wave_pull_winner_trials,
                "eligible_hits": wave_pull_winner_hits,
                "empirical_eligibility_rate": wp_winner_rate,
                "wilson_95_ci": [wp_winner_lo, wp_winner_hi],
                "note": (
                    "This is the 'winner's curse' rate the critique named: "
                    "among 12 independent NULL assets, how often does the "
                    "single best-observed one alone show up eligible. If "
                    "this materially exceeds the single-asset rate above, "
                    "selection bias is real and TLT's solo report overstates "
                    "confidence; if it's close to the single-asset rate, the "
                    "eligibility construction is more selection-robust than "
                    "the critique assumed."
                ),
            },
            "real_result_for_comparison": "TLT (selected as the best-p-value asset of 12) = eligible, multiplier 0.674",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replications", type=int, default=DEFAULT_REPLICATIONS)
    args = parser.parse_args()

    report = run(args.replications)
    output_path = OUTPUT_DIR / "calibration-report.json"
    _atomic_json(output_path, report)
    print(json.dumps(report, sort_keys=True, indent=2, default=str))
    print(f"\nWritten to {output_path}")


if __name__ == "__main__":
    main()
