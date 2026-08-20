"""Thesis Track: placebo-window construction, randomization p-value, z-score/score helpers."""
from __future__ import annotations

import numpy as np
import pytest

from app import thesis_track


def test_trailing_zscore_is_nan_before_lookback_and_excludes_current_value() -> None:
    values = np.array([1.0, 1.0, 1.0, 1.0, 10.0])
    z = thesis_track.trailing_zscore(values, lookback=4)
    assert np.isnan(z[:4]).all()
    # window for index 4 is [1,1,1,1] (std=0) -> NaN, not a divide-by-zero crash
    assert np.isnan(z[4])


def test_trailing_zscore_matches_hand_computation() -> None:
    values = np.array([1.0, 2.0, 3.0, 4.0, 100.0])
    z = thesis_track.trailing_zscore(values, lookback=4)
    window = values[:4]
    expected = (values[4] - window.mean()) / window.std()
    assert z[4] == pytest.approx(expected)


def test_yield_stress_score_rewards_long_stress_penalizes_short_deviation() -> None:
    z_long = np.array([2.0, 2.0, 2.0])
    z_short = np.array([0.0, 1.0, -1.0])
    score = thesis_track.yield_stress_score(z_long, z_short)
    assert list(score) == [2.0, 1.0, 1.0]


def test_placebo_windows_returns_requested_count_and_length_never_overlapping_excluded() -> None:
    rng = np.random.default_rng(1)
    windows = thesis_track.placebo_windows(
        n_dates=1000, window_length=60, excluded_ranges=[(400, 460)], count=50, rng=rng
    )
    assert len(windows) == 50
    for start, end in windows:
        assert end - start == 60
        assert not (start < 460 and end > 400)


def test_placebo_windows_raises_when_impossible() -> None:
    rng = np.random.default_rng(1)
    with pytest.raises(RuntimeError):
        thesis_track.placebo_windows(
            n_dates=100, window_length=60, excluded_ranges=[(0, 100)], count=1, rng=rng,
            max_attempts_per_window=20,
        )


def test_thesis_track_p_value_detects_a_planted_favourable_effect() -> None:
    n_dates = 5000
    window_length = 60
    values = np.zeros(n_dates)
    real_windows = [(1000, 1060), (2000, 2060), (3000, 3060), (4000, 4060)]
    for start, end in real_windows:
        values[start:end] = 10.0  # obviously elevated inside real episodes

    def statistic(start: int, end: int) -> float:
        return float(values[start:end].max())

    real_stats = [statistic(s, e) for s, e in real_windows]
    result = thesis_track.thesis_track_p_value(
        real_stats, statistic, n_dates=n_dates, window_length=window_length,
        excluded_ranges=real_windows, resamples=500, seed=17291,
    )
    assert result["p_value"] < 0.01
    assert result["observed_mean_statistic"] == pytest.approx(10.0)


def test_thesis_track_p_value_is_reproducible_with_same_seed() -> None:
    n_dates = 2000
    rng_data = np.random.default_rng(3)
    values = rng_data.normal(size=n_dates)
    real_windows = [(500, 560), (1000, 1060)]

    def statistic(start: int, end: int) -> float:
        return float(values[start:end].mean())

    real_stats = [statistic(s, e) for s, e in real_windows]
    first = thesis_track.thesis_track_p_value(
        real_stats, statistic, n_dates=n_dates, window_length=60,
        excluded_ranges=real_windows, resamples=200, seed=42,
    )
    second = thesis_track.thesis_track_p_value(
        real_stats, statistic, n_dates=n_dates, window_length=60,
        excluded_ranges=real_windows, resamples=200, seed=42,
    )
    assert first == second


def test_thesis_track_p_value_rejects_empty_statistics_or_nonpositive_resamples() -> None:
    with pytest.raises(ValueError):
        thesis_track.thesis_track_p_value(
            [], lambda s, e: 0.0, n_dates=100, window_length=10, excluded_ranges=[], resamples=10, seed=1,
        )
    with pytest.raises(ValueError):
        thesis_track.thesis_track_p_value(
            [1.0], lambda s, e: 0.0, n_dates=100, window_length=10, excluded_ranges=[], resamples=0, seed=1,
        )
