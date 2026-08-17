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


def _known_number(value) -> float | None:
    return float(value) if value is not None and pd.notna(value) else None


def _entry_levels(
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


def simulate(
    bars: pd.DataFrame,
    strategy_name: str,
    params: dict,
    *,
    initial_cash: float = 100_000.0,
    commission: float = 0.001,
    fixed_shares: int | None = None,
) -> Simulation:
    """Replay one long-only strategy without any same-bar fills."""
    required = {"date", "open", "high", "low", "close", "volume"}
    missing = required - set(bars.columns)
    if missing:
        raise ValueError(f"bars missing columns: {', '.join(sorted(missing))}")
    if bars.empty:
        return Simulation(strategy=strategy_name, position=Position())

    rules = build_rules(bars, strategy_name, params)
    position = Position()
    result = Simulation(strategy=strategy_name, position=position)
    cash = float(initial_cash)
    pending_signal_index: int | None = None
    exposure_bars = 0

    for index in range(len(bars)):
        row = bars.iloc[index]
        date = str(row["date"])
        open_price = float(row["open"])
        close = float(row["close"])

        if position.state == "entry_pending":
            assert pending_signal_index is not None
            shares = (
                fixed_shares
                if fixed_shares is not None
                else math.floor(cash / (open_price * (1 + commission)))
            )
            if shares > 0:
                cost = shares * open_price
                entry_fee = cost * commission
                cash -= cost + entry_fee
                stop, target = _entry_levels(
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
            if strategy_name in TRAILING_STRATEGIES:
                current_atr = _known_number(rules.atr.iloc[index])
                if current_atr is not None:
                    candidate = close - float(params.get("atr_mult", 3.0)) * current_atr
                    position.stop = max(position.stop, candidate) if position.stop is not None else candidate

            reason = None
            if bool(rules.exits.iloc[index]):
                reason = "strategy"
            elif position.stop is not None and close < position.stop:
                reason = "stop"
            elif position.target is not None and close >= position.target:
                reason = "target"
            elif strategy_name == "S/R Bounce":
                stop = _known_number(rules.stop_levels.iloc[index])
                target = _known_number(rules.target_levels.iloc[index])
                if stop is not None and close < stop:
                    reason = "stop"
                elif target is not None and close >= target:
                    reason = "target"

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


def metrics(simulation: Simulation, bars: pd.DataFrame, initial_cash: float) -> dict:
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
    return {
        "Start": str(bars["date"].iloc[0]),
        "End": str(bars["date"].iloc[-1]),
        "Duration": f"{len(bars)} bars",
        "Exposure Time [%]": sum(row["exposed"] for row in simulation.equity)
        / len(simulation.equity)
        * 100,
        "Return [%]": (float(equity.iloc[-1]) / initial_cash - 1) * 100,
        "Buy & Hold Return [%]": (float(bars["close"].iloc[-1]) / float(bars["close"].iloc[0]) - 1) * 100,
        "Max. Drawdown [%]": float(drawdown.min() * 100),
        "Win Rate [%]": len(wins) / len(returns) * 100 if returns else None,
        "Profit Factor": profit_factor,
        "Sharpe Ratio": sharpe,
        "# Trades": len(simulation.trades),
        "Open Position": simulation.position.state in {"long", "exit_pending"},
        "Pending Order": simulation.position.state if simulation.position.state.endswith("pending") else None,
    }
