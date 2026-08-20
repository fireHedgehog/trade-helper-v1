"""Treasury buyback ingestion: parsing, settled-only filtering, long-end classification.

No live network call -- requests.get is monkeypatched.
"""
from __future__ import annotations

import pytest

from app import store, treasury_buybacks


@pytest.fixture
def isolated_store(tmp_path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(store, "DATA_DIR", tmp_path)
    monkeypatch.setattr(store, "DB_PATH", tmp_path / "market.db")
    return store


class _FakeResponse:
    def __init__(self, rows: list[dict]):
        self._rows = rows

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return {"data": self._rows}


def _row(**overrides) -> dict:
    row = {
        "operation_date": "2026-08-18",
        "maturity_bucket": "20Y to 30Y",
        "security_type": "Nominal Coupons",
        "settlement_date": "2026-08-19",
        "operation_type": "Liquidity Support",
        "nbr_issues_accepted": "3",
        "nbr_issues_eligible": "36",
        "total_par_amt_offered": "19868000000.00",
        "total_par_amt_accepted": "2000000000.00",
    }
    row.update(overrides)
    return row


def test_fetch_operations_drops_unsettled_rows(monkeypatch: pytest.MonkeyPatch) -> None:
    unsettled = _row(operation_date="2026-08-20", total_par_amt_accepted="null", nbr_issues_accepted="null")
    monkeypatch.setattr(
        treasury_buybacks.requests, "get", lambda url, params, timeout: _FakeResponse([_row(), unsettled])
    )
    df = treasury_buybacks.fetch_operations()
    assert len(df) == 1
    assert list(df["operation_date"]) == ["2026-08-18"]


def test_fetch_operations_fills_missing_bucket_and_security_type(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    legacy = _row(operation_date="2000-03-09", maturity_bucket="null", security_type="null")
    monkeypatch.setattr(
        treasury_buybacks.requests, "get", lambda url, params, timeout: _FakeResponse([legacy])
    )
    df = treasury_buybacks.fetch_operations()
    assert df.iloc[0]["maturity_bucket"] == ""
    assert df.iloc[0]["security_type"] == ""


@pytest.mark.parametrize(
    "bucket,expected",
    [
        ("20Y to 30Y", True),
        ("10Y to 20Y", True),
        ("7.5Y to 30Y", True),
        ("10Y to 30Y", True),
        ("7Y to 10Y", False),
        ("3Y to 5Y", False),
        ("1Mo to 2Y", False),
        ("", False),
    ],
)
def test_is_long_end(bucket: str, expected: bool) -> None:
    assert treasury_buybacks.is_long_end(bucket) is expected


def test_ingest_stores_settled_rows_and_is_idempotent(
    isolated_store, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        treasury_buybacks.requests, "get", lambda url, params, timeout: _FakeResponse([_row()])
    )
    first = treasury_buybacks.ingest()
    second = treasury_buybacks.ingest()
    assert first == 1
    assert second == 1
    assert len(isolated_store.load_treasury_buybacks()) == 1


def test_ingest_empty_response_stores_nothing(
    isolated_store, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(treasury_buybacks.requests, "get", lambda url, params, timeout: _FakeResponse([]))
    count = treasury_buybacks.ingest()
    assert count == 0
    assert isolated_store.load_treasury_buybacks() == []
