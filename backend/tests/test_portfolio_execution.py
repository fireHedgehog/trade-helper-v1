"""Stage 5 integration tests for the shared-cash portfolio replay."""

from __future__ import annotations

import pandas as pd
import pytest

from app.portfolio import PortfolioConfig
from app.portfolio_execution import AssetClassification, simulate_portfolio
from app.rules import RuleSet


def _bars(
    *,
    opens: list[float],
    closes: list[float] | None = None,
    marker: int = 1,
    start: str = "2026-01-05",
) -> pd.DataFrame:
    closes = closes or opens
    dates = pd.bdate_range(start, periods=len(opens))
    return pd.DataFrame(
        {
            "date": dates.strftime("%Y-%m-%d"),
            "open": opens,
            "high": [max(open_, close) + 1 for open_, close in zip(opens, closes)],
            "low": [min(open_, close) - 1 for open_, close in zip(opens, closes)],
            "close": closes,
            "volume": [marker] * len(opens),
        }
    )


def _rules(
    length: int,
    *,
    entries: set[int] = frozenset(),
    exits: set[int] = frozenset(),
    stop: float = 90.0,
) -> RuleSet:
    return RuleSet(
        entries=pd.Series([index in entries for index in range(length)]),
        exits=pd.Series([index in exits for index in range(length)]),
        atr=pd.Series([float("nan")] * length),
        stop_levels=pd.Series([stop] * length, dtype=float),
        target_levels=pd.Series([float("nan")] * length),
    )


def _classifications(*symbols: str) -> dict[str, AssetClassification]:
    return {
        symbol: AssetClassification(sector=f"sector-{symbol}", cluster=f"cluster-{symbol}")
        for symbol in symbols
    }


def test_replay_fails_closed_when_symbol_calendars_differ() -> None:
    first = _bars(opens=[100, 101, 102])
    second = _bars(opens=[100, 101, 102], start="2026-01-06")

    with pytest.raises(ValueError, match="calendar differs"):
        simulate_portfolio(
            {"AAA": first, "BBB": second},
            strategy_name="S/R Bounce",
            params={},
            classifications=_classifications("AAA", "BBB"),
        )


def test_replay_requires_explicit_classification() -> None:
    with pytest.raises(ValueError, match="missing classifications"):
        simulate_portfolio(
            {"AAA": _bars(opens=[100, 101])},
            strategy_name="S/R Bounce",
            params={},
            classifications={},
        )


def test_close_signals_fill_at_next_open_and_mark_one_account(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bars = _bars(
        opens=[100, 110, 120, 80, 81],
        closes=[100, 111, 120, 80, 81],
    )
    monkeypatch.setattr(
        "app.portfolio_execution.build_rules",
        lambda *_args, **_kwargs: _rules(len(bars), entries={0}, exits={2}),
    )
    config = PortfolioConfig(commission=0, spread=0, slippage=0)

    replay = simulate_portfolio(
        {"AAA": bars},
        strategy_name="S/R Bounce",
        params={},
        classifications=_classifications("AAA"),
        config=config,
    )

    assert [(fill.side, fill.fill_date, fill.price) for fill in replay.fills] == [
        ("entry", str(bars["date"].iloc[1]), 110),
        ("exit", str(bars["date"].iloc[3]), 80),
    ]
    assert replay.trades[0].shares == 25  # gap widened stop risk from $10 to $20
    assert replay.trades[0].pnl == -750
    assert replay.equity[0].position_count == 0
    assert replay.equity[1].position_count == 1
    assert replay.equity[1].equity == 100_025
    assert replay.equity[3].cash == 97_250
    assert replay.equity[3].unsettled_cash == 2_000
    assert replay.equity[-1].cash == 99_250
    assert replay.equity[-1].equity == 99_250


def test_fill_prices_charge_spread_slippage_and_commission(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bars = _bars(opens=[100, 100, 100, 100], closes=[100, 100, 100, 100])
    monkeypatch.setattr(
        "app.portfolio_execution.build_rules",
        lambda *_args, **_kwargs: _rules(len(bars), entries={0}, exits={1}, stop=90),
    )
    config = PortfolioConfig(commission=0.01, spread=0.02, slippage=0.01)

    replay = simulate_portfolio(
        {"AAA": bars},
        strategy_name="S/R Bounce",
        params={},
        classifications=_classifications("AAA"),
        config=config,
    )

    entry, exit_ = replay.fills
    assert entry.price == pytest.approx(102)
    assert entry.fee == pytest.approx(entry.shares * 102 * 0.01)
    assert exit_.price == pytest.approx(98)
    assert exit_.fee == pytest.approx(exit_.shares * 98 * 0.01)


def test_concurrent_entries_share_cash_in_locked_priority_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bars = _bars(opens=[100, 100, 100])
    monkeypatch.setattr(
        "app.portfolio_execution.build_rules",
        lambda *_args, **_kwargs: _rules(len(bars), entries={0}, stop=99),
    )
    config = PortfolioConfig(
        initial_cash=15_000,
        risk_per_trade=0.5,
        max_position_fraction=0.8,
        max_sector_fraction=1,
        max_cluster_fraction=1,
        commission=0,
        spread=0,
        slippage=0,
    )

    replay = simulate_portfolio(
        {"AAA": bars, "BBB": bars.copy()},
        strategy_name="S/R Bounce",
        params={},
        classifications=_classifications("AAA", "BBB"),
        priority_scores={"AAA": 1, "BBB": 2},
        config=config,
    )

    entries = [fill for fill in replay.fills if fill.side == "entry"]
    assert [(fill.symbol, fill.shares) for fill in entries] == [("BBB", 120), ("AAA", 30)]
    assert replay.equity[1].cash == 0
    assert replay.equity[1].market_value == 15_000
    assert replay.equity[1].gross_exposure == 1


def test_same_day_close_cannot_change_later_fills_at_the_same_open(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    aaa = _bars(opens=[100, 100, 100], closes=[100, 1_000, 1_000])
    bbb = _bars(opens=[100, 100, 100], closes=[100, 100, 100])
    monkeypatch.setattr(
        "app.portfolio_execution.build_rules",
        lambda *_args, **_kwargs: _rules(len(aaa), entries={0}, stop=99),
    )
    config = PortfolioConfig(
        initial_cash=20_000,
        risk_per_trade=0.5,
        max_position_fraction=0.5,
        max_sector_fraction=0.75,
        max_cluster_fraction=1,
        commission=0,
        spread=0,
        slippage=0,
    )
    classification = AssetClassification(sector="Shared", cluster="Shared")

    replay = simulate_portfolio(
        {"AAA": aaa, "BBB": bbb},
        strategy_name="S/R Bounce",
        params={},
        classifications={"AAA": classification, "BBB": classification},
        priority_scores={"AAA": 2, "BBB": 1},
        config=config,
    )

    entries = [fill for fill in replay.fills if fill.side == "entry"]
    assert [(fill.symbol, fill.shares) for fill in entries] == [("AAA", 100), ("BBB", 50)]


def test_sale_proceeds_cannot_fund_signal_before_next_session_settlement(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    aaa = _bars(opens=[100] * 5, marker=1)
    bbb = _bars(opens=[100] * 5, marker=2)

    def rules_for(bars: pd.DataFrame, *_args, **_kwargs) -> RuleSet:
        if int(bars["volume"].iloc[0]) == 1:
            return _rules(len(bars), entries={0}, exits={2}, stop=99)
        return _rules(len(bars), entries={3}, stop=99)

    monkeypatch.setattr("app.portfolio_execution.build_rules", rules_for)
    config = PortfolioConfig(
        initial_cash=10_000,
        risk_per_trade=1,
        max_position_fraction=1,
        max_sector_fraction=1,
        max_cluster_fraction=1,
        commission=0,
        spread=0,
        slippage=0,
    )

    replay = simulate_portfolio(
        {"AAA": aaa, "BBB": bbb},
        strategy_name="S/R Bounce",
        params={},
        classifications=_classifications("AAA", "BBB"),
        config=config,
    )

    exit_date = str(aaa["date"].iloc[3])
    settlement_date = str(aaa["date"].iloc[4])
    exit_snapshot = next(row for row in replay.equity if row.date == exit_date)
    settled_snapshot = next(row for row in replay.equity if row.date == settlement_date)
    assert exit_snapshot.cash == 0
    assert exit_snapshot.unsettled_cash == 10_000
    assert exit_snapshot.equity == 10_000
    assert settled_snapshot.cash == 10_000
    assert settled_snapshot.unsettled_cash == 0
    assert any(
        row.symbol == "BBB" and row.reason == "insufficient_cash"
        for row in replay.state.rejected_orders
    )


def test_adverse_entry_gap_reduces_fill_to_available_cash(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bars = _bars(opens=[100, 120, 120], closes=[100, 120, 120])
    monkeypatch.setattr(
        "app.portfolio_execution.build_rules",
        lambda *_args, **_kwargs: _rules(len(bars), entries={0}, stop=95),
    )
    config = PortfolioConfig(
        initial_cash=10_000,
        risk_per_trade=1,
        max_position_fraction=1,
        max_sector_fraction=1,
        max_cluster_fraction=1,
        commission=0,
        spread=0,
        slippage=0,
    )

    replay = simulate_portfolio(
        {"AAA": bars},
        strategy_name="S/R Bounce",
        params={},
        classifications=_classifications("AAA"),
        config=config,
    )

    entry = replay.fills[0]
    assert entry.requested_shares == 100
    assert entry.shares == 83
    assert replay.state.cash == 40


def test_gap_rechecks_sector_capacity_at_actual_fill(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bars = _bars(opens=[100, 200, 200], closes=[100, 200, 200])
    monkeypatch.setattr(
        "app.portfolio_execution.build_rules",
        lambda *_args, **_kwargs: _rules(len(bars), entries={0}, stop=90),
    )
    config = PortfolioConfig(
        risk_per_trade=1,
        max_position_fraction=1,
        max_sector_fraction=0.25,
        max_cluster_fraction=1,
        commission=0,
        spread=0,
        slippage=0,
    )

    replay = simulate_portfolio(
        {"AAA": bars},
        strategy_name="S/R Bounce",
        params={},
        classifications=_classifications("AAA"),
        config=config,
    )

    entry = replay.fills[0]
    assert entry.requested_shares == 250
    assert entry.shares == 125
    assert replay.equity[1].sector_values["sector-AAA"] == 25_000


def test_gap_below_static_stop_rejects_entry_at_fill(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bars = _bars(opens=[100, 90, 90], closes=[100, 90, 90])
    monkeypatch.setattr(
        "app.portfolio_execution.build_rules",
        lambda *_args, **_kwargs: _rules(len(bars), entries={0}, stop=95),
    )

    replay = simulate_portfolio(
        {"AAA": bars},
        strategy_name="S/R Bounce",
        params={},
        classifications=_classifications("AAA"),
        config=PortfolioConfig(commission=0, spread=0, slippage=0),
    )

    assert replay.fills == ()
    assert replay.state.rejected_orders[-1].reason == "invalid_stop_at_fill"
    assert replay.state.cash == 100_000


def test_final_close_signal_remains_pending_without_fake_fill(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bars = _bars(opens=[100, 100, 100])
    monkeypatch.setattr(
        "app.portfolio_execution.build_rules",
        lambda *_args, **_kwargs: _rules(len(bars), entries={2}, stop=90),
    )

    replay = simulate_portfolio(
        {"AAA": bars},
        strategy_name="S/R Bounce",
        params={},
        classifications=_classifications("AAA"),
        config=PortfolioConfig(commission=0, spread=0, slippage=0),
    )

    assert replay.fills == ()
    assert len(replay.state.pending_orders) == 1
    assert replay.state.pending_orders[0].order_date is None


def test_future_price_changes_cannot_change_earlier_replay_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bars = _bars(opens=[100, 100, 101, 102, 103], closes=[100, 101, 102, 103, 104])
    monkeypatch.setattr(
        "app.portfolio_execution.build_rules",
        lambda frame, *_args, **_kwargs: _rules(len(frame), entries={0}, stop=90),
    )
    kwargs = {
        "strategy_name": "S/R Bounce",
        "params": {},
        "classifications": _classifications("AAA"),
        "config": PortfolioConfig(commission=0, spread=0, slippage=0),
    }
    baseline = simulate_portfolio({"AAA": bars}, **kwargs)
    changed = bars.copy()
    changed.loc[3:, ["open", "high", "low", "close"]] *= 10

    future_changed = simulate_portfolio({"AAA": changed}, **kwargs)

    assert future_changed.equity[:3] == baseline.equity[:3]
    assert [fill for fill in future_changed.fills if fill.fill_date <= bars["date"].iloc[2]] == [
        fill for fill in baseline.fills if fill.fill_date <= bars["date"].iloc[2]
    ]


def test_replay_integrates_with_real_cta_rules(research_bars: pd.DataFrame) -> None:
    replay = simulate_portfolio(
        {"AAA": research_bars, "BBB": research_bars.copy()},
        strategy_name="CTA Trend",
        params={
            "n_entry": 100,
            "n_exit": 40,
            "trend_ma": 100,
            "atr_period": 14,
            "atr_mult": 3.0,
            "atr_tp_mult": 0.0,
        },
        classifications=_classifications("AAA", "BBB"),
    )

    assert len(replay.equity) == len(research_bars)
    assert replay.equity[0].date == research_bars["date"].iloc[0]
    assert any(fill.side == "entry" for fill in replay.fills)
    assert all(snapshot.cash >= 0 for snapshot in replay.equity)
    assert all(
        snapshot.equity
        == pytest.approx(
            snapshot.cash + snapshot.unsettled_cash + snapshot.market_value
        )
        for snapshot in replay.equity
    )
    assert all(
        position.stop < position.entry_price
        for position in replay.state.positions.values()
    )
