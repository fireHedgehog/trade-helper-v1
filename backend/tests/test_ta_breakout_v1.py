"""TA Breakout v1 — rejected-resistance breakout vs. raw new-high placebo.

Implements the unit-fixture requirement from
docs/research-protocols/ta-breakout-v1.md's lock checklist: prove no future
bar affects an earlier resistance, rejection, event, or placebo value, and
that the event/placebo distinction behaves as designed (event requires prior
rejections; placebo does not).
"""

from __future__ import annotations

import numpy as np
import pytest

from app import research


def _synthetic_closes(n: int, seed: int = 23) -> np.ndarray:
    rng = np.random.default_rng(seed)
    log_returns = rng.normal(loc=0.0001, scale=0.01, size=n - 1)
    return 100.0 * np.exp(np.concatenate([[0.0], np.cumsum(log_returns)]))


def test_events_unaffected_by_future_bars() -> None:
    closes = _synthetic_closes(400)
    full_event, full_placebo = research.ta_breakout_events(closes)

    truncate_at = 200
    truncated_event, truncated_placebo = research.ta_breakout_events(closes[:truncate_at])

    assert np.array_equal(full_event[:truncate_at], truncated_event)
    assert np.array_equal(full_placebo[:truncate_at], truncated_placebo)


def test_event_requires_rejections_placebo_does_not() -> None:
    # Rally straight through a level with zero prior touches: should qualify
    # as a placebo breakout but never as an event (no rejection history).
    closes = np.concatenate([np.full(90, 100.0), np.linspace(100.0, 130.0, 40)])
    event, placebo = research.ta_breakout_events(closes, window=60, min_rejections=2)

    assert placebo.any()
    assert not event.any()


def test_event_fires_after_two_rejections_then_breakout() -> None:
    flat = np.full(70, 100.0)
    touch1 = [99.5, 100.0]   # approach and reject at the flat high
    pull1 = [98.0, 98.5]
    touch2 = [99.6, 100.0]   # second rejection
    pull2 = [98.5, 99.0]
    breakout = [102.0]       # clears the 100 level by > 0.5%
    tail = np.full(20, 103.0)
    closes = np.concatenate([flat, touch1, pull1, touch2, pull2, breakout, tail])

    event, placebo = research.ta_breakout_events(
        closes, window=60, tolerance=0.01, buffer=0.005, min_rejections=2
    )
    assert event.any()
    assert placebo.any()
    # every event index must also be a placebo index (event is a strict subset)
    assert np.all(placebo[event])


def test_resistance_excludes_the_current_bar() -> None:
    # Strictly increasing closes: today's close is always the new all-time
    # high, so resistance(t) must equal yesterday's close, not today's own
    # (higher) value -- a direct check that shift(1) excludes the current bar.
    closes = np.arange(100.0, 180.0, 1.0)
    resistance = research._rolling_max_excluding_today(closes, window=60)
    idx = 70
    assert resistance[idx] == pytest.approx(closes[idx - 1])


def test_bootstrap_p_values_are_valid_probabilities() -> None:
    closes = _synthetic_closes(500)
    result = research.ta_breakout_bootstrap(closes, resamples=50, seed=1)
    if not result["insufficient_events"]:
        assert 0.0 <= result["p_event"] <= 1.0


def test_bootstrap_rejects_series_shorter_than_warm_up() -> None:
    closes = _synthetic_closes(120)
    with pytest.raises(ValueError, match="too short"):
        research.ta_breakout_bootstrap(closes, resamples=5)
