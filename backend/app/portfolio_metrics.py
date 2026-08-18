"""Account-level metrics for a completed portfolio replay.

These metrics describe the simulated account. Benchmark-relative comparisons
are attached by the API only after the separately tested ADR 0005 benchmark is
calculated on the same common calendar.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass
from datetime import date

from .portfolio_execution import PortfolioReplay


@dataclass(frozen=True)
class PortfolioMetrics:
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
    max_gross_exposure: float
    max_sector_concentration: float
    max_cluster_concentration: float
    annual_turnover: float
    trade_count: int
    win_rate: float | None
    profit_factor: float | None
    expectancy: float | None
    realized_pnl: float
    rejection_count: int
    risk_event_count: int
    halted: bool
    open_positions: int
    pending_entries: int
    pending_exits: int


def _validated_daily_returns(replay: PortfolioReplay) -> list[float]:
    snapshots = replay.equity
    if snapshots[0].daily_return is not None:
        raise ValueError("first portfolio snapshot must not have a daily return")
    returns: list[float] = []
    for previous, current in zip(snapshots, snapshots[1:]):
        if previous.equity <= 0:
            raise ValueError("daily return is undefined after non-positive equity")
        expected = current.equity / previous.equity - 1
        if current.daily_return is None or not math.isfinite(current.daily_return):
            raise ValueError("portfolio daily returns must be finite")
        if not math.isclose(current.daily_return, expected, rel_tol=1e-12, abs_tol=1e-12):
            raise ValueError("portfolio daily return does not match equity history")
        returns.append(current.daily_return)
    return returns


def portfolio_metrics(replay: PortfolioReplay) -> PortfolioMetrics:
    """Calculate deterministic account metrics from common-close equity."""
    snapshots = replay.equity
    if not snapshots:
        raise ValueError("portfolio metrics require at least one equity snapshot")
    if any(not math.isfinite(row.equity) or row.equity < 0 for row in snapshots):
        raise ValueError("portfolio equity must be finite and non-negative")
    dates = [date.fromisoformat(row.date) for row in snapshots]
    if dates != sorted(dates) or len(dates) != len(set(dates)):
        raise ValueError("portfolio snapshot dates must be unique and increasing")

    daily = _validated_daily_returns(replay)
    initial_equity = snapshots[0].equity
    final_equity = snapshots[-1].equity
    if initial_equity <= 0:
        raise ValueError("initial portfolio equity must be positive")
    total_return = final_equity / initial_equity - 1
    years = max((dates[-1] - dates[0]).days / 365.25, 1 / 252)
    cagr = (1 + total_return) ** (1 / years) - 1 if total_return > -1 else -1.0

    annual_volatility = None
    sharpe = None
    if len(daily) > 1:
        daily_std = statistics.stdev(daily)
        annual_volatility = daily_std * math.sqrt(252)
        if daily_std > 0:
            sharpe = statistics.fmean(daily) / daily_std * math.sqrt(252)
    downside_deviation = None
    sortino = None
    if daily:
        downside_deviation = math.sqrt(
            statistics.fmean(min(value, 0.0) ** 2 for value in daily)
        ) * math.sqrt(252)
        if downside_deviation > 0:
            sortino = statistics.fmean(daily) * 252 / downside_deviation

    max_drawdown_bars = 0
    current_drawdown_bars = 0
    for snapshot in snapshots:
        current_drawdown_bars = (
            current_drawdown_bars + 1 if snapshot.drawdown < 0 else 0
        )
        max_drawdown_bars = max(max_drawdown_bars, current_drawdown_bars)

    sector_concentrations = [
        max(snapshot.sector_values.values(), default=0.0) / snapshot.equity
        if snapshot.equity > 0
        else 0.0
        for snapshot in snapshots
    ]
    cluster_concentrations = [
        max(snapshot.cluster_values.values(), default=0.0) / snapshot.equity
        if snapshot.equity > 0
        else 0.0
        for snapshot in snapshots
    ]
    average_equity = statistics.fmean(snapshot.equity for snapshot in snapshots)
    traded_notional = sum(fill.shares * fill.price for fill in replay.fills)
    annual_turnover = (
        traded_notional / average_equity / years if average_equity > 0 else 0.0
    )

    pnls = [trade.pnl for trade in replay.trades]
    wins = [value for value in pnls if value > 0]
    losses = [value for value in pnls if value < 0]
    profit_factor = sum(wins) / abs(sum(losses)) if losses else None

    max_drawdown = min(snapshot.drawdown for snapshot in snapshots)
    return PortfolioMetrics(
        start_date=snapshots[0].date,
        end_date=snapshots[-1].date,
        bars=len(snapshots),
        initial_equity=initial_equity,
        final_equity=final_equity,
        total_return=total_return,
        cagr=cagr,
        annual_volatility=annual_volatility,
        sharpe=sharpe,
        downside_deviation=downside_deviation,
        sortino=sortino,
        max_drawdown=max_drawdown,
        max_drawdown_bars=max_drawdown_bars,
        calmar=cagr / abs(max_drawdown) if max_drawdown < 0 else None,
        average_gross_exposure=statistics.fmean(
            snapshot.gross_exposure for snapshot in snapshots
        ),
        max_gross_exposure=max(snapshot.gross_exposure for snapshot in snapshots),
        max_sector_concentration=max(sector_concentrations),
        max_cluster_concentration=max(cluster_concentrations),
        annual_turnover=annual_turnover,
        trade_count=len(replay.trades),
        win_rate=len(wins) / len(pnls) if pnls else None,
        profit_factor=profit_factor,
        expectancy=statistics.fmean(pnls) if pnls else None,
        realized_pnl=sum(pnls),
        rejection_count=len(replay.state.rejected_orders),
        risk_event_count=len(replay.risk_events),
        halted=replay.state.halted,
        open_positions=len(replay.state.positions),
        pending_entries=len(replay.state.pending_orders),
        pending_exits=len(replay.state.pending_exits),
    )
