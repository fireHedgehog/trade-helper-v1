"""Stage 1 tests for the canonical close-signal/next-open state machine."""

from __future__ import annotations

import pandas as pd
import pytest

from app.engine import (
    ANNUAL_CASH_YIELD,
    COMMISSION,
    SLIPPAGE,
    SPREAD,
    backtest_bars_payload,
)
from app.execution import simulate, validate_bars
from app.rules import RuleSet
from app.signals import _replay_ledger, compute_stateful_signal
from app.strategies import STRATEGY_PARAMS


def _bars(closes: list[float], opens: list[float] | None = None) -> pd.DataFrame:
    opens = opens or closes
    dates = pd.bdate_range("2024-01-02", periods=len(closes))
    return pd.DataFrame(
        {
            "date": dates.strftime("%Y-%m-%d"),
            "open": opens,
            "high": [max(o, c) + 0.5 for o, c in zip(opens, closes)],
            "low": [min(o, c) - 0.5 for o, c in zip(opens, closes)],
            "close": closes,
            "volume": [1_000_000] * len(closes),
        }
    )


def test_sma_signals_fill_only_at_next_open() -> None:
    bars = _bars(
        closes=[10, 9, 8, 11, 12, 7, 6],
        opens=[10, 9, 8, 15, 12, 5, 6],
    )
    result = simulate(
        bars,
        "SMA Cross",
        {"n_fast": 2, "n_slow": 3},
        initial_cash=10_000,
        commission=0,
    )

    assert len(result.trades) == 1
    trade = result.trades[0]
    assert trade["entry_date"] == bars["date"].iloc[4]
    assert trade["entry_price"] == 12
    assert trade["exit_date"] == bars["date"].iloc[6]
    assert trade["exit_price"] == 6
    assert trade["exit_reason"] == "strategy"


def test_final_bar_signal_stays_pending_without_fake_trade() -> None:
    bars = _bars(closes=[10, 9, 8, 11], opens=[10, 9, 8, 15])
    result = simulate(
        bars,
        "SMA Cross",
        {"n_fast": 2, "n_slow": 3},
        initial_cash=10_000,
        commission=0,
    )

    assert result.position.state == "entry_pending"
    assert result.last_event == "entry"
    assert result.trades == []


def test_initial_atr_stop_uses_signal_bar_not_fill_bar(monkeypatch: pytest.MonkeyPatch) -> None:
    bars = _bars(closes=[10, 11, 12], opens=[10, 12, 12])
    rules = RuleSet(
        entries=pd.Series([True, False, False]),
        exits=pd.Series([False, False, False]),
        atr=pd.Series([2.0, 100.0, 100.0]),
        stop_levels=pd.Series([float("nan")] * 3),
        target_levels=pd.Series([float("nan")] * 3),
    )
    monkeypatch.setattr("app.execution.build_rules", lambda *_args, **_kwargs: rules)

    result = simulate(
        bars,
        "CTA Trend",
        {"atr_mult": 3.0, "atr_tp_mult": 0.0},
        initial_cash=10_000,
        commission=0,
    )

    assert result.position.state == "long"
    assert result.position.entry_price == 12
    assert result.position.stop == 6  # 12 - 3 × signal-bar ATR(2), not fill-bar ATR(100)


def test_fixed_share_ledger_pnl_matches_its_label() -> None:
    bars = _bars(
        closes=[10, 9, 8, 11, 12, 7, 6],
        opens=[10, 9, 8, 15, 12, 5, 6],
    )
    result = simulate(
        bars,
        "SMA Cross",
        {"n_fast": 2, "n_slow": 3},
        initial_cash=100_000,
        commission=0,
        fixed_shares=100,
    )

    assert result.trades[0]["size"] == 100
    assert result.trades[0]["pnl"] == -600  # 100 × (6 exit - 12 entry)


@pytest.mark.parametrize("strategy_name", list(STRATEGY_PARAMS))
def test_api_payload_is_the_same_canonical_simulation(
    research_bars: pd.DataFrame, strategy_name: str
) -> None:
    params = {key: meta["default"] for key, meta in STRATEGY_PARAMS[strategy_name].items()}
    direct = simulate(
        research_bars,
        strategy_name,
        params,
        commission=COMMISSION,
        spread=SPREAD,
        slippage=SLIPPAGE,
        annual_cash_yield=ANNUAL_CASH_YIELD,
    )
    payload = backtest_bars_payload(research_bars, "FIXTURE", strategy_name, params)

    assert payload["metrics"]["# Trades"] == len(direct.trades)
    assert payload["metrics"]["Pending Order"] == (
        direct.position.state if direct.position.state.endswith("pending") else None
    )
    assert (payload["open_position"] is not None) == (
        direct.position.state in {"long", "exit_pending"}
    )
    assert [trade["entry_date"] for trade in payload["trades"]] == [
        trade["entry_date"] for trade in direct.trades
    ]
    assert [trade["exit_date"] for trade in payload["trades"]] == [
        trade["exit_date"] for trade in direct.trades
    ]


def test_adjusted_price_rounding_noise_is_not_an_invalid_candle() -> None:
    bars = _bars([100.0, 101.0], [100.0, 101.0])
    bars.loc[0, "high"] = bars.loc[0, "close"] * (1 - 1e-14)
    bars.loc[0, "low"] = bars.loc[0, "close"] * (1 + 1e-14)
    validate_bars(bars)


@pytest.mark.parametrize("strategy_name", list(STRATEGY_PARAMS))
def test_ledger_and_display_use_canonical_position(
    research_bars: pd.DataFrame, strategy_name: str
) -> None:
    params = {key: meta["default"] for key, meta in STRATEGY_PARAMS[strategy_name].items()}
    direct = simulate(research_bars, strategy_name, params)
    ledger = _replay_ledger(research_bars, strategy_name, params)
    display = compute_stateful_signal(research_bars, strategy_name, params)

    assert ledger["state"] == direct.position.state
    assert ledger["entry_date"] == direct.position.entry_date
    if direct.position.entry_price is None:
        assert ledger["entry_price"] is None
    else:
        assert ledger["entry_price"] == pytest.approx(direct.position.entry_price, abs=0.01)
    assert display is not None
    assert display["state"] == (
        "long" if direct.position.state in {"long", "exit_pending"} else "flat"
    )
    assert display["event"] == direct.last_event
