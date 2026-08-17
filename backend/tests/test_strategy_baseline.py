"""Frozen pre-refactor outputs for every default strategy.

These assertions are characterization tests, not claims that the results are
desirable or profitable. Stage 1 may intentionally update the baseline when it
fixes an execution defect, but each change must be explained and reviewed.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd
import pytest
from backtesting import Backtest

from app.engine import CASH, COMMISSION, to_ohlc
from app.strategies import STRATEGIES


BASELINE_PATH = Path(__file__).parent / "baselines" / "default_strategy_metrics.json"


def _metrics(bars: pd.DataFrame, strategy_name: str) -> dict:
    stats = Backtest(
        to_ohlc(bars),
        STRATEGIES[strategy_name],
        cash=CASH,
        commission=COMMISSION,
        finalize_trades=True,
    ).run()
    win_rate = float(stats["Win Rate [%]"])
    return {
        "trades": int(stats["# Trades"]),
        "return_pct": round(float(stats["Return [%]"]), 6),
        "buy_hold_pct": round(float(stats["Buy & Hold Return [%]"]), 6),
        "max_drawdown_pct": round(float(stats["Max. Drawdown [%]"]), 6),
        "win_rate_pct": None if math.isnan(win_rate) else round(win_rate, 6),
    }


@pytest.mark.parametrize("strategy_name", list(STRATEGIES))
def test_default_strategy_baseline(research_bars: pd.DataFrame, strategy_name: str) -> None:
    expected = json.loads(BASELINE_PATH.read_text())[strategy_name]
    actual = _metrics(research_bars, strategy_name)

    assert actual["trades"] == expected["trades"]
    assert actual["win_rate_pct"] == expected["win_rate_pct"]
    for metric in ("return_pct", "buy_hold_pct", "max_drawdown_pct"):
        assert actual[metric] == pytest.approx(expected[metric], abs=1e-5)
