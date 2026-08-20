"""Thesis Track: placebo-in-time randomization inference for small-n regime
episodes. See docs/thesis-track-small-n.md. General-purpose: a candidate
supplies its own per-window statistic function; this module only handles
placebo-window construction and the randomization p-value. Distinct from
`research.py`'s circular_block_bootstrap_p_value family, which assumes a
large quasi-independent daily sample -- wrong tool for ~3-5 episodes.
"""
from collections.abc import Callable

import numpy as np


def placebo_windows(
    n_dates: int,
    window_length: int,
    excluded_ranges: list[tuple[int, int]],
    count: int,
    rng: np.random.Generator,
    *,
    max_attempts_per_window: int = 1000,
) -> list[tuple[int, int]]:
    """count random (start, end) index windows of window_length within
    [0, n_dates), each rejected and redrawn if it overlaps any excluded
    range (the real episodes' own windows, so the null isn't contaminated
    by the real signal)."""
    if window_length > n_dates:
        raise ValueError("window_length exceeds available dates")
    windows: list[tuple[int, int]] = []
    for _ in range(count):
        for _ in range(max_attempts_per_window):
            start = int(rng.integers(0, n_dates - window_length + 1))
            end = start + window_length
            if not any(start < ex_end and end > ex_start for ex_start, ex_end in excluded_ranges):
                windows.append((start, end))
                break
        else:
            raise RuntimeError(
                "could not find a non-overlapping placebo window after "
                f"{max_attempts_per_window} attempts -- excluded_ranges may "
                "cover too much of the series"
            )
    return windows


def thesis_track_p_value(
    real_episode_statistics: list[float],
    compute_statistic_for_window: Callable[[int, int], float],
    *,
    n_dates: int,
    window_length: int,
    excluded_ranges: list[tuple[int, int]],
    resamples: int,
    seed: int,
) -> dict:
    """One-sided p-value for a favourable (high) mean episode statistic.

    Null: draw `len(real_episode_statistics)` non-overlapping-with-real-
    episodes placebo windows per resample, compute the same statistic on
    each via compute_statistic_for_window, and see how often the
    synthetic mean is >= the real mean -- the episode-level randomization
    inference docs/thesis-track-small-n.md specifies, not a bootstrap.
    """
    if not real_episode_statistics:
        raise ValueError("no episode statistics supplied")
    if resamples <= 0:
        raise ValueError("resamples must be positive")
    observed_mean = float(np.mean(real_episode_statistics))
    n_episodes = len(real_episode_statistics)
    rng = np.random.default_rng(seed)
    at_least = 0
    for _ in range(resamples):
        windows = placebo_windows(n_dates, window_length, excluded_ranges, n_episodes, rng)
        synthetic_mean = float(np.mean([compute_statistic_for_window(s, e) for s, e in windows]))
        if synthetic_mean >= observed_mean:
            at_least += 1
    return {
        "observed_mean_statistic": observed_mean,
        "episode_statistics": [float(x) for x in real_episode_statistics],
        "n_episodes": n_episodes,
        "p_value": (at_least + 1) / (resamples + 1),
        "resamples": resamples,
    }


def trailing_zscore(values: np.ndarray, lookback: int) -> np.ndarray:
    """NaN-padded z-score of values[i] against values[i-lookback:i] (strictly
    trailing, excludes today -- no look-ahead)."""
    n = len(values)
    z = np.full(n, np.nan)
    for i in range(lookback, n):
        window = values[i - lookback : i]
        std = window.std()
        if std > 0:
            z[i] = (values[i] - window.mean()) / std
    return z


def yield_stress_score(z_long: np.ndarray, z_short: np.ndarray) -> np.ndarray:
    """score(t) = z_long(t) - |z_short(t)| -- high when the long end is
    stressed relative to its own history while the short end stays near
    its own mean. NaN where either input is NaN (propagates naturally)."""
    return z_long - np.abs(z_short)
