"""Manual data-refresh inventory and progress contracts."""

from __future__ import annotations

import threading
import time
from datetime import date

import pandas as pd
import pytest

from app import data_management


def _frame(symbol: str, latest: str = "2026-08-17") -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "symbol": symbol,
                "date": latest,
                "open": 100.0,
                "high": 102.0,
                "low": 99.0,
                "close": 101.0,
                "volume": 1_000,
            }
        ]
    )


def _wait(manager: data_management.DataRefreshManager) -> dict:
    deadline = time.monotonic() + 2
    while time.monotonic() < deadline:
        snapshot = manager.snapshot()
        if snapshot["state"] != "running":
            return snapshot
        time.sleep(0.001)
    pytest.fail("refresh worker did not finish")


@pytest.mark.parametrize(
    ("latest", "state", "age", "lag"),
    [
        ("2026-08-18", "fresh", 0, 0),
        ("2026-08-17", "aging", 1, 1),
        ("2026-08-14", "stale", 4, 2),
        ("not-a-date", "invalid", 0, None),
    ],
)
def test_freshness_uses_expected_completed_weekday_session(
    latest: str, state: str, age: int, lag: int | None
) -> None:
    assert data_management.freshness(
        latest, expected=date(2026, 8, 18)
    ) == (state, age, lag)


def test_expected_session_uses_new_york_close_and_skips_weekend() -> None:
    before_monday_close = pd.Timestamp("2026-08-17T20:00:00Z").to_pydatetime()
    after_monday_close = pd.Timestamp("2026-08-18T00:00:00Z").to_pydatetime()

    assert data_management.expected_latest_session(before_monday_close) == date(
        2026, 8, 14
    )
    assert data_management.expected_latest_session(after_monday_close) == date(
        2026, 8, 17
    )


def test_refresh_scope_selection_is_stable_and_stored_only() -> None:
    inventory = [
        {"symbol": "QQQ", "freshness": "fresh"},
        {"symbol": "SPY", "freshness": "stale"},
        {"symbol": "XLK", "freshness": "aging"},
        {"symbol": "DGS2", "freshness": "provider_managed", "provider": "fred"},
    ]

    assert data_management.select_refresh_symbols(
        "core", inventory, ["SPY", "MISSING", "QQQ"]
    ) == ["SPY", "QQQ"]
    assert data_management.select_refresh_symbols("stale", inventory, []) == [
        "SPY",
        "XLK",
    ]
    assert data_management.select_refresh_symbols("all", inventory, []) == [
        "QQQ",
        "SPY",
        "XLK",
    ]


def test_inventory_keeps_fred_out_of_yahoo_freshness_counts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        data_management.store,
        "bar_inventory",
        lambda: [
            {
                "symbol": "SPY",
                "rows": 10,
                "first_date": "2026-08-01",
                "latest_date": "2026-08-18",
            },
            {
                "symbol": "DGS2",
                "rows": 10,
                "first_date": "2026-08-01",
                "latest_date": "2026-08-01",
            },
        ],
    )

    payload = data_management.inventory_payload(today=date(2026, 8, 18))

    assert payload["summary"]["fresh"] == 1
    assert payload["summary"]["stale"] == 0
    assert payload["summary"]["fred_managed"] == 1
    assert payload["symbols"][1]["provider"] == "fred"
    assert payload["symbols"][1]["freshness"] == "provider_managed"


def test_refresh_manager_records_each_result_and_fixed_delay(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    published = []
    delays = []
    monkeypatch.setattr(data_management.store, "upsert_bars", lambda frame: None)
    monkeypatch.setattr(data_management.store, "row_count", lambda _symbol: 123)
    manager = data_management.DataRefreshManager(
        fetcher=lambda symbol, period: (
            _frame(symbol)
            if period == data_management.REFRESH_PERIOD
            else pytest.fail("unexpected period")
        ),
        sleeper=delays.append,
        on_publish=lambda: published.append(True),
    )

    started = manager.start(["SPY", "QQQ"])
    finished = _wait(manager)

    assert started["total"] == 2
    assert finished["state"] == "complete"
    assert finished["completed"] == 2
    assert finished["failed"] == 0
    assert [item["state"] for item in finished["items"]] == [
        "complete",
        "complete",
    ]
    assert [item["latest_date"] for item in finished["items"]] == [
        "2026-08-17",
        "2026-08-17",
    ]
    assert delays == [data_management.REQUEST_DELAY_SECONDS]
    assert len(published) == 2


def test_refresh_manager_continues_after_symbol_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fetcher(symbol: str, _period: str) -> pd.DataFrame:
        if symbol == "BAD":
            raise RuntimeError("provider failed")
        return _frame(symbol)

    monkeypatch.setattr(data_management.store, "upsert_bars", lambda frame: None)
    monkeypatch.setattr(data_management.store, "row_count", lambda _symbol: 1)
    manager = data_management.DataRefreshManager(
        fetcher=fetcher,
        sleeper=lambda _seconds: None,
    )

    manager.start(["BAD", "SPY"])
    finished = _wait(manager)

    assert finished["state"] == "complete_with_errors"
    assert finished["completed"] == 1
    assert finished["failed"] == 1
    assert finished["items"][0]["state"] == "failed"
    assert "provider failed" in finished["items"][0]["message"]
    assert finished["items"][1]["state"] == "complete"


def test_refresh_manager_rejects_concurrent_job(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entered = threading.Event()
    release = threading.Event()

    def fetcher(symbol: str, _period: str) -> pd.DataFrame:
        entered.set()
        assert release.wait(timeout=2)
        return _frame(symbol)

    monkeypatch.setattr(data_management.store, "upsert_bars", lambda frame: None)
    monkeypatch.setattr(data_management.store, "row_count", lambda _symbol: 1)
    manager = data_management.DataRefreshManager(
        fetcher=fetcher,
        sleeper=lambda _seconds: None,
    )

    manager.start(["SPY"])
    assert entered.wait(timeout=2)
    with pytest.raises(
        data_management.RefreshAlreadyRunning,
        match="already running",
    ):
        manager.start(["QQQ"])
    release.set()
    assert _wait(manager)["state"] == "complete"
