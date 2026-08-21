"""Ensemble-construction engine smoke test -- does the new facility work?

Usage (from backend/):
    python -m app.run_ensemble_smoke_test

Not a new Stage 9A candidate and not a sizing decision. Combines the two
real, already-evaluated Chapter 4 signals this project has
(`atr_normalized`, `amihud_illiquidity`) through the real engine
(`backend/app/ensemble.py`) end to end, on real point-in-time data, for
the most recent available session -- exactly what the user asked for:
"2 factor is not enough... but at least > 1 so can do a smoke test of new
facility work or not." Confidence multipliers for both signals are
computed the same way (`factor_zoo.evaluate_factor` +
`block_bootstrap_confidence_interval` + `chapter4_confidence_multiplier`),
not invented, so the ensemble sees real inputs.

Disclosed placeholder: stop distance for the ADR 0004 position cap uses a
simple 2x-ATR(14) approximation per symbol (a common, real convention),
not a per-strategy stop rule -- a full implementation would use each
signal's own stop logic; this is a smoke test of the pipeline shape, not a
sizing proposal.
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


def _confidence_multiplier_for(name: str, masked_factor, close) -> tuple[float, dict]:
    evaluation = factor_zoo.evaluate_factor(
        name, masked_factor, close, round_trip_cost_bps=STANDARD_ROUND_TRIP_BPS
    )
    ci = block_bootstrap_confidence_interval(evaluation.daily_spread_returns.to_numpy())
    multiplier = chapter4_confidence_multiplier(ci["observed_mean"], ci["lower_bound"])
    return multiplier, {
        "sharpe": evaluation.sharpe, "cagr": evaluation.cagr,
        "observed_mean": ci["observed_mean"], "lower_bound": ci["lower_bound"],
        "confidence_multiplier": multiplier,
    }


def main() -> None:
    panel, date_index, symbols, eligible = build_masked_panel()

    raw_atr = factor_zoo.atr_normalized(panel).where(eligible)
    raw_amihud = factor_zoo.amihud_illiquidity(panel).where(eligible)

    mult_atr, stats_atr = _confidence_multiplier_for("atr_normalized_pit", raw_atr, panel.close)
    mult_amihud, stats_amihud = _confidence_multiplier_for("amihud_illiquidity_pit", raw_amihud, panel.close)

    # Most recent session with a full 252-day return history behind it.
    t = len(date_index) - 1
    eligible_today = eligible.iloc[t]
    membership_eligible = [s for s in symbols if eligible_today[s]]

    # A valid factor score at t is not the same requirement as a complete
    # trailing return history for the covariance step -- a recently-listed
    # S&P 500 member (e.g. added within the last year) can have both,
    # producing a real, silent NaN in shrinkage_covariance's diagonal for
    # that symbol alone (np.cov propagates NaN from an incomplete column).
    # Caught by this smoke test, not assumed: the eligibility mask must
    # cover every input the pipeline actually needs, not just the factor.
    has_full_history = (
        panel.returns[membership_eligible]
        .iloc[t - COVARIANCE_LOOKBACK + 1 : t + 1]
        .notna().all()
    )
    today_symbols = [s for s in membership_eligible if has_full_history[s]]
    dropped_for_history = len(membership_eligible) - len(today_symbols)

    raw_scores = {
        "atr_normalized": raw_atr.iloc[t][today_symbols].to_numpy(dtype=float),
        "amihud_illiquidity": raw_amihud.iloc[t][today_symbols].to_numpy(dtype=float),
    }
    confidence_multipliers = {"atr_normalized": mult_atr, "amihud_illiquidity": mult_amihud}
    composite = ensemble.composite_alpha_scores(raw_scores, confidence_multipliers, today_symbols)

    returns_window = panel.returns[today_symbols].iloc[t - COVARIANCE_LOOKBACK + 1 : t + 1].to_numpy()
    covariance = ensemble.shrinkage_covariance(returns_window)

    prices = panel.close.iloc[t][today_symbols].to_numpy(dtype=float)
    atr14 = factor_zoo.atr_normalized(panel).mul(panel.close)  # de-normalize back to price units
    stop_distances = np.clip(
        2.0 * atr14.iloc[t][today_symbols].to_numpy(dtype=float), 0.01, None
    )

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
        "dropped_for_incomplete_return_history": dropped_for_history,
        "signal_confidence": {"atr_normalized": stats_atr, "amihud_illiquidity": stats_amihud},
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

    output = ROOT / "output/research/ensemble-smoke-test-v1"
    _atomic_json(output / "result.json", result)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
