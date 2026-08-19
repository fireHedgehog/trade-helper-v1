"""RSI(14) oversold-crossing short-horizon reversal.

Implements the unit-fixture requirement from
docs/research-protocols/rsi-oversold-reversal-v1.md's lock checklist: prove no
future bar affects an earlier event or placebo value, and cross-check that the
reconstructed-price RSI computation matches the existing RsiReversion
prototype's own formula computed directly on real closes.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from app import research


def _synthetic_closes(n: int, seed: int = 11) -> np.ndarray:
    rng = np.random.default_rng(seed)
    log_returns = rng.normal(loc=0.0002, scale=0.012, size=n - 1)
    return 100.0 * np.exp(np.concatenate([[0.0], np.cumsum(log_returns)]))


def _rsi_reference(closes: np.ndarray, period: int = 14) -> np.ndarray:
    """Direct port of strategies.py::RsiReversion's own RSI formula, computed
    straight from real closes (not through the log-return/price-proxy path)."""
    close = pd.Series(closes)
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / period, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / period, adjust=False).mean()
    return (100 - 100 / (1 + gain / loss.replace(0, 1e-12))).to_numpy()


def test_rsi_matches_existing_prototype_formula_on_real_closes() -> None:
    closes = _synthetic_closes(400)
    reference = _rsi_reference(closes)

    log_returns = research.log_returns_from_closes(closes)
    reconstructed = research.rsi_from_log_returns(log_returns)

    # delta[0] differs (reference has NaN diff at t=0; reconstructed uses 0),
    # which only affects the first EWM step negligibly after warm-up.
    np.testing.assert_allclose(reconstructed[50:], reference[50:], rtol=1e-6, atol=1e-9)


def test_rsi_events_unaffected_by_future_bars() -> None:
    closes = _synthetic_closes(400)
    log_returns = research.log_returns_from_closes(closes)
    rsi_full = research.rsi_from_log_returns(log_returns)
    full_events = research.rsi_crossing_events(rsi_full)

    truncate_at = 200
    rsi_truncated = research.rsi_from_log_returns(log_returns[:truncate_at])
    truncated_events = research.rsi_crossing_events(rsi_truncated)

    assert np.array_equal(full_events[:truncate_at], truncated_events)


def test_placebo_events_unaffected_by_future_bars() -> None:
    closes = _synthetic_closes(400)
    log_returns = research.log_returns_from_closes(closes)
    full_placebo = research.rsi_placebo_events(log_returns)

    truncate_at = 200
    truncated_placebo = research.rsi_placebo_events(log_returns[:truncate_at])

    assert np.array_equal(full_placebo[:truncate_at], truncated_placebo)


def test_cooldown_suppresses_events_within_window() -> None:
    events = np.array([5, 6, 8, 20, 21, 45])
    kept = research._apply_cooldown(events, cooldown=10)
    assert list(kept) == [5, 20, 45]


def test_forward_return_excludes_events_too_close_to_sample_end() -> None:
    log_returns = np.zeros(50)
    events = np.array([10, 45])  # 45 + 10 >= 50, must be excluded
    mean, count = research._mean_forward_return(log_returns, events, horizon=10)
    assert count == 1
    assert mean == pytest.approx(0.0)


def test_forward_return_positive_when_event_precedes_a_rally() -> None:
    calm = np.full(100, 0.0)
    rally = np.full(10, 0.01)
    tail = np.full(50, 0.0)
    log_returns = np.concatenate([[0.0], calm, rally, tail])

    event_index = 100  # immediately before the 10-session rally
    mean, count = research._mean_forward_return(
        log_returns, np.array([event_index]), horizon=10
    )
    assert count == 1
    assert mean == pytest.approx(0.10, abs=1e-9)


def test_bootstrap_reports_insufficient_events_honestly() -> None:
    closes = _synthetic_closes(200, seed=99)  # short, low-volatility, few events
    result = research.rsi_bootstrap(closes, resamples=20, warm_up=100)
    if result["event_count"] < research.RSI_MIN_EVENT_COUNT:
        assert result["insufficient_events"] is True
        assert result["p_event"] is None


def test_bootstrap_rejects_series_shorter_than_warm_up() -> None:
    closes = _synthetic_closes(50)
    with pytest.raises(ValueError, match="too short"):
        research.rsi_bootstrap(closes, resamples=5)
