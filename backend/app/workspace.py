"""Explicit, persistent strategy workspace snapshots.

Opening a UI view must never trigger a scan. This module performs a scan only
when an action endpoint calls it, then stores a compact immutable snapshot that
later menu visits can read from SQLite immediately.
"""

from __future__ import annotations

from . import store
from .execution import simulate
from .signals import LOOKBACK, compute_signal


def _last_entry(replay) -> dict | None:
    position = replay.position
    if position.entry_date:
        return {
            "date": position.entry_date,
            "price": round(float(position.entry_price), 2),
        }
    if replay.trades:
        trade = replay.trades[-1]
        return {
            "date": trade["entry_date"],
            "price": round(float(trade["entry_price"]), 2),
        }
    return None


def _last_exit(replay) -> dict | None:
    if not replay.last_exit:
        return None
    return {
        "date": replay.last_exit["exit_date"],
        "price": round(float(replay.last_exit["exit_price"]), 2),
        "reason": replay.last_exit["exit_reason"],
        "return_pct": round(float(replay.last_exit["return_pct"]), 2),
    }


def _position_label(state: str, has_exit: bool) -> tuple[str, str]:
    if state == "long":
        return "holding", "hold"
    if state == "exit_pending":
        return "holding · exit pending", "exit next available open"
    if state == "entry_pending":
        return "entry pending", "enter next available open"
    if has_exit:
        return "exited", "observe"
    return "flat · never entered", "observe"


def create_strategy_snapshot(
    strategy: str,
    params: dict,
    *,
    watch_symbols: list[str],
    discovery_symbols: list[str],
) -> dict:
    """Evaluate declared symbols once and return user-owned and discovered views."""
    requested = list(dict.fromkeys(watch_symbols + discovery_symbols))
    watched = set(watch_symbols)
    rows: list[dict] = []
    missing: list[str] = []
    failed: list[dict] = []
    for symbol in requested:
        bars = store.load_bars(symbol)
        if bars.empty:
            missing.append(symbol)
            continue
        try:
            signal = compute_signal(
                bars.tail(max(LOOKBACK, 500)).reset_index(drop=True),
                strategy,
                params,
            )
            if signal is None:
                failed.append({"symbol": symbol, "error": "not enough history"})
                continue
            replay = simulate(bars, strategy, params)
        except Exception as exc:
            failed.append(
                {"symbol": symbol, "error": str(exc), "type": type(exc).__name__}
            )
            continue
        position = replay.position
        last_entry = _last_entry(replay)
        last_exit = _last_exit(replay)
        status, next_action = _position_label(position.state, last_exit is not None)
        rows.append(
            {
                "symbol": symbol,
                "watched": symbol in watched,
                "data_as_of": str(bars["date"].iloc[-1]),
                "close": round(float(bars["close"].iloc[-1]), 2),
                "state": position.state,
                "status": status,
                "next_action": next_action,
                "event": replay.last_event,
                "note": (
                    f"position open since {position.entry_date}; no exit signal"
                    if position.state == "long"
                    else signal["note"]
                ),
                "rank": signal["rank"],
                "rank_note": signal["rank_note"],
                "entry_date": position.entry_date,
                "entry_price": (
                    round(float(position.entry_price), 2)
                    if position.entry_price is not None
                    else None
                ),
                "stop": (
                    round(float(position.stop), 2)
                    if position.stop is not None
                    else None
                ),
                "last_entry": last_entry,
                "last_exit": last_exit,
            }
        )
    by_symbol = {row["symbol"]: row for row in rows}
    watch_rows = [
        by_symbol.get(
            symbol,
            {
                "symbol": symbol,
                "watched": True,
                "state": "unavailable",
                "status": "unavailable",
                "next_action": "review data failure",
                "note": "No completed snapshot result",
                "last_entry": None,
                "last_exit": None,
            },
        )
        for symbol in watch_symbols
    ]
    ranked = sorted(rows, key=lambda row: (-row["rank"], row["symbol"]))
    entry_candidates = [row for row in ranked if row["state"] == "entry_pending"]
    return {
        "data_as_of": max(
            (row["data_as_of"] for row in rows),
            default=None,
        ),
        "watchlist": watch_rows,
        "entry_candidates": entry_candidates,
        "ranked": ranked[:50],
        "coverage": {
            "requested": len(requested),
            "processed": len(rows),
            "missing": missing,
            "failed": failed,
        },
        "ranking_warning": (
            "Rule-agreement rank is a descriptive heuristic, not a validated "
            "probability or permission to trade."
        ),
    }
