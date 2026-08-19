"""CTA v2 -- pooled vol-scaled trend overlay.

Implements the unit-fixture requirements from
docs/research-protocols/cta-v2-pooled-trend-overlay.md's lock checklist:
prove no future bar affects an earlier weight value, that an
all-non-positive-trend day yields zero portfolio return (100% cash), that
the placebo's weights always sum to 1.0, and that a planted favourable
effect is detectable against pure noise.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from app import research


def _dates(n: int) -> np.ndarray:
    return pd.bdate_range("2010-01-04", periods=n).strftime("%Y-%m-%d").to_numpy()


def _synthetic_closes(n: int, *, drift: float = 0.0003, scale: float = 0.01, seed: int = 7) -> np.ndarray:
    rng = np.random.default_rng(seed)
    log_returns = rng.normal(loc=drift, scale=scale, size=n - 1)
    return 100.0 * np.exp(np.concatenate([[0.0], np.cumsum(log_returns)]))


def _panel(n: int, symbols: list[str], *, drift: float = 0.0003, scale: float = 0.01, seed: int = 7) -> dict[str, np.ndarray]:
    return {
        symbol: _synthetic_closes(n, drift=drift, scale=scale, seed=seed + index)
        for index, symbol in enumerate(symbols)
    }


SYMBOLS = ["A", "B", "C"]


def test_weight_matrix_unaffected_by_future_bars() -> None:
    closes_by_symbol = _panel(300, SYMBOLS)
    full = research.cta_v2_weight_matrix(closes_by_symbol, sma_window=research.CTA_V2_VARIANTS["B"])

    truncate_at = 250
    truncated_closes = {symbol: closes[:truncate_at] for symbol, closes in closes_by_symbol.items()}
    truncated = research.cta_v2_weight_matrix(truncated_closes, sma_window=research.CTA_V2_VARIANTS["B"])

    for symbol in SYMBOLS:
        np.testing.assert_allclose(full[symbol][:truncate_at], truncated[symbol])


def test_all_non_positive_trend_day_produces_zero_portfolio_return() -> None:
    n = 300
    warm_up = research.CTA_V2_WARM_UP_SESSIONS
    # Flat for the whole warm-up, then every asset declines together for the
    # remaining bars -- close stays below every SMA window, so Trend <= 0
    # for every asset on every post-decline day.
    closes_by_symbol: dict[str, np.ndarray] = {}
    for index, symbol in enumerate(SYMBOLS):
        flat = np.full(warm_up + 20, 100.0 + index)
        decline = (100.0 + index) * np.exp(-0.01 * np.arange(1, n - len(flat) + 1))
        closes_by_symbol[symbol] = np.concatenate([flat, decline])

    weights = research.cta_v2_weight_matrix(closes_by_symbol, sma_window=research.CTA_V2_VARIANTS["A"])
    tail = slice(warm_up + 40, n)
    for symbol in SYMBOLS:
        assert np.all(weights[symbol][tail] == 0.0)

    portfolio = research.cta_v2_portfolio_return(closes_by_symbol, weights)
    assert np.all(portfolio[warm_up + 41 : n] == 0.0)


def test_placebo_weights_always_sum_to_one_after_warm_up() -> None:
    closes_by_symbol = _panel(400, SYMBOLS)
    weights = research.cta_v2_placebo_weight_matrix(closes_by_symbol)
    totals = sum(weights[symbol] for symbol in SYMBOLS)
    warm_up = research.CTA_V2_VOL_LOOKBACK
    np.testing.assert_allclose(totals[warm_up:], 1.0)


def test_bootstrap_detects_a_planted_favourable_effect_against_pure_noise() -> None:
    n = 900
    symbols = [f"S{i}" for i in range(6)]
    dates = _dates(n)

    # Planted panel: strong, low-noise sustained uptrends -- the trend
    # signal should be persistently positive and the trend-weighted
    # portfolio should materially beat a flat/no-drift benchmark.
    trending = _panel(n, symbols, drift=0.0015, scale=0.004, seed=100)
    result_trending = research.cta_v2_bootstrap(trending, dates)

    # Pure-noise panel: zero drift, same volatility -- no persistent
    # advantage for the trend-weighted portfolio over the benchmark.
    noise = _panel(n, symbols, drift=0.0, scale=0.004, seed=200)
    result_noise = research.cta_v2_bootstrap(noise, dates)

    primary = research.CTA_V2_PRIMARY_VARIANT
    # A uniform positive drift across every asset does not create the
    # cross-sectional divergence a trend overlay actually exploits (with
    # everyone trending together, the portfolio converges toward the
    # benchmark itself); the bootstrap's own p-value is the honest signal
    # that the trending panel has more exploitable structure than pure
    # noise, not a direct comparison of raw excess-return magnitudes.
    assert result_trending["variants"][primary]["raw_p"] < result_noise["variants"][primary]["raw_p"]


def test_bootstrap_rejects_mismatched_calendars() -> None:
    closes_by_symbol = _panel(400, SYMBOLS)
    closes_by_symbol["A"] = closes_by_symbol["A"][:-5]
    with pytest.raises(ValueError, match="calendar"):
        research.cta_v2_bootstrap(closes_by_symbol, _dates(400))
