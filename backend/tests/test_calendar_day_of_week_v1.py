"""Calendar Day-of-Week v1 — Monday daily-return differential vs.
block-resampled null.

Implements the unit-fixture requirement from
docs/research-protocols/calendar-day-of-week-v1.md's lock checklist: prove
the event mask matches a hand-computed calendar, that a planted
(negative-direction) differential is detected, and that the bootstrap's
test direction is genuinely flipped relative to Calendar Turn-of-Month v1
(favourable is negative here, not positive).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from app import research


def test_event_mask_matches_hand_computed_calendar() -> None:
    # 2020-01-06 through 2020-01-12 is Mon, Tue, Wed, Thu, Fri, (weekend
    # skipped in a trading calendar), Mon.
    dates = [
        "2020-01-06", "2020-01-07", "2020-01-08", "2020-01-09", "2020-01-10",
        "2020-01-13",
    ]
    expected = [True, False, False, False, False, True]
    mask = research.dow_event_mask(dates)
    assert mask.tolist() == expected


def test_default_target_weekday_is_monday() -> None:
    assert research.DOW_TARGET_WEEKDAY == 0


def test_planted_negative_dow_effect_is_detected() -> None:
    dates = pd.bdate_range("2015-01-01", periods=1000)
    mask = research.dow_event_mask(dates)
    assert mask[1:].sum() > 150  # plenty of Mondays in the fixture

    rng = np.random.default_rng(9)
    noise = rng.normal(loc=0.0, scale=0.001, size=len(dates))
    returns_padded = np.zeros(len(dates))
    # Plant a genuine underperformance on Mondays.
    returns_padded[1:] = noise[1:] - np.where(mask[1:], 0.01, 0.0)
    closes = 100.0 * np.exp(np.cumsum(returns_padded))

    diff, event_count, non_event_count = research.tom_daily_differential(
        research.log_returns_from_closes(closes), mask
    )
    assert diff < -0.005
    assert event_count > 0 and non_event_count > 0

    result = research.dow_bootstrap(closes, dates, resamples=200, seed=4, min_event_count=50)
    assert not result["insufficient_events"]
    assert result["p_event"] < 0.05


def test_no_planted_effect_gives_a_non_significant_p_value() -> None:
    # Sanity check that the flipped test direction doesn't spuriously fire on
    # pure noise with no Monday effect at all.
    dates = pd.bdate_range("2015-01-01", periods=1000)
    rng = np.random.default_rng(21)
    returns_padded = np.concatenate([[0.0], rng.normal(loc=0.0, scale=0.01, size=len(dates) - 1)])
    closes = 100.0 * np.exp(np.cumsum(returns_padded))

    result = research.dow_bootstrap(closes, dates, resamples=200, seed=6, min_event_count=50)
    assert not result["insufficient_events"]
    assert result["p_event"] > 0.05


def test_bootstrap_rejects_mismatched_lengths() -> None:
    dates = pd.bdate_range("2015-01-01", periods=100)
    closes = np.full(50, 100.0)
    with pytest.raises(ValueError, match="same length"):
        research.dow_bootstrap(closes, dates, resamples=5)


def test_insufficient_events_flag_when_min_event_count_not_met() -> None:
    dates = pd.bdate_range("2015-01-01", periods=100)
    rng = np.random.default_rng(2)
    returns_padded = np.concatenate([[0.0], rng.normal(scale=0.01, size=len(dates) - 1)])
    closes = 100.0 * np.exp(np.cumsum(returns_padded))

    result = research.dow_bootstrap(closes, dates, resamples=10, min_event_count=200)
    assert result["insufficient_events"] is True
    assert result["p_event"] is None
