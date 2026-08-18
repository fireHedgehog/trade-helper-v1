"""Stage 5 checks for portfolio-level return and risk reporting."""

from __future__ import annotations

from dataclasses import replace

import pandas as pd
import pytest

from app.portfolio import PortfolioConfig
from app.portfolio_execution import AssetClassification, simulate_portfolio
from app.portfolio_metrics import portfolio_metrics
from app.rules import RuleSet


def _bars(values: list[float]) -> pd.DataFrame:
    dates = pd.bdate_range("2026-01-05", periods=len(values))
    return pd.DataFrame(
        {
            "date": dates.strftime("%Y-%m-%d"),
            "open": values,
            "high": [value + 1 for value in values],
            "low": [value - 1 for value in values],
            "close": values,
            "volume": [1_000_000] * len(values),
        }
    )


def _rules(length: int, *, entry: int | None = None) -> RuleSet:
    return RuleSet(
        entries=pd.Series([index == entry for index in range(length)]),
        exits=pd.Series([False] * length),
        atr=pd.Series([float("nan")] * length),
        stop_levels=pd.Series([1.0] * length),
        target_levels=pd.Series([float("nan")] * length),
    )


def _replay(monkeypatch: pytest.MonkeyPatch, values: list[float], *, entry=None):
    bars = _bars(values)
    monkeypatch.setattr(
        "app.portfolio_execution.build_rules",
        lambda *_args, **_kwargs: _rules(len(bars), entry=entry),
    )
    config = PortfolioConfig(
        risk_per_trade=1,
        max_position_fraction=1,
        max_sector_fraction=1,
        max_cluster_fraction=1,
        commission=0,
        spread=0,
        slippage=0,
    )
    return simulate_portfolio(
        {"AAA": bars},
        strategy_name="S/R Bounce",
        params={},
        classifications={
            "AAA": AssetClassification(sector="Equity", cluster="Risk Asset")
        },
        config=config,
    )


def test_flat_account_metrics_are_defined_without_fake_ratios(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    replay = _replay(monkeypatch, [100, 100, 100, 100])

    metrics = portfolio_metrics(replay)

    assert [row.daily_return for row in replay.equity] == [None, 0, 0, 0]
    assert metrics.total_return == 0
    assert metrics.cagr == 0
    assert metrics.annual_volatility == 0
    assert metrics.sharpe is None
    assert metrics.sortino is None
    assert metrics.max_drawdown == 0
    assert metrics.annual_turnover == 0
    assert metrics.trade_count == 0
    assert metrics.win_rate is None
    assert metrics.profit_factor is None


def test_metrics_capture_kill_switch_loss_exposure_turnover_and_trade(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    replay = _replay(monkeypatch, [100, 100, 80, 70, 70], entry=0)

    metrics = portfolio_metrics(replay)

    assert [row.daily_return for row in replay.equity] == pytest.approx(
        [None, 0, -0.20, -0.125, 0], nan_ok=True
    )
    assert metrics.initial_equity == 100_000
    assert metrics.final_equity == 70_000
    assert metrics.total_return == pytest.approx(-0.30)
    assert metrics.max_drawdown == pytest.approx(-0.30)
    assert metrics.max_drawdown_bars == 3
    assert metrics.max_gross_exposure == 1
    assert metrics.max_sector_concentration == 1
    assert metrics.max_cluster_concentration == 1
    assert metrics.annual_turnover > 0
    assert metrics.trade_count == 1
    assert metrics.win_rate == 0
    assert metrics.profit_factor == 0
    assert metrics.expectancy == -30_000
    assert metrics.realized_pnl == -30_000
    assert metrics.risk_event_count == 1
    assert metrics.halted


def test_metrics_reject_daily_return_that_disagrees_with_equity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    replay = _replay(monkeypatch, [100, 100, 100])
    corrupted = replace(
        replay,
        equity=(
            replay.equity[0],
            replace(replay.equity[1], daily_return=0.5),
            replay.equity[2],
        ),
    )

    with pytest.raises(ValueError, match="does not match"):
        portfolio_metrics(corrupted)


def test_metrics_do_not_claim_an_undefined_portfolio_benchmark(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    metrics = portfolio_metrics(_replay(monkeypatch, [100, 101, 102]))

    assert not hasattr(metrics, "benchmark_return")
    assert not hasattr(metrics, "excess_return")
