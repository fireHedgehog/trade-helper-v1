"""ATR Vol Premium: real per-symbol backtest survey -- Sharpe, CAGR,
drawdown, no p-value.

Usage (from backend/):
    python -m app.run_atr_vol_premium_survey

Direct user feedback (2026-08-21): ATR Vol Premium has run live in the app
since it was built, but nothing documents its actual performance --
Strategy Management shows "no closed result yet" because no falsification
protocol has been run against it, and this project has separately been
told (correctly) to stop defaulting to falsification for Chapter-4-sourced
candidates. The gap is real: not running a p-value test does not mean not
documenting anything. This script runs the strategy's own real backtest
engine (backend/app/engine.py:backtest_payload -- real commission, spread,
slippage, the same engine every Tier A strategy in this app already uses)
across the same 501-symbol point-in-time universe cross-sectional-momentum-v1
locked, and reports the real cross-sectional distribution of Sharpe, CAGR,
and drawdown -- not a single cherry-picked symbol, not a null-hypothesis
test.

Exploratory status, ahead of ADR 0007 clauses 1/2 formal sign-off, same as
run_sector_rotation_chapter4.py.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from .engine import backtest_payload
from .run_experiment import _atomic_json

ROOT = Path(__file__).parents[2]
CS01_SPEC_PATH = ROOT / "research/experiments/cross-sectional-momentum-v1.json"
STRATEGY_NAME = "ATR Vol Premium"
MIN_BARS = 300  # need real formation + lookback history to be meaningful
# Common window for every symbol -- each symbol's own full history varies from
# a few years to five decades (e.g. AAPL), which makes "beat buy & hold" and
# drawdown comparisons meaningless across symbols unless the window is fixed.
# 2015-01-01 onward: long enough to include 2020 and 2022, short enough that
# most of the 501-symbol universe has real coverage.
WINDOW_START = "2015-01-01"


def _symbol_universe() -> list[str]:
    spec = json.loads(CS01_SPEC_PATH.read_text(encoding="utf-8"))
    return list(spec["universe"])


def run_survey() -> dict:
    symbols = _symbol_universe()
    per_symbol = []
    skipped = []
    for symbol in symbols:
        try:
            payload = backtest_payload(symbol, STRATEGY_NAME, start=WINDOW_START)
        except Exception as exc:
            skipped.append({"symbol": symbol, "reason": str(exc)})
            continue
        metrics = payload["metrics"]
        if metrics.get("# Trades", 0) < 1:
            skipped.append({"symbol": symbol, "reason": "zero trades in this window"})
            continue
        per_symbol.append(
            {
                "symbol": symbol,
                "return_pct": metrics.get("Return [%]"),
                "buy_hold_pct": metrics.get("Buy & Hold Return [%]"),
                "cagr_pct": metrics.get("CAGR [%]"),
                "sharpe": metrics.get("Sharpe Ratio"),
                "calmar": metrics.get("Calmar Ratio"),
                "max_drawdown_pct": metrics.get("Max. Drawdown [%]"),
                "win_rate_pct": metrics.get("Win Rate [%]"),
                "profit_factor": metrics.get("Profit Factor"),
                "trades": metrics.get("# Trades"),
            }
        )

    sharpes = np.array([r["sharpe"] for r in per_symbol if r["sharpe"] is not None])
    cagrs = np.array([r["cagr_pct"] for r in per_symbol if r["cagr_pct"] is not None])
    excess = np.array(
        [
            r["return_pct"] - r["buy_hold_pct"]
            for r in per_symbol
            if r["return_pct"] is not None and r["buy_hold_pct"] is not None
        ]
    )
    drawdowns = np.array([r["max_drawdown_pct"] for r in per_symbol if r["max_drawdown_pct"] is not None])
    calmars = np.array(
        [r["calmar"] for r in per_symbol if r["calmar"] is not None and np.isfinite(r["calmar"])]
    )
    profit_factors = np.array(
        [
            r["profit_factor"]
            for r in per_symbol
            if r["profit_factor"] is not None and np.isfinite(r["profit_factor"])
        ]
    )
    win_rates = np.array([r["win_rate_pct"] for r in per_symbol if r["win_rate_pct"] is not None])
    trade_counts = np.array([r["trades"] for r in per_symbol if r["trades"] is not None])

    summary = {
        "symbols_run": len(per_symbol),
        "symbols_skipped": len(skipped),
        "median_sharpe": float(np.median(sharpes)) if len(sharpes) else None,
        "mean_sharpe": float(np.mean(sharpes)) if len(sharpes) else None,
        "pct_positive_sharpe": float(np.mean(sharpes > 0) * 100) if len(sharpes) else None,
        "median_cagr_pct": float(np.median(cagrs)) if len(cagrs) else None,
        "median_calmar": float(np.median(calmars)) if len(calmars) else None,
        "median_profit_factor": float(np.median(profit_factors)) if len(profit_factors) else None,
        "median_win_rate_pct": float(np.median(win_rates)) if len(win_rates) else None,
        "median_trade_count": float(np.median(trade_counts)) if len(trade_counts) else None,
        "pct_beat_buy_hold": float(np.mean(excess > 0) * 100) if len(excess) else None,
        "median_excess_vs_buy_hold_pct": float(np.median(excess)) if len(excess) else None,
        "median_max_drawdown_pct": float(np.median(drawdowns)) if len(drawdowns) else None,
        "worst_max_drawdown_pct": float(np.min(drawdowns)) if len(drawdowns) else None,
    }
    return {"summary": summary, "per_symbol": per_symbol, "skipped": skipped}


def main() -> None:
    result = run_survey()
    output = ROOT / "output/research/atr-vol-premium-survey-v1"
    _atomic_json(output / "manifest.json", {"strategy": STRATEGY_NAME, "status": "exploratory"})
    _atomic_json(output / "summary.json", result["summary"])
    _atomic_json(output / "per-symbol.json", result["per_symbol"])
    print(json.dumps(result["summary"], indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
