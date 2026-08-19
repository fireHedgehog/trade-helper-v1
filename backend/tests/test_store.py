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


def test_data_refresh_state_round_trips_as_a_single_durable_record(isolated_store) -> None:
    first = {"job_id": "one", "state": "running", "items": [{"symbol": "SPY"}]}
    second = {"job_id": "one", "state": "complete", "items": [{"symbol": "SPY"}]}

    assert isolated_store.load_data_refresh_state() is None
    isolated_store.save_data_refresh_state(first)
    assert isolated_store.load_data_refresh_state() == first
    isolated_store.save_data_refresh_state(second)
    assert isolated_store.load_data_refresh_state() == second


def test_daily_pipeline_state_round_trips_as_single_record(isolated_store) -> None:
    first = {"job_id": "one", "state": "running", "strategy_jobs": []}
    second = {"job_id": "two", "state": "complete", "strategy_jobs": []}
    assert isolated_store.load_daily_pipeline_state() is None
    isolated_store.save_daily_pipeline_state(first)
    assert isolated_store.load_daily_pipeline_state() == first
    isolated_store.save_daily_pipeline_state(second)
    assert isolated_store.load_daily_pipeline_state() == second


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


def test_negative_settlement_context_is_stored_without_weakening_equities(
    isolated_store,
) -> None:
    context = pd.DataFrame(
        [
            {
                "symbol": "CL=F", "date": "2020-04-20", "open": 17.73,
                "high": 17.85, "low": -40.32, "close": -37.63, "volume": 1,
            }
        ]
    )
    isolated_store.upsert_bars(context)
    assert isolated_store.row_count("CL=F") == 1

    equity = context.assign(symbol="TEST")
    with pytest.raises(ValueError, match="positive"):
        isolated_store.upsert_bars(equity)


def test_negative_fred_series_value_is_stored_without_weakening_equities(
    isolated_store,
) -> None:
    macro = pd.DataFrame(
        [
            {
                "symbol": "A191RL1Q225SBEA", "date": "2020-04-01", "open": -31.2,
                "high": -31.2, "low": -31.2, "close": -31.2, "volume": 0,
            }
        ]
    )
    isolated_store.upsert_bars(macro)
    assert isolated_store.row_count("A191RL1Q225SBEA") == 1

    equity = macro.assign(symbol="TEST")
    with pytest.raises(ValueError, match="positive"):
        isolated_store.upsert_bars(equity)


def test_context_settlement_may_fall_outside_intraday_envelope(isolated_store) -> None:
    rows = pd.DataFrame(
        [
            {
                "symbol": "GC=F", "date": "2011-09-28", "open": 1650.0,
                "high": 1650.0, "low": 1650.0, "close": 1616.3, "volume": 1,
            }
        ]
    )
    isolated_store.upsert_bars(rows)
    assert isolated_store.row_count("GC=F") == 1


def test_duplicate_dates_in_one_batch_are_rejected(isolated_store) -> None:
    rows = _valid_rows()
    rows.loc[1, "date"] = rows.loc[0, "date"]
    with pytest.raises(ValueError, match="unique"):
        isolated_store.upsert_bars(rows)


def test_non_monotonic_dates_are_rejected(isolated_store) -> None:
    rows = _valid_rows().iloc[::-1].reset_index(drop=True)
    with pytest.raises(ValueError, match="increasing"):
        isolated_store.upsert_bars(rows)


def test_upsert_replaces_rather_than_merges_by_date(isolated_store) -> None:
    """A symbol's whole row set is replaced, not merged, so a stale row from
    an earlier adjustment vintage can never survive next to a fresh one."""
    first_batch = pd.DataFrame(
        [
            {"symbol": "TEST", "date": "2024-01-02", "open": 10, "high": 12,
             "low": 9, "close": 11, "volume": 1000},
            {"symbol": "TEST", "date": "2024-01-03", "open": 11, "high": 13,
             "low": 10, "close": 12, "volume": 1100},
            {"symbol": "TEST", "date": "2024-01-04", "open": 12, "high": 14,
             "low": 11, "close": 13, "volume": 1200},
        ]
    )
    isolated_store.upsert_bars(first_batch)
    assert isolated_store.row_count("TEST") == 3

    # A fresh full-history fetch with different (re-adjusted) prices for the
    # same dates, covering the exact same range: prices should be fully
    # replaced, not merged with the stale first-batch values.
    second_batch = first_batch.copy()
    second_batch[["open", "high", "low", "close"]] = [
        [19, 22, 18, 21], [20, 23, 19, 22], [21, 24, 20, 23],
    ]
    isolated_store.upsert_bars(second_batch)
    stored = isolated_store.load_bars("TEST")
    assert isolated_store.row_count("TEST") == 3
    assert stored["close"].tolist() == [21, 22, 23]


def test_upsert_rejects_a_batch_that_would_truncate_stored_history(isolated_store) -> None:
    full_history = pd.DataFrame(
        [
            {"symbol": "TEST", "date": "2020-01-02", "open": 10, "high": 12,
             "low": 9, "close": 11, "volume": 1000},
            {"symbol": "TEST", "date": "2020-01-03", "open": 11, "high": 13,
             "low": 10, "close": 12, "volume": 1100},
            {"symbol": "TEST", "date": "2020-01-06", "open": 12, "high": 14,
             "low": 11, "close": 13, "volume": 1200},
        ]
    )
    isolated_store.upsert_bars(full_history)
    assert isolated_store.row_count("TEST") == 3

    # A short, truncated fetch (e.g. Yahoo returning only recent history)
    # must not silently overwrite the longer history already stored.
    truncated = full_history.iloc[[2]].copy()
    with pytest.raises(ValueError, match="shrink or truncate"):
        isolated_store.upsert_bars(truncated)
    assert isolated_store.row_count("TEST") == 3
    assert isolated_store.load_bars("TEST")["date"].tolist() == [
        "2020-01-02", "2020-01-03", "2020-01-06",
    ]


def test_upsert_shrink_guard_rolls_back_the_whole_batch_not_just_one_symbol(
    isolated_store,
) -> None:
    """One offending symbol in a multi-symbol batch must not let any other
    symbol in the same call partially publish."""
    isolated_store.upsert_bars(
        pd.DataFrame(
            [
                {"symbol": "AAA", "date": "2020-01-02", "open": 1, "high": 1,
                 "low": 1, "close": 1, "volume": 1},
                {"symbol": "AAA", "date": "2020-01-03", "open": 1, "high": 1,
                 "low": 1, "close": 1, "volume": 1},
            ]
        )
    )
    batch = pd.DataFrame(
        [
            {"symbol": "AAA", "date": "2020-01-03", "open": 1, "high": 1,
             "low": 1, "close": 1, "volume": 1},  # shrinks AAA from 2 to 1
            {"symbol": "BBB", "date": "2020-01-02", "open": 1, "high": 1,
             "low": 1, "close": 1, "volume": 1},  # brand-new symbol, fine alone
        ]
    )
    with pytest.raises(ValueError, match="shrink or truncate"):
        isolated_store.upsert_bars(batch)
    assert isolated_store.row_count("AAA") == 2
    assert isolated_store.row_count("BBB") == 0


def test_upsert_allow_shrink_permits_an_intentional_rebuild(isolated_store) -> None:
    full_history = pd.DataFrame(
        [
            {"symbol": "TEST", "date": "2020-01-02", "open": 10, "high": 12,
             "low": 9, "close": 11, "volume": 1000},
            {"symbol": "TEST", "date": "2020-01-03", "open": 11, "high": 13,
             "low": 10, "close": 12, "volume": 1100},
        ]
    )
    isolated_store.upsert_bars(full_history)

    rebuilt = full_history.iloc[[1]].copy()
    isolated_store.upsert_bars(rebuilt, allow_shrink=True)
    assert isolated_store.row_count("TEST") == 1


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
