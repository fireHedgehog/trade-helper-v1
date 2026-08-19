"""Overnight Gap Continuation v1 — gap-conditioned signed forward return vs.
joint-paired-resampled null.

Implements the unit-fixture requirement from
docs/research-protocols/overnight-gap-continuation-v1.md's lock checklist:
prove the (overnight, intraday) decomposition sums to the ordinary daily
return, that the joint-paired resampling mechanism genuinely preserves
(g, d) pairing (the design's one load-bearing correctness property), that a
planted continuation effect is detected, and that the placebo isolates the
overnight component specifically.
"""

from __future__ import annotations

import numpy as np
import pytest

from app import research


def _synthetic_ohlc(n: int, seed: int = 41) -> tuple[np.ndarray, np.ndarray]:
    """Independent small overnight/intraday noise, no planted effect."""
    rng = np.random.default_rng(seed)
    g = rng.normal(loc=0.0, scale=0.003, size=n)
    d = rng.normal(loc=0.0, scale=0.003, size=n)
    g[0] = 0.0
    closes = 100.0 * np.exp(np.cumsum(g + d))
    opens = np.concatenate([[closes[0]], closes[:-1] * np.exp(g[1:])])
    return opens, closes


def test_gap_and_intraday_returns_sum_to_ordinary_daily_return() -> None:
    opens, closes = _synthetic_ohlc(300)
    g, d = research.gap_and_intraday_returns(opens, closes)
    ordinary = research.log_returns_from_closes(closes)
    assert np.allclose((g + d)[1:], ordinary[1:])


def test_event_mask_matches_hand_computed_quantile() -> None:
    # 19 modestly varied "normal" values (0.10-0.19) followed by one clearly
    # extreme value. Because the expanding quantile is self-referential
    # (includes today's own value, matching RSI's placebo precedent), the
    # very first observation is always trivially "at its own threshold" --
    # that degeneracy is exactly why GAP_WARM_UP_SESSIONS excludes early
    # indices from event eligibility, not asserted here. What this fixture
    # verifies instead: once enough history exists, a normal value is
    # correctly classified False (hand-computed 90th percentile of the
    # first 19 values is 0.18; the 19th value itself is 0.17, below it) and
    # the extreme value is correctly classified True.
    component = np.array([
        0.10, 0.15, 0.12, 0.18, 0.11, 0.14, 0.13, 0.16, 0.17, 0.19,
        0.10, 0.12, 0.15, 0.11, 0.13, 0.14, 0.16, 0.18, 0.17, 5.00,
    ])
    mask = research.overnight_gap_event_mask(component, quantile=0.90)
    assert mask[18] == False  # noqa: E712 (explicit bool comparison for clarity)
    assert mask[19] == True  # noqa: E712


def test_resampling_preserves_gd_pairing() -> None:
    g_values = np.array([10.0, 20.0, 30.0, 40.0, 50.0, 60.0])
    d_values = np.array([-1.0, -2.0, -3.0, -4.0, -5.0, -6.0])
    rng = np.random.default_rng(3)
    indexes = research._circular_block_resample_indexes(len(g_values), block_bars=2, rng=rng)

    resampled_g = g_values[indexes]
    resampled_d = d_values[indexes]

    # Every resampled row's two components must come from the SAME original
    # day -- the one property this design's correctness depends on.
    for gi, di in zip(resampled_g, resampled_d):
        original_day = int(np.where(g_values == gi)[0][0])
        assert d_values[original_day] == di


def test_planted_gap_continuation_effect_is_detected() -> None:
    n = 1500
    rng = np.random.default_rng(17)
    g = rng.normal(loc=0.0, scale=0.002, size=n)
    d = rng.normal(loc=0.0, scale=0.002, size=n)
    g[0] = 0.0

    # Every 15 sessions, plant a large gap (random sign) and a genuine
    # forward continuation drift in that same direction over the next 10
    # sessions, so the Gap track should detect it and the intraday
    # component carries no such signal.
    plant_days = np.arange(20, n - 15, 15)
    gap_sign = rng.choice([-1.0, 1.0], size=len(plant_days))
    g[plant_days] = gap_sign * 0.03
    for day, sign in zip(plant_days, gap_sign):
        d[day + 1 : day + 11] += sign * 0.004

    closes = 100.0 * np.exp(np.cumsum(g + d))
    opens = np.concatenate([[closes[0]], closes[:-1] * np.exp(g[1:])])

    result = research.overnight_gap_bootstrap(opens, closes, resamples=200, seed=5, min_event_count=15)
    assert not result["insufficient_events"]
    assert result["observed_gap_mean_signed_forward_return"] > 0.01
    assert result["p_event"] < 0.05
    # The planted drift was injected into forward days generically, not
    # specifically triggered by the intraday component's own sign, so the
    # placebo should not show nearly as strong an effect.
    assert result["observed_gap_mean_signed_forward_return"] > result["observed_placebo_mean_signed_forward_return"]


def test_bootstrap_p_values_are_valid_probabilities() -> None:
    opens, closes = _synthetic_ohlc(1200, seed=9)
    result = research.overnight_gap_bootstrap(opens, closes, resamples=50, seed=1, min_event_count=15)
    if not result["insufficient_events"]:
        assert 0.0 <= result["p_event"] <= 1.0
        assert 0.0 <= result["p_gap_vs_placebo"] <= 1.0
    assert "diagnostics" in result
    for key in ("up_gap_mean_forward_return", "up_gap_count", "down_gap_mean_forward_return", "down_gap_count"):
        assert key in result["diagnostics"]


def test_bootstrap_rejects_mismatched_lengths() -> None:
    closes = np.full(200, 100.0)
    opens = np.full(150, 100.0)
    with pytest.raises(ValueError, match="same length"):
        research.overnight_gap_bootstrap(opens, closes, resamples=5)


def test_bootstrap_rejects_non_positive_prices() -> None:
    opens, closes = _synthetic_ohlc(300, seed=6)
    closes = closes.copy()
    closes[150] = 0.0
    with pytest.raises(ValueError, match="strictly positive"):
        research.overnight_gap_bootstrap(opens, closes, resamples=5)


def test_insufficient_events_flag_when_min_event_count_not_met() -> None:
    opens, closes = _synthetic_ohlc(100, seed=2)
    result = research.overnight_gap_bootstrap(opens, closes, resamples=10, min_event_count=1000)
    assert result["insufficient_events"] is True
    assert result["p_event"] is None
    assert result["p_gap_vs_placebo"] is None


def test_degenerate_tied_zero_history_does_not_flag_almost_everything() -> None:
    # A pre-lock review found that a long tied-at-zero stretch (e.g. stale
    # or forward-filled opens) collapses the expanding quantile to zero,
    # and a non-strict ">=" comparison alone would then flag almost every
    # day as an "event" -- defeating the self-calibrating design entirely.
    # This must stay guarded regardless of whether today's real universe
    # happens to trigger it.
    rng = np.random.default_rng(13)
    n = 300
    g = np.zeros(n)
    tied_mask = rng.random(n) >= 0.05  # ~95% exactly tied at zero
    g[~tied_mask] = rng.normal(loc=0.0, scale=0.01, size=int((~tied_mask).sum()))
    mask = research.overnight_gap_event_mask(g, quantile=0.90)
    qualifying_fraction = mask[research.GAP_WARM_UP_SESSIONS :].mean()
    assert qualifying_fraction < 0.20  # nowhere near the degenerate ~100% a bare ">=" would give


def test_correctly_paired_bootstrap_does_not_falsely_reject_on_anti_correlated_noise() -> None:
    # The protocol's own lock checklist requires this exact fixture: strong
    # SAME-DAY anti-correlation between the overnight and intraday
    # components (a gap-then-fade pattern) with NO genuine forward
    # continuation effect planted anywhere. A correctly joint-paired
    # bootstrap must not manufacture significance purely from this
    # within-day correlation structure -- the key correctness property the
    # whole joint-pairing design exists to preserve.
    n = 1500
    rng = np.random.default_rng(23)
    g = rng.normal(loc=0.0, scale=0.006, size=n)
    g[0] = 0.0
    noise = rng.normal(loc=0.0, scale=0.001, size=n)
    d = -0.9 * g + noise  # strong intraday fade of the overnight gap, same day only

    closes = 100.0 * np.exp(np.cumsum(g + d))
    opens = np.concatenate([[closes[0]], closes[:-1] * np.exp(g[1:])])

    result = research.overnight_gap_bootstrap(opens, closes, resamples=300, seed=8, min_event_count=15)
    assert not result["insufficient_events"]
    # No real continuation was planted, so a correctly-specified null should
    # not reject at conventional significance.
    assert result["p_event"] > 0.05
