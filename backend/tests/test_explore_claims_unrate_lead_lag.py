"""Unit coverage for the pure-function rolling-window/inflection/pairing
logic in explore_claims_unrate_lead_lag.py. This script is deliberately a
non-evidential bounded exploration (no lock, no fingerprint, no decision
vocabulary), but its rolling-window semantics (YoY pct_change(52),
DateOffset(months=24) pairing, the Sahm Rule's trailing-low window) are
exactly the kind of thing that can fail silently without a test -- flagged
directly by a pre-lock-style review of this script.
"""

from __future__ import annotations

import pandas as pd

from app.explore_claims_unrate_lead_lag import (
    icsa_inflections,
    pair_lead_times,
    sahm_triggers,
)


def test_icsa_inflections_detects_a_sustained_yoy_upturn_at_the_right_week() -> None:
    # Two flat 52-week blocks (200, then 300), jump exactly at week 52. Hand
    # traced: the first week where both the 4-week MA and its 52-week-prior
    # comparison are fully clean of the transition, and the YoY change is
    # positive for 4 consecutive weeks, is week 55 (see PR description).
    dates = pd.date_range("2015-01-02", periods=110, freq="W")
    values = pd.Series([200.0] * 52 + [300.0] * 58, index=dates)

    inflections = icsa_inflections(values)

    assert len(inflections) == 1
    assert inflections[0] == dates[55]


def test_icsa_inflections_finds_nothing_in_a_flat_series() -> None:
    dates = pd.date_range("2015-01-02", periods=110, freq="W")
    values = pd.Series([200.0] * 110, index=dates)
    assert icsa_inflections(values) == []


def test_icsa_inflections_requires_the_sustain_window_not_a_single_week_blip() -> None:
    # A single-week spike that reverts immediately must not count -- only a
    # run of >= ICSA_SUSTAIN_WEEKS (4) consecutive positive YoY weeks does.
    dates = pd.date_range("2015-01-02", periods=110, freq="W")
    values = [200.0] * 52
    # One-week blip at week 52, then back to a level that keeps YoY
    # negative-or-zero (still 200) for the rest of the series.
    values += [300.0] + [200.0] * 57
    series = pd.Series(values, index=dates)
    assert icsa_inflections(series) == []


def test_sahm_triggers_fires_when_the_3mo_average_rises_half_a_point_above_its_trailing_low() -> None:
    # 12 flat months at 4.0, then a jump to 4.6. Hand traced: the first
    # month where the 3-month moving average minus its trailing-12-month
    # low reaches the 0.50pp threshold is month index 14 (see PR
    # description).
    dates = pd.date_range("2015-01-01", periods=40, freq="MS")
    values = pd.Series([4.0] * 12 + [4.6] * 28, index=dates)

    triggers = sahm_triggers(values)

    assert len(triggers) == 1
    assert triggers[0] == dates[14]


def test_sahm_triggers_finds_nothing_when_the_rate_never_rises() -> None:
    dates = pd.date_range("2015-01-01", periods=40, freq="MS")
    values = pd.Series([4.0] * 40, index=dates)
    assert sahm_triggers(values) == []


def test_sahm_triggers_does_not_fire_below_the_half_point_threshold() -> None:
    dates = pd.date_range("2015-01-01", periods=40, freq="MS")
    # A 0.3pp rise, sustained -- below the locked 0.50pp Sahm threshold.
    values = pd.Series([4.0] * 12 + [4.3] * 28, index=dates)
    assert sahm_triggers(values) == []


def test_pair_lead_times_computes_a_positive_lead_for_an_in_window_match() -> None:
    inflect = pd.Timestamp("2019-01-04")
    trigger = pd.Timestamp("2019-09-06")  # 35 weeks later, well inside 24 months

    pairs = pair_lead_times([inflect], [trigger])

    assert len(pairs) == 1
    assert pairs[0]["miss"] is False
    assert pairs[0]["sahm_trigger"] == str(trigger.date())
    expected_weeks = (trigger - inflect).days / 7.0
    assert pairs[0]["lead_weeks"] == round(expected_weeks, 1)


def test_pair_lead_times_records_a_miss_when_no_trigger_falls_in_the_24mo_window() -> None:
    inflect = pd.Timestamp("2019-01-04")
    trigger = pd.Timestamp("2021-06-01")  # ~29 months later, outside the window

    pairs = pair_lead_times([inflect], [trigger])

    assert len(pairs) == 1
    assert pairs[0]["miss"] is True
    assert pairs[0]["sahm_trigger"] is None
    assert pairs[0]["lead_weeks"] is None


def test_pair_lead_times_picks_the_earliest_matching_trigger_not_the_closest_to_window_end() -> None:
    inflect = pd.Timestamp("2019-01-04")
    early_trigger = pd.Timestamp("2019-04-05")
    late_trigger = pd.Timestamp("2020-06-01")

    pairs = pair_lead_times([inflect], [early_trigger, late_trigger])

    assert pairs[0]["sahm_trigger"] == str(early_trigger.date())


def test_pair_lead_times_excludes_a_trigger_that_precedes_the_inflection() -> None:
    inflect = pd.Timestamp("2019-06-01")
    earlier_trigger = pd.Timestamp("2019-01-04")  # before the inflection -- must not match

    pairs = pair_lead_times([inflect], [earlier_trigger])

    assert pairs[0]["miss"] is True
