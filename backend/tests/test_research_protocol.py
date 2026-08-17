"""Chronological research partitions must make future leakage difficult."""

from __future__ import annotations

import pandas as pd
import pytest

from app.research import reserve_final_holdout, walk_forward_folds


def test_final_holdout_is_removed_from_development(research_bars: pd.DataFrame) -> None:
    development, holdout = reserve_final_holdout(research_bars, holdout_bars=100)
    assert len(development) == len(research_bars) - 100
    assert development["date"].iloc[-1] < holdout.start
    assert holdout.end == research_bars["date"].iloc[-1]


def test_walk_forward_boundaries_are_strictly_chronological(
    research_bars: pd.DataFrame,
) -> None:
    development, _ = reserve_final_holdout(research_bars, holdout_bars=100)
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
