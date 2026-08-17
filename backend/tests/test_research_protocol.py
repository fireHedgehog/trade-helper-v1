"""Chronological research partitions must make future leakage difficult."""

from __future__ import annotations

import pandas as pd
import pytest

from app.research import evaluate_window, partition_candidate_holdout, walk_forward_folds


def test_candidate_holdout_is_removed_from_development(research_bars: pd.DataFrame) -> None:
    development, holdout = partition_candidate_holdout(research_bars, holdout_bars=100)
    assert len(development) == len(research_bars) - 100
    assert development["date"].iloc[-1] < holdout.start
    assert holdout.end == research_bars["date"].iloc[-1]


def test_walk_forward_boundaries_are_strictly_chronological(
    research_bars: pd.DataFrame,
) -> None:
    development, _ = partition_candidate_holdout(research_bars, holdout_bars=100)
    folds = walk_forward_folds(
        development, train_bars=200, validation_bars=50, test_bars=50
    )
    assert len(folds) > 1
    for fold in folds:
        assert fold.train_end < fold.validation_start
        assert fold.validation_end < fold.test_start
        assert fold.test_end <= development["date"].iloc[-1]
    assert [fold.train_bars for fold in folds] == sorted(
        fold.train_bars for fold in folds
    )


@pytest.mark.parametrize(
    "kwargs",
    [
        {"train_bars": 0, "validation_bars": 20, "test_bars": 20},
        {"train_bars": 200, "validation_bars": -1, "test_bars": 20},
        {"train_bars": 200, "validation_bars": 20, "test_bars": 0},
    ],
)
def test_walk_forward_rejects_invalid_sizes(
    research_bars: pd.DataFrame, kwargs: dict
) -> None:
    with pytest.raises(ValueError, match="must be positive"):
        walk_forward_folds(research_bars, **kwargs)


def _evaluation(bars: pd.DataFrame, **costs):
    return evaluate_window(
        bars,
        strategy_name="SMA Cross",
        params={"n_fast": 20, "n_slow": 50},
        start=str(bars["date"].iloc[300]),
        end=str(bars["date"].iloc[500]),
        **costs,
    )


def test_window_returns_and_benchmark_have_identical_dates(
    research_bars: pd.DataFrame,
) -> None:
    result = _evaluation(research_bars)
    assert result.actual_start >= result.requested_start
    assert result.actual_end == result.requested_end
    assert result.bars == len(result.strategy_daily_returns)
    assert result.bars == len(result.benchmark_daily_returns)
    assert result.bars == len(result.excess_daily_returns)
    assert result.excess_daily_returns == tuple(
        strategy - benchmark
        for strategy, benchmark in zip(
            result.strategy_daily_returns, result.benchmark_daily_returns
        )
    )


def test_future_bars_cannot_change_earlier_window(research_bars: pd.DataFrame) -> None:
    baseline = _evaluation(research_bars)
    mutated = research_bars.copy()
    future = mutated["date"] > baseline.requested_end
    mutated.loc[future, ["open", "high", "low", "close"]] *= 10
    changed_future = _evaluation(mutated)
    assert changed_future == baseline


def test_fold_window_includes_costs(research_bars: pd.DataFrame) -> None:
    free = _evaluation(research_bars, commission=0, spread=0, slippage=0)
    costed = _evaluation(
        research_bars, commission=0.001, spread=0.0002, slippage=0.0005
    )
    assert costed.strategy_return < free.strategy_return


def test_window_rejects_reversed_dates(research_bars: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="start"):
        evaluate_window(
            research_bars,
            strategy_name="SMA Cross",
            params={"n_fast": 20, "n_slow": 50},
            start="2022-01-01",
            end="2021-01-01",
        )
