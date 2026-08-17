"""Daily signal scan for the Today view — raw first version.

What this IS:
- A stateless scan: compute each strategy's signal on the last bars of every
  fetched symbol, and return today's entries / exits / holdings.

What this is NOT (yet — see README design notes):
- A state machine with persistent per-symbol trade state (entry/exit/hold).
- A rule-based multi-factor rank / confidence score. The "rank" here is a
  12-week momentum placeholder, honestly labeled as such.
- Aware of saved/tuned param sets.
"""
import pandas as pd

from .store import load_recent_bars
from .strategies import STRATEGY_PARAMS

LOOKBACK = 300  # bars needed to compute signals


def _rsi(close: pd.Series, period: int) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / period, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / period, adjust=False).mean()
    return 100 - 100 / (1 + gain / loss.replace(0, 1e-12))


def compute_signal(bars: pd.DataFrame, strategy_name: str, params: dict) -> dict | None:
    """bars: recent daily bars (ascending). Returns the signal for the last bar."""
    if len(bars) < 60:
        return None
    close = bars["close"]
    rank = round(float(close.iloc[-1] / close.iloc[-60] - 1) * 100, 2)  # momentum placeholder

    if strategy_name == "SMA Cross":
        fast = close.rolling(int(params.get("n_fast", 20))).mean()
        slow = close.rolling(int(params.get("n_slow", 50))).mean()
        state = "long" if fast.iloc[-1] > slow.iloc[-1] else "flat"
        crossed_up = fast.iloc[-1] > slow.iloc[-1] and fast.iloc[-2] <= slow.iloc[-2]
        crossed_down = fast.iloc[-1] < slow.iloc[-1] and fast.iloc[-2] >= slow.iloc[-2]
        event = "entry" if crossed_up else ("exit" if crossed_down else "none")
        note = f"fast {fast.iloc[-1]:.2f} vs slow {slow.iloc[-1]:.2f}"

    elif strategy_name == "Donchian Trend":
        n_entry = int(params.get("n_entry", 55))
        upper = bars["high"].shift(1).rolling(n_entry).max()
        state = "long" if close.iloc[-1] > upper.iloc[-1] else "flat"
        crossed = close.iloc[-1] > upper.iloc[-1] and close.iloc[-2] <= upper.iloc[-2]
        event = "entry" if crossed else "none"
        note = f"close {close.iloc[-1]:.2f} vs {n_entry}d high {upper.iloc[-1]:.2f}"

    elif strategy_name == "RSI Reversion":
        rsi = _rsi(close, int(params.get("period", 14)))
        buy_below = int(params.get("buy_below", 30))
        state = "long" if rsi.iloc[-1] < buy_below else "flat"
        crossed = rsi.iloc[-1] < buy_below and rsi.iloc[-2] >= buy_below
        event = "entry" if crossed else "none"
        note = f"RSI {rsi.iloc[-1]:.1f} vs buy zone {buy_below}"

    else:
        return None

    return {"state": state, "event": event, "rank": rank, "note": note}


def scan(strategy_name: str, symbols: list[str]) -> dict:
    """Scan all symbols for today's entries/exits/holdings."""
    params = {
        key: value["default"] for key, value in STRATEGY_PARAMS[strategy_name].items()
    }
    rows = []
    for symbol in symbols:
        bars = load_recent_bars(symbol, LOOKBACK)
        if bars.empty:
            continue
        try:
            signal = compute_signal(bars, strategy_name, params)
        except Exception:
            continue  # one broken symbol must not kill the scan
        if signal is not None:
            rows.append({"symbol": symbol, **signal})

    entries = sorted((r for r in rows if r["event"] == "entry"), key=lambda r: -r["rank"])
    exits = sorted((r for r in rows if r["event"] == "exit"), key=lambda r: -r["rank"])
    holding = sorted((r for r in rows if r["state"] == "long"), key=lambda r: -r["rank"])
    return {
        "entries": entries,
        "exits": exits,
        "holding": holding,
        "scanned": len(rows),
    }
