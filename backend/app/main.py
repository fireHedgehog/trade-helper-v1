"""FastAPI server: REST API + serves the static frontend.

Run (from backend/):
    uvicorn app.main:app --reload
"""
import time
import math
from datetime import date
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import confidence as confidence_module, store
from .calendar import macro_events
from .confidence import compute_confidence
from .data_management import (
    DataRefreshManager,
    RefreshAlreadyRunning,
    inventory_payload,
    select_refresh_symbols,
)
from .engine import backtest_payload
from .fred import MANAGED_SERIES as FRED_MANAGED_SERIES
from .portfolio_api import portfolio_payload
from .signals import (
    CORE_WATCHLIST,
    advance_positions,
    compute_stateful_signal,
    positions_payload,
    scan,
)
from .strategies import STRATEGIES, STRATEGY_INFO, STRATEGY_PARAMS
from .universe import DEFAULT_BASKET
from .version import APP_VERSION
from .workspace import create_strategy_snapshot

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"

MACRO_SYMBOLS = {
    "SPY": "S&P 500",
    "GC=F": "Gold",
    "CL=F": "Crude",
    "^TNX": "US 10Y yield",
    "DGS2": "US 2Y yield",
}

_today_cache: dict = {}
_portfolio_cache: dict = {}


def _invalidate_derived_caches() -> None:
    _today_cache.clear()
    _portfolio_cache.clear()
    confidence_module.clear_cache()


_data_refresh_manager = DataRefreshManager(on_publish=_invalidate_derived_caches)

app = FastAPI(title="trade-helper-v1", version=APP_VERSION)


class DataRefreshRequest(BaseModel):
    scope: Literal["core", "stale", "all"] = "core"


class StrategyWatchlistRequest(BaseModel):
    symbols: list[str]


class StrategyRunRequest(BaseModel):
    strategy: str = "CTA Trend"
    set: str = "defaults"
    scope: Literal["watchlist", "watchlist_core", "all"] = "watchlist_core"


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


def _resolved_params(strategy: str, set_name: str) -> dict:
    if strategy not in STRATEGIES:
        raise HTTPException(status_code=400, detail=f"unknown strategy: {strategy}")
    params = {
        key: value["default"] for key, value in STRATEGY_PARAMS[strategy].items()
    }
    if set_name != "defaults":
        saved = store.list_param_sets(strategy)
        chosen = next((row for row in saved if row["name"] == set_name), None)
        if chosen is None:
            raise HTTPException(status_code=404, detail=f"unknown param set: {set_name}")
        params.update(chosen["params"])
    return _validated_strategy_params(strategy, params)


@app.get("/api/health")
def health():
    return {"status": "ok", "version": APP_VERSION}


@app.get("/api/symbols")
def symbols():
    stored = store.list_symbols()
    return {
        "symbols": [symbol for symbol in stored if symbol not in FRED_MANAGED_SERIES],
        "data_series": [symbol for symbol in stored if symbol in FRED_MANAGED_SERIES],
        "default_basket": DEFAULT_BASKET,
    }


@app.get("/api/data/status")
def data_status(details: bool = True):
    result = inventory_payload()
    result["refresh"] = _data_refresh_manager.snapshot()
    if not details:
        result.pop("symbols", None)
        result["refresh"].pop("items", None)
    return result


@app.post("/api/data/refresh", status_code=202)
def start_data_refresh(request: DataRefreshRequest):
    status = inventory_payload()
    selected = select_refresh_symbols(
        request.scope, status["symbols"], CORE_WATCHLIST
    )
    if not selected:
        raise HTTPException(
            status_code=400,
            detail=f"no stored symbols need the {request.scope} refresh",
        )
    try:
        refresh = _data_refresh_manager.start(selected)
    except RefreshAlreadyRunning as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return {
        "scope": request.scope,
        "refresh": refresh,
        "warning": status["refresh_policy"]["note"],
    }


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


@app.get("/api/strategy-watchlist")
def strategy_watchlist(strategy: str = "CTA Trend"):
    if strategy not in STRATEGIES:
        raise HTTPException(status_code=400, detail=f"unknown strategy: {strategy}")
    rows = store.list_strategy_watchlist(strategy)
    return {
        "strategy": strategy,
        "symbols": [row["symbol"] for row in rows],
        "items": rows,
        "suggested_defaults": CORE_WATCHLIST,
    }


@app.put("/api/strategy-watchlist")
def save_strategy_watchlist(strategy: str, request: StrategyWatchlistRequest):
    if strategy not in STRATEGIES:
        raise HTTPException(status_code=400, detail=f"unknown strategy: {strategy}")
    stored_symbols = set(store.list_symbols()) - set(FRED_MANAGED_SERIES)
    normalized = list(dict.fromkeys(symbol.strip().upper() for symbol in request.symbols))
    unknown = [symbol for symbol in normalized if symbol not in stored_symbols]
    if unknown:
        raise HTTPException(
            status_code=400,
            detail="watchlist symbols have no stored security data: " + ", ".join(unknown),
        )
    store.replace_strategy_watchlist(strategy, normalized)
    return {"strategy": strategy, "symbols": normalized, "saved": True}


@app.get("/api/strategy-runs/latest")
def latest_strategy_run(
    strategy: str = "CTA Trend",
    set: str = "defaults",
    scope: Literal["watchlist", "watchlist_core", "all"] | None = None,
    latest_any_set: bool = False,
):
    if strategy not in STRATEGIES:
        raise HTTPException(status_code=400, detail=f"unknown strategy: {strategy}")
    run = store.latest_strategy_run(
        strategy,
        None if latest_any_set else set,
        scope,
    )
    return {
        "strategy": strategy,
        "set": run["set"] if run else set,
        "run": run,
        "watchlist": store.list_strategy_watchlist(strategy),
    }


@app.post("/api/strategy-runs", status_code=201)
def run_strategy_snapshot(request: StrategyRunRequest):
    params = _resolved_params(request.strategy, request.set)
    watch = [
        row["symbol"] for row in store.list_strategy_watchlist(request.strategy)
    ]
    if request.scope == "watchlist":
        if not watch:
            raise HTTPException(
                status_code=400,
                detail="strategy watchlist is empty; save symbols in Strategy Lab first",
            )
        discovery = []
    elif request.scope == "watchlist_core":
        if not watch:
            watch = list(CORE_WATCHLIST)
        discovery = list(CORE_WATCHLIST)
    else:
        discovery = [
            symbol
            for symbol in store.list_symbols()
            if symbol not in FRED_MANAGED_SERIES
        ]
    result = create_strategy_snapshot(
        request.strategy,
        params,
        watch_symbols=watch,
        discovery_symbols=discovery,
    )
    run_id = store.save_strategy_run(
        request.strategy,
        request.set,
        request.scope,
        "complete",
        result["data_as_of"],
        params,
        result,
    )
    return store.get_strategy_run(run_id)


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
    commission: float = 0.001,
    spread: float = 0.0002,
    slippage: float = 0.0005,
    cash_yield: float = 0.0,
):
    reserved = {
        "symbol", "strategy", "start", "end", "commission", "spread",
        "slippage", "cash_yield",
    }
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
    cost_values = {
        "commission": (commission, 0.0, 0.05),
        "spread": (spread, 0.0, 0.05),
        "slippage": (slippage, 0.0, 0.05),
        "cash_yield": (cash_yield, -0.2, 0.5),
    }
    for name, (value, lower, upper) in cost_values.items():
        if not math.isfinite(value) or not lower <= value <= upper:
            raise HTTPException(
                status_code=400,
                detail=f"{name} must be between {lower} and {upper}",
            )
    try:
        return backtest_payload(
            symbol,
            strategy,
            params=params,
            start=start,
            end=end,
            commission=commission,
            spread=spread,
            slippage=slippage,
            annual_cash_yield=cash_yield,
        )
    except KeyError:
        raise HTTPException(status_code=400, detail=f"unknown strategy: {strategy}")
    except RuntimeError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.get("/api/portfolio")
def portfolio(
    request: Request,
    strategy: str = "CTA Trend",
    set: str = "defaults",
    refresh: bool = False,
):
    """Historical shared-account replay for the locked ETF universe."""
    unknown = (
        {*request.query_params}
        - {"strategy", "set", "refresh"}
        - {*STRATEGY_PARAMS.get(strategy, {})}
    )
    if unknown:
        raise HTTPException(
            status_code=400, detail=f"unknown parameter: {sorted(unknown)[0]}"
        )
    raw = {
        key: value
        for key, value in request.query_params.items()
        if key not in {"strategy", "set", "refresh"}
    }
    parsed = _validated_strategy_params(strategy, raw)
    params = {
        key: value["default"] for key, value in STRATEGY_PARAMS[strategy].items()
    }
    if set != "defaults":
        if parsed:
            raise HTTPException(
                status_code=400,
                detail="saved set cannot be combined with parameter overrides",
            )
        saved = store.list_param_sets(strategy)
        chosen = next((row for row in saved if row["name"] == set), None)
        if chosen is None:
            raise HTTPException(status_code=404, detail=f"unknown param set: {set}")
        params.update(chosen["params"])
    params.update(parsed)
    cache_key = (strategy, set, tuple(sorted(params.items())))
    cached = _portfolio_cache.get(cache_key)
    if not refresh and cached and time.time() - cached["at"] < 60:
        return cached["data"]
    try:
        result = portfolio_payload(strategy, params)
        result["param_set"] = set
        _portfolio_cache[cache_key] = {"at": time.time(), "data": result}
        return result
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=503, detail=str(exc))


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
                "date": str(last["date"]),
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
