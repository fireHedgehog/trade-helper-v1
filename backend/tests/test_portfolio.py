"""Stage 5 tests for deterministic portfolio sizing and allocation."""

from __future__ import annotations

from dataclasses import replace

import pytest

from app.portfolio import (
    CandidateOrder,
    PortfolioConfig,
    PortfolioPosition,
    PortfolioState,
    allocate_entries,
    initial_portfolio,
    size_entry,
)


def _candidate(
    symbol: str,
    *,
    score: float = 1.0,
    expected_open: float = 100.0,
    stop: float | None = 95.0,
    sector: str | None = "Technology",
    cluster: str | None = "US Equity",
) -> CandidateOrder:
    return CandidateOrder(
        signal_date="2026-08-17",
        order_date="2026-08-18",
        symbol=symbol,
        expected_open=expected_open,
        stop=stop,
        score=score,
        sector=sector,
        cluster=cluster,
    )


def _position(
    symbol: str,
    *,
    market_value: float,
    sector: str = "Technology",
    cluster: str = "US Equity",
) -> PortfolioPosition:
    return PortfolioPosition(
        symbol=symbol,
        shares=100,
        entry_date="2026-08-10",
        entry_price=market_value / 100,
        entry_fee=0.0,
        stop=market_value / 100 * 0.95,
        sector=sector,
        cluster=cluster,
        market_price=market_value / 100,
        target=None,
    )


def test_initial_portfolio_has_explicit_capital_and_peak() -> None:
    state = initial_portfolio()

    assert state.cash == 100_000
    assert state.peak_equity == 100_000
    assert state.positions == {}
    assert not state.halted


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("initial_cash", 0),
        ("risk_per_trade", 0),
        ("max_position_fraction", 1.1),
        ("max_sector_fraction", float("nan")),
        ("drawdown_limit", -0.1),
        ("commission", 1),
        ("spread", -0.1),
    ],
)
def test_config_fails_closed_on_invalid_limits(field: str, value: float) -> None:
    with pytest.raises(ValueError):
        PortfolioConfig(**{field: value})


def test_position_size_uses_smaller_of_stop_risk_and_notional_cap() -> None:
    config = PortfolioConfig(commission=0, spread=0, slippage=0)

    ordinary = size_entry(expected_open=100, stop=95, equity=100_000, config=config)
    wide_stop = size_entry(expected_open=100, stop=80, equity=100_000, config=config)

    assert ordinary.requested_shares == 100  # both budgets permit exactly 100
    assert wide_stop.requested_shares == 25  # $500 risk / $20 per share


def test_round_trip_costs_are_included_in_stop_risk() -> None:
    free = size_entry(
        expected_open=100,
        stop=95,
        equity=100_000,
        config=PortfolioConfig(commission=0, spread=0, slippage=0),
    )
    costed = size_entry(
        expected_open=100,
        stop=95,
        equity=100_000,
        config=PortfolioConfig(),
    )

    assert costed.estimated_loss_per_share > free.estimated_loss_per_share
    assert costed.requested_shares < free.requested_shares


@pytest.mark.parametrize("stop", [0, 100, 101, float("nan")])
def test_sizing_rejects_unknown_or_non_protective_risk(stop: float) -> None:
    with pytest.raises(ValueError, match="stop"):
        size_entry(
            expected_open=100,
            stop=stop,
            equity=100_000,
            config=PortfolioConfig(),
        )


def test_concurrent_orders_use_score_then_symbol_and_can_be_reduced_for_cash() -> None:
    config = PortfolioConfig(commission=0, spread=0, slippage=0)
    state = replace(initial_portfolio(config), cash=25_000)
    candidates = [
        _candidate("BBB", score=2, sector="B", cluster="B"),
        _candidate("AAA", score=2, sector="A", cluster="A"),
        _candidate("CCC", score=3, sector="C", cluster="C"),
    ]

    result = allocate_entries(candidates, state=state, equity=100_000, config=config)

    assert [order.symbol for order in result.accepted] == ["CCC", "AAA", "BBB"]
    assert [order.shares for order in result.accepted] == [100, 100, 50]
    assert result.remaining_cash == 0


def test_order_is_rejected_when_cash_cannot_buy_one_share() -> None:
    config = PortfolioConfig(commission=0, spread=0, slippage=0)
    state = replace(initial_portfolio(config), cash=50)

    result = allocate_entries([_candidate("AAA")], state=state, equity=100_000, config=config)

    assert result.accepted == ()
    assert result.rejected[0].reason == "insufficient_cash"
    assert result.rejected[0].requested_shares == 100
    assert result.rejected[0].available_cash == 50


def test_existing_pending_order_reserves_cash_for_later_allocation() -> None:
    config = PortfolioConfig(commission=0, spread=0, slippage=0)
    initial = initial_portfolio(config)
    first = allocate_entries(
        [_candidate("AAA", sector="A", cluster="A")],
        state=initial,
        equity=100_000,
        config=config,
    )
    state = replace(initial, pending_orders=first.accepted)

    second = allocate_entries(
        [_candidate("BBB", sector="B", cluster="B")],
        state=state,
        equity=100_000,
        config=config,
    )

    assert second.accepted[0].shares == 100
    assert second.remaining_cash == 80_000


def test_order_is_reduced_to_remaining_sector_capacity() -> None:
    config = PortfolioConfig(commission=0, spread=0, slippage=0)
    state = PortfolioState(
        cash=80_000,
        peak_equity=100_000,
        positions={"OLD": _position("OLD", market_value=20_000)},
    )

    result = allocate_entries([_candidate("NEW")], state=state, equity=100_000, config=config)

    assert result.accepted[0].requested_shares == 100
    assert result.accepted[0].shares == 50


def test_sector_limit_accounts_for_existing_marked_position() -> None:
    config = PortfolioConfig(commission=0, spread=0, slippage=0)
    state = PortfolioState(
        cash=75_000,
        peak_equity=100_000,
        positions={"OLD": _position("OLD", market_value=25_000)},
    )

    result = allocate_entries([_candidate("NEW")], state=state, equity=100_000, config=config)

    assert result.accepted == ()
    assert result.rejected[0].reason == "sector_limit"


def test_cluster_limit_accounts_for_existing_marked_position() -> None:
    config = PortfolioConfig(commission=0, spread=0, slippage=0)
    state = PortfolioState(
        cash=70_000,
        peak_equity=100_000,
        positions={
            "OLD": _position(
                "OLD", market_value=30_000, sector="Bonds", cluster="Risk Assets"
            )
        },
    )

    result = allocate_entries(
        [_candidate("NEW", sector="Technology", cluster="Risk Assets")],
        state=state,
        equity=100_000,
        config=config,
    )

    assert result.accepted == ()
    assert result.rejected[0].reason == "cluster_limit"


def test_existing_symbol_and_missing_classification_are_logged() -> None:
    config = PortfolioConfig(commission=0, spread=0, slippage=0)
    state = PortfolioState(
        cash=90_000,
        peak_equity=100_000,
        positions={"AAA": _position("AAA", market_value=10_000)},
    )

    result = allocate_entries(
        [_candidate("AAA"), _candidate("BBB", sector=None)],
        state=state,
        equity=100_000,
        config=config,
    )

    assert [(row.symbol, row.reason) for row in result.rejected] == [
        ("AAA", "position_exists"),
        ("BBB", "missing_classification"),
    ]


def test_halted_portfolio_rejects_otherwise_valid_entry() -> None:
    config = PortfolioConfig(commission=0, spread=0, slippage=0)
    state = replace(initial_portfolio(config), halted=True)

    result = allocate_entries([_candidate("AAA")], state=state, equity=100_000, config=config)

    assert result.accepted == ()
    assert result.rejected[0].reason == "portfolio_halted"
