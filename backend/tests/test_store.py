"""SQLite idempotency and rejection of malformed market data."""

from __future__ import annotations

import pandas as pd
import pytest

from app import store


@pytest.fixture
def isolated_store(tmp_path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(store, "DATA_DIR", tmp_path)
    monkeypatch.setattr(store, "DB_PATH", tmp_path / "market.db")
    return store


def _valid_rows() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"symbol": "TEST", "date": "2024-01-02", "open": 10, "high": 12,
             "low": 9, "close": 11, "volume": 1000},
            {"symbol": "TEST", "date": "2024-01-03", "open": 11, "high": 13,
             "low": 10, "close": 12, "volume": 1100},
        ]
    )


def test_upsert_is_idempotent(isolated_store) -> None:
    rows = _valid_rows()
    isolated_store.upsert_bars(rows)
    isolated_store.upsert_bars(rows)
    assert isolated_store.row_count("TEST") == 2


def test_bar_inventory_reports_compact_symbol_coverage(isolated_store) -> None:
    isolated_store.upsert_bars(_valid_rows())

    assert isolated_store.bar_inventory() == [
        {
            "symbol": "TEST",
            "rows": 2,
            "first_date": "2024-01-02",
            "latest_date": "2024-01-03",
        }
    ]


@pytest.mark.parametrize(
    ("column", "value", "message"),
    [
        ("open", 0, "positive"),
        ("high", 5, "below open or close"),
        ("low", 20, "above open or close"),
        ("close", float("nan"), "finite"),
        ("volume", -1, "negative"),
        ("volume", float("nan"), "finite"),
    ],
)
def test_invalid_batch_is_rejected_without_partial_write(
    isolated_store, column: str, value, message: str
) -> None:
    rows = _valid_rows()
    rows.loc[1, column] = value
    with pytest.raises(ValueError, match=message):
        isolated_store.upsert_bars(rows)
    assert isolated_store.row_count("TEST") == 0


def test_duplicate_dates_in_one_batch_are_rejected(isolated_store) -> None:
    rows = _valid_rows()
    rows.loc[1, "date"] = rows.loc[0, "date"]
    with pytest.raises(ValueError, match="unique"):
        isolated_store.upsert_bars(rows)


def test_non_monotonic_dates_are_rejected(isolated_store) -> None:
    rows = _valid_rows().iloc[::-1].reset_index(drop=True)
    with pytest.raises(ValueError, match="increasing"):
        isolated_store.upsert_bars(rows)


def test_strategy_watchlist_is_persistent_ordered_and_replaceable(isolated_store) -> None:
    isolated_store.replace_strategy_watchlist("CTA Trend", ["SPY", "QQQ", "SPY"])
    assert [row["symbol"] for row in isolated_store.list_strategy_watchlist("CTA Trend")] == [
        "SPY",
        "QQQ",
    ]

    isolated_store.replace_strategy_watchlist("CTA Trend", ["IWM", "SPY"])
    assert [row["symbol"] for row in isolated_store.list_strategy_watchlist("CTA Trend")] == [
        "IWM",
        "SPY",
    ]


def test_strategy_runs_append_and_latest_read_does_not_recalculate(isolated_store) -> None:
    first = isolated_store.save_strategy_run(
        "CTA Trend", "defaults", "watchlist", "complete", "2024-01-02", {"n": 1}, {"ranked": []}
    )
    second = isolated_store.save_strategy_run(
        "CTA Trend", "defaults", "all", "complete", "2024-01-03", {"n": 2}, {"ranked": [{"symbol": "SPY"}]}
    )
    third = isolated_store.save_strategy_run(
        "CTA Trend", "saved", "all", "complete", "2024-01-04", {"n": 3}, {"ranked": []}
    )
    assert second > first
    assert third > second
    latest = isolated_store.latest_strategy_run("CTA Trend")
    assert latest["id"] == second
    assert latest["scope"] == "all"
    assert latest["params"] == {"n": 2}
    assert latest["result"]["ranked"] == [{"symbol": "SPY"}]
    assert isolated_store.latest_strategy_run(
        "CTA Trend", scope="watchlist"
    )["id"] == first
    latest_full_scan = isolated_store.latest_strategy_run(
        "CTA Trend", set_name=None, scope="all"
    )
    assert latest_full_scan["id"] == third
    assert latest_full_scan["set"] == "saved"
    assert isolated_store.get_strategy_run(first)["params"] == {"n": 1}
    assert isolated_store.latest_strategy_run("SMA Cross") is None
