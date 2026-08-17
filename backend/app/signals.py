"""Signals, ranking, and the simulated-position ledger.

- compute_signal(): stateless signal for the LAST bar of a window, with
  human-readable notes, an indicator snapshot, and a rule-based rank.
- scan(): Today-view scan across symbols.
- advance_positions()/positions_payload(): the paper ledger. One simulated
  position per symbol+strategy on the core watchlist, fixed 100 shares.
  Entries at the next open after a signal; exits on a 3×ATR trailing stop or
  a 2×ATR take-profit (whichever first). State persists in the `positions`
  table and advances whenever /api/today is fetched.
"""
import pandas as pd

from . import store
from .store import load_bars, load_recent_bars
from .strategies import STRATEGY_PARAMS
from .universe import XL_ETFS

LOOKBACK = 300  # bars needed to compute signals

# Default short watchlist for the Today view (order matters).
CORE_WATCHLIST = ["SPY", "QQQ", "MAGS", "SOXX", "IGV"] + XL_ETFS

POSITION_SHARES = 100
STOP_ATR_MULT = 3.0
TP_ATR_MULT = 2.0


def _rsi(close: pd.Series, period: int) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / period, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / period, adjust=False).mean()
    return 100 - 100 / (1 + gain / loss.replace(0, 1e-12))


def _atr(bars: pd.DataFrame, period: int) -> pd.Series:
    high, low, close = bars["high"], bars["low"], bars["close"]
    pc = close.shift(1)
    tr = pd.concat([high - low, (high - pc).abs(), (low - pc).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / period, adjust=False).mean()


def _rule_rank(bars: pd.DataFrame) -> tuple[float, str]:
    """Rule-agreement rank: momentum + trend rules + volatility penalty.
    Honest label: it is a score, not a probability."""
    close = bars["close"]
    momentum = float(close.iloc[-1] / close.iloc[-60] - 1) * 100
    trend = 0
    if len(bars) >= 50 and float(close.iloc[-1]) > float(close.rolling(50).mean().iloc[-1]):
        trend += 20
    if len(bars) >= 200:
        trend += 20 if float(close.iloc[-1]) > float(close.rolling(200).mean().iloc[-1]) else -20
    wild = 0
    atr = _atr(bars, 14)
    if len(atr) and float(atr.iloc[-1]) / float(close.iloc[-1]) > 0.06:
        wild = -10
    rank = round(momentum + trend + wild, 1)
    return rank, f"mom {momentum:+.0f}% · trend {trend:+d} · vol {wild:+d}"


def _entry_series(bars: pd.DataFrame, strategy_name: str, params: dict) -> pd.Series:
    """Boolean series: True on bars where an entry signal fires."""
    close = bars["close"]
    if strategy_name == "SMA Cross":
        nf, ns = int(params.get("n_fast", 20)), int(params.get("n_slow", 50))
        up = close.rolling(nf).mean() > close.rolling(ns).mean()
        return up & ~up.shift(1, fill_value=False)
    if strategy_name == "Donchian Trend":
        upper = bars["high"].shift(1).rolling(int(params.get("n_entry", 55))).max()
        above = close > upper
        return above & ~above.shift(1, fill_value=False)
    if strategy_name == "S/R Bounce":
        support = bars["low"].shift(1).rolling(int(params.get("n_window", 20))).min()
        return (close > support) & (bars["low"] <= support)
    if strategy_name == "Fib Retrace":
        h = bars["high"].shift(1).rolling(int(params.get("n_swing", 60))).max()
        l = bars["low"].shift(1).rolling(int(params.get("m_pullback", 10))).min()
        level = l + float(params.get("fib", 0.618)) * (h - l)
        return (h > l) & (close > level) & (close.shift(1) <= level.shift(1))
    if strategy_name == "Wave Pull":
        impulse = (
            close / close.shift(int(params.get("impulse_bars", 8))) - 1
            >= float(params.get("impulse_pct", 6.0)) / 100
        )
        breakout = bars["high"].shift(1).rolling(int(params.get("pullback_bars", 3))).max()
        return impulse & (close > breakout)
    if strategy_name == "RSI Reversion":
        in_zone = _rsi(close, int(params.get("period", 14))) < int(params.get("buy_below", 30))
        return in_zone & ~in_zone.shift(1, fill_value=False)
    return pd.Series(False, index=bars.index)


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
    """Signal for the LAST bar, with note, indicators and rule rank."""
    if len(bars) < 60:
        return None
    close = bars["close"]
    rank, rank_note = _rule_rank(bars)
    result = {"rank": rank, "rank_note": rank_note}
    entry_index = None

    if strategy_name == "SMA Cross":
        nf, ns = int(params.get("n_fast", 20)), int(params.get("n_slow", 50))
        fast = close.rolling(nf).mean()
        slow = close.rolling(ns).mean()
        up = fast > slow
        crossed_up = up & ~up.shift(1, fill_value=False)
        crossed_down = ~up & up.shift(1, fill_value=False)
        long_now = bool(up.iloc[-1])
        result["state"] = "long" if long_now else "flat"
        if bool(crossed_up.iloc[-1]):
            result["event"] = "entry"
            result["note"] = f"{nf}-day avg crossed ABOVE {ns}-day avg"
        elif bool(crossed_down.iloc[-1]):
            result["event"] = "exit"
            result["note"] = f"{nf}-day avg crossed BELOW {ns}-day avg"
        elif long_now:
            result["event"] = "none"
            result["note"] = f"uptrend: {nf}-day avg above {ns}-day avg"
        else:
            result["event"] = "none"
            result["note"] = f"flat: {nf}-day avg below {ns}-day avg"
        result["indicators"] = {
            f"SMA {nf}": round(float(fast.iloc[-1]), 2),
            f"SMA {ns}": round(float(slow.iloc[-1]), 2),
        }
        entry_index = _last_entry_index(crossed_up) if long_now else None

    elif strategy_name == "Donchian Trend":
        n_entry = int(params.get("n_entry", 55))
        n_exit = int(params.get("n_exit", 20))
        upper = bars["high"].shift(1).rolling(n_entry).max()
        lower = bars["low"].shift(1).rolling(n_exit).min()
        above = close > upper
        crossed = above & ~above.shift(1, fill_value=False)
        long_now = bool(above.iloc[-1])
        result["state"] = "long" if long_now else "flat"
        result["event"] = "entry" if bool(crossed.iloc[-1]) else "none"
        result["note"] = f"closed above the {n_entry}-day high" if long_now else "no breakout"
        result["indicators"] = {
            f"{n_entry}-day high": round(float(upper.iloc[-1]), 2),
            f"{n_exit}-day low": round(float(lower.iloc[-1]), 2),
        }
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
            f"held {n_window}-day support at {support.iloc[-1]:.2f}" if long_now
            else f"below {n_window}-day support at {support.iloc[-1]:.2f}"
        )
        result["indicators"] = {
            f"{n_window}-day support": round(float(support.iloc[-1]), 2),
            f"{n_window}-day resistance": round(float(resistance.iloc[-1]), 2),
        }
        entry_index = _last_entry_index(tested) if long_now else None

    elif strategy_name == "Fib Retrace":
        h = bars["high"].shift(1).rolling(int(params.get("n_swing", 60))).max()
        l = bars["low"].shift(1).rolling(int(params.get("m_pullback", 10))).min()
        fib = float(params.get("fib", 0.618))
        level = l + fib * (h - l)
        crossed = (h > l) & (close > level) & (close.shift(1) <= level.shift(1))
        long_now = bool((h.iloc[-1] > l.iloc[-1]) and close.iloc[-1] > level.iloc[-1])
        result["state"] = "long" if long_now else "flat"
        result["event"] = "entry" if bool(crossed.iloc[-1]) else "none"
        result["note"] = (
            f"above the {fib:.2f} retrace at {level.iloc[-1]:.2f}" if long_now
            else f"below the {fib:.2f} retrace at {level.iloc[-1]:.2f}"
        )
        result["indicators"] = {
            "swing high": round(float(h.iloc[-1]), 2),
            "pullback low": round(float(l.iloc[-1]), 2),
            f"fib {fib:.2f} level": round(float(level.iloc[-1]), 2),
        }
        entry_index = _last_entry_index(crossed) if long_now else None

    elif strategy_name == "Wave Pull":
        impulse_bars = int(params.get("impulse_bars", 8))
        impulse_pct = float(params.get("impulse_pct", 6.0))
        impulse = (
            close / close.shift(impulse_bars) - 1 >= impulse_pct / 100
        )
        breakout = bars["high"].shift(1).rolling(int(params.get("pullback_bars", 3))).max()
        pullback_low = bars["low"].shift(1).rolling(int(params.get("pullback_bars", 3))).min()
        crossed = impulse & (close > breakout)
        long_now = bool(impulse.iloc[-1] and close.iloc[-1] > breakout.iloc[-1])
        result["state"] = "long" if long_now else "flat"
        result["event"] = "entry" if bool(crossed.iloc[-1]) else "none"
        moved_pct = (float(close.iloc[-1]) / float(close.iloc[-1 - impulse_bars]) - 1) * 100
        result["note"] = (
            f"impulse +{moved_pct:.1f}% in {impulse_bars} days, then breakout"
            if long_now else "no impulse-pullback setup"
        )
        result["indicators"] = {
            "pullback high": round(float(breakout.iloc[-1]), 2),
            "pullback low": round(float(pullback_low.iloc[-1]), 2),
        }
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
            f"RSI {rsi.iloc[-1]:.0f} in buy zone (<{buy_below})" if long_now
            else f"RSI {rsi.iloc[-1]:.0f} — no buy-zone signal"
        )
        result["indicators"] = {"RSI": round(float(rsi.iloc[-1]), 1)}
        entry_index = _last_entry_index(crossed) if long_now else None

    else:
        return None

    return _finish(result, bars, entry_index)


def scan(strategy_name: str, symbols: list[str], params: dict | None = None) -> dict:
    """Scan all symbols for today's entries/exits/holdings."""
    if params is None:
        params = {key: value["default"] for key, value in STRATEGY_PARAMS[strategy_name].items()}
    rows = []
    for symbol in symbols:
        bars = load_recent_bars(symbol, LOOKBACK)
        if bars.empty:
            continue
        try:
            signal = compute_signal(bars, strategy_name, params)
        except Exception:
            continue
        if signal is not None:
            rows.append({"symbol": symbol, **signal})
    entries = sorted((r for r in rows if r["event"] == "entry"), key=lambda r: -r["rank"])
    exits = sorted((r for r in rows if r["event"] == "exit"), key=lambda r: -r["rank"])
    holding = sorted((r for r in rows if r["state"] == "long"), key=lambda r: -r["rank"])
    return {"entries": entries, "exits": exits, "holding": holding, "scanned": len(rows)}


# ---------------------------------------------------------------------------
# Simulated-position ledger (state machine) — core watchlist only for now.
# ---------------------------------------------------------------------------

def _default_params(strategy_name: str) -> dict:
    return {key: value["default"] for key, value in STRATEGY_PARAMS[strategy_name].items()}


def _new_position_from_window(bars: pd.DataFrame, strategy_name: str, params: dict) -> dict | None:
    """Initial state for a symbol with no ledger row yet (first run)."""
    signal = compute_signal(bars.tail(LOOKBACK), strategy_name, params)
    if signal is None:
        return None
    if signal["state"] == "long":
        window = bars.tail(LOOKBACK)
        idx = _last_entry_index(_entry_series(window, strategy_name, params))
        if idx is not None and idx + 1 < len(window):
            entry_price = float(window["open"].iloc[idx + 1])
            atr = float(_atr(window, 14).iloc[idx + 1])
            return {
                "state": "long",
                "entry_date": str(window["date"].iloc[idx + 1]),
                "entry_price": round(entry_price, 2),
                "stop": round(entry_price - STOP_ATR_MULT * atr, 2),
                "tp": round(entry_price + TP_ATR_MULT * atr, 2),
            }
    if signal["event"] == "entry":
        return {"state": "entry_pending", "entry_date": None, "entry_price": None,
                "stop": None, "tp": None}
    return None


def advance_positions(strategy_name: str, params: dict | None = None, set_name: str = "defaults") -> None:
    """Advance the core-watchlist ledger to the latest bar (idempotent per day)."""
    if params is None:
        params = _default_params(strategy_name)
    for symbol in CORE_WATCHLIST:
        bars = load_bars(symbol)
        if bars.empty:
            continue
        latest_date = str(bars["date"].iloc[-1])
        row = store.get_position(symbol, strategy_name, set_name)
        if row is None:
            new = _new_position_from_window(bars, strategy_name, params)
            if new:
                # Replay from the entry date so exits (stop/TP) that happened
                # between entry and now are simulated, not skipped.
                updated = new["entry_date"] if new["state"] == "long" else latest_date
                store.save_position(symbol, strategy_name, new, updated, set_name)
                row = store.get_position(symbol, strategy_name, set_name)
            else:
                continue
        if row["updated"] >= latest_date:
            continue
        state = {
            "state": row["state"], "entry_date": row["entry_date"],
            "entry_price": row["entry_price"], "stop": row["stop"], "tp": row["tp"],
        }
        for i in bars.index[bars["date"] > row["updated"]]:
            window = bars.iloc[max(0, i + 1 - LOOKBACK): i + 1]
            signal = compute_signal(window, strategy_name, params)
            if signal is None:
                continue
            open_px = float(bars["open"].iloc[i])
            close_px = float(bars["close"].iloc[i])
            atr_px = None
            if i >= 14:
                atr_px = float(_atr(bars.iloc[max(0, i + 1 - 60): i + 1], 14).iloc[-1])
            if state["state"] == "flat":
                if signal["event"] == "entry":
                    state = {"state": "entry_pending", "entry_date": None,
                             "entry_price": None, "stop": None, "tp": None}
            elif state["state"] == "entry_pending":
                state = {
                    "state": "long",
                    "entry_date": str(bars["date"].iloc[i]),
                    "entry_price": round(open_px, 2),
                    "stop": round(open_px - STOP_ATR_MULT * atr_px, 2) if atr_px else None,
                    "tp": round(open_px + TP_ATR_MULT * atr_px, 2) if atr_px else None,
                }
            elif state["state"] == "long":
                if atr_px and state["stop"] is not None:
                    state["stop"] = round(max(state["stop"], close_px - STOP_ATR_MULT * atr_px), 2)
                if state["stop"] is not None and close_px < state["stop"]:
                    state = {"state": "flat", "entry_date": None, "entry_price": None,
                             "stop": None, "tp": None}
                elif state["tp"] is not None and close_px >= state["tp"]:
                    state = {"state": "flat", "entry_date": None, "entry_price": None,
                             "stop": None, "tp": None}
        if state["state"] == "flat":
            store.delete_position(symbol, strategy_name, set_name)
        else:
            store.save_position(symbol, strategy_name, state, latest_date, set_name)


def positions_payload(strategy_name: str, set_name: str = "defaults") -> list[dict]:
    """The ledger for display: every core symbol in order; nulls where flat."""
    rows = []
    for symbol in CORE_WATCHLIST:
        row = store.get_position(symbol, strategy_name, set_name)
        if not row or row["state"] == "flat":
            rows.append({"symbol": symbol, "state": "flat"})
            continue
        bars = load_bars(symbol)
        if bars.empty:
            rows.append({"symbol": symbol, "state": "flat"})
            continue
        now = round(float(bars["close"].iloc[-1]), 2)
        item = {
            "symbol": symbol,
            "state": row["state"],
            "since": row["entry_date"],
            "entry": row["entry_price"],
            "now": now,
            "stop": row["stop"],
            "tp": row["tp"],
            "note": "entry pending → next open" if row["state"] == "entry_pending" else "",
        }
        if row["state"] == "long" and row["entry_price"]:
            pnl_pct = round((now / row["entry_price"] - 1) * 100, 2)
            item["pnl_pct"] = pnl_pct
            item["pnl_usd"] = round(POSITION_SHARES * (now - row["entry_price"]), 2)
        rows.append(item)
    return rows

