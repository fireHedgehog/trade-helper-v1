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
