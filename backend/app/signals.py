"""Signals, ranking, and the simulated-position ledger.

- compute_signal(): stateless signal for the LAST bar of a window, with
  human-readable notes, an indicator snapshot, and a rule-based rank.
- scan(): Today-view scan across symbols.
- advance_positions()/positions_payload(): the model ledger. One simulated
  position per symbol+strategy on the core watchlist, fixed 100 shares. Entry,
  strategy exits, configured stops, and targets use the canonical next-open
  engine. State persists in `positions` and refreshes with /api/today.
"""
import pandas as pd

from . import store
from .execution import simulate
from .rules import atr as canonical_atr
from .rules import build_rules
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
    return canonical_atr(bars, period)


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
    return build_rules(bars, strategy_name, params).entries


def _exit_series(bars: pd.DataFrame, strategy_name: str, params: dict) -> pd.Series:
    """Boolean series: True on bars where the strategy's OWN exit rule fires
    ("trend changed"). Complements the generic ATR stop / take-profit."""
    return build_rules(bars, strategy_name, params).exits


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

    elif strategy_name == "CTA Trend":
        n_entry = int(params.get("n_entry", 100))
        n_exit = int(params.get("n_exit", 40))
        trend_ma = int(params.get("trend_ma", 100))
        upper = bars["high"].shift(1).rolling(n_entry).max()
        lower = bars["low"].shift(1).rolling(n_exit).min()
        trend = close.rolling(trend_ma).mean()
        up = (close > upper) & (close > trend)
        crossed = up & ~up.shift(1, fill_value=False)
        exited = (close < lower) & ~(close < lower).shift(1, fill_value=False)
        long_now = bool(up.iloc[-1])
        result["state"] = "long" if long_now else "flat"
        if bool(crossed.iloc[-1]):
            result["event"] = "entry"
            result["note"] = f"new {n_entry}-day high above the {trend_ma}-day trend"
        elif bool(exited.iloc[-1]):
            result["event"] = "exit"
            result["note"] = f"closed below the {n_exit}-day low — trend changed"
        elif long_now:
            result["event"] = "none"
            result["note"] = f"trend on: above the {n_entry}-day high and the {trend_ma}-day average"
        else:
            result["event"] = "none"
            result["note"] = "no trend setup"
        result["indicators"] = {
            f"{n_entry}-day high": round(float(upper.iloc[-1]), 2) if pd.notna(upper.iloc[-1]) else None,
            f"{n_exit}-day low": round(float(lower.iloc[-1]), 2) if pd.notna(lower.iloc[-1]) else None,
            f"SMA {trend_ma}": round(float(trend.iloc[-1]), 2) if pd.notna(trend.iloc[-1]) else None,
        }
        entry_index = _last_entry_index(crossed) if long_now else None

    else:
        return None

    return _finish(result, bars, entry_index)


def compute_stateful_signal(
    bars: pd.DataFrame, strategy_name: str, params: dict
) -> dict | None:
    """Latest display signal backed by the canonical full-history position."""
    recent = bars.tail(max(LOOKBACK, 500)).reset_index(drop=True)
    signal = compute_signal(recent, strategy_name, params)
    if signal is None:
        return None
    replay = simulate(bars, strategy_name, params)
    state = replay.position.state
    signal["event"] = replay.last_event
    signal["state"] = "long" if state in {"long", "exit_pending"} else "flat"
    if state == "entry_pending":
        signal["note"] = "entry signal confirmed — order pending for next open"
    elif state == "exit_pending":
        signal["note"] = (
            f"exit signal confirmed ({replay.position.pending_reason}) — "
            "order pending for next open"
        )
    elif state == "long":
        signal["note"] = (
            f"position open since {replay.position.entry_date}; no exit signal"
        )
    if state in {"long", "exit_pending"} and replay.position.entry_price:
        signal.update(
            {
                "entry_date": replay.position.entry_date,
                "entry_price": round(replay.position.entry_price, 2),
                "close": round(float(bars["close"].iloc[-1]), 2),
                "pnl_pct": round(
                    (float(bars["close"].iloc[-1]) / replay.position.entry_price - 1)
                    * 100,
                    2,
                ),
            }
        )
    return signal


def scan(strategy_name: str, symbols: list[str], params: dict | None = None) -> dict:
    """Scan symbols using the same full-history state machine as the backtest."""
    if params is None:
        params = {key: value["default"] for key, value in STRATEGY_PARAMS[strategy_name].items()}
    rows = []
    for symbol in symbols:
        bars = load_bars(symbol)
        if bars.empty:
            continue
        try:
            signal = compute_stateful_signal(bars, strategy_name, params)
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


def _closed_position(state: dict, date_str: str, close_px: float, reason: str) -> dict:
    """Record the last exit (date, price, reason, realized P&L) and go flat."""
    entry_px = state.get("entry_price")
    pnl_pct = round((close_px / entry_px - 1) * 100, 2) if entry_px else None
    pnl_usd = round(POSITION_SHARES * (close_px - entry_px), 2) if entry_px else None
    return {
        "state": "flat",
        "entry_date": None, "entry_price": None, "stop": None, "tp": None,
        "exit_date": date_str,
        "exit_price": round(close_px, 2),
        "exit_reason": reason,
        "exit_pnl_pct": pnl_pct,
        "exit_pnl_usd": pnl_usd,
    }


def _replay_ledger(bars: pd.DataFrame, strategy_name: str, params: dict) -> dict:
    """Compatibility payload backed by the canonical execution simulation."""
    replay = simulate(
        bars,
        strategy_name,
        params,
        fixed_shares=POSITION_SHARES,
    )
    position = replay.position
    state = {
        "state": position.state,
        "entry_date": position.entry_date,
        "entry_price": round(position.entry_price, 2) if position.entry_price else None,
        "stop": round(position.stop, 2) if position.stop is not None else None,
        "tp": round(position.target, 2) if position.target is not None else None,
        "exit_date": None,
        "exit_price": None,
        "exit_reason": None,
        "exit_pnl_pct": None,
        "exit_pnl_usd": None,
    }
    if replay.last_exit:
        last = replay.last_exit
        state.update(
            {
                "exit_date": last["exit_date"],
                "exit_price": round(last["exit_price"], 2),
                "exit_reason": "trend" if last["exit_reason"] == "strategy" else last["exit_reason"],
                "exit_pnl_pct": round(last["return_pct"], 2),
                "exit_pnl_usd": round(last["pnl"], 2),
            }
        )
    return state


def advance_positions(strategy_name: str, params: dict | None = None, set_name: str = "defaults") -> None:
    """Replay the paper ledger for the core watchlist from full history.

    Deterministic and idempotent: signals at a completed close fill at the next
    available open. The latest realized exit is kept so a flat row shows why.
    """
    if params is None:
        params = _default_params(strategy_name)
    for symbol in CORE_WATCHLIST:
        bars = load_bars(symbol)
        if bars.empty:
            continue
        state = _replay_ledger(bars, strategy_name, params)
        store.save_position(symbol, strategy_name, state, str(bars["date"].iloc[-1]), set_name)


def _trend_exit_info(bars: pd.DataFrame, strategy_name: str, params: dict) -> dict:
    """Current strategy-exit trigger for display: label, level, and the rule
    in plain words (used by the Today exit-plan column)."""
    close = bars["close"]
    if strategy_name == "SMA Cross":
        return {"label": "cross", "level": None,
                "why": "fast average crosses below the slow average → trend changed"}
    if strategy_name in ("Donchian Trend", "CTA Trend"):
        n_exit = int(params.get("n_exit", 40 if strategy_name == "CTA Trend" else 20))
        low = bars["low"].shift(1).rolling(n_exit).min().iloc[-1]
        return {"label": "trend", "level": round(float(low), 2) if pd.notna(low) else None,
                "why": f"close below the {n_exit}-day low → trend changed"}
    if strategy_name == "S/R Bounce":
        support = bars["low"].shift(1).rolling(int(params.get("n_window", 20))).min().iloc[-1]
        return {"label": "support", "level": round(float(support), 2) if pd.notna(support) else None,
                "why": "close below support → trend changed"}
    if strategy_name in ("Fib Retrace", "Wave Pull"):
        n = int(params.get("m_pullback", 10)) if strategy_name == "Fib Retrace" \
            else int(params.get("pullback_bars", 3))
        low = bars["low"].shift(1).rolling(n).min().iloc[-1]
        return {"label": "pullback", "level": round(float(low), 2) if pd.notna(low) else None,
                "why": "close below the pullback low → trend changed"}
    if strategy_name == "RSI Reversion":
        sell = int(params.get("sell_above", 70))
        return {"label": "RSI", "level": sell,
                "why": f"RSI recovers above {sell} → exit"}
    return {"label": None, "level": None, "why": ""}


def positions_payload(strategy_name: str, set_name: str = "defaults", params: dict | None = None) -> list[dict]:
    """The ledger for display: every core symbol in order; nulls where flat."""
    if params is None:
        params = _default_params(strategy_name)
    rows = []
    for symbol in CORE_WATCHLIST:
        row = store.get_position(symbol, strategy_name, set_name)
        if not row or row["state"] == "flat":
            item = {"symbol": symbol, "state": "flat"}
            if row and row.get("exit_date"):
                item["last_exit"] = {
                    "date": row.get("exit_date"),
                    "price": row.get("exit_price"),
                    "reason": row.get("exit_reason"),
                    "pnl_pct": row.get("exit_pnl_pct"),
                    "pnl_usd": row.get("exit_pnl_usd"),
                }
            rows.append(item)
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
        if row["state"] in {"long", "exit_pending"} and row["entry_price"]:
            pnl_pct = round((now / row["entry_price"] - 1) * 100, 2)
            item["pnl_pct"] = pnl_pct
            item["pnl_usd"] = round(POSITION_SHARES * (now - row["entry_price"]), 2)
        if row["state"] in {"long", "exit_pending"}:
            item["exit_plan"] = {
                "trend": _trend_exit_info(bars, strategy_name, params),
                "stop": {"level": row["stop"],
                         "why": "close below trailing stop → stop loss"},
                "target": {"level": row["tp"],
                           "why": "close reaches take-profit → take profit"}
                if row["tp"] is not None else None,
            }
        if row["state"] == "exit_pending":
            item["note"] = "exit pending → next open"
        rows.append(item)
    return rows
