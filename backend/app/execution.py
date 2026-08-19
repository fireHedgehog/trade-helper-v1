"""Canonical daily-bar execution state machine.

Signals are calculated from a completed close and fill at the next available
open. Stops are close-based signals until an explicit intraday ordering model is
designed. This module is deterministic and performs no I/O.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import pandas as pd

from .rules import RuleSet, build_rules


@dataclass
class Position:
    state: str = "flat"
    entry_date: str | None = None
    entry_price: float | None = None
    entry_fee: float = 0.0
    shares: int = 0
    stop: float | None = None
    target: float | None = None
    pending_reason: str | None = None


@dataclass
class Simulation:
    strategy: str
    position: Position
    trades: list[dict] = field(default_factory=list)
    equity: list[dict] = field(default_factory=list)
    last_exit: dict | None = None
    last_event: str = "none"


TRAILING_STRATEGIES = {"CTA Trend", "Donchian Trend"}


def validate_bars(
    bars: pd.DataFrame,
    *,
    require_positive: bool = True,
    enforce_ohlc_envelope: bool = True,
) -> None:
    """Reject malformed market bars before they can produce plausible metrics."""
    required = {"date", "open", "high", "low", "close", "volume"}
    missing = required - set(bars.columns)
    if missing:
        raise ValueError(f"bars missing columns: {', '.join(sorted(missing))}")
    if bars.empty:
        return
    if bars["date"].isna().any() or bars["date"].duplicated().any():
        raise ValueError("bar dates must be present and unique")
    dates = pd.to_datetime(bars["date"], errors="coerce")
    if dates.isna().any() or not dates.is_monotonic_increasing:
        raise ValueError("bar dates must be valid and strictly increasing")
    for column in ("open", "high", "low", "close", "volume"):
        numeric = pd.to_numeric(bars[column], errors="coerce")
        if numeric.isna().any() or not numeric.map(math.isfinite).all():
            raise ValueError(f"bar {column} values must be finite numbers")
    if require_positive and (bars[["open", "high", "low", "close"]] <= 0).any().any():
        raise ValueError("OHLC prices must be positive")
    if (bars["volume"] < 0).any():
        raise ValueError("volume cannot be negative")
    if not enforce_ohlc_envelope:
        if (bars["low"] > bars["high"]).any():
            raise ValueError("bar low cannot exceed high")
        return
    expected_high = bars[["open", "close"]].max(axis=1)
    expected_low = bars[["open", "close"]].min(axis=1)
    # Adjusted provider data can differ at the final binary floating-point bit
    # (for example 2.8e-14 at a $246 close). Keep real candle violations strict
    # while accepting representation noise far below any tradable precision.
    relative_tolerance = 1e-12
    if (bars["high"] + expected_high * relative_tolerance < expected_high).any():
        raise ValueError("bar high cannot be below open or close")
    if (bars["low"] - expected_low * relative_tolerance > expected_low).any():
        raise ValueError("bar low cannot be above open or close")
    if (bars["low"] - bars["high"] * relative_tolerance > bars["high"]).any():
        raise ValueError("bar low cannot exceed high")


def _known_number(value) -> float | None:
    return float(value) if value is not None and pd.notna(value) else None


def entry_levels(
    strategy_name: str,
    rules: RuleSet,
    params: dict,
    signal_index: int,
    entry_price: float,
) -> tuple[float | None, float | None]:
    if strategy_name in TRAILING_STRATEGIES:
        known_atr = _known_number(rules.atr.iloc[signal_index])
        stop = (
            entry_price - float(params.get("atr_mult", 3.0)) * known_atr
            if known_atr is not None
            else None
        )
        tp_mult = float(params.get("atr_tp_mult", 0.0))
        target = entry_price + tp_mult * known_atr if known_atr and tp_mult > 0 else None
        return stop, target
    return (
        _known_number(rules.stop_levels.iloc[signal_index]),
        _known_number(rules.target_levels.iloc[signal_index]),
    )


def close_exit_decision(
    strategy_name: str,
    rules: RuleSet,
    params: dict,
    index: int,
    close: float,
    stop: float | None,
    target: float | None,
) -> tuple[float | None, str | None]:
    """Return the close-known trailing stop and any canonical exit reason."""
    updated_stop = stop
    if strategy_name in TRAILING_STRATEGIES:
        current_atr = _known_number(rules.atr.iloc[index])
        if current_atr is not None:
            candidate = close - float(params.get("atr_mult", 3.0)) * current_atr
            updated_stop = max(stop, candidate) if stop is not None else candidate

    reason = None
    if bool(rules.exits.iloc[index]):
        reason = "strategy"
    elif updated_stop is not None and close < updated_stop:
        reason = "stop"
    elif target is not None and close >= target:
        reason = "target"
    elif strategy_name == "S/R Bounce":
        current_stop = _known_number(rules.stop_levels.iloc[index])
        current_target = _known_number(rules.target_levels.iloc[index])
        if current_stop is not None and close < current_stop:
            reason = "stop"
        elif current_target is not None and close >= current_target:
            reason = "target"
    return updated_stop, reason


def simulate(
    bars: pd.DataFrame,
    strategy_name: str,
    params: dict,
    *,
    initial_cash: float = 100_000.0,
    commission: float = 0.001,
    fixed_shares: int | None = None,
    spread: float = 0.0,
    slippage: float = 0.0,
    annual_cash_yield: float = 0.0,
) -> Simulation:
    """Replay one long-only strategy without any same-bar fills."""
    validate_bars(bars)
    for name, value in {
        "commission": commission,
        "spread": spread,
        "slippage": slippage,
    }.items():
        if not math.isfinite(value) or not 0 <= value < 1:
            raise ValueError(f"{name} must be finite and between 0 and 1")
    if not math.isfinite(annual_cash_yield) or annual_cash_yield <= -1:
        raise ValueError("annual_cash_yield must be finite and greater than -1")
    if initial_cash <= 0 or not math.isfinite(initial_cash):
        raise ValueError("initial_cash must be finite and positive")
    if bars.empty:
        return Simulation(strategy=strategy_name, position=Position())

    rules = build_rules(bars, strategy_name, params)
    position = Position()
    result = Simulation(strategy=strategy_name, position=position)
    cash = float(initial_cash)
    daily_cash_rate = (1 + annual_cash_yield) ** (1 / 252) - 1
    pending_signal_index: int | None = None
    exposure_bars = 0

    for index in range(len(bars)):
        row = bars.iloc[index]
        date = str(row["date"])
        market_open = float(row["open"])
        close = float(row["close"])

        if index > 0 and cash > 0 and annual_cash_yield:
            cash *= 1 + daily_cash_rate

        if position.state == "entry_pending":
            assert pending_signal_index is not None
            open_price = market_open * (1 + spread / 2 + slippage)
            shares = (
                fixed_shares
                if fixed_shares is not None
                else math.floor(cash / (open_price * (1 + commission)))
            )
            if shares > 0:
                cost = shares * open_price
                entry_fee = cost * commission
                cash -= cost + entry_fee
                stop, target = entry_levels(
                    strategy_name, rules, params, pending_signal_index, open_price
                )
                position = Position(
                    state="long",
                    entry_date=date,
                    entry_price=open_price,
                    entry_fee=entry_fee,
                    shares=shares,
                    stop=stop,
                    target=target,
                )
                result.position = position
            else:
                position = Position()
                result.position = position
            pending_signal_index = None

        elif position.state == "exit_pending":
            assert position.entry_price is not None
            open_price = market_open * (1 - spread / 2 - slippage)
            proceeds = position.shares * open_price
            exit_fee = proceeds * commission
            cash += proceeds - exit_fee
            pnl = (
                (open_price - position.entry_price) * position.shares
                - position.entry_fee
                - exit_fee
            )
            basis = position.entry_price * position.shares + position.entry_fee
            trade = {
                "entry_date": position.entry_date,
                "entry_price": round(position.entry_price, 6),
                "exit_date": date,
                "exit_price": round(open_price, 6),
                "size": position.shares,
                "pnl": round(pnl, 6),
                "return_pct": round(pnl / basis * 100, 6),
                "exit_reason": position.pending_reason,
            }
            result.trades.append(trade)
            result.last_exit = trade
            position = Position()
            result.position = position

        if position.state in {"long", "exit_pending"}:
            exposure_bars += 1

        equity = cash + position.shares * close
        result.equity.append(
            {"date": date, "equity": equity, "exposed": position.shares > 0}
        )

        if position.state == "long":
            position.stop, reason = close_exit_decision(
                strategy_name,
                rules,
                params,
                index,
                close,
                position.stop,
                position.target,
            )

            if reason:
                position.state = "exit_pending"
                position.pending_reason = reason
                result.last_event = "exit"

        elif position.state == "flat" and bool(rules.entries.iloc[index]):
            position.state = "entry_pending"
            pending_signal_index = index
            result.last_event = "entry"

        if index != len(bars) - 1:
            result.last_event = "none"

    result.position = position
    return result


def metrics(
    simulation: Simulation,
    bars: pd.DataFrame,
    initial_cash: float,
    *,
    annual_cash_yield: float = 0.0,
) -> dict:
    """Core performance metrics over canonical marked-to-market equity."""
    if not simulation.equity:
        return {}
    equity = pd.Series([row["equity"] for row in simulation.equity], dtype=float)
    daily = equity.pct_change().dropna()
    drawdown = equity / equity.cummax() - 1
    returns = [float(trade["pnl"]) for trade in simulation.trades]
    wins = [value for value in returns if value > 0]
    losses = [value for value in returns if value < 0]
    sharpe = None
    if len(daily) > 1 and float(daily.std(ddof=1)) > 0:
        sharpe = float(daily.mean() / daily.std(ddof=1) * math.sqrt(252))
    profit_factor = sum(wins) / abs(sum(losses)) if losses else None
    start_date = pd.Timestamp(bars["date"].iloc[0])
    end_date = pd.Timestamp(bars["date"].iloc[-1])
    years = max((end_date - start_date).days / 365.25, 1 / 252)
    total_return = float(equity.iloc[-1]) / initial_cash - 1
    cagr = (1 + total_return) ** (1 / years) - 1 if total_return > -1 else -1.0
    volatility = float(daily.std(ddof=1) * math.sqrt(252)) if len(daily) > 1 else None
    downside = daily.clip(upper=0)
    downside_deviation = (
        float(math.sqrt(float((downside**2).mean())) * math.sqrt(252))
        if len(downside)
        else None
    )
    sortino = (
        float(daily.mean() * 252 / downside_deviation)
        if downside_deviation and downside_deviation > 0
        else None
    )
    max_drawdown = float(drawdown.min())
    calmar = cagr / abs(max_drawdown) if max_drawdown < 0 else None
    underwater = drawdown < 0
    max_drawdown_bars = 0
    current = 0
    for value in underwater:
        current = current + 1 if value else 0
        max_drawdown_bars = max(max_drawdown_bars, current)
    exposure = sum(row["exposed"] for row in simulation.equity) / len(simulation.equity)
    asset_daily = bars["close"].astype(float).pct_change().fillna(0)
    cash_daily = (1 + annual_cash_yield) ** (1 / 252) - 1
    matched_daily = exposure * asset_daily + (1 - exposure) * cash_daily
    matched_return = float((1 + matched_daily).prod() - 1)
    traded_notional = sum(
        trade["size"] * (trade["entry_price"] + trade["exit_price"])
        for trade in simulation.trades
    )
    annual_turnover = traded_notional / float(equity.mean()) / years
    return {
        "Start": str(bars["date"].iloc[0]),
        "End": str(bars["date"].iloc[-1]),
        "Duration": f"{len(bars)} bars",
        "Exposure Time [%]": exposure * 100,
        "Return [%]": total_return * 100,
        "Buy & Hold Return [%]": (float(bars["close"].iloc[-1]) / float(bars["close"].iloc[0]) - 1) * 100,
        "Exposure-Matched Benchmark [%]": matched_return * 100,
        "CAGR [%]": cagr * 100,
        "Annual Volatility [%]": volatility * 100 if volatility is not None else None,
        "Downside Deviation [%]": downside_deviation * 100 if downside_deviation is not None else None,
        "Sortino Ratio": sortino,
        "Calmar Ratio": calmar,
        "Max. Drawdown [%]": max_drawdown * 100,
        "Max. Drawdown Duration [bars]": max_drawdown_bars,
        "Win Rate [%]": len(wins) / len(returns) * 100 if returns else None,
        "Profit Factor": profit_factor,
        "Sharpe Ratio": sharpe,
        "Expectancy [$]": sum(returns) / len(returns) if returns else None,
        "Expectancy [%]": sum(trade["return_pct"] for trade in simulation.trades)
        / len(simulation.trades)
        if simulation.trades
        else None,
        "Annual Turnover [x]": annual_turnover,
        "# Trades": len(simulation.trades),
        "Open Position": simulation.position.state in {"long", "exit_pending"},
        "Pending Order": simulation.position.state if simulation.position.state.endswith("pending") else None,
    }
