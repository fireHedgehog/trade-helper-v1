"""Checks for the frozen Stage 0 research fixture."""

from __future__ import annotations

import pandas as pd


def test_fixture_is_valid_ohlc(research_bars: pd.DataFrame) -> None:
    assert len(research_bars) == 636
    assert research_bars["date"].is_monotonic_increasing
    assert research_bars["date"].is_unique
    assert (research_bars[["open", "high", "low", "close"]] > 0).all().all()
    assert (research_bars["high"] >= research_bars[["open", "close"]].max(axis=1)).all()
    assert (research_bars["low"] <= research_bars[["open", "close"]].min(axis=1)).all()


def test_fixture_contains_gaps_and_reversals(research_bars: pd.DataFrame) -> None:
    dates = pd.to_datetime(research_bars["date"])
    business_steps = dates.diff().dt.days.fillna(1)
    overnight_gap = (research_bars["open"] / research_bars["close"].shift(1) - 1).abs()
    daily_return = research_bars["close"].pct_change()

    assert (business_steps > 3).any()
    assert (overnight_gap > 0.02).any()
    assert (daily_return > 0.03).any()
    assert (daily_return < -0.03).any()
