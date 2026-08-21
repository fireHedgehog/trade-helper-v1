"""Ensemble-construction engine, real breadth test: 3 independent signals.

Usage (from backend/):
    python -m app.run_ensemble_smoke_test_v2

v1 (run_ensemble_smoke_test.py) proved the facility works but ended up
single-signal (atr_normalized's cross-sectional confidence multiplier came
out 0.0). Since then, two new independent candidates were found
(academic-anomalies-chapter4-v1.md): max_effect (confidence multiplier
0.56) and expected_skewness_proxy (0.81), both below this project's own
|r|>=0.5 redundancy threshold against amihud_illiquidity and each other.
This is the real breadth test the smoke test's own writeup said was still
missing: 3 independent, positive signals, combined for real.

Same disclosed placeholder as v1: stop distance uses a 2x-ATR(14)
approximation, not a per-strategy stop rule.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from . import ensemble, factor_zoo
from .research import block_bootstrap_confidence_interval, chapter4_confidence_multiplier
from .run_amihud_illiquidity_chapter4 import STANDARD_ROUND_TRIP_BPS, build_masked_panel
from .run_experiment import _atomic_json

ROOT = Path(__file__).parents[2]
EQUITY = 100_000.0
COVARIANCE_LOOKBACK = 252
SIGNALS = ["amihud_illiquidity", "max_effect", "expected_skewness_proxy"]


def _confidence_multiplier_for(name: str, masked_factor, close, flip: bool) -> tuple[float, dict, object]:
    evaluation = factor_zoo.evaluate_factor(
        name, masked_factor, close, round_trip_cost_bps=STANDARD_ROUND_TRIP_BPS
    )
    daily_returns = -evaluation.daily_spread_returns if flip else evaluation.daily_spread_returns
    ci = block_bootstrap_confidence_interval(daily_returns.to_numpy())
    multiplier = chapter4_confidence_multiplier(ci["observed_mean"], ci["lower_bound"])
    return multiplier, {
        "sharpe_correct_direction": evaluation.sharpe * (-1 if flip else 1),
        "observed_mean": ci["observed_mean"], "lower_bound": ci["lower_bound"],
        "confidence_multiplier": multiplier,
    }, evaluation


def main() -> None:
    panel, date_index, symbols, eligible = build_masked_panel()

    raw_by_signal = {}
    confidence_multipliers = {}
    stats_by_signal = {}
    for name in SIGNALS:
        formula = factor_zoo.ACADEMIC_ANOMALIES[name]
        masked = formula(panel).where(eligible)
        flip = name in factor_zoo.NEGATIVE_EXPECTED_DIRECTION
        mult, stats, _ = _confidence_multiplier_for(f"{name}_pit", masked, panel.close, flip)
        # If the correct-direction trade is "long low readings" (flip=True),
        # negate the raw per-symbol score too, so ranking direction matches
        # the direction that was actually confidence-scored.
        raw_by_signal[name] = -masked if flip else masked
        confidence_multipliers[name] = mult
        stats_by_signal[name] = stats

    t = len(date_index) - 1
    eligible_today = eligible.iloc[t]
    membership_eligible = [s for s in symbols if eligible_today[s]]
    has_full_history = (
        panel.returns[membership_eligible]
        .iloc[t - COVARIANCE_LOOKBACK + 1 : t + 1]
        .notna().all()
    )
    today_symbols = [s for s in membership_eligible if has_full_history[s]]

    raw_scores = {
        name: raw_by_signal[name].iloc[t][today_symbols].to_numpy(dtype=float)
        for name in SIGNALS
    }
    composite = ensemble.composite_alpha_scores(raw_scores, confidence_multipliers, today_symbols)

    returns_window = panel.returns[today_symbols].iloc[t - COVARIANCE_LOOKBACK + 1 : t + 1].to_numpy()
    covariance = ensemble.shrinkage_covariance(returns_window)

    prices = panel.close.iloc[t][today_symbols].to_numpy(dtype=float)
    atr14 = factor_zoo.atr_normalized(panel).mul(panel.close)
    stop_distances = np.clip(2.0 * atr14.iloc[t][today_symbols].to_numpy(dtype=float), 0.01, None)

    sizes = ensemble.construct_portfolio(
        composite, covariance, today_symbols, EQUITY, prices, stop_distances,
    )

    long_positions = {s: q for s, q in sizes.items() if q > 0}
    short_positions = {s: q for s, q in sizes.items() if q < 0}
    gross = sum(abs(q) * prices[today_symbols.index(s)] for s, q in sizes.items())
    net = sum(q * prices[today_symbols.index(s)] for s, q in sizes.items())

    result = {
        "as_of_date": str(date_index[t]),
        "eligible_universe_size": len(today_symbols),
        "signals_used": SIGNALS,
        "signal_confidence": stats_by_signal,
        "long_count": len(long_positions),
        "short_count": len(short_positions),
        "gross_exposure_pct_of_equity": gross / EQUITY * 100,
        "net_exposure_pct_of_equity": net / EQUITY * 100,
        "top_5_long": sorted(
            ((s, q * prices[today_symbols.index(s)]) for s, q in long_positions.items()),
            key=lambda x: -x[1],
        )[:5],
        "top_5_short": sorted(
            ((s, abs(q * prices[today_symbols.index(s)])) for s, q in short_positions.items()),
            key=lambda x: -x[1],
        )[:5],
    }

    output = ROOT / "output/research/ensemble-smoke-test-v2"
    _atomic_json(output / "result.json", result)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
