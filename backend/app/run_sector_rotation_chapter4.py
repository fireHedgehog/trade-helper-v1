"""Sector rotation, evaluated as a Chapter 4 candidate: real backtest, real
Sharpe/CAGR/drawdown, block-bootstrap EV confidence interval -- not a
falsification p-value.

Usage (from backend/):
    python -m app.run_sector_rotation_chapter4

Chapter 2's sector-rotation-v1 protocol asked "is pooled sector rank
correlation distinguishable from a temporally-scrambled null" and closed
`not_material_or_not_consistent` -- the correct answer to that specific
question, but the wrong question for a modest, potentially episodic,
personally-observed edge (per direct user feedback, 2026-08-21): that
question belongs to Chapter 4 (ADR 0007), evaluated on realized Sharpe/EV
with a bootstrap confidence interval, not a null-hypothesis test.

Trading rule (a real entry/exit rule, not sector-rotation-v1's fixed
monthly rebalance): at each session t, rank the 11 GICS sectors by
trailing 252-session return (computed through close t). Long the top-3
ranked sectors, short the bottom-3, equal-weighted within each side,
50%/50% gross (ADR 0010's default market-neutral split). Positions change
only when the top-3/bottom-3 SET changes from the prior session (holds
through a ranking that doesn't change, rather than rebalancing on a fixed
calendar) -- this is the entry/exit rule Chapter 2's design lacked.

No transaction cost, slippage, or capacity model -- explicitly exploratory,
ahead of ADR 0007 clauses 1/2 formal sign-off, same status
`atr_normalized`'s own Tier A translation carried before its own mechanism
was written down.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .research import block_bootstrap_confidence_interval, chapter4_confidence_multiplier
from .run_experiment import _atomic_json
from .run_sector_rotation_v1 import build_sector_panel

ROOT = Path(__file__).parents[2]
SPEC_PATH = ROOT / "research/experiments/sector-rotation-v1.json"
FORMATION_WINDOW = 252
TOP_K = 3
BOTTOM_K = 3
LONG_GROSS = 0.5
SHORT_GROSS = 0.5
TRADING_DAYS_PER_YEAR = 252


def _rank_sets(sector_levels: dict[str, np.ndarray], t: int, formation: int) -> tuple[frozenset, frozenset]:
    sectors = sorted(sector_levels)
    formation_returns = {
        s: sector_levels[s][t] / sector_levels[s][t - formation] - 1 for s in sectors
    }
    ordered = sorted(sectors, key=lambda s: formation_returns[s], reverse=True)
    return frozenset(ordered[:TOP_K]), frozenset(ordered[-BOTTOM_K:])


def backtest(sector_levels: dict[str, np.ndarray], date_index: pd.Index) -> dict:
    sectors = sorted(sector_levels)
    n = len(date_index)
    daily_returns = {
        s: np.concatenate([[0.0], sector_levels[s][1:] / sector_levels[s][:-1] - 1])
        for s in sectors
    }

    portfolio_returns = np.zeros(n)
    long_set: frozenset = frozenset()
    short_set: frozenset = frozenset()
    rebalance_count = 0
    for t in range(FORMATION_WINDOW, n - 1):
        new_long, new_short = _rank_sets(sector_levels, t, FORMATION_WINDOW)
        if new_long != long_set or new_short != short_set:
            rebalance_count += 1
        long_set, short_set = new_long, new_short
        long_ret = np.mean([daily_returns[s][t + 1] for s in long_set])
        short_ret = np.mean([daily_returns[s][t + 1] for s in short_set])
        portfolio_returns[t + 1] = LONG_GROSS * long_ret - SHORT_GROSS * short_ret

    active = portfolio_returns[FORMATION_WINDOW + 1:]
    equity = 100.0 * np.cumprod(1.0 + active)
    running_max = np.maximum.accumulate(equity)
    drawdown = equity / running_max - 1.0

    total_return = equity[-1] / 100.0 - 1.0
    years = len(active) / TRADING_DAYS_PER_YEAR
    cagr = (equity[-1] / 100.0) ** (1 / years) - 1 if years > 0 else float("nan")
    ann_vol = float(np.std(active, ddof=1) * np.sqrt(TRADING_DAYS_PER_YEAR))
    ann_return = float(np.mean(active) * TRADING_DAYS_PER_YEAR)
    sharpe = ann_return / ann_vol if ann_vol > 0 else float("nan")
    max_drawdown = float(drawdown.min())
    calmar = cagr / abs(max_drawdown) if max_drawdown < 0 else float("nan")

    # Benchmark: equal-weighted, always-long, all-11-sector buy-and-hold.
    bench_returns = np.mean(
        [daily_returns[s][FORMATION_WINDOW + 1:] for s in sectors], axis=0
    )
    bench_equity = 100.0 * np.cumprod(1.0 + bench_returns)
    bench_cagr = (bench_equity[-1] / 100.0) ** (1 / years) - 1 if years > 0 else float("nan")

    ci = block_bootstrap_confidence_interval(active)
    multiplier = chapter4_confidence_multiplier(ci["observed_mean"], ci["lower_bound"])

    return {
        "session_count": len(active),
        "rebalance_count": rebalance_count,
        "total_return": total_return,
        "cagr": cagr,
        "annualized_return": ann_return,
        "annualized_vol": ann_vol,
        "sharpe": sharpe,
        "max_drawdown": max_drawdown,
        "calmar": calmar,
        "benchmark_cagr": bench_cagr,
        "daily_ev_confidence_interval": ci,
        "chapter4_confidence_multiplier": multiplier,
    }


def main() -> None:
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    sector_levels, date_index, coverage = build_sector_panel(spec)
    result = backtest(sector_levels, date_index)

    output = ROOT / "output/research/sector-rotation-chapter4-v1"
    _atomic_json(
        output / "manifest.json",
        {
            "experiment_id": "sector-rotation-chapter4-v1",
            "status": "exploratory",
            "evidential_status": "ahead of ADR 0007 clauses 1/2 formal sign-off",
            "rule": f"long top-{TOP_K}, short bottom-{BOTTOM_K} GICS sectors by trailing {FORMATION_WINDOW}-session return, rebalance on rank-set change only",
            "no_cost_model": True,
            "coverage": coverage,
        },
    )
    _atomic_json(output / "result.json", result)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
