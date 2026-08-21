"""GICS sector classification: parsing, storage, read-back.

No live network call is made anywhere in this suite -- the Wikipedia fetch
is monkeypatched. This exercises the parsing/storage logic end-to-end; it
does not verify Wikipedia's live table shape (that was live-verified once
by hand at introduction: 503 symbols, 11 GICS sectors).
"""
from __future__ import annotations

import pandas as pd
import pytest

from app import store, universe, universe_sectors


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


FIXTURE_HTML = """
<table>
<tr><th>Symbol</th><th>Security</th><th>GICS Sector</th><th>GICS Sub-Industry</th></tr>
<tr><td>NVDA</td><td>Nvidia</td><td>Information Technology</td><td>Semiconductors</td></tr>
<tr><td>MSFT</td><td>Microsoft</td><td>Information Technology</td><td>Systems Software</td></tr>
<tr><td>BF.B</td><td>Brown-Forman</td><td>Consumer Staples</td><td>Distillers &amp; Vintners</td></tr>
</table>
"""


def test_get_sp500_sectors_normalizes_tickers(monkeypatch):
    monkeypatch.setattr(universe.requests, "get", lambda *a, **k: _FakeResponse(FIXTURE_HTML))
    df = universe.get_sp500_sectors()
    assert list(df.columns) == ["symbol", "gics_sector", "gics_sub_industry"]
    assert set(df["symbol"]) == {"NVDA", "MSFT", "BF-B"}
    row = df[df["symbol"] == "NVDA"].iloc[0]
    assert row["gics_sector"] == "Information Technology"
    assert row["gics_sub_industry"] == "Semiconductors"


def test_ingest_and_read_back(monkeypatch, isolated_store):
    monkeypatch.setattr(universe.requests, "get", lambda *a, **k: _FakeResponse(FIXTURE_HTML))
    universe_sectors.main()
    sectors = isolated_store.load_equity_sectors()
    assert sectors["NVDA"]["gics_sub_industry"] == "Semiconductors"
    assert sectors["MSFT"]["gics_sub_industry"] == "Systems Software"
    assert "as_of_date" in sectors["NVDA"]


def test_reingest_replaces_rather_than_accumulates(monkeypatch, isolated_store):
    monkeypatch.setattr(universe.requests, "get", lambda *a, **k: _FakeResponse(FIXTURE_HTML))
    universe_sectors.main()
    universe_sectors.main()
    with isolated_store.connect() as conn:
        (count,) = conn.execute("SELECT COUNT(*) FROM equity_sectors").fetchone()
    assert count == 3


def test_upsert_equity_sectors_requires_columns(isolated_store):
    with pytest.raises(ValueError, match="missing columns"):
        isolated_store.upsert_equity_sectors(pd.DataFrame({"symbol": ["NVDA"]}), "2026-08-21")
