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

import pandas as pd

from .signals import CORE_WATCHLIST, _entry_series
from .store import list_symbols, load_bars, load_recent_bars
from .strategies import STRATEGY_PARAMS

HORIZON = 20  # trading days of forward return
CACHE_TTL = 600  # seconds

# Local-friendly defaults — README says never raise these on a laptop.
DEFAULT_SAMPLE_SYMBOLS = 5
DEFAULT_SAMPLE_DAYS = 252  # one trading year

_cache: dict = {}


def _summarize(returns: list[float]) -> dict:
    if not returns:
        return {"samples": 0, "hit_rate": None, "avg_return": None}
    series = pd.Series(returns)
    return {
        "samples": int(len(series)),
        "hit_rate": round(float((series > 0).mean() * 100), 1),
        "avg_return": round(float(series.mean() * 100), 2),
    }


def _ordered_symbols(limit: int) -> list[str]:
    symbols = list_symbols()
    core = [s for s in CORE_WATCHLIST if s in symbols]
    rest = [s for s in symbols if s not in CORE_WATCHLIST]
    return (core + rest)[:limit]


def compute_confidence(
    strategy_name: str,
    force: bool = False,
    max_symbols: int = DEFAULT_SAMPLE_SYMBOLS,
    max_days: int = DEFAULT_SAMPLE_DAYS,
) -> dict:
    """Confidence stats for one strategy, over a sample-limited symbol/bars set.

    max_symbols <= 0 -> all symbols. max_days <= 0 -> full history.
    """
    key = f"{strategy_name}|{max_symbols}|{max_days}"
    cached = _cache.get(key)
    if not force and cached and time.time() - cached["at"] < CACHE_TTL:
        return cached["data"]

    symbols = list_symbols() if max_symbols <= 0 else _ordered_symbols(max_symbols)
    params = {k: v["default"] for k, v in STRATEGY_PARAMS[strategy_name].items()}
    returns: list[float] = []
    dates: list[str] = []

    for symbol in symbols:
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
        mask = entries & forward.notna()
        if not mask.any():
            continue
        returns.extend(forward[mask].astype(float).tolist())
        dates.extend(bars["date"][mask].astype(str).tolist())

    all_time = _summarize(returns)
    last_3y = {"samples": 0, "hit_rate": None, "avg_return": None}
    if dates:
        cutoff = (
            datetime.strptime(max(dates), "%Y-%m-%d") - timedelta(days=365 * 3)
        ).strftime("%Y-%m-%d")
        last_3y = _summarize([r for d, r in zip(dates, returns) if d >= cutoff])

    data = {
        "strategy": strategy_name,
        "horizon_days": HORIZON,
        "sample": {
            "symbols": len(symbols),
            "days": max_days if max_days > 0 else None,
        },
        "all_time": all_time,
        "last_3y": last_3y,
    }
    _cache[key] = {"at": time.time(), "data": data}
    return data

