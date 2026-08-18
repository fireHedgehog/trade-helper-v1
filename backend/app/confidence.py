"""Historical post-signal statistics — per strategy.

Honest descriptive statistics over past signals, NOT probabilities:
- hit rate: % of past entry signals with a positive N-day forward return
- avg return: mean N-day forward return after a signal
- sample count: how many past signals (small samples = noise)

Two slices: the selected sample window and the last 3 years (when available).

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
MIN_SAMPLES = 30
BOOTSTRAP_ITERATIONS = 1_000

DEFAULT_SAMPLE_DAYS = 252  # one trading year

_cache: dict = {}


def clear_cache() -> None:
    """Discard derived statistics after underlying market data changes."""
    _cache.clear()


def _summarize(returns: list[float]) -> dict:
    if not returns:
        return {"samples": 0, "hit_rate": None, "avg_return": None,
                "hit_rate_ci95": None, "avg_return_ci95": None,
                "sufficient_sample": False, "warning": "fewer than 30 observations"}
    series = pd.Series(returns).replace([np.inf, -np.inf], np.nan).dropna()
    if series.empty:
        return {"samples": 0, "hit_rate": None, "avg_return": None,
                "hit_rate_ci95": None, "avg_return_ci95": None,
                "sufficient_sample": False, "warning": "fewer than 30 observations"}
    count = len(series)
    wins = int((series > 0).sum())
    proportion = wins / count
    z = 1.96
    denominator = 1 + z * z / count
    center = (proportion + z * z / (2 * count)) / denominator
    half = z * ((proportion * (1 - proportion) / count + z * z / (4 * count**2)) ** 0.5) / denominator
    mean = float(series.mean())
    mean_half = z * float(series.std(ddof=1)) / count**0.5 if count > 1 else 0.0
    return {
        "samples": int(count),
        "hit_rate": round(proportion * 100, 1),
        "avg_return": round(mean * 100, 2),
        "hit_rate_ci95": [round(max(0.0, center - half) * 100, 1),
                          round(min(1.0, center + half) * 100, 1)],
        "avg_return_ci95": [round((mean - mean_half) * 100, 2),
                            round((mean + mean_half) * 100, 2)],
        "sufficient_sample": count >= MIN_SAMPLES,
        "warning": None if count >= MIN_SAMPLES else "fewer than 30 observations",
    }


def _cluster_bootstrap_summary(observations: list[tuple[str, float]]) -> dict:
    """Bootstrap calendar-month clusters to retain contemporaneous outcomes.

    A month cluster contains every selected symbol observation whose signal fell
    in that month. Resampling clusters therefore does not pretend simultaneous
    symbol outcomes are independent. It remains an approximation, disclosed in
    the API methodology and ADR 0003.
    """
    summary = _summarize([value for _, value in observations])
    groups: dict[str, list[float]] = {}
    for date, value in observations:
        groups.setdefault(date[:7], []).append(float(value))
    clusters = list(groups.values())
    if len(clusters) < 3:
        summary["ci_method"] = "Wilson/normal fallback; fewer than 3 month clusters"
        return summary

    rng = np.random.default_rng(17_291)
    hit_rates: list[float] = []
    means: list[float] = []
    for _ in range(BOOTSTRAP_ITERATIONS):
        indexes = rng.integers(0, len(clusters), size=len(clusters))
        sample = [value for index in indexes for value in clusters[int(index)]]
        if sample:
            values = np.asarray(sample, dtype=float)
            hit_rates.append(float(np.mean(values > 0) * 100))
            means.append(float(np.mean(values) * 100))
    summary["hit_rate_ci95"] = [round(float(v), 1) for v in np.quantile(hit_rates, [0.025, 0.975])]
    summary["avg_return_ci95"] = [round(float(v), 2) for v in np.quantile(means, [0.025, 0.975])]
    summary["ci_method"] = f"calendar-month cluster bootstrap ({BOOTSTRAP_ITERATIONS} resamples)"
    return summary


def _non_overlapping_mask(entries: pd.Series, valid: pd.Series) -> pd.Series:
    """Keep signals at least one forward horizon apart within each symbol."""
    selected = pd.Series(False, index=entries.index)
    last = -HORIZON
    for position in range(len(entries)):
        if bool(entries.iloc[position]) and bool(valid.iloc[position]) and position - last >= HORIZON:
            selected.iloc[position] = True
            last = position
    return selected


def _resolve_symbols(symbols: list[str] | None) -> tuple[list[str], list[str]]:
    """Symbols to sample: the explicitly chosen list, or the deliberate
    liquid basket (16 explainable names). Never a blind random draw."""
    available = set(list_symbols())
    requested = symbols or DEFAULT_BASKET
    return (
        [symbol for symbol in requested if symbol in available],
        [symbol for symbol in requested if symbol not in available],
    )


def compute_confidence(
    strategy_name: str,
    force: bool = False,
    symbols: list[str] | None = None,
    max_days: int = DEFAULT_SAMPLE_DAYS,
) -> dict:
    """Confidence stats for one strategy over a chosen symbol list + bar window.

    symbols=None -> the DEFAULT_BASKET. max_days <= 0 -> full history (heavy).
    """
    chosen, missing = _resolve_symbols(symbols)
    key = f"{strategy_name}|{','.join(chosen)}|{max_days}"
    cached = _cache.get(key)
    data_date = latest_bar_date()
    # Date-aware cache: same bar count on a new day still recomputes.
    if not force and cached and cached["data"].get("data_date") == data_date:
        return cached["data"]

    params = {k: v["default"] for k, v in STRATEGY_PARAMS[strategy_name].items()}
    signal_observations: list[tuple[str, float]] = []
    baseline_observations: list[tuple[str, float]] = []
    failures: list[dict] = []
    sample_dates: list[str] = []

    for symbol in chosen:
        if max_days > 0:
            bars = load_recent_bars(symbol, max_days + HORIZON)
        else:
            bars = load_bars(symbol)  # full history — cloud only
        if len(bars) < 120:
            continue
        try:
            entries = _entry_series(bars, strategy_name, params)
        except Exception as exc:
            failures.append(
                {"symbol": symbol, "error": str(exc), "type": type(exc).__name__}
            )
            continue
        forward = bars["close"].shift(-HORIZON) / bars["close"] - 1
        valid = forward.notna()
        baseline_positions = [i for i in range(0, len(bars) - HORIZON, HORIZON)]
        for position in baseline_positions:
            value = forward.iloc[position]
            if pd.notna(value):
                baseline_observations.append((str(bars["date"].iloc[position]), float(value)))
        mask = _non_overlapping_mask(entries, valid)
        sample_dates.extend(bars["date"].astype(str).tolist())
        if not mask.any():
            continue
        signal_observations.extend(
            zip(bars["date"][mask].astype(str).tolist(), forward[mask].astype(float).tolist())
        )

    selected_window = _cluster_bootstrap_summary(signal_observations)
    baseline = _cluster_bootstrap_summary(baseline_observations)  # if high, any long works
    recent_3y = _summarize([])
    if signal_observations:
        cutoff = (
            datetime.strptime(max(date for date, _ in signal_observations), "%Y-%m-%d")
            - timedelta(days=365 * 3)
        ).strftime("%Y-%m-%d")
        recent_3y = _cluster_bootstrap_summary(
            [(date, value) for date, value in signal_observations if date >= cutoff]
        )

    data = {
        "strategy": strategy_name,
        "horizon_days": HORIZON,
        "data_date": data_date,
        "sample": {
            "symbols": len(chosen),
            "names": chosen,
            "days": max_days if max_days > 0 else None,
            "start": min(sample_dates) if sample_dates else None,
            "end": max(sample_dates) if sample_dates else None,
        },
        "coverage": {
            "requested": len(chosen) + len(missing),
            "processed": len(chosen) - len(failures),
            "missing": missing,
            "failed": failures,
        },
        "selected_window": selected_window,
        "recent_3y": recent_3y,
        # Backward-compatible aliases for older clients. These must not be
        # presented as all-time when max_days limits the selected window.
        "all_time": selected_window,
        "last_3y": recent_3y,
        "baseline": baseline,
        "methodology": {
            "outcome": "close-to-close forward return",
            "signals": "at least 20 trading bars apart within each symbol",
            "baseline": "every 20th eligible bar within each symbol",
            "costs_included": False,
            "probability": False,
            "minimum_sample_warning": MIN_SAMPLES,
            "ci_note": (
                "95% calendar-month cluster bootstrap intervals preserve "
                "contemporaneous cross-symbol outcomes; dependence across adjacent "
                "months and selection bias may remain"
            ),
        },
    }
    _cache[key] = {"at": time.time(), "data": data}
    return data
