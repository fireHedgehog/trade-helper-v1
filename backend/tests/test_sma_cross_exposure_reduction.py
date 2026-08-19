"""SMA Cross v1 exposure-reduction / volatility-state placebo.

Implements the unit-fixture requirement from
docs/research-protocols/sma-cross-v1-exposure-reduction.md's lock checklist:
prove no future bar affects an earlier state value, and pin the delta_sigma /
delta_mdd sign convention (negative is favourable) that a future edit could
silently flip.
"""

from __future__ import annotations

import numpy as np
import pytest

from app import research


def _synthetic_closes(n: int, seed: int = 7) -> np.ndarray:
    rng = np.random.default_rng(seed)
    log_returns = rng.normal(loc=0.0002, scale=0.01, size=n - 1)
    return 100.0 * np.exp(np.concatenate([[0.0], np.cumsum(log_returns)]))


def test_sma_cross_state_unaffected_by_future_bars() -> None:
    closes = _synthetic_closes(300)
    log_returns = research.log_returns_from_closes(closes)
    full_state = research.sma_cross_state(log_returns)

    truncate_at = 150
    truncated_state = research.sma_cross_state(log_returns[:truncate_at])

    assert np.array_equal(full_state[:truncate_at], truncated_state)


def test_volatility_state_unaffected_by_future_bars() -> None:
    closes = _synthetic_closes(300)
    log_returns = research.log_returns_from_closes(closes)
    full_state = research.sma_cross_volatility_state(log_returns)

    truncate_at = 150
    truncated_state = research.sma_cross_volatility_state(log_returns[:truncate_at])

    assert np.array_equal(full_state[:truncate_at], truncated_state)


def test_delta_stats_negative_when_gating_avoids_a_crash() -> None:
    # 260 calm days, then a 20-day crash, then 20 calm days. A state that is
    # False exactly during the crash should show a favourable (negative)
    # delta_sigma and delta_mdd relative to staying fully exposed throughout.
    calm = np.full(260, 0.0003)
    crash = np.full(20, -0.05)
    recovery = np.full(20, 0.0003)
    log_returns = np.concatenate([[0.0], calm, crash, recovery])

    state = np.ones(len(log_returns), dtype=bool)
    state[260:280] = False  # state(t-1) gates return(t); this excludes the crash

    delta_sigma, delta_mdd = research.sma_cross_delta_stats(log_returns, state)

    assert delta_sigma < 0
    assert delta_mdd < 0


def test_delta_stats_zero_when_state_is_always_on() -> None:
    closes = _synthetic_closes(300)
    log_returns = research.log_returns_from_closes(closes)
    always_on = np.ones(len(log_returns), dtype=bool)

    delta_sigma, delta_mdd = research.sma_cross_delta_stats(log_returns, always_on)

    assert delta_sigma == pytest.approx(0.0, abs=1e-12)
    assert delta_mdd == pytest.approx(0.0, abs=1e-12)


def test_max_drawdown_magnitude_is_nonnegative() -> None:
    closes = _synthetic_closes(300)
    log_returns = research.log_returns_from_closes(closes)
    assert research._max_drawdown_magnitude(log_returns[1:]) >= 0.0
    assert research._max_drawdown_magnitude(np.zeros(50)) == pytest.approx(0.0)


def test_bootstrap_p_values_are_valid_probabilities() -> None:
    closes = _synthetic_closes(320)
    result = research.sma_cross_bootstrap(
        closes, research.sma_cross_state, resamples=50, block_bars=20, seed=1
    )
    assert 0.0 <= result["p_delta_sigma"] <= 1.0
    assert 0.0 <= result["p_delta_mdd"] <= 1.0


def test_bootstrap_rejects_series_shorter_than_warm_up_plus_evaluation() -> None:
    closes = _synthetic_closes(100)
    with pytest.raises(ValueError, match="too short"):
        research.sma_cross_bootstrap(closes, research.sma_cross_state, resamples=5)
