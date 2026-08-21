"""Ensemble-construction engine v1 -- against its own written acceptance
checklist in docs/ensemble-construction-engine-v1.md."""

from __future__ import annotations

import numpy as np
import pytest

from app import ensemble


# --- composite_alpha_scores -------------------------------------------------

def test_equal_confidence_signals_weight_equally():
    symbols = ["A", "B", "C", "D"]
    raw_scores = {
        "sig1": np.array([1.0, 2.0, 3.0, 4.0]),
        "sig2": np.array([4.0, 3.0, 2.0, 1.0]),  # exact opposite ranking
    }
    confidence = {"sig1": 0.5, "sig2": 0.5}
    composite = ensemble.composite_alpha_scores(raw_scores, confidence, symbols)
    # Two equally-weighted, exactly opposite-ranked signals cancel to ~0 for everyone.
    np.testing.assert_allclose(composite, 0.0, atol=1e-9)


def test_zero_confidence_signal_contributes_nothing():
    symbols = ["A", "B", "C", "D"]
    raw_scores = {
        "sig1": np.array([1.0, 2.0, 3.0, 4.0]),
        "sig_ignored": np.array([100.0, -50.0, 7.0, 0.0]),
    }
    confidence = {"sig1": 1.0, "sig_ignored": 0.0}
    composite = ensemble.composite_alpha_scores(raw_scores, confidence, symbols)
    solo = ensemble.composite_alpha_scores(
        {"sig1": raw_scores["sig1"]}, {"sig1": 1.0}, symbols
    )
    np.testing.assert_allclose(composite, solo)


def test_zscore_uses_only_the_eligible_cross_section_not_full_history():
    """Two independent calls (simulating two different dates) with
    different eligible universes must not leak information between them --
    each call's z-score depends only on its own arguments."""
    symbols_t1 = ["A", "B", "C"]
    scores_t1 = np.array([1.0, 2.0, 3.0])
    c1 = ensemble.composite_alpha_scores({"sig": scores_t1}, {"sig": 1.0}, symbols_t1)

    symbols_t2 = ["A", "B", "C", "D", "E"]
    scores_t2 = np.array([1.0, 2.0, 3.0, 100.0, -100.0])
    c2 = ensemble.composite_alpha_scores({"sig": scores_t2}, {"sig": 1.0}, symbols_t2)

    # The first call's result must be identical regardless of what a later,
    # differently-shaped call computes -- no shared/cached statistics.
    c1_again = ensemble.composite_alpha_scores({"sig": scores_t1}, {"sig": 1.0}, symbols_t1)
    np.testing.assert_allclose(c1, c1_again)
    assert not np.allclose(c1, c2[:3])  # different universe -> different z-scores


def test_symbol_missing_from_every_signal_gets_nan():
    symbols = ["A", "B", "C"]
    raw_scores = {"sig1": np.array([1.0, np.nan, 3.0])}
    composite = ensemble.composite_alpha_scores(raw_scores, {"sig1": 1.0}, symbols)
    assert np.isnan(composite[1])
    assert np.isfinite(composite[0]) and np.isfinite(composite[2])


# --- shrinkage_covariance ----------------------------------------------------

def test_diagonal_equals_sample_variance_exactly():
    rng = np.random.default_rng(7)
    returns = rng.normal(size=(300, 6))
    cov = ensemble.shrinkage_covariance(returns, delta=0.3)
    sample = np.cov(returns, rowvar=False)
    np.testing.assert_allclose(np.diag(cov), np.diag(sample))


def test_shrunk_covariance_is_symmetric_and_psd():
    rng = np.random.default_rng(11)
    returns = rng.normal(size=(250, 8))
    cov = ensemble.shrinkage_covariance(returns, delta=0.3)
    np.testing.assert_allclose(cov, cov.T)
    eigenvalues = np.linalg.eigvalsh(cov)
    assert (eigenvalues >= -1e-8).all()


# --- construct_portfolio -----------------------------------------------------

def _toy_inputs():
    symbols = ["A", "B", "C", "D", "E", "F"]
    composite = np.array([1.41, 0.71, 0.53, 0.18, -0.71, -1.41])
    vols = np.array([0.02, 0.035, 0.03, 0.025, 0.03, 0.04])
    covariance = np.diag(vols**2)
    equity = 100_000.0
    prices = np.array([100.0, 50.0, 80.0, 60.0, 40.0, 30.0])
    stop_distances = prices * 0.05  # 5% stop for every name
    return symbols, composite, covariance, equity, prices, stop_distances


def test_gross_exposure_never_exceeds_100_pct():
    symbols, composite, covariance, equity, prices, stop_distances = _toy_inputs()
    sizes = ensemble.construct_portfolio(
        composite, covariance, symbols, equity, prices, stop_distances,
        min_names_per_side=2,
    )
    gross_notional = sum(abs(q) * prices[symbols.index(s)] for s, q in sizes.items())
    assert gross_notional <= equity * 1.0 + 1e-6


def test_long_and_short_sides_get_correct_sign():
    symbols, composite, covariance, equity, prices, stop_distances = _toy_inputs()
    sizes = ensemble.construct_portfolio(
        composite, covariance, symbols, equity, prices, stop_distances,
        min_names_per_side=2,
    )
    # A has the highest composite score -> long (positive shares).
    assert sizes["A"] > 0
    # F has the lowest composite score -> short (negative shares).
    assert sizes["F"] < 0


def test_no_position_exceeds_adr0004_stop_distance_cap():
    symbols, composite, covariance, equity, prices, stop_distances = _toy_inputs()
    sizes = ensemble.construct_portfolio(
        composite, covariance, symbols, equity, prices, stop_distances,
        min_names_per_side=2,
    )
    for symbol, shares in sizes.items():
        i = symbols.index(symbol)
        cap = np.floor(min(0.005 * equity / stop_distances[i], 0.10 * equity / prices[i]))
        assert abs(shares) <= cap + 1e-9


def test_insufficient_breadth_returns_no_trade():
    symbols = ["A", "B", "C"]
    composite = np.array([1.0, 0.5, -1.0])
    covariance = np.eye(3) * 0.01
    equity = 100_000.0
    prices = np.array([100.0, 50.0, 30.0])
    stop_distances = prices * 0.05
    sizes = ensemble.construct_portfolio(
        composite, covariance, symbols, equity, prices, stop_distances,
        min_names_per_side=5,
    )
    assert sizes == {}


def test_fewer_than_min_names_eligible_is_no_trade_not_a_smaller_book():
    symbols = ["A", "B", "C", "D", "E", "F"]
    composite = np.array([1.0, np.nan, np.nan, np.nan, np.nan, -1.0])
    covariance = np.eye(6) * 0.01
    equity = 100_000.0
    prices = np.full(6, 50.0)
    stop_distances = prices * 0.05
    sizes = ensemble.construct_portfolio(
        composite, covariance, symbols, equity, prices, stop_distances,
        min_names_per_side=5,
    )
    assert sizes == {}


def test_within_side_weight_favors_lower_volatility():
    """docs/ensemble-construction-engine-v1.md section 4's illustration
    (A outweighs B on the long side because A has lower volatility) --
    checked here at a realistic breadth (10 names/side) rather than the
    doc's tiny 6-asset illustration, because at only 2 names per side the
    ADR 0004 10%-of-equity notional cap always binds identically for both
    (any 2-name, 50%-gross-per-side target necessarily exceeds a 10% cap),
    which would flatten the ordering this test exists to check -- exactly
    why ADR 0010 set min_names_per_side=5 in the first place, and 5 is
    still tight enough that a wider group makes the check unambiguous."""
    n = 40
    symbols = [f"S{i}" for i in range(n)]
    composite = np.linspace(2.0, -2.0, n)  # S0 highest, S39 lowest
    vols = np.linspace(0.01, 0.05, n)  # S0 lowest vol ... S39 highest vol
    covariance = np.diag(vols**2)
    equity = 10_000_000.0
    prices = np.full(n, 50.0)
    stop_distances = np.full(n, 2.0)  # wide relative to natural weights -- not the binding constraint here

    sizes = ensemble.construct_portfolio(
        composite, covariance, symbols, equity, prices, stop_distances,
        long_short_fraction=0.5, min_names_per_side=5,
    )
    # Long side: S0..S19 (top half by composite score), lowest-vol name (S0)
    # should get more weight than a higher-vol long-side name (S10).
    notional_s0 = sizes["S0"] * prices[0]
    notional_s10 = sizes["S10"] * prices[10]
    assert notional_s0 > notional_s10 > 0
    # Short side: S20..S39, S39 has the highest vol among shorts -> smallest
    # magnitude weight; S20 (lowest vol among shorts) gets the most.
    notional_s20 = abs(sizes["S20"] * prices[20])
    notional_s39 = abs(sizes["S39"] * prices[39])
    assert notional_s20 > notional_s39
