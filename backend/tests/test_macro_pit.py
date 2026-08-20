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
    def __init__(self, payload: dict):
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self._payload


def _fake_observations(rows: list[dict]) -> _FakeResponse:
    return _FakeResponse({"observations": rows})


def test_missing_api_key_raises_actionable_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="FRED_API_KEY"):
        macro_pit.fetch_all_vintages("DFII10")


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
