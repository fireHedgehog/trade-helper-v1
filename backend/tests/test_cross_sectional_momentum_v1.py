"""Cross-sectional equity momentum (CS-01), point-in-time-masked engine.

Implements the unit-fixture requirement from
docs/research-hypotheses/cross-sectional-momentum-v1.md's "What must change
in the engine" section: real point-in-time membership means the eligible
column set changes by rebalance date, unlike ETF-12 rotation's fixed panel.
"""

from __future__ import annotations

import numpy as np
import pytest

from app import research


def _persistent_rank_panel(n: int, num_assets: int = 12, seed: int = 7) -> dict:
    rng = np.random.default_rng(seed)
    panel = {}
    for i in range(num_assets):
        drift = 0.0005 * (num_assets - i)  # asset 0 drifts fastest
        noise = rng.normal(loc=0.0, scale=0.006, size=n - 1)
        log_returns = drift + noise
        panel[f"A{i}"] = 100.0 * np.exp(np.concatenate([[0.0], np.cumsum(log_returns)]))
    return panel


def test_masked_ranking_excludes_non_members_on_a_given_date() -> None:
    """A flatlined 'poison' asset that would otherwise sit mid-rank must be
    excluded entirely from a date's rank when its membership mask is False --
    not ranked-and-then-ignored, genuinely absent from the pool."""
    n = 400
    panel = _persistent_rank_panel(n, num_assets=4)
    symbols = sorted(panel)
    closes_matrix = np.column_stack([panel[s] for s in symbols])

    # All 4 assets are always members.
    full_mask = np.ones_like(closes_matrix, dtype=bool)
    corr_full, count_full, ranks_full = research.rotation_pooled_correlation_masked(
        closes_matrix, full_mask, warm_up=100, spacing=20, formation=60, holding=20
    )
    assert count_full > 0
    # Every rebalance date's rank must be a permutation of 1..4 (all present).
    for rank in ranks_full.values():
        assert sorted(rank.tolist()) == [1.0, 2.0, 3.0, 4.0]

    # Now A3 (index 3, symbol sorted last) is never a member -- masked out.
    partial_mask = full_mask.copy()
    partial_mask[:, 3] = False
    corr_partial, count_partial, ranks_partial = research.rotation_pooled_correlation_masked(
        closes_matrix, partial_mask, warm_up=100, spacing=20, formation=60, holding=20
    )
    assert count_partial == count_full  # still enough eligible members (3) at every date
    for rank in ranks_partial.values():
        assert len(rank) == 3
        assert sorted(rank.tolist()) == [1.0, 2.0, 3.0]


def test_rebalance_date_skipped_when_fewer_than_two_eligible() -> None:
    n = 400
    panel = _persistent_rank_panel(n, num_assets=3)
    symbols = sorted(panel)
    closes_matrix = np.column_stack([panel[s] for s in symbols])
    mask = np.zeros_like(closes_matrix, dtype=bool)
    mask[:, 0] = True  # only one asset ever eligible -- no rank is computable

    corr, count, ranks = research.rotation_pooled_correlation_masked(
        closes_matrix, mask, warm_up=100, spacing=20, formation=60, holding=20
    )
    assert count == 0
    assert corr == 0.0
    assert ranks == {}


def test_membership_unaffected_by_future_bars() -> None:
    """Same no-look-ahead guarantee as the unmasked engine: truncating the
    series must not change a shared rebalance date's formation rank."""
    n = 500
    panel = _persistent_rank_panel(n, num_assets=6)
    symbols = sorted(panel)
    closes_matrix_full = np.column_stack([panel[s] for s in symbols])
    mask_full = np.ones_like(closes_matrix_full, dtype=bool)
    mask_full[:, -1] = False  # last asset never eligible

    _, _, ranks_full = research.rotation_pooled_correlation_masked(closes_matrix_full, mask_full)

    truncate_at = 300
    closes_truncated = closes_matrix_full[:truncate_at]
    mask_truncated = mask_full[:truncate_at]
    _, _, ranks_truncated = research.rotation_pooled_correlation_masked(closes_truncated, mask_truncated)

    shared_dates = set(ranks_full) & set(ranks_truncated)
    assert shared_dates
    for date in shared_dates:
        assert np.array_equal(ranks_full[date], ranks_truncated[date])


def test_bootstrap_detects_persistent_rank_masked() -> None:
    """Sanity: with membership held fixed (all-True), the masked bootstrap
    must reproduce the same qualitative result as the unmasked engine on a
    panel engineered to have genuine rank persistence."""
    n = 1200
    panel = _persistent_rank_panel(n, num_assets=12)
    membership = {s: np.ones(n, dtype=bool) for s in panel}

    result = research.cross_sectional_momentum_bootstrap(
        panel, membership, formation=60, holding=20, warm_up=100, spacing=20,
        resamples=200, seed=17291,
    )
    assert result["observed_correlation"] > 0.10
    assert result["rebalance_date_count"] > 0
    assert 0.0 <= result["p_value"] <= 1.0


def test_bootstrap_rejects_mismatched_membership_keys() -> None:
    panel = _persistent_rank_panel(300, num_assets=3)
    membership = {s: np.ones(300, dtype=bool) for s in list(panel)[:2]}  # missing one symbol
    with pytest.raises(ValueError, match="same symbols"):
        research.cross_sectional_momentum_bootstrap(panel, membership)


def test_bootstrap_rejects_misaligned_membership_length() -> None:
    panel = _persistent_rank_panel(300, num_assets=3)
    membership = {s: np.ones(299, dtype=bool) for s in panel}  # wrong length
    with pytest.raises(ValueError, match="align 1:1"):
        research.cross_sectional_momentum_bootstrap(panel, membership)
