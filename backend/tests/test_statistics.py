"""Research-statistic semantics and explicit cost assumptions."""

from __future__ import annotations

import pandas as pd

from app.confidence import _cluster_bootstrap_summary, _non_overlapping_mask, _summarize
from app.execution import simulate
from app.engine import backtest_bars_payload


def test_costs_reduce_identical_strategy_result(research_bars: pd.DataFrame) -> None:
    params = {"n_fast": 20, "n_slow": 50}
    free = backtest_bars_payload(
        research_bars,
        "FIXTURE",
        "SMA Cross",
        params,
        commission=0,
        spread=0,
        slippage=0,
    )
    costed = backtest_bars_payload(
        research_bars,
        "FIXTURE",
        "SMA Cross",
        params,
        commission=0.001,
        spread=0.0002,
        slippage=0.0005,
    )
    assert costed["metrics"]["Return [%]"] < free["metrics"]["Return [%]"]
    assert costed["assumptions"]["commission_per_side"] == 0.001
    assert costed["assumptions"]["quoted_spread"] == 0.0002
    assert costed["assumptions"]["slippage_per_fill"] == 0.0005


def test_extended_risk_metrics_are_reported(research_bars: pd.DataFrame) -> None:
    payload = backtest_bars_payload(
        research_bars, "FIXTURE", "SMA Cross", {"n_fast": 20, "n_slow": 50}
    )
    metrics = payload["metrics"]
    for name in (
        "Exposure-Matched Benchmark [%]",
        "CAGR [%]",
        "Annual Volatility [%]",
        "Downside Deviation [%]",
        "Sortino Ratio",
        "Calmar Ratio",
        "Max. Drawdown Duration [bars]",
        "Expectancy [$]",
        "Expectancy [%]",
        "Annual Turnover [x]",
    ):
        assert name in metrics


def test_post_signal_intervals_include_uncertainty() -> None:
    summary = _summarize([0.10, 0.05, -0.02, 0.03, -0.01])
    assert summary["samples"] == 5
    assert summary["hit_rate"] == 60.0
    assert summary["hit_rate_ci95"][0] < 60 < summary["hit_rate_ci95"][1]
    assert summary["avg_return_ci95"][0] < summary["avg_return"]
    assert summary["avg_return_ci95"][1] > summary["avg_return"]
    assert summary["sufficient_sample"] is False


def test_cluster_bootstrap_is_deterministic_and_disclosed() -> None:
    observations = [
        (f"2024-{month:02d}-05", value)
        for month, value in enumerate([0.10, -0.02, 0.05, -0.03, 0.07, 0.01], start=1)
    ]
    first = _cluster_bootstrap_summary(observations)
    second = _cluster_bootstrap_summary(observations)
    assert first == second
    assert "cluster bootstrap" in first["ci_method"]


def test_forward_signal_samples_do_not_overlap() -> None:
    entries = pd.Series([True] * 45)
    valid = pd.Series([True] * 45)
    positions = list(_non_overlapping_mask(entries, valid)[lambda value: value].index)
    assert positions == [0, 20, 40]


def test_simulator_rejects_negative_trading_costs(research_bars: pd.DataFrame) -> None:
    try:
        simulate(research_bars, "SMA Cross", {"n_fast": 20, "n_slow": 50}, spread=-0.01)
    except ValueError as exc:
        assert "spread" in str(exc)
    else:
        raise AssertionError("negative spread must be rejected")
