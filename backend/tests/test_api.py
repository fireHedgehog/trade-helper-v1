"""FastAPI contract checks that do not need the market database."""

from __future__ import annotations

import httpx
import pandas as pd
import pytest

from app import main


pytestmark = pytest.mark.anyio


@pytest.fixture
async def client():
    transport = httpx.ASGITransport(app=main.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as value:
        yield value


async def test_health(client) -> None:
    assert (await client.get("/api/health")).json() == {"status": "ok"}


async def test_backtest_rejects_unknown_strategy(client) -> None:
    response = await client.get("/api/backtest/SPY", params={"strategy": "Magic"})
    assert response.status_code == 400
    assert response.json()["detail"] == "unknown strategy: Magic"


async def test_backtest_rejects_out_of_range_parameter(client) -> None:
    response = await client.get(
        "/api/backtest/SPY", params={"strategy": "CTA Trend", "atr_mult": 999}
    )
    assert response.status_code == 400
    assert "atr_mult must be between" in response.json()["detail"]


async def test_backtest_rejects_invalid_parameter_relationship(client) -> None:
    response = await client.get(
        "/api/backtest/SPY",
        params={"strategy": "SMA Cross", "n_fast": 100, "n_slow": 50},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "n_fast must be below n_slow"


async def test_backtest_rejects_unknown_parameter(client) -> None:
    response = await client.get(
        "/api/backtest/SPY", params={"strategy": "CTA Trend", "secret_alpha": 1}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "unknown parameter: secret_alpha"


async def test_backtest_rejects_bad_window(client) -> None:
    invalid = await client.get("/api/backtest/SPY", params={"start": "yesterday"})
    reversed_window = await client.get(
        "/api/backtest/SPY", params={"start": "2025-01-02", "end": "2024-01-02"}
    )
    assert invalid.status_code == 400
    assert reversed_window.status_code == 400


async def test_valid_backtest_parameters_reach_engine(client, monkeypatch) -> None:
    captured = {}

    def fake_payload(symbol, strategy, params, start, end):
        captured.update(
            {"symbol": symbol, "strategy": strategy, "params": params,
             "start": start, "end": end}
        )
        return {"ok": True}

    monkeypatch.setattr(main, "backtest_payload", fake_payload)
    response = await client.get(
        "/api/backtest/SPY",
        params={"strategy": "CTA Trend", "atr_mult": "4.5", "n_entry": "120"},
    )
    assert response.status_code == 200
    assert response.json() == {"ok": True}
    assert captured["params"] == {"atr_mult": 4.5, "n_entry": 120}


async def test_saved_set_rejects_invalid_params(client) -> None:
    response = await client.post(
        "/api/param-sets",
        json={"name": "bad", "strategy": "CTA Trend", "params": {"atr_mult": -2}},
    )
    assert response.status_code == 400


async def test_bars_reports_missing_symbol(client, monkeypatch) -> None:
    monkeypatch.setattr(main.store, "load_bars", lambda _symbol: pd.DataFrame())
    response = await client.get("/api/bars/NOPE")
    assert response.status_code == 404
    assert response.json()["detail"] == "no bars for NOPE"


async def test_bars_rejects_oversized_request(client) -> None:
    response = await client.get("/api/bars/SPY", params={"days": 100_001})
    assert response.status_code == 400
    assert response.json()["detail"] == "days must be between 0 and 10000"
