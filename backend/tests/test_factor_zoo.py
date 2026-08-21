"""Unit tests for backend/app/factor_zoo.py's operators and evaluation harness.

Operator tests use tiny, hand-checkable synthetic panels. The evaluation
tests use synthetic data with a known planted relationship (or none) --
they check the harness measures what it claims to, not that any real-market
alpha is real (no such claim is made by this module).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from app import factor_zoo as fz


def _panel(values: dict[str, list[float]], dates: list[str] | None = None) -> pd.DataFrame:
    dates = dates or [f"2024-01-{i + 1:02d}" for i in range(len(next(iter(values.values()))))]
    return pd.DataFrame(values, index=dates)


# ---------------------------------------------------------------------------
# Operators
# ---------------------------------------------------------------------------


def test_rank_is_cross_sectional_percentile_per_date():
    df = _panel({"A": [1, 3], "B": [2, 1], "C": [3, 2]})
    result = fz.rank(df)
    # date 0: A=1(min)->1/3, B=2(mid)->2/3, C=3(max)->3/3
    assert result.loc["2024-01-01", "A"] == pytest.approx(1 / 3)
    assert result.loc["2024-01-01", "B"] == pytest.approx(2 / 3)
    assert result.loc["2024-01-01", "C"] == pytest.approx(3 / 3)
    # date 1: B=1(min)->1/3, C=2(mid)->2/3, A=3(max)->3/3
    assert result.loc["2024-01-02", "B"] == pytest.approx(1 / 3)
    assert result.loc["2024-01-02", "A"] == pytest.approx(3 / 3)


def test_delay_and_delta():
    df = _panel({"A": [1.0, 2.0, 4.0]})
    assert fz.delay(df, 1)["A"].tolist()[1:] == [1.0, 2.0]
    assert np.isnan(fz.delay(df, 1)["A"].iloc[0])
    delta = fz.delta(df, 1)["A"]
    assert delta.iloc[1] == pytest.approx(1.0)
    assert delta.iloc[2] == pytest.approx(2.0)


def test_ts_rank_ordinal_rank_of_last_value_in_window():
    df = _panel({"A": [5.0, 1.0, 3.0]})
    result = fz.ts_rank(df, 3)["A"]
    # window [5,1,3]: last value 3 -> 2 values (5) are >= not smaller; strictly
    # smaller than 3: {1} -> rank = 1 + 1 = 2
    assert result.iloc[2] == pytest.approx(2.0)


def test_ts_argmax_position_of_max_in_window():
    df = _panel({"A": [1.0, 5.0, 2.0]})
    result = fz.ts_argmax(df, 3)["A"]
    # max (5.0) is at position index 1 (0-based) -> +1 = 2
    assert result.iloc[2] == pytest.approx(2.0)


def test_decay_linear_weights_recent_values_more():
    df = _panel({"A": [1.0, 1.0, 4.0]})
    result = fz.decay_linear(df, 3)["A"]
    # weights 1,2,3 sum=6: (1*1 + 1*2 + 4*3)/6 = 15/6 = 2.5
    assert result.iloc[2] == pytest.approx(2.5)


def test_scale_rescales_each_row_to_unit_abs_sum():
    df = _panel({"A": [2.0], "B": [-2.0]}, dates=["2024-01-01"])
    result = fz.scale(df, k=1.0)
    assert abs(result.loc["2024-01-01"]).sum() == pytest.approx(1.0)
    assert result.loc["2024-01-01", "A"] == pytest.approx(0.5)
    assert result.loc["2024-01-01", "B"] == pytest.approx(-0.5)


def test_scale_handles_all_zero_row_without_raising():
    df = _panel({"A": [0.0], "B": [0.0]}, dates=["2024-01-01"])
    result = fz.scale(df)
    assert (result.loc["2024-01-01"] == 0.0).all()


def test_correlation_rolling_pairwise_columnwise():
    dates = [f"2024-01-{i + 1:02d}" for i in range(5)]
    x = _panel({"A": [1.0, 2.0, 3.0, 4.0, 5.0]}, dates=dates)
    y = _panel({"A": [5.0, 4.0, 3.0, 2.0, 1.0]}, dates=dates)
    result = fz.correlation(x, y, 3)["A"]
    # perfectly negatively correlated -> -1 once the window is full
    assert result.iloc[-1] == pytest.approx(-1.0, abs=1e-9)


def test_correlation_replaces_inf_and_nan_with_zero():
    dates = [f"2024-01-{i + 1:02d}" for i in range(3)]
    constant = _panel({"A": [1.0, 1.0, 1.0]}, dates=dates)  # zero variance
    other = _panel({"A": [1.0, 2.0, 3.0]}, dates=dates)
    result = fz.correlation(constant, other, 3)["A"]
    assert result.iloc[-1] == 0.0


def test_signed_power_preserves_sign():
    df = _panel({"A": [-3.0, 2.0]}, dates=["2024-01-01", "2024-01-02"])
    result = fz.signed_power(df, 2.0)
    assert result.loc["2024-01-01", "A"] == pytest.approx(-9.0)
    assert result.loc["2024-01-02", "A"] == pytest.approx(4.0)


# ---------------------------------------------------------------------------
# Evaluation harness
# ---------------------------------------------------------------------------


def _synthetic_close_panel(rng: np.random.Generator, n_days: int, n_symbols: int) -> pd.DataFrame:
    dates = [f"2024-{1 + i // 28:02d}-{1 + i % 28:02d}" for i in range(n_days)]
    symbols = [f"S{i:03d}" for i in range(n_symbols)]
    log_returns = rng.normal(0, 0.01, size=(n_days, n_symbols))
    prices = 100 * np.exp(np.cumsum(log_returns, axis=0))
    return pd.DataFrame(prices, index=dates, columns=symbols)


def test_evaluate_factor_recovers_planted_predictive_signal():
    rng = np.random.default_rng(7)
    n_days, n_symbols = 120, 40
    close = _synthetic_close_panel(rng, n_days, n_symbols)
    forward_return = close.shift(-1) / close - 1.0
    # A factor built directly from tomorrow's return (plus noise) must show
    # strong positive rank-IC and a positive quintile spread -- this checks
    # the harness measures a known-true relationship correctly, not that
    # any real alpha is real.
    noise = rng.normal(0, 0.001, size=forward_return.shape)
    factor = forward_return + noise
    evaluation = fz.evaluate_factor("planted", factor, close, min_symbols=10)
    assert evaluation.ic_mean > 0.5
    assert evaluation.sharpe is not None and evaluation.sharpe > 0


def test_evaluate_factor_on_pure_noise_shows_near_zero_ic():
    rng = np.random.default_rng(11)
    n_days, n_symbols = 150, 40
    close = _synthetic_close_panel(rng, n_days, n_symbols)
    unrelated_factor = pd.DataFrame(
        rng.normal(size=close.shape), index=close.index, columns=close.columns
    )
    evaluation = fz.evaluate_factor("noise", unrelated_factor, close, min_symbols=10)
    assert abs(evaluation.ic_mean) < 0.15


def test_evaluate_factor_zero_cost_default_is_unchanged():
    """round_trip_cost_bps defaults to 0.0 -- every existing factor-zoo-v1
    number must stay reproducible after this parameter was added."""
    rng = np.random.default_rng(7)
    close = _synthetic_close_panel(rng, 60, 20)
    forward_return = close.shift(-1) / close - 1.0
    factor = forward_return + rng.normal(0, 0.001, size=forward_return.shape)
    with_default = fz.evaluate_factor("planted", factor, close, min_symbols=10)
    explicit_zero = fz.evaluate_factor(
        "planted", factor, close, min_symbols=10, round_trip_cost_bps=0.0
    )
    pd.testing.assert_series_equal(
        with_default.daily_spread_returns, explicit_zero.daily_spread_returns
    )


def test_evaluate_factor_cost_charges_only_quintile_turnover():
    """Hand-constructed panel, quintile_size=1 (5 symbols): day 0 has no
    prior day to compare against, so it is turnover-free regardless of
    cost. Day 1's top AND bottom both fully turn over (A/E -> B/A), so at
    round_trip_cost_bps=100 (1%) the cost drag is exactly
    (1.0 + 1.0) * 0.01 = 0.02 -- chosen so it exactly cancels day 1's
    0.01 - (-0.01) = 0.02 raw spread, landing on a hand-checkable zero."""
    dates = ["2024-01-01", "2024-01-02", "2024-01-03"]
    close = _panel(
        {
            # Day 0 -> day 1 closes vary slightly across C/D/E so day 0 also
            # has a valid (non-tied) rank-IC; A/B are what day 1's spread
            # actually prices, via day 1 -> day 2 below.
            "A": [100.0, 100.0, 101.0],
            "B": [100.0, 100.0, 99.0],
            "C": [100.0, 100.0, 100.0],
            "D": [100.0, 100.5, 100.0],
            "E": [100.0, 99.5, 100.0],
        },
        dates=dates,
    )
    factor = _panel(
        {
            "A": [1.0, 5.0, 5.0],
            "B": [2.0, 1.0, 1.0],
            "C": [3.0, 3.0, 3.0],
            "D": [4.0, 4.0, 4.0],
            "E": [5.0, 2.0, 2.0],
        },
        dates=dates,
    )
    zero_cost = fz.evaluate_factor("turnover", factor, close, min_symbols=5)
    costed = fz.evaluate_factor(
        "turnover", factor, close, min_symbols=5, round_trip_cost_bps=100.0
    )
    day0, day1 = dates[0], dates[1]
    # Day 0 has no prior day to compare against -- turnover-free regardless
    # of cost, whatever its raw spread happens to be.
    assert costed.daily_spread_returns[day0] == pytest.approx(zero_cost.daily_spread_returns[day0])
    assert zero_cost.daily_spread_returns[day1] == pytest.approx(0.02)
    assert costed.daily_spread_returns[day1] == pytest.approx(0.0, abs=1e-9)


def test_evaluate_factor_raises_on_insufficient_cross_section():
    close = _panel({"A": [100.0, 101.0, 102.0]})
    factor = _panel({"A": [1.0, 2.0, 3.0]})
    with pytest.raises(ValueError):
        fz.evaluate_factor("too_thin", factor, close, min_symbols=5)


def test_factor_return_metrics_matches_hand_computed_sharpe():
    daily_returns = pd.Series([0.01, -0.005, 0.02, 0.0, -0.01])
    metrics = fz.factor_return_metrics(daily_returns)
    import math
    expected_sharpe = daily_returns.mean() / daily_returns.std() * math.sqrt(252)
    assert metrics["sharpe"] == pytest.approx(expected_sharpe)
    assert metrics["win_rate"] == pytest.approx(2 / 5)


def test_regime_concentration_flags_the_year_that_flips_the_sign():
    """Hand-constructed: 2023 (3 days, all +0.01) and 2024 (2 days, both
    -0.10). Full mean = (0.03 - 0.20) / 5 = -0.034 (negative). Excluding
    2024 leaves only the +0.01 days -> mean flips to positive. Excluding
    2023 leaves only the -0.10 days -> stays negative, no flip."""
    daily_returns = pd.Series(
        [0.01, 0.01, 0.01, -0.10, -0.10],
        index=["2023-01-01", "2023-01-02", "2023-01-03", "2024-01-01", "2024-01-02"],
    )
    result = fz.regime_concentration_by_year(daily_returns)
    assert result["full_sample_mean"] == pytest.approx(-0.034)
    by_year = {row["year"]: row for row in result["by_year"]}
    assert by_year["2023"]["mean_excluding_year"] == pytest.approx(-0.10)
    assert by_year["2023"]["flips_sign"] is False
    assert by_year["2024"]["mean_excluding_year"] == pytest.approx(0.01)
    assert by_year["2024"]["flips_sign"] is True
    assert result["any_year_flips_sign"] is True


def test_pairwise_orthogonality_flags_identical_series_as_redundant():
    dates = [f"2024-01-{i + 1:02d}" for i in range(40)]
    series = pd.Series(np.linspace(-0.01, 0.01, 40), index=dates)
    eval_a = fz.FactorEvaluation(
        name="a", n_days=40, n_symbols_median=20, ic_mean=0.1, ic_std=0.1, ic_ir=1.0,
        daily_spread_returns=series, sharpe=1.0, cagr=0.1, annual_volatility=0.1,
        max_drawdown=-0.05, calmar=2.0, win_rate=0.5, total_return=0.1,
    )
    eval_b = fz.FactorEvaluation(
        name="b", n_days=40, n_symbols_median=20, ic_mean=0.1, ic_std=0.1, ic_ir=1.0,
        daily_spread_returns=series.copy(), sharpe=1.0, cagr=0.1, annual_volatility=0.1,
        max_drawdown=-0.05, calmar=2.0, win_rate=0.5, total_return=0.1,
    )
    results = fz.pairwise_orthogonality([eval_a, eval_b])
    assert len(results) == 1
    assert results[0]["redundant"] is True
    assert results[0]["correlation"] == pytest.approx(1.0)


def _synthetic_panel(rng: np.random.Generator, n_days: int, n_symbols: int) -> fz.Panel:
    dates = [f"2024-{1 + i // 28:02d}-{1 + i % 28:02d}" for i in range(n_days)]
    symbols = [f"S{i:03d}" for i in range(n_symbols)]
    close = _synthetic_close_panel(rng, n_days, n_symbols)
    open_ = close * (1 + rng.normal(0, 0.001, close.shape))
    high = pd.DataFrame(
        np.maximum(open_.to_numpy(), close.to_numpy()) * 1.001, index=dates, columns=symbols
    )
    low = pd.DataFrame(
        np.minimum(open_.to_numpy(), close.to_numpy()) * 0.999, index=dates, columns=symbols
    )
    volume = pd.DataFrame(
        rng.integers(1000, 100000, size=close.shape), index=dates, columns=symbols
    ).astype(float)
    return fz.Panel.build(open_, high, low, close, volume)


def test_all_registered_alphas_run_without_error_on_synthetic_panel():
    rng = np.random.default_rng(3)
    panel = _synthetic_panel(rng, 60, 15)
    for name, formula in fz.ALPHAS.items():
        result = formula(panel)
        assert isinstance(result, pd.DataFrame), name
        assert result.shape == panel.close.shape, name


def test_all_classic_indicators_run_without_error_on_synthetic_panel():
    rng = np.random.default_rng(5)
    panel = _synthetic_panel(rng, 60, 15)
    for name, formula in fz.CLASSIC_INDICATORS.items():
        result = formula(panel)
        assert isinstance(result, pd.DataFrame), name
        assert result.shape == panel.close.shape, name


# ---------------------------------------------------------------------------
# Classic indicators -- hand-checkable correctness
# ---------------------------------------------------------------------------


def _flat_panel(close_values: list[float]) -> fz.Panel:
    dates = [f"2024-01-{i + 1:02d}" for i in range(len(close_values))]
    close = pd.DataFrame({"A": close_values}, index=dates)
    high = close * 1.01
    low = close * 0.99
    open_ = close.shift(1).fillna(close.iloc[0])
    volume = pd.DataFrame({"A": [10000.0] * len(close_values)}, index=dates)
    return fz.Panel.build(open_, high, low, close, volume)


def test_rsi14_is_100_when_no_losses_in_the_window():
    panel = _flat_panel([100.0 + i for i in range(20)])  # strictly increasing
    result = fz.rsi14(panel)["A"]
    assert result.iloc[-1] == pytest.approx(100.0)


def test_rsi14_is_bounded_0_to_100():
    rng = np.random.default_rng(1)
    panel = _synthetic_panel(rng, 60, 5)
    result = fz.rsi14(panel)
    valid = result.dropna()
    assert (valid >= 0).all().all()
    assert (valid <= 100).all().all()


def test_bollinger_pct_b_is_one_at_the_upper_band():
    values = [100.0] * 19 + [130.0]  # a sharp spike after a flat run
    panel = _flat_panel(values)
    result = fz.bollinger_pct_b(panel)["A"]
    mid = np.mean(values[-20:])
    std = np.std(values[-20:], ddof=1)
    expected = (values[-1] - (mid - 2 * std)) / (4 * std)
    assert result.iloc[-1] == pytest.approx(expected)


def _flat_hlc_panel(close_values: list[float]) -> fz.Panel:
    """Like _flat_panel but high == low == close, for tests where the
    high/low series (not close) must exactly reach the window extreme."""
    dates = [f"2024-01-{i + 1:02d}" for i in range(len(close_values))]
    close = pd.DataFrame({"A": close_values}, index=dates)
    open_ = close.shift(1).fillna(close.iloc[0])
    volume = pd.DataFrame({"A": [10000.0] * len(close_values)}, index=dates)
    return fz.Panel.build(open_, close.copy(), close.copy(), close, volume)


def test_stochastic_k_is_zero_at_the_14_day_low():
    values = [110.0 - i for i in range(15)]  # strictly falling, last value is the low
    panel = _flat_hlc_panel(values)
    result = fz.stochastic_k(panel)["A"]
    assert result.iloc[-1] == pytest.approx(0.0)


def test_williams_r_is_zero_at_the_14_day_high():
    values = [100.0 + i for i in range(15)]  # strictly rising, last value is the high
    panel = _flat_hlc_panel(values)
    result = fz.williams_r(panel)["A"]
    assert result.iloc[-1] == pytest.approx(0.0)


def test_roc12_matches_hand_computed_rate_of_change():
    values = [100.0] * 12 + [110.0]
    panel = _flat_panel(values)
    result = fz.roc12(panel)["A"]
    assert result.iloc[-1] == pytest.approx(0.10)
