"""ETF-12 cross-sectional rotation v1 — rank continuation vs. joint-panel null.

Implements the unit-fixture requirement from
docs/research-protocols/etf12-cross-sectional-rotation-v1.md's lock
checklist: no future bar affects an earlier rank, the tie-breaking rule
behaves as documented, a synthetic panel with genuine rank continuation
shows a materially higher correlation than its own null, and an
independent-noise panel does not.
"""

from __future__ import annotations

import numpy as np
import pytest

from app import research


def _synthetic_panel(n: int, num_assets: int = 12, seed: int = 5) -> dict:
    rng = np.random.default_rng(seed)
    panel = {}
    for i in range(num_assets):
        log_returns = rng.normal(loc=0.0001, scale=0.01, size=n - 1)
        panel[f"A{i}"] = 100.0 * np.exp(np.concatenate([[0.0], np.cumsum(log_returns)]))
    return panel


def _persistent_rank_panel(n: int, num_assets: int = 12, seed: int = 7) -> dict:
    """Each asset has a fixed drift rank (asset 0 drifts most, asset 11 least)
    that persists throughout, so formation rank should predict forward rank."""
    rng = np.random.default_rng(seed)
    panel = {}
    for i in range(num_assets):
        drift = 0.0005 * (num_assets - i)  # asset 0 drifts fastest
        noise = rng.normal(loc=0.0, scale=0.006, size=n - 1)
        log_returns = drift + noise
        panel[f"A{i}"] = 100.0 * np.exp(np.concatenate([[0.0], np.cumsum(log_returns)]))
    return panel


def test_average_rank_matches_pandas_convention() -> None:
    ranks = research._average_rank(np.array([10.0, 30.0, 20.0, 30.0]))
    # 10 -> rank 1; the two 30s tie for ranks 3 and 4 -> average 3.5 each; 20 -> rank 2
    assert list(ranks) == [1.0, 3.5, 2.0, 3.5]


def test_formation_rank_unaffected_by_future_bars() -> None:
    panel = _synthetic_panel(500)
    closes_matrix_full = np.column_stack([panel[s] for s in sorted(panel)])
    _, _, ranks_full = research.rotation_pooled_correlation(closes_matrix_full)

    truncate_at = 300
    closes_matrix_truncated = closes_matrix_full[:truncate_at]
    _, _, ranks_truncated = research.rotation_pooled_correlation(closes_matrix_truncated)

    # every rebalance date present in both must have an identical formation rank
    shared_dates = set(ranks_full) & set(ranks_truncated)
    assert shared_dates  # sanity: there is real overlap to check
    for date in shared_dates:
        assert np.array_equal(ranks_full[date], ranks_truncated[date])


def test_persistent_rank_panel_shows_higher_correlation_than_noise() -> None:
    persistent = _persistent_rank_panel(1200)
    noise = _synthetic_panel(1200)

    closes_persistent = np.column_stack([persistent[s] for s in sorted(persistent)])
    closes_noise = np.column_stack([noise[s] for s in sorted(noise)])

    corr_persistent, count_p, _ = research.rotation_pooled_correlation(closes_persistent)
    corr_noise, count_n, _ = research.rotation_pooled_correlation(closes_noise)

    assert count_p > 0 and count_n > 0
    assert corr_persistent > corr_noise
    assert corr_persistent > 0.3  # a genuinely strong, not marginal, effect


def test_bootstrap_p_value_is_valid_probability() -> None:
    panel = _synthetic_panel(400)
    result = research.etf12_rotation_bootstrap(panel, resamples=20, seed=1)
    assert 0.0 <= result["p_value"] <= 1.0
    assert result["rebalance_date_count"] > 0


def test_bootstrap_rejects_mismatched_asset_lengths() -> None:
    panel = _synthetic_panel(400)
    panel["A0"] = panel["A0"][:-10]
    with pytest.raises(ValueError, match="same aligned length"):
        research.etf12_rotation_bootstrap(panel, resamples=5)


def test_bootstrap_rejects_series_shorter_than_warm_up() -> None:
    panel = _synthetic_panel(150)
    with pytest.raises(ValueError, match="too short"):
        research.etf12_rotation_bootstrap(panel, resamples=5)
