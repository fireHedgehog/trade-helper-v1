"""Point-in-time S&P 500 membership: parsing, storage, as-of reconstruction.

No live network call is made anywhere in this suite -- requests.get is
monkeypatched. This exercises the parsing/storage/as-of logic end-to-end; it
does not verify the real GitHub source's live response shape (that was
live-verified once by hand at introduction: 1259 intervals, 1206 distinct
symbols, 503 currently active).
"""
from __future__ import annotations

import pandas as pd
import pytest

from app import store, universe_pit


@pytest.fixture
def isolated_store(tmp_path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(store, "DATA_DIR", tmp_path)
    monkeypatch.setattr(store, "DB_PATH", tmp_path / "market.db")
    return store


class _FakeResponse:
    def __init__(self, text: str, status_code: int = 200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


FIXTURE_CSV = (
    "ticker,start_date,end_date\n"
    "AAPL,1996-01-02,\n"
    "BF.B,1996-01-02,2005-06-01\n"
    "SNDK,2000-01-01,2016-05-12\n"
    "SNDK,2025-02-19,\n"
)


def test_fetch_membership_normalizes_tickers(monkeypatch):
    monkeypatch.setattr(universe_pit.requests, "get", lambda *a, **k: _FakeResponse(FIXTURE_CSV))
    df = universe_pit.fetch_membership()
    assert set(df["symbol"]) == {"AAPL", "BF-B", "SNDK"}
    assert len(df) == 4  # SNDK appears twice: two disjoint membership intervals


def test_ingest_and_asof_reconstructs_membership(monkeypatch, isolated_store):
    monkeypatch.setattr(universe_pit.requests, "get", lambda *a, **k: _FakeResponse(FIXTURE_CSV))
    universe_pit.ingest_membership()

    # AAPL: open-ended membership from 1996 -> still in today.
    assert "AAPL" in isolated_store.members_asof("2026-08-01")
    assert "AAPL" in isolated_store.members_asof("1996-01-02")

    # BF-B: left the index in 2005 -- must not appear after its end_date.
    assert "BF-B" in isolated_store.members_asof("2005-05-01")
    assert "BF-B" not in isolated_store.members_asof("2005-06-02")

    # SNDK: two disjoint intervals (delisted 2016, relisted 2025) -- the gap
    # year must not show it as a member, exactly the re-entry case the real
    # dataset has (Western Digital's SanDisk spin-off reusing the ticker).
    assert "SNDK" in isolated_store.members_asof("2010-01-01")
    assert "SNDK" not in isolated_store.members_asof("2020-01-01")
    assert "SNDK" in isolated_store.members_asof("2026-01-01")


def test_reingest_replaces_rather_than_accumulates(monkeypatch, isolated_store):
    monkeypatch.setattr(universe_pit.requests, "get", lambda *a, **k: _FakeResponse(FIXTURE_CSV))
    universe_pit.ingest_membership()
    universe_pit.ingest_membership()
    with isolated_store.connect() as conn:
        (count,) = conn.execute("SELECT COUNT(*) FROM universe_membership").fetchone()
    assert count == 4  # re-running must replace, not double-insert


def test_upsert_universe_membership_requires_columns(isolated_store):
    with pytest.raises(ValueError, match="missing columns"):
        isolated_store.upsert_universe_membership(pd.DataFrame({"symbol": ["AAPL"]}), "SP500")


def test_members_asof_unknown_index_is_empty(isolated_store):
    assert isolated_store.members_asof("2020-01-01", index_name="NOPE") == []
