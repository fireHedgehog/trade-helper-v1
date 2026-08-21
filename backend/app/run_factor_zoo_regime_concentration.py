"""ADR 0007 clause 5's regime-concentration check for atr_normalized --
Chapter 4 Sec.5's one surviving candidate (factor-zoo-cost-sensitivity-v1
closed the reversal cluster on cost grounds; this is the other named
next step for the one that survived).

Usage (from backend/):
    python -m app.run_factor_zoo_regime_concentration

Clause 5 requires the positive point estimate be disclosed "alongside
what fraction of it traces to any single year or episode (the same
calculation CTA v2's own closed result already discloses)" -- see
cta-v2-pooled-trend-overlay.md's regime diagnostic. That check spot-tested
3 named crisis years against a 20-year sample; atr_normalized's sample is
~8 years, short enough to sweep every year rather than a chosen few --
more complete, not a different calculation
(factor_zoo.regime_concentration_by_year).
"""
from __future__ import annotations

import json
from pathlib import Path

from . import factor_zoo
from .run_experiment import _atomic_json
from .run_factor_zoo_scan import load_universe_panels

ROOT = Path(__file__).parents[2]
OUTPUT_DIR = ROOT / "output/research/factor-zoo-regime-concentration-v1"
MIN_SYMBOLS = 30
FACTOR_NAME = "atr_normalized"


def main() -> None:
    panel, present_symbols, missing_symbols = load_universe_panels()
    factor_values = factor_zoo.CLASSIC_INDICATORS[FACTOR_NAME](panel)
    evaluation = factor_zoo.evaluate_factor(
        FACTOR_NAME, factor_values, panel.close, min_symbols=MIN_SYMBOLS
    )
    concentration = factor_zoo.regime_concentration_by_year(evaluation.daily_spread_returns)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "factor": FACTOR_NAME,
        "universe_size": len(present_symbols),
        "missing_symbols": missing_symbols,
        "common_date_start": str(panel.close.index[0]),
        "common_date_end": str(panel.close.index[-1]),
        "sharpe": evaluation.sharpe,
        "cagr": evaluation.cagr,
        "max_drawdown": evaluation.max_drawdown,
        "evidential_status": "non-evidential -- screening scan only, same standing as factor-zoo-v1",
        "regime_concentration": concentration,
    }
    _atomic_json(OUTPUT_DIR / "regime-concentration-report.json", report)

    print(json.dumps({
        "output": str(OUTPUT_DIR),
        "factor": FACTOR_NAME,
        "sharpe": evaluation.sharpe,
        "full_sample_mean": concentration["full_sample_mean"],
        "any_year_flips_sign": concentration["any_year_flips_sign"],
        "by_year": concentration["by_year"],
    }, indent=2, default=str))


if __name__ == "__main__":
    main()
