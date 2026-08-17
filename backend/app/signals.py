"""Daily signal scan for the Today view — raw-plus version.

State is still recomputed from recent bars (no persistent state machine yet —
see README design notes). "Since entry" P&L uses the last entry signal inside
the lookback window and executes at the NEXT open (NDO — no lookahead).
"""
import pandas as pd

from .store import load_recent_bars
from .strategies import STRATEGY_PARAMS
from .universe import XL_ETFS

LOOKBACK = 300  # bars needed to compute signals

# Default short watchlist for the Today view.
CORE_WATCHLIST = ["SPY", "QQQ", "MAGS", "SOXX", "IGV"] + XL_ETFS


def _rsi(close: pd.Series, period: int) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / period, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / period, adjust=False).mean()
    return 100 - 100 / (1 + gain / loss.replace(0, 1e-12))


def _last_entry_index(crossed: pd.Series) -> int | None:
    """Positional index of the most recent True in a boolean signal series."""
    for i in range(len(crossed) - 1, -1, -1):
        if bool(crossed.iloc[i]):
            return i
    return None


def _finish(result: dict, bars: pd.DataFrame, entry_index: int | None) -> dict:
    """Attach since-entry fields (entry executed at next open)."""
    if entry_index is not None and entry_index + 1 < len(bars):
        entry_price = float(bars["open"].iloc[entry_index + 1])
        result.update(
            {
                "entry_date": str(bars["date"].iloc[entry_index + 1]),
                "entry_price": round(entry_price, 2),
                "close": round(float(bars["close"].iloc[-1]), 2),
                "pnl_pct": round(
                    (float(bars["close"].iloc[-1]) / entry_price - 1) * 100, 2
                ),
            }
        )
    return result


def compute_signal(bars: pd.DataFrame, strategy_name: str, params: dict) -> dict | None:
    """bars: recent daily bars (ascending). Returns the signal for the last bar."""
    if len(bars) < 60:
        return None
    close = bars["close"]
    result = {"rank": round(float(close.iloc[-1] / close.iloc[-60] - 1) * 100, 2)}

    if strategy_name == "SMA Cross":
        n_fast = int(params.get("n_fast", 20))
        n_slow = int(params.get("n_slow", 50))
        fast = close.rolling(n_fast).mean()
        slow = close.rolling(n_slow).mean()
        up = fast > slow
        crossed_up = up & ~up.shift(1, fill_value=False)
        crossed_down = ~up & up.shift(1, fill_value=False)
        long_now = bool(up.iloc[-1])
        result["state"] = "long" if long_now else "flat"
        if bool(crossed_up.iloc[-1]):
            result["event"] = "entry"
            result["note"] = f"{n_fast}-day avg crossed ABOVE {n_slow}-day avg"
        elif bool(crossed_down.iloc[-1]):
            result["event"] = "exit"
            result["note"] = f"{n_fast}-day avg crossed BELOW {n_slow}-day avg"
        elif long_now:
            result["event"] = "none"
            result["note"] = f"uptrend: {n_fast}-day avg above {n_slow}-day avg"
        else:
            result["event"] = "none"
            result["note"] = f"flat: {n_fast}-day avg below {n_slow}-day avg"
        entry_index = _last_entry_index(crossed_up) if long_now else None

    elif strategy_name == "Donchian Trend":
        n_entry = int(params.get("n_entry", 55))
        upper = bars["high"].shift(1).rolling(n_entry).max()
        above = close > upper
        crossed = above & ~above.shift(1, fill_value=False)
        long_now = bool(above.iloc[-1])
        result["state"] = "long" if long_now else "flat"
        result["event"] = "entry" if bool(crossed.iloc[-1]) else "none"
        result["note"] = (
            f"closed above the {n_entry}-day high" if long_now else "no breakout"
        )
        entry_index = _last_entry_index(crossed) if long_now else None

    elif strategy_name == "RSI Reversion":
        period = int(params.get("period", 14))
        buy_below = int(params.get("buy_below", 30))
        rsi = _rsi(close, period)
        in_zone = rsi < buy_below
        crossed = in_zone & ~in_zone.shift(1, fill_value=False)
        long_now = bool(in_zone.iloc[-1])
        result["state"] = "long" if long_now else "flat"
        result["event"] = "entry" if bool(crossed.iloc[-1]) else "none"
        result["note"] = (
            f"RSI {rsi.iloc[-1]:.0f} in buy zone (<{buy_below})"
            if long_now
            else f"RSI {rsi.iloc[-1]:.0f} — no buy-zone signal"
        )
        entry_index = _last_entry_index(crossed) if long_now else None

    elif strategy_name == "S/R Bounce":
        n_window = int(params.get("n_window", 20))
        support = bars["low"].shift(1).rolling(n_window).min()
        resistance = bars["high"].shift(1).rolling(n_window).max()
        tested = (close > support) & (bars["low"] <= support)
        long_now = bool(close.iloc[-1] > support.iloc[-1])
        result["state"] = "long" if long_now else "flat"
        result["event"] = "entry" if bool(tested.iloc[-1]) else "none"
        result["note"] = (
            f"held {n_window}-day support at {support.iloc[-1]:.2f}"
            if long_now
            else f"below {n_window}-day support at {support.iloc[-1]:.2f}"
        )
        entry_index = _last_entry_index(tested) if long_now else None

    else:
        return None

    return _finish(result, bars, entry_index)


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
