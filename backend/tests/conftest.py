"""Deterministic, network-free fixtures for trading-engine tests."""

from __future__ import annotations

import math

import pandas as pd
import pytest


def make_research_bars() -> pd.DataFrame:
    """Synthetic daily OHLC with trends, reversals, gaps, and missing dates.

    The values are deliberately deterministic. They are not intended to resemble
    a particular security or prove that a strategy works; they only freeze engine
    behaviour so refactors cannot silently change fills or metrics.
    """
    dates = pd.bdate_range("2020-01-02", periods=640)
    skipped = {87, 211, 389, 512}  # market/data gaps
    rows: list[dict] = []
    previous_close = 100.0

    for index, date in enumerate(dates):
        if index in skipped:
            continue

        if index < 120:
            drift = 0.35
        elif index < 200:
            drift = -0.55
        elif index < 360:
            drift = 0.50
        elif index < 455:
            drift = -0.45
        else:
            drift = 0.40

        cycle = 0.75 * math.sin(index / 5.0) + 0.35 * math.sin(index / 17.0)
        shock = {120: -7.0, 200: 10.0, 360: -8.0, 455: 10.0}.get(index, 0.0)
        close = max(5.0, previous_close + drift + cycle * 0.18 + shock)

        gap = 0.0
        if index in {121, 361}:
            gap = -3.5
        elif index in {201, 456}:
            gap = 2.5
        open_price = max(4.0, previous_close + gap + 0.12 * math.sin(index / 3.0))
        intraday = 0.65 + 0.25 * abs(math.sin(index / 7.0))
        high = max(open_price, close) + intraday
        low = min(open_price, close) - intraday

        rows.append(
            {
                "date": date.strftime("%Y-%m-%d"),
                "open": round(open_price, 4),
                "high": round(high, 4),
                "low": round(low, 4),
                "close": round(close, 4),
                "volume": 1_000_000 + index * 1_000,
            }
        )
        previous_close = close

    return pd.DataFrame(rows)


@pytest.fixture(scope="session")
def research_bars() -> pd.DataFrame:
    return make_research_bars()


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"
