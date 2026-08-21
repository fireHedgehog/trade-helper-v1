"""Remaining academic-anomalies factors: real point-in-time Chapter 4
evaluation, no p-value.

Usage (from backend/):
    python -m app.run_academic_anomalies_chapter4

factor-zoo-academic-anomalies-v1 closed `low_volatility` and `max_effect`
as "redundant with atr_normalized" (r=0.81-0.98) and left
`corwin_schultz_spread`/`expected_skewness_proxy` as clean nulls -- all
four using today's-membership data, no Chapter 4 evaluation. Since
atr_normalized's own cross-sectional form just failed point-in-time
correction (see ensemble-smoke-test-v1.md), "redundant with atr_normalized"
is no longer a reason to leave low_volatility/max_effect unexamined on
their own merits. This re-scores all four, masked to real point-in-time
S&P 500 membership, via Sharpe/CAGR/drawdown/Calmar/Calmar and a
block-bootstrap EV confidence interval -- not rank-IC alone, not a
p-value. Per this project's post-2026-08-21 rule, this is the default
instrument for a new (or re-scoped) candidate.

Sign handling: `max_effect` and `expected_skewness_proxy` are literature-
predicted to have a NEGATIVE raw spread under this harness's "high
reading = long" convention (lottery-demand overpricing -- the real trade
is long LOW readings, not high). Their daily spread-return series is
negated before computing Sharpe/CAGR/CI/confidence-multiplier, so a
positive result here means "the anomaly, correctly expressed, made
money" -- not "the raw convention happened to work."
"""
from __future__ import annotations

import json
from pathlib import Path

from . import factor_zoo
from .engine import COMMISSION, SLIPPAGE, SPREAD
from .research import block_bootstrap_confidence_interval, chapter4_confidence_multiplier
from .run_amihud_illiquidity_chapter4 import build_masked_panel
from .run_experiment import _atomic_json

ROOT = Path(__file__).parents[2]
STANDARD_ROUND_TRIP_BPS = (2 * COMMISSION + SPREAD + 2 * SLIPPAGE) * 10_000
FACTORS = ["low_volatility", "max_effect", "corwin_schultz_spread", "expected_skewness_proxy"]


def main() -> None:
    panel, date_index, symbols, eligible = build_masked_panel()

    results = {}
    for name in FACTORS:
        formula = factor_zoo.ACADEMIC_ANOMALIES[name]
        masked_factor = formula(panel).where(eligible)
        evaluation = factor_zoo.evaluate_factor(
            f"{name}_pit", masked_factor, panel.close,
            round_trip_cost_bps=STANDARD_ROUND_TRIP_BPS,
        )
        daily_returns = evaluation.daily_spread_returns
        flip = name in factor_zoo.NEGATIVE_EXPECTED_DIRECTION
        if flip:
            daily_returns = -daily_returns
        ci = block_bootstrap_confidence_interval(daily_returns.to_numpy())
        multiplier = chapter4_confidence_multiplier(ci["observed_mean"], ci["lower_bound"])
        results[name] = {
            "sign_flipped_for_expected_direction": flip,
            "n_days": evaluation.n_days,
            "n_symbols_median": evaluation.n_symbols_median,
            "ic_mean": evaluation.ic_mean,
            "sharpe_raw_direction": evaluation.sharpe,
            "cagr_raw_direction": evaluation.cagr,
            "max_drawdown_raw_direction": evaluation.max_drawdown,
            "calmar_raw_direction": evaluation.calmar,
            "round_trip_cost_bps": STANDARD_ROUND_TRIP_BPS,
            "daily_ev_confidence_interval_correct_direction": ci,
            "chapter4_confidence_multiplier": multiplier,
        }

    output = ROOT / "output/research/academic-anomalies-chapter4-v1"
    _atomic_json(
        output / "manifest.json",
        {
            "experiment_id": "academic-anomalies-chapter4-v1",
            "status": "exploratory",
            "evidential_status": "ahead of ADR 0007 clauses 1/2 formal sign-off",
            "universe": "same 501-symbol point-in-time universe as amihud-illiquidity-chapter4-v1",
            "no_p_value": True,
        },
    )
    _atomic_json(output / "result.json", results)
    print(json.dumps(results, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
