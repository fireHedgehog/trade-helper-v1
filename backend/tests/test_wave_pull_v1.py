"""Wave Pull v1 — impulse-pullback continuation vs. plain-breakout placebo.

Implements the unit-fixture requirement from
docs/research-protocols/wave-pull-v1.md's lock checklist: prove no future
bar affects an earlier impulse, pullback-high, event, or placebo value, and
that the event/placebo distinction behaves as designed (event is a strict
subset of placebo, requiring the impulse precondition).
"""

from __future__ import annotations

import numpy as np
import pytest

from app import research


def _synthetic_closes(n: int, seed: int = 41) -> np.ndarray:
    rng = np.random.default_rng(seed)
    log_returns = rng.normal(loc=0.0001, scale=0.01, size=n - 1)
    return 100.0 * np.exp(np.concatenate([[0.0], np.cumsum(log_returns)]))


def test_events_unaffected_by_future_bars() -> None:
    closes = _synthetic_closes(400)
    full_event, full_placebo = research.wave_pull_events(closes)

    truncate_at = 200
    truncated_event, truncated_placebo = research.wave_pull_events(closes[:truncate_at])

    assert np.array_equal(full_event[:truncate_at], truncated_event)
    assert np.array_equal(full_placebo[:truncate_at], truncated_placebo)


def test_event_is_a_strict_subset_of_placebo() -> None:
    closes = _synthetic_closes(600)
    event, placebo = research.wave_pull_events(closes)
    assert np.all(placebo[event])
    assert placebo.sum() >= event.sum()


def test_placebo_fires_without_a_prior_impulse() -> None:
    # A slow, gentle grind to new highs: no 8-day move ever reaches 6%, so no
    # impulse and thus no event, but the market still makes plain 3-day
    # breakouts constantly -- placebo should fire, event should not.
    closes = np.concatenate([np.full(90, 100.0), np.linspace(100.0, 108.0, 60)])
    event, placebo = research.wave_pull_events(closes)
    assert placebo.any()
    assert not event.any()


def test_event_fires_after_a_genuine_impulse_and_breakout() -> None:
    flat = np.full(90, 100.0)
    impulse = np.linspace(100.0, 110.0, 8)  # +10% over 8 sessions, clears the 6% bar
    pullback = [109.0, 108.5, 108.8]
    breakout = [111.0]
    tail = np.full(10, 112.0)
    closes = np.concatenate([flat, impulse, pullback, breakout, tail])

    event, placebo = research.wave_pull_events(closes)
    assert event.any()


def test_bootstrap_p_values_are_valid_probabilities() -> None:
    closes = _synthetic_closes(500)
    result = research.wave_pull_bootstrap(closes, resamples=50, seed=1)
    if not result["insufficient_events"]:
        assert 0.0 <= result["p_event"] <= 1.0


def test_bootstrap_rejects_series_shorter_than_warm_up() -> None:
    closes = _synthetic_closes(100)  # <= warm_up (100) + impulse_lookback (8)
    with pytest.raises(ValueError, match="too short"):
        research.wave_pull_bootstrap(closes, resamples=5)
