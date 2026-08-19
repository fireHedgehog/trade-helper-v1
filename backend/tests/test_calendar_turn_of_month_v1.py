"""Calendar Turn-of-Month v1 — daily-return differential vs. block-resampled
null.

Implements the unit-fixture requirement from
docs/research-protocols/calendar-turn-of-month-v1.md's lock checklist: prove
the event mask matches a hand-computed calendar for a small fixture, that a
planted differential is detected, and that no *completed* month's
classification is altered by data added after it (the honest form of "no
future bar affects an earlier event" for a calendar-fixed, not
price-derived, event: the *final, possibly-partial* month in a truncated
series is not claimed to be stable, only months strictly before it).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from app import research


def test_event_mask_matches_hand_computed_calendar() -> None:
    dates = [
        "2020-01-02", "2020-01-03", "2020-01-06", "2020-01-07", "2020-01-08",
        "2020-01-09", "2020-01-30", "2020-01-31",
        "2020-02-03", "2020-02-04", "2020-02-05", "2020-02-06", "2020-02-07",
        "2020-02-27", "2020-02-28",
    ]
    expected = [
        True, True, True, False, False, False, False, True,
        True, True, True, False, False, False, True,
    ]
    mask = research.tom_event_mask(dates)
    assert mask.tolist() == expected


def test_earlier_complete_months_unaffected_by_later_truncation() -> None:
    dates = pd.bdate_range("2015-01-01", periods=200)
    period = pd.Series(dates).dt.to_period("M")
    cutoff = 150

    full_mask = research.tom_event_mask(dates)
    truncated_mask = research.tom_event_mask(dates[:cutoff])

    final_period_in_truncated = period.iloc[cutoff - 1]
    stable_count = int((period < final_period_in_truncated).sum())
    assert 0 < stable_count < cutoff
    assert np.array_equal(full_mask[:stable_count], truncated_mask[:stable_count])


def test_planted_tom_effect_is_detected() -> None:
    dates = pd.bdate_range("2015-01-01", periods=1000)
    mask = research.tom_event_mask(dates)
    assert mask[1:].sum() > 100  # plenty of turn-of-month days in the fixture

    rng = np.random.default_rng(7)
    noise = rng.normal(loc=0.0, scale=0.001, size=len(dates))
    returns_padded = np.zeros(len(dates))
    returns_padded[1:] = noise[1:] + np.where(mask[1:], 0.01, 0.0)
    closes = 100.0 * np.exp(np.cumsum(returns_padded))

    diff, event_count, non_event_count = research.tom_daily_differential(
        research.log_returns_from_closes(closes), mask
    )
    assert diff > 0.005
    assert event_count > 0 and non_event_count > 0

    result = research.tom_bootstrap(closes, dates, resamples=200, seed=3, min_event_count=50)
    assert not result["insufficient_events"]
    assert result["p_event"] < 0.05


def test_bootstrap_p_values_are_valid_probabilities() -> None:
    dates = pd.bdate_range("2015-01-01", periods=1000)
    rng = np.random.default_rng(11)
    returns_padded = np.concatenate([[0.0], rng.normal(loc=0.0001, scale=0.01, size=len(dates) - 1)])
    closes = 100.0 * np.exp(np.cumsum(returns_padded))

    result = research.tom_bootstrap(closes, dates, resamples=50, seed=1, min_event_count=50)
    if not result["insufficient_events"]:
        assert 0.0 <= result["p_event"] <= 1.0
    assert "diagnostics" in result
    assert "event_std" in result["diagnostics"]


def test_bootstrap_rejects_mismatched_lengths() -> None:
    dates = pd.bdate_range("2015-01-01", periods=100)
    closes = np.full(50, 100.0)
    with pytest.raises(ValueError, match="same length"):
        research.tom_bootstrap(closes, dates, resamples=5)


def test_insufficient_events_flag_when_min_event_count_not_met() -> None:
    dates = pd.bdate_range("2015-01-01", periods=100)
    rng = np.random.default_rng(5)
    returns_padded = np.concatenate([[0.0], rng.normal(scale=0.01, size=len(dates) - 1)])
    closes = 100.0 * np.exp(np.cumsum(returns_padded))

    result = research.tom_bootstrap(closes, dates, resamples=10, min_event_count=200)
    assert result["insufficient_events"] is True
    assert result["p_event"] is None
