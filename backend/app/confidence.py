"""Historical hit-rate confidence — per strategy.

Honest descriptive statistics over past signals, NOT probabilities:
- hit rate: % of past entry signals with a positive N-day forward return
- avg return: mean N-day forward return after a signal
- sample count: how many past signals (small samples = noise)

Two slices: all-time and the last 3 years (regimes change).

LOCAL COMPUTE SAFETY: the scan is sample-limited by default (few symbols,
few bars) so a laptop can compute it in milliseconds. The full-universe run
is opt-in (Strategy Lab trigger) and is meant for cloud compute.
"""
import time
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from .signals import _entry_series
from .store import latest_bar_date, list_symbols, load_bars, load_recent_bars
from .strategies import STRATEGY_PARAMS
from .universe import DEFAULT_BASKET

HORIZON = 20  # trading days of forward return
CACHE_TTL = 600  # seconds

DEFAULT_SAMPLE_DAYS = 252  # one trading year

_cache: dict = {}


def _summarize(returns: list[float]) -> dict:
    if not returns:
        return {"samples": 0, "hit_rate": None, "avg_return": None}
    series = pd.Series(returns).replace([np.inf, -np.inf], np.nan).dropna()
    if series.empty:
        return {"samples": 0, "hit_rate": None, "avg_return": None}
    return {
        "samples": int(len(series)),
        "hit_rate": round(float((series > 0).mean() * 100), 1),
        "avg_return": round(float(series.mean() * 100), 2),
    }


def _resolve_symbols(symbols: list[str] | None) -> list[str]:
    """Symbols to sample: the explicitly chosen list, or the deliberate
    liquid basket (16 explainable names). Never a blind random draw."""
    available = set(list_symbols())
    if symbols:
        return [s for s in symbols if s in available]
    return [s for s in DEFAULT_BASKET if s in available]


def compute_confidence(
    strategy_name: str,
    force: bool = False,
    symbols: list[str] | None = None,
    max_days: int = DEFAULT_SAMPLE_DAYS,
) -> dict:
    """Confidence stats for one strategy over a chosen symbol list + bar window.

    symbols=None -> the DEFAULT_BASKET. max_days <= 0 -> full history (heavy).
    """
    chosen = _resolve_symbols(symbols)
    key = f"{strategy_name}|{','.join(chosen)}|{max_days}"
    cached = _cache.get(key)
    data_date = latest_bar_date()
    # Date-aware cache: same bar count on a new day still recomputes.
    if not force and cached and cached["data"].get("data_date") == data_date:
        return cached["data"]

    params = {k: v["default"] for k, v in STRATEGY_PARAMS[strategy_name].items()}
    returns: list[float] = []
    dates: list[str] = []
    all_forward: list[float] = []  # every window -> market baseline

    for symbol in chosen:
        if max_days > 0:
            bars = load_recent_bars(symbol, max_days + HORIZON)
        else:
            bars = load_bars(symbol)  # full history — cloud only
        if len(bars) < 120:
            continue
        try:
            entries = _entry_series(bars, strategy_name, params)
        except Exception:
            continue
        forward = bars["close"].shift(-HORIZON) / bars["close"] - 1
        valid = forward.notna()
        all_forward.extend(forward[valid].astype(float).tolist())
        mask = entries & valid
        if not mask.any():
            continue
        returns.extend(forward[mask].astype(float).tolist())
        dates.extend(bars["date"][mask].astype(str).tolist())

    all_time = _summarize(returns)
    baseline = _summarize(all_forward)  # if baseline is high, any long works
    last_3y = {"samples": 0, "hit_rate": None, "avg_return": None}
    if dates:
        cutoff = (
            datetime.strptime(max(dates), "%Y-%m-%d") - timedelta(days=365 * 3)
        ).strftime("%Y-%m-%d")
        last_3y = _summarize([r for d, r in zip(dates, returns) if d >= cutoff])

    data = {
        "strategy": strategy_name,
        "horizon_days": HORIZON,
        "data_date": data_date,
        "sample": {
            "symbols": len(chosen),
            "names": chosen,
            "days": max_days if max_days > 0 else None,
        },
        "all_time": all_time,
        "last_3y": last_3y,
        "baseline": baseline,
    }
    _cache[key] = {"at": time.time(), "data": data}
    return data

