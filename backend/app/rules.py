"""Canonical vectorized entry/exit rules shared by every product surface."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class RuleSet:
    entries: pd.Series
    exits: pd.Series
    atr: pd.Series
    stop_levels: pd.Series
    target_levels: pd.Series


def rsi(close: pd.Series, period: int) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(
        alpha=1 / period, adjust=False, min_periods=period
    ).mean()
    loss = (-delta.clip(upper=0)).ewm(
        alpha=1 / period, adjust=False, min_periods=period
    ).mean()
    return 100 - 100 / (1 + gain / loss.replace(0, 1e-12))


def atr(bars: pd.DataFrame, period: int) -> pd.Series:
    high, low, close = bars["high"], bars["low"], bars["close"]
    previous_close = close.shift(1)
    true_range = pd.concat(
        [
            high - low,
            (high - previous_close).abs(),
            (low - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return true_range.ewm(
        alpha=1 / period, adjust=False, min_periods=period
    ).mean()


def _false(index: pd.Index) -> pd.Series:
    return pd.Series(False, index=index, dtype=bool)


def _nan(index: pd.Index) -> pd.Series:
    return pd.Series(float("nan"), index=index, dtype=float)


def build_rules(bars: pd.DataFrame, strategy_name: str, params: dict) -> RuleSet:
    """Return close-known rules; execution happens in ``execution.simulate``."""
    close = bars["close"]
    index = bars.index
    period = int(params.get("atr_period", 14))
    atr_values = atr(bars, period)
    entries = _false(index)
    exits = _false(index)
    stop_levels = _nan(index)
    target_levels = _nan(index)

    if strategy_name == "SMA Cross":
        fast = close.rolling(int(params.get("n_fast", 20))).mean()
        slow = close.rolling(int(params.get("n_slow", 50))).mean()
        above = fast > slow
        entries = above & ~above.shift(1, fill_value=False)
        exits = ~above & above.shift(1, fill_value=False)

    elif strategy_name == "Donchian Trend":
        upper = bars["high"].shift(1).rolling(int(params.get("n_entry", 55))).max()
        lower = bars["low"].shift(1).rolling(int(params.get("n_exit", 20))).min()
        above = close > upper
        entries = above & ~above.shift(1, fill_value=False)
        exits = close < lower

    elif strategy_name == "CTA Trend":
        upper = bars["high"].shift(1).rolling(int(params.get("n_entry", 100))).max()
        lower = bars["low"].shift(1).rolling(int(params.get("n_exit", 40))).min()
        trend = close.rolling(int(params.get("trend_ma", 100))).mean()
        above = (close > upper) & (close > trend)
        entries = above & ~above.shift(1, fill_value=False)
        exits = close < lower

    elif strategy_name == "RSI Reversion":
        values = rsi(close, int(params.get("period", 14)))
        oversold = values < int(params.get("buy_below", 30))
        entries = oversold & ~oversold.shift(1, fill_value=False)
        exits = values > int(params.get("sell_above", 70))

    elif strategy_name == "S/R Bounce":
        support = bars["low"].shift(1).rolling(int(params.get("n_window", 20))).min()
        resistance = bars["high"].shift(1).rolling(int(params.get("n_window", 20))).max()
        entries = (close > support) & (bars["low"] <= support)
        stop_levels = support - float(params.get("atr_mult", 3.0)) * atr_values
        target_levels = resistance

    elif strategy_name == "Fib Retrace":
        high = bars["high"].shift(1).rolling(int(params.get("n_swing", 60))).max()
        low = bars["low"].shift(1).rolling(int(params.get("m_pullback", 10))).min()
        level = low + float(params.get("fib", 0.618)) * (high - low)
        entries = (high > low) & (close > level) & (close.shift(1) <= level.shift(1))
        stop_levels = low
        target_levels = high

    elif strategy_name == "Wave Pull":
        impulse_bars = int(params.get("impulse_bars", 8))
        impulse = close / close.shift(impulse_bars) - 1 >= float(
            params.get("impulse_pct", 6.0)
        ) / 100
        pullback_bars = int(params.get("pullback_bars", 3))
        high = bars["high"].shift(1).rolling(pullback_bars).max()
        low = bars["low"].shift(1).rolling(pullback_bars).min()
        entries = impulse & (close > high)
        risk = high - low
        stop_levels = low
        target_levels = high + 2 * risk

    else:
        raise KeyError(f"unknown strategy: {strategy_name}")

    return RuleSet(
        entries=entries.fillna(False).astype(bool),
        exits=exits.fillna(False).astype(bool),
        atr=atr_values,
        stop_levels=stop_levels,
        target_levels=target_levels,
    )
