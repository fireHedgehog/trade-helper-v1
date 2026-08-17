"""Unit checks for canonical indicators, warm-up, and strategy rules."""

from __future__ import annotations

import pandas as pd
import pytest

from app.rules import atr, build_rules
from app.strategies import STRATEGY_PARAMS


def _defaults(strategy_name: str) -> dict:
    return {
        key: meta["default"] for key, meta in STRATEGY_PARAMS[strategy_name].items()
    }


def test_atr_uses_true_range() -> None:
    bars = pd.DataFrame(
        {
            "high": [11.0, 14.0, 13.0],
            "low": [9.0, 11.0, 10.0],
            "close": [10.0, 12.0, 11.0],
        }
    )
    values = atr(bars, 2)
    assert pd.isna(values.iloc[0])
    assert values.iloc[1:].tolist() == pytest.approx([3.0, 3.0])


@pytest.mark.parametrize("strategy_name", list(STRATEGY_PARAMS))
def test_default_rules_are_aligned_and_boolean(
    research_bars: pd.DataFrame, strategy_name: str
) -> None:
    rules = build_rules(research_bars, strategy_name, _defaults(strategy_name))
    assert rules.entries.index.equals(research_bars.index)
    assert rules.exits.index.equals(research_bars.index)
    assert rules.entries.dtype == bool
    assert rules.exits.dtype == bool
    assert rules.entries.any(), f"fixture must exercise {strategy_name} entries"


@pytest.mark.parametrize(
    ("strategy_name", "warmup"),
    [
        ("CTA Trend", 100),
        ("SMA Cross", 49),
        ("Donchian Trend", 55),
        ("S/R Bounce", 20),
        ("Fib Retrace", 60),
        ("Wave Pull", 8),
        ("RSI Reversion", 14),
    ],
)
def test_rules_do_not_fire_before_indicator_warmup(
    research_bars: pd.DataFrame, strategy_name: str, warmup: int
) -> None:
    rules = build_rules(research_bars, strategy_name, _defaults(strategy_name))
    assert not rules.entries.iloc[:warmup].any()
