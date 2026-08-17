"""FastAPI server: REST API + serves the static frontend.

Run (from backend/):
    uvicorn app.main:app --reload
"""
import time
from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles

from . import store
from .calendar import macro_events
from .confidence import compute_confidence
from .engine import backtest_payload
from .signals import (
    CORE_WATCHLIST,
    advance_positions,
    compute_stateful_signal,
    positions_payload,
    scan,
)
from .strategies import STRATEGIES, STRATEGY_INFO, STRATEGY_PARAMS
from .universe import DEFAULT_BASKET

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"

MACRO_SYMBOLS = {
    "SPY": "S&P 500",
    "GC=F": "Gold",
    "CL=F": "Crude",
    "^TNX": "US 10Y yield",
    "DGS2": "US 2Y yield",
}

_today_cache: dict = {}

app = FastAPI(title="trade-helper-v1")


def _validated_strategy_params(strategy: str, raw: dict) -> dict:
    """Coerce and enforce the same parameter contract advertised to the UI."""
    if strategy not in STRATEGIES:
        raise HTTPException(status_code=400, detail=f"unknown strategy: {strategy}")
    meta = STRATEGY_PARAMS[strategy]
    parsed = {}
    for key, value in raw.items():
        if key not in meta:
            raise HTTPException(status_code=400, detail=f"unknown parameter: {key}")
        try:
            parsed[key] = float(value) if meta[key]["type"] == "float" else int(value)
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail=f"bad value for {key}: {value}")
        if not meta[key]["min"] <= parsed[key] <= meta[key]["max"]:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"{key} must be between {meta[key]['min']} and "
                    f"{meta[key]['max']}"
                ),
            )
    resolved = {key: value["default"] for key, value in meta.items()}
    resolved.update(parsed)
    if strategy == "SMA Cross" and resolved["n_fast"] >= resolved["n_slow"]:
        raise HTTPException(status_code=400, detail="n_fast must be below n_slow")
    if strategy in {"CTA Trend", "Donchian Trend"} and resolved["n_exit"] >= resolved["n_entry"]:
        raise HTTPException(status_code=400, detail="n_exit must be below n_entry")
    if strategy == "RSI Reversion" and resolved["buy_below"] >= resolved["sell_above"]:
        raise HTTPException(status_code=400, detail="buy_below must be below sell_above")
    return parsed


def _validated_window(start: str | None, end: str | None) -> None:
    try:
        parsed_start = date.fromisoformat(start) if start else None
        parsed_end = date.fromisoformat(end) if end else None
    except ValueError:
        raise HTTPException(status_code=400, detail="start/end must be YYYY-MM-DD")
    if parsed_start and parsed_end and parsed_start > parsed_end:
        raise HTTPException(status_code=400, detail="start must not be after end")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/symbols")
def symbols():
    return {"symbols": store.list_symbols(), "default_basket": DEFAULT_BASKET}


@app.get("/api/bars/{symbol}")
def bars(symbol: str, days: int = 0):
    if days < 0 or days > 10_000:
        raise HTTPException(status_code=400, detail="days must be between 0 and 10000")
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
def signal_now(symbol: str, strategy: str = "CTA Trend"):
    if strategy not in STRATEGIES:
        raise HTTPException(status_code=400, detail=f"unknown strategy: {strategy}")
    bars = store.load_bars(symbol)
    if bars.empty:
        raise HTTPException(status_code=404, detail=f"no bars for {symbol}")
    params = {
        key: value["default"] for key, value in STRATEGY_PARAMS[strategy].items()
    }
    result = compute_stateful_signal(bars, strategy, params)
    if result is None:
        raise HTTPException(status_code=404, detail="not enough bars")
    return {"symbol": symbol, "strategy": strategy, **result}


@app.get("/api/positions")
def positions(strategy: str = "CTA Trend", set: str = "defaults"):
    if strategy not in STRATEGIES:
        raise HTTPException(status_code=400, detail=f"unknown strategy: {strategy}")
    params = None
    if set != "defaults":
        saved = store.list_param_sets(strategy)
        chosen = next((s for s in saved if s["name"] == set), None)
        if chosen is None:
            raise HTTPException(status_code=404, detail=f"unknown param set: {set}")
        params = chosen["params"]
    return {"positions": positions_payload(strategy, set, params)}


@app.get("/api/confidence")
def confidence(
    strategy: str = "CTA Trend",
    symbols: str = "",
    days: int = 252,
    force: bool = False,
):
    """Hit-rate stats over a chosen symbol list and bar window. Defaults to
    the deliberate liquid basket (16 names). days <= 0 = full history — heavy
    on many symbols, so the UI warns before running it."""
    if strategy not in STRATEGIES:
        raise HTTPException(status_code=400, detail=f"unknown strategy: {strategy}")
    days = max(-1, min(int(days), 100000))
    chosen = [s.strip().upper() for s in symbols.split(",") if s.strip()] or None
    return compute_confidence(strategy, force=force, symbols=chosen, max_days=days)


@app.get("/api/backtest/{symbol}")
def backtest(
    symbol: str,
    request: Request,
    strategy: str = "CTA Trend",
    start: str | None = None,
    end: str | None = None,
):
    reserved = {"symbol", "strategy", "start", "end"}
    unknown = set(request.query_params) - reserved - set(STRATEGY_PARAMS.get(strategy, {}))
    if unknown:
        raise HTTPException(status_code=400, detail=f"unknown parameter: {sorted(unknown)[0]}")
    raw = {
        key: value
        for key, value in request.query_params.items()
        if key not in reserved
    }
    params = _validated_strategy_params(strategy, raw)
    _validated_window(start, end)
    try:
        return backtest_payload(symbol, strategy, params=params, start=start, end=end)
    except KeyError:
        raise HTTPException(status_code=400, detail=f"unknown strategy: {strategy}")
    except RuntimeError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.get("/api/today")
def today(
    strategy: str = "CTA Trend",
    scope: str = "core",
    set: str = "defaults",
    refresh: bool = False,
):
    if strategy not in STRATEGIES:
        raise HTTPException(status_code=400, detail=f"unknown strategy: {strategy}")
    symbols = CORE_WATCHLIST if scope == "core" else store.list_symbols()
    cache_key = f"{strategy}|{scope}|{set}"
    cached = _today_cache.get(cache_key)
    if not refresh and cached and time.time() - cached["at"] < 60:
        return cached["data"]
    params = None
    if set != "defaults":
        saved = store.list_param_sets(strategy)
        chosen = next((s for s in saved if s["name"] == set), None)
        if chosen is None:
            raise HTTPException(status_code=404, detail=f"unknown param set: {set}")
        params = chosen["params"]
    if scope == "core":
        advance_positions(strategy, params, set)  # advance the paper ledger
    result = scan(strategy, symbols, params)
    result["strategy"] = strategy
    result["scope"] = scope
    result["set"] = set
    _today_cache[cache_key] = {"at": time.time(), "data": result}
    return result


@app.get("/api/score-return")
def score_return(
    strategy: str = "CTA Trend",
    symbols: str = "",
    days: int = 252,
):
    """Median strategy return vs median buy & hold over the chosen sample
    and window — the honest performance comparison for the scoreboard."""
    if strategy not in STRATEGIES:
        raise HTTPException(status_code=400, detail=f"unknown strategy: {strategy}")
    days = max(-1, min(int(days), 100000))
    chosen = [s.strip().upper() for s in symbols.split(",") if s.strip()] or DEFAULT_BASKET

    def median(values: list[float]) -> float | None:
        if not values:
            return None
        values = sorted(values)
        mid = len(values) // 2
        return round((values[mid] if len(values) % 2 else (values[mid - 1] + values[mid]) / 2), 1)

    returns, buy_hold = [], []
    for symbol in chosen:
        start = None
        if days > 0:
            recent = store.load_recent_bars(symbol, days)
            if recent.empty:
                continue
            start = str(recent["date"].iloc[0])
        try:
            metrics = backtest_payload(symbol, strategy, params=None, start=start)["metrics"]
        except (RuntimeError, KeyError):
            continue
        if metrics.get("Return [%]") is not None:
            returns.append(metrics["Return [%]"])
        if metrics.get("Buy & Hold Return [%]") is not None:
            buy_hold.append(metrics["Buy & Hold Return [%]"])
    return {
        "strategy": strategy,
        "symbols": len(chosen),
        "ret_med": median(returns),
        "bh_med": median(buy_hold),
    }


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
    params = _validated_strategy_params(strategy, params)
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
    us10y = next(
        (c for c in cards if c["symbol"] in ("DGS10", "^TNX")), None
    )
    return {
        "cards": cards,
        "events": macro_events(),
        "regime": {
            "us10y": us10y["close"] if us10y else None,
            "threshold": 5.0,
            "ok": us10y is None or us10y["close"] < 5.0,
        },
    }


# Last: serve the static frontend for everything not matched above.
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
