"""Investable passive comparisons for the locked shared-capital portfolio.

The primary benchmark follows ADR 0005: equal-weight the same locked ETF
opportunity set, use whole shares and canonical costs, and begin each annual
rebalance at the first common open. Sale proceeds remain unavailable until the
next shared session, so a rebalance may complete its underweight purchases one
session later rather than assuming impossible same-day reuse of proceeds.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import asdict, dataclass
from datetime import date

import pandas as pd

from .execution import validate_bars
from .portfolio import PortfolioConfig


@dataclass(frozen=True)
class BenchmarkFill:
    date: str
    symbol: str
    side: str
    shares: int
    price: float
    fee: float


@dataclass(frozen=True)
class BenchmarkSnapshot:
    date: str
    cash: float
    unsettled_cash: float
    market_value: float
    equity: float
    drawdown: float
    gross_exposure: float
    daily_return: float


@dataclass(frozen=True)
class BenchmarkMetrics:
    start_date: str
    end_date: str
    bars: int
    initial_equity: float
    final_equity: float
    total_return: float
    cagr: float
    annual_volatility: float | None
    sharpe: float | None
    downside_deviation: float | None
    sortino: float | None
    max_drawdown: float
    max_drawdown_bars: int
    calmar: float | None
    average_gross_exposure: float
    annual_turnover: float
    total_fees: float
    fill_count: int


@dataclass(frozen=True)
class BenchmarkResult:
    name: str
    symbols: tuple[str, ...]
    rebalance: str
    metrics: BenchmarkMetrics
    equity: tuple[BenchmarkSnapshot, ...]
    fills: tuple[BenchmarkFill, ...]

    def summary(self) -> dict:
        return {
            "name": self.name,
            "symbols": list(self.symbols),
            "rebalance": self.rebalance,
            "metrics": asdict(self.metrics),
        }


def _prepare_common_bars(
    bars_by_symbol: dict[str, pd.DataFrame],
) -> tuple[tuple[str, ...], tuple[str, ...], dict[str, pd.DataFrame]]:
    if not bars_by_symbol:
        raise ValueError("benchmark requires at least one symbol")
    symbols = tuple(sorted(bars_by_symbol))
    prepared: dict[str, pd.DataFrame] = {}
    calendar: tuple[str, ...] | None = None
    for symbol in symbols:
        frame = bars_by_symbol[symbol].reset_index(drop=True).copy()
        validate_bars(frame)
        if frame.empty:
            raise ValueError(f"{symbol} has no benchmark bars")
        dates = tuple(str(value) for value in frame["date"])
        if calendar is None:
            calendar = dates
        elif dates != calendar:
            raise ValueError(f"{symbol} benchmark calendar differs")
        prepared[symbol] = frame
    assert calendar is not None
    return symbols, calendar, prepared


def _metrics(
    snapshots: list[BenchmarkSnapshot],
    fills: list[BenchmarkFill],
    initial_cash: float,
) -> BenchmarkMetrics:
    returns = [row.daily_return for row in snapshots]
    start = date.fromisoformat(snapshots[0].date)
    end = date.fromisoformat(snapshots[-1].date)
    years = max((end - start).days / 365.25, 1 / 252)
    final_equity = snapshots[-1].equity
    total_return = final_equity / initial_cash - 1
    cagr = (1 + total_return) ** (1 / years) - 1 if total_return > -1 else -1.0
    annual_volatility = None
    sharpe = None
    if len(returns) > 1:
        daily_std = statistics.stdev(returns)
        annual_volatility = daily_std * math.sqrt(252)
        if daily_std > 0:
            sharpe = statistics.fmean(returns) / daily_std * math.sqrt(252)
    downside_deviation = math.sqrt(
        statistics.fmean(min(value, 0.0) ** 2 for value in returns)
    ) * math.sqrt(252)
    sortino = (
        statistics.fmean(returns) * 252 / downside_deviation
        if downside_deviation > 0
        else None
    )
    max_drawdown = min(row.drawdown for row in snapshots)
    drawdown_bars = 0
    longest_drawdown = 0
    for row in snapshots:
        drawdown_bars = drawdown_bars + 1 if row.drawdown < 0 else 0
        longest_drawdown = max(longest_drawdown, drawdown_bars)
    average_equity = statistics.fmean(row.equity for row in snapshots)
    traded_notional = sum(fill.shares * fill.price for fill in fills)
    return BenchmarkMetrics(
        start_date=snapshots[0].date,
        end_date=snapshots[-1].date,
        bars=len(snapshots),
        initial_equity=initial_cash,
        final_equity=final_equity,
        total_return=total_return,
        cagr=cagr,
        annual_volatility=annual_volatility,
        sharpe=sharpe,
        downside_deviation=downside_deviation,
        sortino=sortino,
        max_drawdown=max_drawdown,
        max_drawdown_bars=longest_drawdown,
        calmar=cagr / abs(max_drawdown) if max_drawdown < 0 else None,
        average_gross_exposure=statistics.fmean(
            row.gross_exposure for row in snapshots
        ),
        annual_turnover=(
            traded_notional / average_equity / years if average_equity > 0 else 0.0
        ),
        total_fees=sum(fill.fee for fill in fills),
        fill_count=len(fills),
    )


def simulate_passive_benchmark(
    bars_by_symbol: dict[str, pd.DataFrame],
    *,
    name: str,
    annual_rebalance: bool,
    config: PortfolioConfig | None = None,
    annual_cash_yield: float = 0.0,
) -> BenchmarkResult:
    """Buy an equal-weight whole-share basket and optionally rebalance yearly."""
    resolved = config or PortfolioConfig()
    if not math.isfinite(annual_cash_yield) or annual_cash_yield < 0:
        raise ValueError("annual_cash_yield must be finite and non-negative")
    symbols, dates, bars = _prepare_common_bars(bars_by_symbol)
    daily_cash_rate = (1 + annual_cash_yield) ** (1 / 252) - 1
    cash = resolved.initial_cash
    holdings = {symbol: 0 for symbol in symbols}
    settlements: list[tuple[str | None, float]] = []
    fills: list[BenchmarkFill] = []
    snapshots: list[BenchmarkSnapshot] = []
    peak = resolved.initial_cash
    previous_equity = resolved.initial_cash
    prior_year: int | None = None
    complete_rebalance = False

    def opening_equity(index: int) -> float:
        return (
            cash
            + sum(amount for _, amount in settlements)
            + sum(
                holdings[symbol] * float(bars[symbol]["open"].iloc[index])
                for symbol in symbols
            )
        )

    def buy_underweights(index: int, target: float) -> None:
        nonlocal cash
        for symbol in symbols:
            raw_open = float(bars[symbol]["open"].iloc[index])
            fill_price = raw_open * (1 + resolved.spread / 2 + resolved.slippage)
            cash_per_share = fill_price * (1 + resolved.commission)
            current_value = holdings[symbol] * raw_open
            desired = max(0, math.floor((target - current_value) / cash_per_share))
            shares = min(desired, math.floor(cash / cash_per_share))
            if shares <= 0:
                continue
            fee = shares * fill_price * resolved.commission
            cash -= shares * fill_price + fee
            holdings[symbol] += shares
            fills.append(BenchmarkFill(dates[index], symbol, "buy", shares, fill_price, fee))

    for index, current_date in enumerate(dates):
        if index > 0 and cash:
            cash *= 1 + daily_cash_rate
        matured = [amount for available, amount in settlements if available == current_date]
        cash += sum(matured)
        settlements = [
            (available, amount)
            for available, amount in settlements
            if available != current_date
        ]
        year = date.fromisoformat(current_date).year
        new_year = annual_rebalance and prior_year is not None and year != prior_year

        if index == 0:
            buy_underweights(index, resolved.initial_cash / len(symbols))
        elif new_year:
            target = opening_equity(index) / len(symbols)
            next_date = dates[index + 1] if index + 1 < len(dates) else None
            for symbol in symbols:
                raw_open = float(bars[symbol]["open"].iloc[index])
                target_shares = math.floor(target / raw_open)
                shares = max(0, holdings[symbol] - target_shares)
                if shares <= 0:
                    continue
                fill_price = raw_open * (1 - resolved.spread / 2 - resolved.slippage)
                fee = shares * fill_price * resolved.commission
                holdings[symbol] -= shares
                settlements.append((next_date, shares * fill_price - fee))
                fills.append(
                    BenchmarkFill(current_date, symbol, "sell", shares, fill_price, fee)
                )
            buy_underweights(index, target)
            complete_rebalance = bool(settlements)
        elif complete_rebalance:
            buy_underweights(index, opening_equity(index) / len(symbols))
            complete_rebalance = False

        market_value = sum(
            holdings[symbol] * float(bars[symbol]["close"].iloc[index])
            for symbol in symbols
        )
        unsettled = sum(amount for _, amount in settlements)
        equity = cash + unsettled + market_value
        if not math.isfinite(equity) or equity < 0:
            raise RuntimeError("benchmark equity must remain finite and non-negative")
        peak = max(peak, equity)
        snapshots.append(
            BenchmarkSnapshot(
                date=current_date,
                cash=cash,
                unsettled_cash=unsettled,
                market_value=market_value,
                equity=equity,
                drawdown=equity / peak - 1,
                gross_exposure=market_value / equity if equity > 0 else 0.0,
                daily_return=equity / previous_equity - 1,
            )
        )
        previous_equity = equity
        prior_year = year

    return BenchmarkResult(
        name=name,
        symbols=symbols,
        rebalance="annual" if annual_rebalance else "none",
        metrics=_metrics(snapshots, fills, resolved.initial_cash),
        equity=tuple(snapshots),
        fills=tuple(fills),
    )


def cash_benchmark(
    dates: tuple[str, ...],
    *,
    initial_cash: float,
    annual_cash_yield: float,
) -> dict:
    """Compound the declared cash yield over the shared recorded sessions."""
    if not dates:
        raise ValueError("cash benchmark requires dates")
    if not math.isfinite(initial_cash) or initial_cash <= 0:
        raise ValueError("cash benchmark initial_cash must be positive")
    if not math.isfinite(annual_cash_yield) or annual_cash_yield < 0:
        raise ValueError("annual_cash_yield must be finite and non-negative")
    final = initial_cash * (1 + annual_cash_yield) ** ((len(dates) - 1) / 252)
    start = date.fromisoformat(dates[0])
    end = date.fromisoformat(dates[-1])
    years = max((end - start).days / 365.25, 1 / 252)
    total_return = final / initial_cash - 1
    return {
        "name": "Declared cash yield",
        "start_date": dates[0],
        "end_date": dates[-1],
        "bars": len(dates),
        "initial_equity": initial_cash,
        "final_equity": final,
        "total_return": total_return,
        "cagr": (1 + total_return) ** (1 / years) - 1,
        "max_drawdown": 0.0,
        "calmar": None,
        "annual_cash_yield": annual_cash_yield,
    }
