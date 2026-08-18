"""Portfolio API adapter and locked-universe contract checks."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import pytest

from app import portfolio_api
from app.portfolio_universe import (
    PORTFOLIO_CLASSIFICATIONS,
    PORTFOLIO_COMMON_START,
    PORTFOLIO_SYMBOLS,
    PORTFOLIO_UNIVERSE_ID,
)


@dataclass(frozen=True)
class _EquityRow:
    index: int


def _common_bars(source: pd.DataFrame) -> pd.DataFrame:
    bars = source.copy()
    bars["date"] = pd.bdate_range(
        PORTFOLIO_COMMON_START, periods=len(bars)
    ).strftime("%Y-%m-%d")
    return bars


def test_locked_portfolio_manifest_is_explicit_and_complete() -> None:
    assert PORTFOLIO_UNIVERSE_ID == "locked-etf-12-v1"
    assert len(PORTFOLIO_SYMBOLS) == 12
    assert len(set(PORTFOLIO_SYMBOLS)) == 12
    assert set(PORTFOLIO_SYMBOLS) == set(PORTFOLIO_CLASSIFICATIONS)
    assert all(
        row.sector.strip() and row.cluster.strip()
        for row in PORTFOLIO_CLASSIFICATIONS.values()
    )


def test_equity_sample_respects_limit_and_preserves_endpoints() -> None:
    rows = tuple(_EquityRow(index) for index in range(5_163))

    sampled = portfolio_api._sample_equity(rows, maximum=500)

    assert len(sampled) == 500
    assert sampled[0]["index"] == 0
    assert sampled[-1]["index"] == 5_162
    assert [row["index"] for row in sampled] == sorted(
        {row["index"] for row in sampled}
    )


def test_common_loader_fails_closed_on_missing_symbol(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(portfolio_api.store, "load_bars", lambda _symbol: pd.DataFrame())

    with pytest.raises(RuntimeError, match="portfolio data missing"):
        portfolio_api._load_common_bars()


def test_strategy_without_protective_stop_is_explicitly_unsupported(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        portfolio_api,
        "_load_common_bars",
        lambda: pytest.fail("unsupported strategy must not start an expensive replay"),
    )

    payload = portfolio_api.portfolio_payload(
        "SMA Cross", {"n_fast": 20, "n_slow": 50}
    )

    assert payload["status"] == "unsupported"
    assert "explicit protective stop" in payload["reason"]
    assert "SMA Cross" not in payload["supported_strategies"]
    assert payload["claim"].startswith("historical mechanics replay")


def test_common_loader_fails_closed_on_mismatched_calendar(
    research_bars: pd.DataFrame, monkeypatch: pytest.MonkeyPatch
) -> None:
    common = _common_bars(research_bars)

    def load(symbol: str) -> pd.DataFrame:
        return common.drop(index=100).reset_index(drop=True) if symbol == "QQQ" else common

    monkeypatch.setattr(portfolio_api.store, "load_bars", load)

    with pytest.raises(RuntimeError, match="calendars differ: QQQ"):
        portfolio_api._load_common_bars()


def test_payload_exposes_account_and_benchmark_contract(
    research_bars: pd.DataFrame, monkeypatch: pytest.MonkeyPatch
) -> None:
    common = _common_bars(research_bars)
    monkeypatch.setattr(portfolio_api.store, "load_bars", lambda _symbol: common)
    params = {
        "n_entry": 100,
        "n_exit": 40,
        "trend_ma": 100,
        "atr_period": 14,
        "atr_mult": 3.0,
        "atr_tp_mult": 0.0,
    }

    payload = portfolio_api.portfolio_payload("CTA Trend", params)

    assert payload["claim"].startswith("historical mechanics replay")
    benchmark = payload["benchmark"]
    assert benchmark["contract"] == "ADR 0005"
    assert benchmark["primary"]["name"] == "Passive ETF-12 v1"
    assert benchmark["primary"]["rebalance"] == "annual"
    assert benchmark["primary"]["symbols"] == sorted(PORTFOLIO_SYMBOLS)
    assert benchmark["secondary"]["spy_buy_and_hold"]["symbols"] == ["SPY"]
    assert benchmark["secondary"]["cash"]["annual_cash_yield"] == 0.0
    assert "total_return_difference" in benchmark["comparison"]
    assert payload["universe"]["id"] == PORTFOLIO_UNIVERSE_ID
    assert payload["universe"]["symbols"] == list(PORTFOLIO_SYMBOLS)
    assert payload["universe"]["bars"] == len(common)
    assert payload["metrics"]["bars"] == len(common)
    assert payload["account"]["equity"] == pytest.approx(
        payload["equity"][-1]["equity"]
    )
    assert payload["assumptions"]["fill_timing"] == "next shared-calendar open"
