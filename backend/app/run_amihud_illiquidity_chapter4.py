"""amihud_illiquidity: real long-short portfolio backtest, point-in-time
universe -- Chapter 4 evaluation, no p-value.

Usage (from backend/):
    python -m app.run_amihud_illiquidity_chapter4

factor-zoo-v1 (Sec.5d) already screened amihud_illiquidity via rank-IC and
a daily-rebalanced quintile spread, cost-checked (Sharpe 0.70 -> 0.29), but
using the same today's-membership universe every factor-zoo screen has used
-- the same reverse-survivorship contamination CS-01 fixed for individual-
stock momentum. This reruns the same, already-built, already-tested engine
(factor_zoo.evaluate_factor, unmodified) with the factor masked to real
point-in-time S&P 500 membership first, to see whether the edge survives
that fix -- and reports Sharpe/CAGR/drawdown/Calmar plus a block-bootstrap
EV confidence interval, matching this project's post-2026-08-21 rule that
a new (or re-scoped) evaluation defaults to Chapter 4's instruments, not a
falsification protocol.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from . import factor_zoo
from .engine import COMMISSION, SLIPPAGE, SPREAD
from .research import block_bootstrap_confidence_interval, chapter4_confidence_multiplier
from .run_cross_sectional_momentum_v1 import _membership_intervals
from .run_experiment import _atomic_json
from .store import connect, load_bars

ROOT = Path(__file__).parents[2]
CS01_SPEC_PATH = ROOT / "research/experiments/cross-sectional-momentum-v1.json"
STANDARD_ROUND_TRIP_BPS = (2 * COMMISSION + SPREAD + 2 * SLIPPAGE) * 10_000
ALIGNMENT_START = "2001-01-01"


def _symbol_universe() -> list[str]:
    spec = json.loads(CS01_SPEC_PATH.read_text(encoding="utf-8"))
    return list(spec["universe"])


def build_masked_panel() -> tuple[factor_zoo.Panel, pd.Index, list[str]]:
    symbols = _symbol_universe()
    spy = load_bars("SPY")
    calendar = spy[spy["date"] >= ALIGNMENT_START]["date"].reset_index(drop=True)
    date_index = pd.Index(calendar)
    date_values = date_index.to_numpy()
    n = len(date_index)

    frames = {col: {} for col in ("open", "high", "low", "close", "volume")}
    for symbol in symbols:
        bars = load_bars(symbol)
        bars = bars[bars["date"] >= ALIGNMENT_START].set_index("date")
        for col in frames:
            frames[col][symbol] = bars[col].reindex(date_index)
    frames = {col: pd.DataFrame(data, index=date_index) for col, data in frames.items()}

    intervals = _membership_intervals()
    by_symbol = {symbol: group for symbol, group in intervals.groupby("symbol")}
    eligible = pd.DataFrame(False, index=date_index, columns=symbols)
    for symbol in symbols:
        mask = np.zeros(n, dtype=bool)
        group = by_symbol.get(symbol)
        if group is not None:
            for row in group.itertuples(index=False):
                end = "9999-12-31" if pd.isna(row.end_date) else row.end_date
                mask |= (date_values >= row.start_date) & (date_values <= end)
        eligible[symbol] = mask

    panel = factor_zoo.Panel.build(
        frames["open"], frames["high"], frames["low"], frames["close"], frames["volume"]
    )
    return panel, date_index, symbols, eligible


def main() -> None:
    panel, date_index, symbols, eligible = build_masked_panel()
    raw_factor = factor_zoo.amihud_illiquidity(panel)
    masked_factor = raw_factor.where(eligible)

    evaluation = factor_zoo.evaluate_factor(
        "amihud_illiquidity_pit", masked_factor, panel.close,
        round_trip_cost_bps=STANDARD_ROUND_TRIP_BPS,
    )
    ci = block_bootstrap_confidence_interval(evaluation.daily_spread_returns.to_numpy())
    multiplier = chapter4_confidence_multiplier(ci["observed_mean"], ci["lower_bound"])

    result = {
        "universe_size": len(symbols),
        "n_days": evaluation.n_days,
        "n_symbols_median": evaluation.n_symbols_median,
        "ic_mean": evaluation.ic_mean,
        "ic_ir": evaluation.ic_ir,
        "sharpe": evaluation.sharpe,
        "cagr": evaluation.cagr,
        "annual_volatility": evaluation.annual_volatility,
        "max_drawdown": evaluation.max_drawdown,
        "calmar": evaluation.calmar,
        "win_rate": evaluation.win_rate,
        "total_return": evaluation.total_return,
        "round_trip_cost_bps": STANDARD_ROUND_TRIP_BPS,
        "daily_ev_confidence_interval": ci,
        "chapter4_confidence_multiplier": multiplier,
    }

    output = ROOT / "output/research/amihud-illiquidity-chapter4-v1"
    _atomic_json(
        output / "manifest.json",
        {
            "experiment_id": "amihud-illiquidity-chapter4-v1",
            "status": "exploratory",
            "evidential_status": "ahead of ADR 0007 clauses 1/2 formal sign-off",
            "universe": "same 501-symbol point-in-time universe as cross-sectional-momentum-v1, masked to real SP500 membership before scoring",
            "no_p_value": True,
        },
    )
    _atomic_json(output / "result.json", result)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
