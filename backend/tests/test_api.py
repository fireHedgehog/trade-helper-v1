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


@pytest.fixture(autouse=True)
def clear_portfolio_cache():
    main._portfolio_cache.clear()
    yield
    main._portfolio_cache.clear()


async def test_health(client) -> None:
    assert (await client.get("/api/health")).json() == {
        "status": "ok",
        "version": "0.45.0",
    }


async def test_symbol_selector_excludes_non_strategy_context(client, monkeypatch) -> None:
    monkeypatch.setattr(
        main.store, "list_symbols", lambda: ["DGS2", "SPY", "GC=F", "AAPL"]
    )

    response = await client.get("/api/symbols")

    assert response.status_code == 200
    assert response.json()["symbols"] == ["SPY", "AAPL"]
    assert response.json()["data_series"] == ["DGS2", "GC=F"]


async def test_data_status_includes_inventory_and_refresh_state(
    client, monkeypatch
) -> None:
    monkeypatch.setattr(
        main,
        "inventory_payload",
        lambda: {"symbols": [{"symbol": "SPY"}], "summary": {"symbols": 1}},
    )
    monkeypatch.setattr(
        main._data_refresh_manager,
        "snapshot",
        lambda: {"state": "idle", "total": 0},
    )

    response = await client.get("/api/data/status")

    assert response.status_code == 200
    assert response.json()["summary"]["symbols"] == 1
    assert response.json()["refresh"]["state"] == "idle"

    summary = await client.get("/api/data/status", params={"details": False})
    assert summary.status_code == 200
    assert "symbols" not in summary.json()
    assert "items" not in summary.json()["refresh"]


async def test_strategy_catalog_exposes_typed_params_and_evidence(client) -> None:
    response = await client.get("/api/strategies")

    assert response.status_code == 200
    cta = next(row for row in response.json()["strategies"] if row["name"] == "CTA Trend")
    assert cta["strategy_id"] == "cta-trend"
    assert cta["version"] == "v1-rejected"
    assert cta["evidence"]["status"] == "rejected_v1"
    assert cta["required_datasets"] == ["yahoo-adjusted-daily-ohlcv-v1"]
    entry = next(row for row in cta["parameter_schema"] if row["name"] == "n_entry")
    assert entry["type"] == "int"
    assert entry["default"] == 100
    assert entry["description"]
    sr = next(row for row in response.json()["strategies"] if row["name"] == "S/R Bounce")
    assert sr["evidence"]["status"] == "exploratory"
    assert "support/resistance" in sr["evidence"]["summary"]


async def test_macro_contract_forbids_signal_inference(client, monkeypatch) -> None:
    bars = pd.DataFrame(
        [
            {"date": "2026-07-01", "close": 4.1},
            {"date": "2026-08-01", "close": 4.2},
        ]
    )
    monkeypatch.setattr(
        main.store,
        "load_bars",
        lambda symbol: bars if symbol == "DGS2" else pd.DataFrame(),
    )
    monkeypatch.setattr(main, "macro_events", lambda: [])

    response = await client.get("/api/macro")

    assert response.status_code == 200
    payload = response.json()
    assert payload["contract"]["status"] == "display_only"
    assert payload["contract"]["signal_eligible"] is False
    assert payload["contract"]["point_in_time_available"] is False
    assert "regime" not in payload
    assert payload["cards"][0]["observation_date"] == "2026-08-01"
    assert payload["cards"][0]["release_datetime"] is None
    assert payload["cards"][0]["revision_status"] == "final_revised_current_FRED"
    assert payload["cards"][0]["signal_eligible"] is False


async def test_data_refresh_selects_stored_core_symbols(client, monkeypatch) -> None:
    captured = []
    monkeypatch.setattr(
        main,
        "inventory_payload",
        lambda: {
            "symbols": [{"symbol": "SPY", "freshness": "fresh"}],
            "refresh_policy": {"note": "rate limit warning"},
        },
    )
    monkeypatch.setattr(
        main._data_refresh_manager,
        "start",
        lambda symbols: captured.extend(symbols) or {"state": "running", "total": 1},
    )

    response = await client.post("/api/data/refresh", json={"scope": "core"})

    assert response.status_code == 202
    assert captured == ["SPY"]
    assert response.json()["refresh"]["state"] == "running"


async def test_data_refresh_rejects_empty_scope(client, monkeypatch) -> None:
    monkeypatch.setattr(
        main,
        "inventory_payload",
        lambda: {
            "symbols": [{"symbol": "SPY", "freshness": "fresh"}],
            "refresh_policy": {"note": "warning"},
        },
    )

    response = await client.post("/api/data/refresh", json={"scope": "stale"})

    assert response.status_code == 400
    assert response.json()["detail"] == "no stored symbols need the stale refresh"


async def test_data_refresh_rejects_overlapping_job(client, monkeypatch) -> None:
    monkeypatch.setattr(
        main,
        "inventory_payload",
        lambda: {
            "symbols": [{"symbol": "SPY", "freshness": "fresh"}],
            "refresh_policy": {"note": "warning"},
        },
    )
    monkeypatch.setattr(
        main._data_refresh_manager,
        "start",
        lambda _symbols: (_ for _ in ()).throw(
            main.RefreshAlreadyRunning("a data refresh is already running")
        ),
    )

    response = await client.post("/api/data/refresh", json={"scope": "core"})

    assert response.status_code == 409
    assert response.json()["detail"] == "a data refresh is already running"


async def test_daily_pipeline_plan_is_read_only_and_dependency_aware(
    client, monkeypatch
) -> None:
    monkeypatch.setattr(
        main,
        "inventory_payload",
        lambda: {
            "expected_latest_session": "2026-08-18",
            "symbols": [
                {
                    "symbol": "SPY",
                    "provider": "yahoo",
                    "dataset_id": "yahoo-adjusted-daily-ohlcv-v1",
                    "rows": 100,
                    "latest_date": "2026-08-17",
                    "freshness": "aging",
                }
            ],
        },
    )
    monkeypatch.setattr(main.store, "list_strategy_watchlist", lambda *_: [])
    monkeypatch.setattr(main.store, "latest_strategy_run", lambda *_: None)

    response = await client.get("/api/daily-pipeline/plan")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "refresh_required"
    assert payload["refresh"]["symbols"] == ["SPY"]
    assert payload["refresh"]["delay_seconds"] == 2.0
    assert payload["refresh"]["minimum_delay_seconds"] == 0
    assert payload["summary"]["blocked_data"] == len(main.STRATEGIES)
    assert payload["summary"]["skipped_empty"] == len(main.STRATEGIES)


async def test_daily_pipeline_requires_explicit_confirmation(client) -> None:
    response = await client.post("/api/daily-pipeline", json={"confirm": False})
    assert response.status_code == 400
    assert "reviewing /api/daily-pipeline/plan" in response.json()["detail"]


async def test_backtest_rejects_unknown_strategy(client) -> None:
    response = await client.get("/api/backtest/SPY", params={"strategy": "Magic"})
    assert response.status_code == 400
    assert response.json()["detail"] == "unknown strategy: Magic"


async def test_signal_accepts_validated_parameter_overrides(
    client, monkeypatch
) -> None:
    monkeypatch.setattr(
        main.store,
        "load_bars",
        lambda _symbol: pd.DataFrame([{"date": "2026-08-17"}]),
    )
    captured = {}

    def fake_signal(_bars, strategy, params):
        captured.update(strategy=strategy, params=params)
        return {"state": "flat", "event": "none", "indicators": {}}

    monkeypatch.setattr(main, "compute_stateful_signal", fake_signal)
    response = await client.get(
        "/api/signal/SPY",
        params={"strategy": "CTA Trend", "n_entry": 120},
    )

    assert response.status_code == 200
    assert captured["params"]["n_entry"] == 120
    assert captured["params"]["n_exit"] == 40


async def test_signal_rejects_unknown_parameter(client) -> None:
    response = await client.get(
        "/api/signal/SPY",
        params={"strategy": "CTA Trend", "secret_alpha": 1},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "unknown parameter: secret_alpha"


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

    def fake_payload(symbol, strategy, params, start, end, **assumptions):
        captured.update(
            {"symbol": symbol, "strategy": strategy, "params": params,
             "start": start, "end": end, "assumptions": assumptions}
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
    assert captured["assumptions"]["spread"] == 0.0002


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


async def test_watchlist_save_rejects_symbols_without_stored_data(
    client, monkeypatch
) -> None:
    monkeypatch.setattr(main.store, "list_symbols", lambda: ["SPY", "QQQ"])
    response = await client.put(
        "/api/strategy-watchlist?strategy=CTA%20Trend",
        json={"symbols": ["SPY", "NOPE"]},
    )
    assert response.status_code == 400
    assert "NOPE" in response.json()["detail"]


async def test_latest_strategy_run_is_read_only_and_returns_empty_state(
    client, monkeypatch
) -> None:
    captured = {}

    def fake_latest(*args):
        captured["args"] = args
        return None

    monkeypatch.setattr(main.store, "latest_strategy_run", fake_latest)
    monkeypatch.setattr(main.store, "list_strategy_watchlist", lambda *_args: [])
    response = await client.get(
        "/api/strategy-runs/latest?strategy=CTA%20Trend"
        "&scope=all&latest_any_set=true"
    )
    assert response.status_code == 200
    assert response.json()["run"] is None
    assert captured["args"] == ("CTA Trend", None, "all")


async def test_explicit_strategy_run_persists_snapshot(client, monkeypatch) -> None:
    monkeypatch.setattr(
        main.store,
        "list_strategy_watchlist",
        lambda *_args: [{"symbol": "SPY"}],
    )
    monkeypatch.setattr(main.store, "save_strategy_run", lambda *_args: 7)
    monkeypatch.setattr(
        main.store,
        "get_strategy_run",
        lambda *_args: {"id": 7, "result": {"watchlist": [{"symbol": "SPY"}]}},
    )
    captured = {}

    def fake_snapshot(strategy, params, *, watch_symbols, discovery_symbols):
        captured.update(
            strategy=strategy,
            params=params,
            watch=watch_symbols,
            discovery=discovery_symbols,
        )
        return {"data_as_of": "2024-01-03", "watchlist": [{"symbol": "SPY"}]}

    monkeypatch.setattr(main, "create_strategy_snapshot", fake_snapshot)
    response = await client.post(
        "/api/strategy-runs",
        json={"strategy": "CTA Trend", "scope": "watchlist"},
    )
    assert response.status_code == 201
    assert response.json()["id"] == 7
    assert captured["watch"] == ["SPY"]
    assert captured["discovery"] == []


async def test_watchlist_run_requires_an_explicit_saved_watchlist(
    client, monkeypatch
) -> None:
    monkeypatch.setattr(main.store, "list_strategy_watchlist", lambda *_args: [])
    response = await client.post(
        "/api/strategy-runs",
        json={"strategy": "CTA Trend", "scope": "watchlist"},
    )
    assert response.status_code == 400
    assert "watchlist is empty" in response.json()["detail"]


async def test_backtest_rejects_impossible_cost_assumption(client) -> None:
    response = await client.get("/api/backtest/SPY", params={"slippage": -0.1})
    assert response.status_code == 400
    assert "slippage must be between" in response.json()["detail"]


async def test_portfolio_endpoint_validates_and_resolves_params(
    client, monkeypatch
) -> None:
    captured = {}

    def fake_payload(strategy: str, params: dict) -> dict:
        captured.update(strategy=strategy, params=params)
        return {"status": "complete"}

    monkeypatch.setattr(main, "portfolio_payload", fake_payload)
    response = await client.get(
        "/api/portfolio", params={"strategy": "CTA Trend", "atr_mult": 4.5}
    )

    assert response.status_code == 200
    assert response.json() == {"status": "complete", "param_set": "defaults"}
    assert captured["strategy"] == "CTA Trend"
    assert captured["params"]["atr_mult"] == 4.5
    assert captured["params"]["n_entry"] == 100


async def test_portfolio_endpoint_rejects_unknown_parameter(client) -> None:
    response = await client.get("/api/portfolio", params={"secret_alpha": 1})

    assert response.status_code == 400
    assert response.json()["detail"] == "unknown parameter: secret_alpha"


async def test_portfolio_endpoint_reports_unavailable_data(
    client, monkeypatch
) -> None:
    monkeypatch.setattr(
        main,
        "portfolio_payload",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("missing")),
    )

    response = await client.get("/api/portfolio")

    assert response.status_code == 503
    assert response.json()["detail"] == "missing"


async def test_portfolio_endpoint_resolves_saved_set(client, monkeypatch) -> None:
    monkeypatch.setattr(
        main.store,
        "list_param_sets",
        lambda _strategy: [{"name": "locked", "params": {"atr_mult": 4.0}}],
    )
    monkeypatch.setattr(
        main,
        "portfolio_payload",
        lambda _strategy, params: {"atr_mult": params["atr_mult"]},
    )

    response = await client.get("/api/portfolio", params={"set": "locked"})

    assert response.status_code == 200
    assert response.json() == {"atr_mult": 4.0, "param_set": "locked"}


async def test_portfolio_endpoint_caches_identical_request_until_refresh(
    client, monkeypatch
) -> None:
    calls = 0

    def fake_payload(_strategy: str, _params: dict) -> dict:
        nonlocal calls
        calls += 1
        return {"generation": calls}

    monkeypatch.setattr(main, "portfolio_payload", fake_payload)

    first = await client.get("/api/portfolio")
    cached = await client.get("/api/portfolio")
    refreshed = await client.get("/api/portfolio", params={"refresh": True})

    assert first.json()["generation"] == 1
    assert cached.json()["generation"] == 1
    assert refreshed.json()["generation"] == 2
    assert calls == 2
