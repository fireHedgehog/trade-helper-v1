"""ADR 0005 passive benchmark accounting checks."""

from __future__ import annotations

import math

import pandas as pd
import pytest

from app.portfolio import PortfolioConfig
from app.portfolio_benchmark import cash_benchmark, simulate_passive_benchmark


def _bars(prices: list[float]) -> pd.DataFrame:
    dates = ["2024-12-30", "2025-01-02", "2025-01-03", "2025-01-06"]
    return pd.DataFrame(
        {
            "date": dates,
            "open": prices,
            "high": [price * 1.01 for price in prices],
            "low": [price * 0.99 for price in prices],
            "close": prices,
            "volume": [1_000.0] * len(prices),
        }
    )


def test_equal_weight_benchmark_uses_whole_shares_costs_and_residual_cash() -> None:
    result = simulate_passive_benchmark(
        {"AAA": _bars([100, 100, 100, 100]), "BBB": _bars([100, 100, 100, 100])},
        name="test",
        annual_rebalance=False,
    )
    buys = result.fills
    assert [(fill.symbol, fill.shares) for fill in buys] == [("AAA", 499), ("BBB", 499)]
    assert all(fill.side == "buy" and fill.fee > 0 for fill in buys)
    assert result.equity[0].cash > 0
    assert result.metrics.total_fees == sum(fill.fee for fill in buys)
    assert result.metrics.total_return < 0


def test_annual_rebalance_waits_for_sale_settlement_before_buying() -> None:
    result = simulate_passive_benchmark(
        {"AAA": _bars([100, 200, 200, 200]), "BBB": _bars([100, 100, 100, 100])},
        name="test",
        annual_rebalance=True,
    )
    sells = [fill for fill in result.fills if fill.side == "sell"]
    later_buys = [
        fill
        for fill in result.fills
        if fill.side == "buy" and fill.date != "2024-12-30"
    ]
    assert sells and all(fill.date == "2025-01-02" for fill in sells)
    assert later_buys and all(fill.date == "2025-01-03" for fill in later_buys)
    assert result.equity[1].unsettled_cash > 0
    assert result.equity[2].unsettled_cash == 0


def test_benchmark_equity_and_daily_returns_reconcile() -> None:
    config = PortfolioConfig(commission=0, spread=0, slippage=0)
    result = simulate_passive_benchmark(
        {"AAA": _bars([100, 110, 105, 120]), "BBB": _bars([100, 90, 95, 80])},
        name="test",
        annual_rebalance=False,
        config=config,
    )
    previous = config.initial_cash
    for row in result.equity:
        assert row.equity == pytest.approx(row.cash + row.unsettled_cash + row.market_value)
        assert row.daily_return == pytest.approx(row.equity / previous - 1)
        previous = row.equity
    assert result.metrics.final_equity == result.equity[-1].equity


def test_benchmark_rejects_mismatched_calendars() -> None:
    changed = _bars([100, 100, 100, 100]).copy()
    changed.loc[1, "date"] = "2025-01-01"
    with pytest.raises(ValueError, match="calendar differs"):
        simulate_passive_benchmark(
            {"AAA": _bars([100, 100, 100, 100]), "BBB": changed},
            name="test",
            annual_rebalance=True,
        )


def test_cash_reference_compounds_declared_yield() -> None:
    dates = tuple(_bars([100, 100, 100, 100])["date"])
    result = cash_benchmark(dates, initial_cash=100_000, annual_cash_yield=0.05)
    assert result["final_equity"] > 100_000
    assert math.isclose(result["max_drawdown"], 0.0)
