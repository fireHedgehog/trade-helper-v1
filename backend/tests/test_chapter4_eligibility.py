"""Chapter 4 (risk-budgeted ensemble eligibility) primitives -- ADR 0007.

block_bootstrap_confidence_interval is a genuinely different bootstrap from
every candidate this session: it characterizes the plausible RANGE of a
true effect size (no centering, no null), not a p-value against a null.
"""

from __future__ import annotations

import numpy as np
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
