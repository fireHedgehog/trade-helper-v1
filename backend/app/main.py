"""FastAPI server: REST API + serves the static frontend.

Run (from backend/):
    uvicorn app.main:app --reload
"""
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles

from . import store
from .confidence import compute_confidence
from .engine import backtest_payload
from .signals import (
    CORE_WATCHLIST,
    advance_positions,
    compute_signal,
    positions_payload,
    scan,
)
from .strategies import STRATEGIES, STRATEGY_INFO, STRATEGY_PARAMS

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"

MACRO_SYMBOLS = {
    "SPY": "S&P 500",
    "GC=F": "Gold",
    "CL=F": "Crude",
    "^TNX": "US 10Y yield",
    "SHY": "US 2Y proxy",
}

# SAMPLE calendar — dates are placeholders until we wire a real source.
MACRO_EVENTS = [
    {"date": "2026-08-27", "name": "Jackson Hole Symposium", "note": "sample — verify"},
    {"date": "2026-09-11", "name": "CPI release", "note": "sample — verify"},
    {"date": "2026-09-15", "name": "FOMC decision", "note": "sample — verify"},
    {"date": "2026-10-02", "name": "Non-farm payrolls", "note": "sample — verify"},
]

_today_cache: dict = {}

app = FastAPI(title="trade-helper-v1")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/symbols")
def symbols():
    return {"symbols": store.list_symbols()}


@app.get("/api/bars/{symbol}")
def bars(symbol: str, days: int = 0):
    frame = store.load_bars(symbol)
    if frame.empty:
        raise HTTPException(status_code=404, detail=f"no bars for {symbol}")
    if days > 0:
        frame = frame.tail(days)
    return {"symbol": symbol, "bars": frame.to_dict("records")}


@app.get("/api/strategies")
def strategies():
    return {
        "strategies": [
            {
                "name": name,
                "params": STRATEGY_PARAMS[name],
                "info": STRATEGY_INFO[name],
            }
            for name in STRATEGIES
        ]
    }


@app.get("/api/signal/{symbol}")
def signal_now(symbol: str, strategy: str = "SMA Cross"):
    if strategy not in STRATEGIES:
        raise HTTPException(status_code=400, detail=f"unknown strategy: {strategy}")
    bars = store.load_recent_bars(symbol, 300)
    if bars.empty:
        raise HTTPException(status_code=404, detail=f"no bars for {symbol}")
    params = {
        key: value["default"] for key, value in STRATEGY_PARAMS[strategy].items()
    }
    result = compute_signal(bars, strategy, params)
    if result is None:
        raise HTTPException(status_code=404, detail="not enough bars")
    return {"symbol": symbol, "strategy": strategy, **result}


@app.get("/api/positions")
def positions(strategy: str = "SMA Cross"):
    if strategy not in STRATEGIES:
        raise HTTPException(status_code=400, detail=f"unknown strategy: {strategy}")
    return {"positions": positions_payload(strategy)}


@app.get("/api/confidence")
def confidence(
    strategy: str = "SMA Cross",
    symbols: int = 5,
    days: int = 252,
    force: bool = False,
):
    """Hit-rate stats. Sample-limited by default (laptop-safe); symbols<=0 or
    days<=0 means the full run — intended for cloud compute."""
    if strategy not in STRATEGIES:
        raise HTTPException(status_code=400, detail=f"unknown strategy: {strategy}")
    symbols = max(-1, min(int(symbols), 1000))
    days = max(-1, min(int(days), 100000))
    return compute_confidence(strategy, force=force, max_symbols=symbols, max_days=days)


@app.get("/api/backtest/{symbol}")
def backtest(
    symbol: str,
    request: Request,
    strategy: str = "SMA Cross",
    start: str | None = None,
    end: str | None = None,
):
    reserved = {"symbol", "strategy", "start", "end"}
    meta = STRATEGY_PARAMS.get(strategy, {})
    params = {}
    for key, value in request.query_params.items():
        if key in reserved or key not in meta:
            continue
        try:
            params[key] = float(value) if meta[key]["type"] == "float" else int(value)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"bad value for {key}: {value}")
    try:
        return backtest_payload(symbol, strategy, params=params, start=start, end=end)
    except KeyError:
        raise HTTPException(status_code=400, detail=f"unknown strategy: {strategy}")
    except RuntimeError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.get("/api/today")
def today(strategy: str = "SMA Cross", scope: str = "core", refresh: bool = False):
    if strategy not in STRATEGIES:
        raise HTTPException(status_code=400, detail=f"unknown strategy: {strategy}")
    symbols = CORE_WATCHLIST if scope == "core" else store.list_symbols()
    cache_key = f"{strategy}|{scope}"
    cached = _today_cache.get(cache_key)
    if not refresh and cached and time.time() - cached["at"] < 60:
        return cached["data"]
    if scope == "core":
        advance_positions(strategy)  # advance the paper ledger to the latest bar
    result = scan(strategy, symbols)
    result["strategy"] = strategy
    result["scope"] = scope
    _today_cache[cache_key] = {"at": time.time(), "data": result}
    return result


@app.get("/api/param-sets")
def param_sets(strategy: str | None = None):
    return {"sets": store.list_param_sets(strategy)}


@app.post("/api/param-sets")
def save_param_set(payload: dict):
    name = (payload.get("name") or "").strip()
    strategy = payload.get("strategy")
    params = payload.get("params") or {}
    if not name or strategy not in STRATEGIES:
        raise HTTPException(status_code=400, detail="need a name and a valid strategy")
    if not isinstance(params, dict):
        raise HTTPException(status_code=400, detail="params must be an object")
    store.save_param_set(name, strategy, params)
    return {"ok": True}


@app.delete("/api/param-sets/{name}")
def delete_param_set(name: str):
    store.delete_param_set(name)
    return {"ok": True}


@app.get("/api/macro")
def macro():
    cards = []
    for symbol, label in MACRO_SYMBOLS.items():
        frame = store.load_bars(symbol)
        if frame.empty:
            continue
        last = frame.iloc[-1]
        prev = frame.iloc[-2] if len(frame) > 1 else last
        cards.append(
            {
                "symbol": symbol,
                "label": label,
                "close": round(float(last["close"]), 2),
                "change_pct": round(float(last["close"] / prev["close"] - 1) * 100, 2),
            }
        )
    tnx = next((c for c in cards if c["symbol"] == "^TNX"), None)
    us10y = tnx["close"] if tnx else None
    return {
        "cards": cards,
        "events": MACRO_EVENTS,
        "regime": {
            "us10y": us10y,
            "threshold": 5.0,
            "ok": us10y is None or us10y < 5.0,
        },
    }


# Last: serve the static frontend for everything not matched above.
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
