"""FastAPI server: REST API + serves the static frontend.

Run (from backend/):
    uvicorn app.main:app --reload
"""
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles

from . import store
from .engine import backtest_payload
from .strategies import STRATEGIES, STRATEGY_PARAMS

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"

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
            {"name": name, "params": STRATEGY_PARAMS[name]} for name in STRATEGIES
        ]
    }


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


# Last: serve the static frontend for everything not matched above.
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
