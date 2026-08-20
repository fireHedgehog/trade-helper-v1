"""Chapter 4 (risk-budgeted ensemble eligibility) primitives -- ADR 0007.

block_bootstrap_confidence_interval is a genuinely different bootstrap from
every candidate this session: it characterizes the plausible RANGE of a
true effect size (no centering, no null), not a p-value against a null.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from app import research


def test_confidence_interval_brackets_a_known_positive_mean() -> None:
    rng = np.random.default_rng(3)
    values = rng.normal(loc=0.01, scale=0.005, size=1000)
    result = research.block_bootstrap_confidence_interval(values, resamples=500, seed=1)
    assert result["lower_bound"] < result["observed_mean"] < result["upper_bound"]
    assert abs(result["observed_mean"] - 0.01) < 0.002


def test_confidence_interval_is_wide_for_noisy_data_and_narrow_for_clean_data() -> None:
    rng = np.random.default_rng(4)
    clean = rng.normal(loc=0.01, scale=0.001, size=1000)
    noisy = rng.normal(loc=0.01, scale=0.05, size=1000)
    clean_ci = research.block_bootstrap_confidence_interval(clean, resamples=500, seed=2)
    noisy_ci = research.block_bootstrap_confidence_interval(noisy, resamples=500, seed=2)
    clean_width = clean_ci["upper_bound"] - clean_ci["lower_bound"]
    noisy_width = noisy_ci["upper_bound"] - noisy_ci["lower_bound"]
    assert noisy_width > clean_width


def test_confidence_interval_rejects_too_few_values() -> None:
    with pytest.raises(ValueError, match="at least two"):
        research.block_bootstrap_confidence_interval([0.01])


def test_confidence_multiplier_is_one_when_lower_bound_matches_point_estimate() -> None:
    assert research.chapter4_confidence_multiplier(0.02, 0.02) == pytest.approx(1.0)


def test_confidence_multiplier_shrinks_with_a_wider_lower_bound_gap() -> None:
    tight = research.chapter4_confidence_multiplier(0.02, 0.018)
    wide = research.chapter4_confidence_multiplier(0.02, 0.002)
    assert tight > wide
    assert 0.0 <= wide < tight <= 1.0


def test_confidence_multiplier_is_zero_when_lower_bound_is_negative() -> None:
    assert research.chapter4_confidence_multiplier(0.02, -0.01) == 0.0


def test_confidence_multiplier_is_zero_when_point_estimate_is_not_positive() -> None:
    assert research.chapter4_confidence_multiplier(-0.01, 0.005) == 0.0
    assert research.chapter4_confidence_multiplier(0.0, 0.0) == 0.0


def test_confidence_multiplier_never_exceeds_one_even_if_lower_bound_exceeds_point_estimate() -> None:
    # Not expected in practice (percentile below the mean), but the cap must
    # hold regardless -- a Chapter 4 signal may never be sized as if fully
    # validated.
    assert research.chapter4_confidence_multiplier(0.02, 0.05) == pytest.approx(1.0)


def test_case_resample_ci_brackets_a_known_positive_mean() -> None:
    rng = np.random.default_rng(5)
    values = rng.normal(loc=0.01, scale=0.02, size=200)
    result = research.case_resample_confidence_interval(values, resamples=500, seed=1)
    assert result["lower_bound"] < result["observed_mean"] < result["upper_bound"]
    assert result["event_count"] == 200


def test_case_resample_ci_is_wide_for_a_small_noisy_sample() -> None:
    rng = np.random.default_rng(6)
    small = rng.normal(loc=0.01, scale=0.03, size=15)
    large = rng.normal(loc=0.01, scale=0.03, size=1000)
    small_ci = research.case_resample_confidence_interval(small, resamples=500, seed=2)
    large_ci = research.case_resample_confidence_interval(large, resamples=500, seed=2)
    small_width = small_ci["upper_bound"] - small_ci["lower_bound"]
    large_width = large_ci["upper_bound"] - large_ci["lower_bound"]
    assert small_width > large_width


def test_case_resample_ci_rejects_too_few_values() -> None:
    with pytest.raises(ValueError, match="at least two"):
        research.case_resample_confidence_interval([0.01])


def test_two_sample_ci_brackets_a_known_positive_difference() -> None:
    rng = np.random.default_rng(8)
    group_a = rng.normal(loc=0.005, scale=0.01, size=500)  # e.g. Monday returns
    group_b = rng.normal(loc=0.0, scale=0.01, size=2000)  # e.g. non-Monday returns
    result = research.two_sample_block_bootstrap_confidence_interval(
        group_a, group_b, resamples=500, seed=1
    )
    assert result["lower_bound"] < result["observed_mean"] < result["upper_bound"]
    assert result["observed_mean"] > 0
    assert result["group_a_count"] == 500
    assert result["group_b_count"] == 2000


def test_two_sample_ci_is_roughly_symmetric_under_no_true_difference() -> None:
    rng = np.random.default_rng(9)
    group_a = rng.normal(loc=0.0, scale=0.01, size=800)
    group_b = rng.normal(loc=0.0, scale=0.01, size=800)
    result = research.two_sample_block_bootstrap_confidence_interval(
        group_a, group_b, resamples=1000, seed=2
    )
    # No planted difference -- the interval should straddle zero, not sit
    # entirely on one side.
    assert result["lower_bound"] < 0 < result["upper_bound"]


def test_two_sample_ci_rejects_too_few_values_in_either_group() -> None:
    with pytest.raises(ValueError, match="at least two"):
        research.two_sample_block_bootstrap_confidence_interval([0.01], [0.01, 0.02, 0.03])


def test_correlation_matrix_flags_a_perfectly_correlated_pair_as_redundant() -> None:
    dates = pd.date_range("2015-01-01", periods=200, freq="D")
    rng = np.random.default_rng(10)
    base = rng.normal(scale=0.01, size=200)
    contributions = {
        "signal_a": pd.Series(base, index=dates),
        "signal_b": pd.Series(base * 2.0, index=dates),  # perfectly correlated, different scale
    }
    result = research.pairwise_signal_correlation_matrix(contributions)
    assert result["matrix"]["signal_a"]["signal_b"] == pytest.approx(1.0, abs=1e-6)
    assert len(result["redundant_pairs"]) == 1
    assert set(result["redundant_pairs"][0]["pair"]) == {"signal_a", "signal_b"}


def test_correlation_matrix_does_not_flag_independent_signals() -> None:
    dates = pd.date_range("2015-01-01", periods=500, freq="D")
    rng = np.random.default_rng(11)
    contributions = {
        "signal_a": pd.Series(rng.normal(scale=0.01, size=500), index=dates),
        "signal_b": pd.Series(rng.normal(scale=0.01, size=500), index=dates),
    }
    result = research.pairwise_signal_correlation_matrix(contributions)
    assert abs(result["matrix"]["signal_a"]["signal_b"]) < 0.3
    assert result["redundant_pairs"] == []


def test_correlation_matrix_handles_non_overlapping_dates_as_none() -> None:
    early = pd.date_range("2010-01-01", periods=100, freq="D")
    late = pd.date_range("2020-01-01", periods=100, freq="D")
    rng = np.random.default_rng(12)
    contributions = {
        "signal_a": pd.Series(rng.normal(size=100), index=early),
        "signal_b": pd.Series(rng.normal(size=100), index=late),
    }
    result = research.pairwise_signal_correlation_matrix(contributions)
    assert result["matrix"]["signal_a"]["signal_b"] is None


def test_wave_pull_daily_contribution_is_nonzero_only_within_holding_windows() -> None:
    rng = np.random.default_rng(13)
    n = 500
    log_returns = np.concatenate([[0.0], rng.normal(loc=0.0002, scale=0.01, size=n - 1)])
    closes = np.exp(np.cumsum(log_returns))
    dates = pd.bdate_range("2015-01-01", periods=n)

    contribution = research.wave_pull_daily_contribution(closes, dates)

    assert len(contribution) == n
    zero_days = (contribution == 0.0).sum()
    nonzero_days = (contribution != 0.0).sum()
    assert nonzero_days <= zero_days  # holding windows are sparse, not the majority


def test_dow_daily_contribution_is_nonzero_only_on_mondays() -> None:
    rng = np.random.default_rng(14)
    n = 500
    log_returns = np.concatenate([[0.0], rng.normal(scale=0.01, size=n - 1)])
    closes = np.exp(np.cumsum(log_returns))
    dates = pd.bdate_range("2015-01-01", periods=n)

    contribution = research.dow_daily_contribution(closes, dates)
    mask = research.dow_event_mask(dates)

    assert (contribution[~mask] == 0.0).all()
    assert not (contribution[mask] == 0.0).all()


def test_wave_pull_event_forward_returns_array_matches_the_mean_it_feeds() -> None:
    rng = np.random.default_rng(7)
    log_returns = np.concatenate([[0.0], rng.normal(loc=0.0002, scale=0.01, size=999)])
    closes = np.exp(np.cumsum(log_returns))
    log_returns_padded = research.log_returns_from_closes(closes)

    array = research.wave_pull_event_forward_returns_array(log_returns_padded)
    observed_mean, count = research.wave_pull_event_forward_return(log_returns_padded)

    if count > 0:
        assert array.size == count
        assert array.mean() == pytest.approx(observed_mean)
    else:
        assert array.size == 0


def _dow_mask_for(n: int) -> np.ndarray:
    dates = pd.bdate_range("2010-01-04", periods=n)  # starts on a Monday
    return research.dow_event_mask(dates)


def test_dow_breadth_null_rejects_mismatched_asset_lengths() -> None:
    rng = np.random.default_rng(20)
    with pytest.raises(ValueError, match="same aligned length"):
        research.dow_breadth_correlation_aware_null(
            {"A": rng.normal(size=500), "B": rng.normal(size=400)},
            _dow_mask_for(500),
        )


def test_dow_breadth_null_rejects_mask_length_mismatch() -> None:
    rng = np.random.default_rng(21)
    with pytest.raises(ValueError, match="event_mask must match"):
        research.dow_breadth_correlation_aware_null(
            {"A": rng.normal(size=500), "B": rng.normal(size=500)},
            _dow_mask_for(400),
        )


def test_dow_breadth_null_is_deterministic_given_a_seed() -> None:
    rng = np.random.default_rng(22)
    log_returns_by_symbol = {
        s: np.concatenate([[0.0], rng.normal(loc=0.0, scale=0.01, size=799)]) for s in "ABC"
    }
    mask = _dow_mask_for(800)
    first = research.dow_breadth_correlation_aware_null(
        log_returns_by_symbol, mask, inner_resamples=50, outer_replications=20, seed=5
    )
    second = research.dow_breadth_correlation_aware_null(
        log_returns_by_symbol, mask, inner_resamples=50, outer_replications=20, seed=5
    )
    assert first == second


def test_dow_breadth_null_observed_count_matches_direct_per_asset_check() -> None:
    rng = np.random.default_rng(23)
    n = 800
    mask = _dow_mask_for(n)
    log_returns_by_symbol = {
        # "UP": a real, strong planted Monday-underperformance-style effect
        # (non-Monday minus Monday is strongly positive) that should clear
        # the eligibility bar on its own, unresampled data.
        "UP": np.concatenate([[0.0], np.where(mask[1:], -0.02, 0.0) + rng.normal(scale=0.001, size=n - 1)]),
        # "FLAT": no planted effect at all.
        "FLAT": np.concatenate([[0.0], rng.normal(scale=0.01, size=n - 1)]),
    }
    result = research.dow_breadth_correlation_aware_null(
        log_returns_by_symbol, mask, inner_resamples=200, outer_replications=5, seed=6
    )

    manual_eligible = {}
    for i, symbol in enumerate(sorted(log_returns_by_symbol)):
        values = log_returns_by_symbol[symbol][1:]
        ci = research.two_sample_block_bootstrap_confidence_interval(
            values[~mask[1:]], values[mask[1:]], resamples=200, seed=6 + 0 + i
        )
        manual_eligible[symbol] = research.chapter4_confidence_multiplier(
            ci["observed_mean"], ci["lower_bound"]
        ) > 0.0

    assert result["observed_count"] == sum(manual_eligible.values())
    assert set(result["observed_eligible_symbols"]) == {s for s, e in manual_eligible.items() if e}
    assert "UP" in result["observed_eligible_symbols"]


def test_dow_breadth_null_preserves_joint_correlation_across_duplicate_assets() -> None:
    """Four assets that are EXACT duplicates of the same series must move
    together (all eligible or all not) in almost every outer replication,
    since one shared block-shift is applied to every asset at once -- this
    is the entire point of the joint null versus an independent-per-asset
    one. Each duplicate's own eligibility is still decided by its own,
    independently-seeded inner CI (a deliberate design choice, confirmed
    correct by pre-lock review -- see dow_breadth_correlation_aware_null's
    docstring), so a rare split on a genuinely near-zero resampled world is
    expected, not a bug; the assertion below tolerates that without
    requiring a mathematically-impossible hard guarantee."""
    rng = np.random.default_rng(24)
    n = 800
    mask = _dow_mask_for(n)
    # A large, clean planted effect (small noise relative to the gap) keeps
    # every duplicate's confidence interval decisively on one side of zero
    # in almost every replication.
    base = np.concatenate([[0.0], np.where(mask[1:], -0.05, 0.05) + rng.normal(scale=0.002, size=n - 1)])
    log_returns_by_symbol = {"DUP1": base, "DUP2": base.copy(), "DUP3": base.copy(), "DUP4": base.copy()}

    result = research.dow_breadth_correlation_aware_null(
        log_returns_by_symbol, mask, inner_resamples=300, outer_replications=15, seed=7
    )

    assert result["observed_count"] in (0, 4)
    split_replications = [c for c in result["null_count_distribution"] if c not in (0, 4)]
    assert len(split_replications) <= 1, f"too many split replications: {split_replications}"


def test_dow_breadth_null_p_value_is_between_zero_and_one() -> None:
    rng = np.random.default_rng(25)
    n = 600
    mask = _dow_mask_for(n)
    log_returns_by_symbol = {
        s: np.concatenate([[0.0], rng.normal(scale=0.01, size=n - 1)]) for s in ("W", "X", "Y", "Z")
    }
    result = research.dow_breadth_correlation_aware_null(
        log_returns_by_symbol, mask, inner_resamples=50, outer_replications=25, seed=8
    )
    assert 0.0 < result["p_value"] <= 1.0
    assert len(result["null_count_distribution"]) == 25
    assert all(0 <= c <= 4 for c in result["null_count_distribution"])
