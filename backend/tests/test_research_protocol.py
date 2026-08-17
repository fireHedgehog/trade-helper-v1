"""Chronological research partitions must make future leakage difficult."""

from __future__ import annotations

import pandas as pd
import pytest

from app.research import (
    CandidateWindowEvaluation,
    evaluate_candidate_window,
    evaluate_window,
    partition_candidate_holdout,
    select_validation_candidate,
    walk_forward_folds,
)


COSTS = {
    "commission_per_side": 0.001,
    "quoted_spread": 0.0002,
    "slippage_per_fill": 0.0005,
    "annual_cash_yield": 0.0,
}


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
    assert result.bars == len(result.dates)
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


def test_candidate_uses_locked_symbols_and_common_dates(
    research_bars: pd.DataFrame,
) -> None:
    result = evaluate_candidate_window(
        {"ONE": research_bars, "TWO": research_bars.copy()},
        universe=["ONE", "TWO", "MISSING"],
        strategy_name="SMA Cross",
        params={"n_fast": 20, "n_slow": 50},
        training_start=str(research_bars["date"].iloc[0]),
        start=str(research_bars["date"].iloc[300]),
        end=str(research_bars["date"].iloc[500]),
        minimum_symbols=2,
        costs=COSTS,
    )
    assert result.eligible_symbols == ("ONE", "TWO")
    assert result.excluded_symbols == (("MISSING", "missing"),)
    assert len(result.dates) == len(result.excess_daily_returns)
    assert len(result.dates) == len(result.strategy_daily_returns)
    assert len(result.dates) == len(result.benchmark_daily_returns)
    assert result.total_closed_trades >= 0


def test_candidate_fails_closed_on_insufficient_coverage(
    research_bars: pd.DataFrame,
) -> None:
    with pytest.raises(ValueError, match="eligible symbols"):
        evaluate_candidate_window(
            {"ONE": research_bars},
            universe=["ONE", "MISSING"],
            strategy_name="SMA Cross",
            params={"n_fast": 20, "n_slow": 50},
            training_start=str(research_bars["date"].iloc[0]),
            start=str(research_bars["date"].iloc[300]),
            end=str(research_bars["date"].iloc[500]),
            minimum_symbols=2,
            costs=COSTS,
        )


def _candidate(name: str, excess: float, score: float) -> CandidateWindowEvaluation:
    return CandidateWindowEvaluation(
        candidate=name,
        params={"name": name},
        eligible_symbols=("ONE", "TWO"),
        excluded_symbols=(),
        median_strategy_return=score,
        median_benchmark_return=0.0,
        median_excess_return=score,
        median_calmar=1.0,
        median_max_drawdown=-0.1,
        median_exposure=0.5,
        total_closed_trades=10,
        dates=tuple(f"2024-01-{day:02d}" for day in range(1, 21)),
        strategy_daily_returns=(excess,) * 20,
        benchmark_daily_returns=(0.0,) * 20,
        excess_daily_returns=(excess,) * 20,
    )


def test_selection_chooses_best_significant_candidate() -> None:
    selected, report = select_validation_candidate(
        [_candidate("lower", 0.01, 0.02), _candidate("higher", 0.02, 0.03)],
        block_bars=4,
        resamples=200,
        alpha=0.05,
        expected_family_size=2,
    )
    assert selected is not None
    assert selected.candidate == "higher"
    assert all(row["reject_zero_excess"] for row in report)


def test_selection_holds_cash_when_nothing_survives() -> None:
    selected, report = select_validation_candidate(
        [_candidate("flat-a", 0.0, 0.0), _candidate("flat-b", 0.0, 0.0)],
        block_bars=4,
        resamples=100,
        alpha=0.05,
        expected_family_size=2,
    )
    assert selected is None
    assert not any(row["reject_zero_excess"] for row in report)


def test_selection_requires_complete_declared_family() -> None:
    with pytest.raises(ValueError, match="expected 2"):
        select_validation_candidate(
            [_candidate("only", 0.01, 0.01)],
            block_bars=4,
            resamples=100,
            alpha=0.05,
            expected_family_size=2,
        )
