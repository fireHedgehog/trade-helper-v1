"""Point-in-time macro ingestion: vintage parsing, revision indexing, as-of queries.

No live network call is made anywhere in this suite -- requests.get is
monkeypatched. This exercises the parsing/indexing/immutability logic
end-to-end; it does not verify the real FRED API's live response shape.
"""
from __future__ import annotations

import pandas as pd
import pytest

from app import macro_pit, store


@pytest.fixture
def isolated_store(tmp_path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(store, "DATA_DIR", tmp_path)
    monkeypatch.setattr(store, "DB_PATH", tmp_path / "market.db")
    return store


class _FakeResponse:
    def __init__(self, payload: dict, status_code: int = 200, text: str = ""):
        self._payload = payload
        self.status_code = status_code
        self.text = text

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self) -> dict:
        return self._payload


def _fake_observations(rows: list[dict]) -> _FakeResponse:
    return _FakeResponse({"observations": rows})


def _fake_vintage_cap_error() -> _FakeResponse:
    return _FakeResponse(
        {},
        status_code=400,
        text='{"error_code":400,"error_message":"Bad Request.  There are 5073 '
        'vintage dates in the specified real-time period... This exceeds the '
        'maximum number of vintage dates allowed for this file type (2000)."}',
    )


def _fake_not_yet_existing_error() -> _FakeResponse:
    return _FakeResponse(
        {},
        status_code=400,
        text='{"error_code":400,"error_message":"Bad Request.  The series does '
        'not exist in ALFRED but may exist in FRED..."}',
    )


def test_fetch_vintage_page_treats_pre_existence_range_as_genuinely_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        macro_pit.requests, "get", lambda url, params, timeout: _fake_not_yet_existing_error()
    )
    df = macro_pit._fetch_vintage_page("DFII10", "1776-07-04", "1901-01-01", "test-key")
    assert list(df.columns) == ["reference_period", "value", "realtime_start"]
    assert df.empty


def test_missing_api_key_raises_actionable_error(isolated_store, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="FRED_API_KEY"):
        macro_pit.fetch_all_vintages("DFII10")


def test_env_var_takes_precedence_over_stored_key(
    isolated_store, monkeypatch: pytest.MonkeyPatch
) -> None:
    isolated_store.set_key("FRED_API_KEY", "stored-key")
    monkeypatch.setenv("FRED_API_KEY", "env-key")
    assert macro_pit._api_key() == "env-key"


def test_falls_back_to_stored_key_when_env_var_is_unset(
    isolated_store, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    isolated_store.set_key("FRED_API_KEY", "stored-key")
    assert macro_pit._api_key() == "stored-key"


def test_fetch_all_vintages_parses_response_and_drops_missing_sentinel(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured = {}

    def fake_get(url, params, timeout):
        captured["url"] = url
        captured["params"] = params
        return _fake_observations(
            [
                {"date": "2024-01-02", "value": "1.50", "realtime_start": "2024-01-02", "realtime_end": "2024-01-31"},
                {"date": "2024-01-02", "value": "1.55", "realtime_start": "2024-02-01", "realtime_end": "9999-12-31"},
                {"date": "2024-01-03", "value": ".", "realtime_start": "2024-01-03", "realtime_end": "9999-12-31"},
            ]
        )

    monkeypatch.setattr(macro_pit.requests, "get", fake_get)
    df = macro_pit.fetch_all_vintages("DFII10", api_key="test-key")

    assert captured["url"] == macro_pit.API_URL
    assert captured["params"]["series_id"] == "DFII10"
    assert captured["params"]["realtime_start"] == macro_pit.ALFRED_EARLIEST
    assert captured["params"]["realtime_end"] == macro_pit.ALFRED_LATEST
    assert list(df["reference_period"]) == ["2024-01-02", "2024-01-02"]
    assert list(df["value"]) == [1.50, 1.55]


def test_fetch_all_vintages_bisects_the_range_on_a_vintage_cap_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Live-verified failure mode (DFII10 has 5,073 vintage dates over full
    history, exceeding FRED's 2,000-per-request cap): the full-range
    request fails, so fetch_all_vintages must split and retry rather than
    raise. Data lives entirely in the second half of the simulated range."""
    calls = []

    def fake_get(url, params, timeout):
        start, end = params["realtime_start"], params["realtime_end"]
        calls.append((start, end))
        if (start, end) == (macro_pit.ALFRED_EARLIEST, macro_pit.ALFRED_LATEST):
            return _fake_vintage_cap_error()
        if start == macro_pit.ALFRED_EARLIEST:  # the older, split-off left branch
            return _fake_observations(
                [{"date": "1990-01-01", "value": "9.00", "realtime_start": "1990-01-01", "realtime_end": "1990-02-01"}]
            )
        if end == macro_pit.ALFRED_LATEST:  # the recent, still-current right branch
            return _fake_observations(
                [{"date": "2024-01-02", "value": "1.50", "realtime_start": "2024-01-02", "realtime_end": "9999-12-31"}]
            )
        return _fake_observations([])

    monkeypatch.setattr(macro_pit.requests, "get", fake_get)
    df = macro_pit.fetch_all_vintages("DFII10", api_key="test-key")

    assert len(calls) >= 3  # at least: the failing full-range call, then a split
    assert sorted(df["reference_period"]) == ["1990-01-01", "2024-01-02"]


def test_to_revision_indexed_orders_by_realtime_start_and_assigns_k() -> None:
    vintages = pd.DataFrame(
        [
            {"reference_period": "2024-01-02", "value": 1.55, "realtime_start": "2024-02-01"},
            {"reference_period": "2024-01-02", "value": 1.50, "realtime_start": "2024-01-02"},
            {"reference_period": "2024-01-03", "value": 1.60, "realtime_start": "2024-01-03"},
        ]
    )
    indexed = macro_pit.to_revision_indexed("DFII10", vintages)

    jan2 = indexed[indexed["reference_period"] == "2024-01-02"].sort_values("revision_index")
    assert list(jan2["revision_index"]) == [0, 1]
    assert list(jan2["value"]) == [1.50, 1.55]
    assert list(jan2["release_datetime"]) == ["2024-01-02", "2024-02-01"]
    assert (indexed["series_id"] == "DFII10").all()


def test_value_asof_returns_latest_revision_visible_at_decision_time(isolated_store) -> None:
    indexed = pd.DataFrame(
        [
            {"series_id": "DFII10", "reference_period": "2024-01-02", "revision_index": 0,
             "release_datetime": "2024-01-02", "value": 1.50},
            {"series_id": "DFII10", "reference_period": "2024-01-02", "revision_index": 1,
             "release_datetime": "2024-02-01", "value": 1.55},
        ]
    )
    isolated_store.upsert_macro_vintages(indexed)

    before_revision = macro_pit.value_asof("DFII10", "2024-01-15")
    assert list(before_revision["value"]) == [1.50]

    after_revision = macro_pit.value_asof("DFII10", "2024-02-15")
    assert list(after_revision["value"]) == [1.55]


def test_value_asof_empty_before_any_release(isolated_store) -> None:
    indexed = pd.DataFrame(
        [
            {"series_id": "DFII10", "reference_period": "2024-01-02", "revision_index": 0,
             "release_datetime": "2024-01-02", "value": 1.50},
        ]
    )
    isolated_store.upsert_macro_vintages(indexed)

    result = macro_pit.value_asof("DFII10", "2023-12-31")
    assert result.empty


def test_value_asof_empty_when_nothing_ingested(isolated_store) -> None:
    result = macro_pit.value_asof("DFII10", "2024-06-01")
    assert result.empty


def test_ingest_stores_rows_and_is_idempotent(isolated_store, monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get(url, params, timeout):
        return _fake_observations(
            [{"date": "2024-01-02", "value": "1.50", "realtime_start": "2024-01-02", "realtime_end": "9999-12-31"}]
        )

    monkeypatch.setattr(macro_pit.requests, "get", fake_get)
    first = macro_pit.ingest("DFII10", api_key="test-key")
    second = macro_pit.ingest("DFII10", api_key="test-key")

    assert first == 1
    assert second == 1
    assert len(isolated_store.macro_vintage_rows("DFII10")) == 1


def test_ingest_empty_response_stores_nothing(isolated_store, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(macro_pit.requests, "get", lambda url, params, timeout: _fake_observations([]))
    count = macro_pit.ingest("DFII10", api_key="test-key")
    assert count == 0
    assert isolated_store.macro_vintage_rows("DFII10") == []
