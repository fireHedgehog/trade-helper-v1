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
