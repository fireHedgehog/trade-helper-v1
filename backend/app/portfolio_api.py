"""JSON-ready adapter around the deterministic portfolio replay."""

from __future__ import annotations

from dataclasses import asdict

import pandas as pd

from . import store
from .portfolio import PortfolioConfig
from .portfolio_benchmark import cash_benchmark, simulate_passive_benchmark
from .portfolio_execution import simulate_portfolio
from .portfolio_metrics import portfolio_metrics
from .portfolio_universe import (
    PORTFOLIO_CLASSIFICATIONS,
    PORTFOLIO_COMMON_START,
    PORTFOLIO_SYMBOLS,
    PORTFOLIO_UNIVERSE_ID,
)


PORTFOLIO_SUPPORTED_STRATEGIES = frozenset(
    {"CTA Trend", "Donchian Trend", "S/R Bounce", "Fib Retrace", "Wave Pull"}
)
PORTFOLIO_CLAIM = (
    "historical mechanics replay; not prospective evidence, investment advice, "
    "or authorization for paper/live trading"
)


def _unsupported_payload(strategy: str, params: dict) -> dict:
    return {
        "status": "unsupported",
        "claim": PORTFOLIO_CLAIM,
        "strategy": strategy,
        "params": params,
        "reason": (
            "shared-account risk sizing requires an explicit protective stop, "
            f"but {strategy} does not define one"
        ),
        "supported_strategies": sorted(PORTFOLIO_SUPPORTED_STRATEGIES),
    }


def _load_common_bars() -> tuple[dict[str, pd.DataFrame], str]:
    frames = {symbol: store.load_bars(symbol) for symbol in PORTFOLIO_SYMBOLS}
    missing = [symbol for symbol, frame in frames.items() if frame.empty]
    if missing:
        raise RuntimeError("portfolio data missing: " + ", ".join(missing))
    common_end = min(str(frame["date"].iloc[-1]) for frame in frames.values())
    prepared = {
        symbol: frame[
            (frame["date"] >= PORTFOLIO_COMMON_START)
            & (frame["date"] <= common_end)
        ].reset_index(drop=True)
        for symbol, frame in frames.items()
    }
    bad_start = [
        symbol
        for symbol, frame in prepared.items()
        if frame.empty or str(frame["date"].iloc[0]) != PORTFOLIO_COMMON_START
    ]
    if bad_start:
        raise RuntimeError(
            "portfolio common start unavailable: " + ", ".join(bad_start)
        )
    reference = tuple(str(value) for value in prepared[PORTFOLIO_SYMBOLS[0]]["date"])
    mismatched = [
        symbol
        for symbol, frame in prepared.items()
        if tuple(str(value) for value in frame["date"]) != reference
    ]
    if mismatched:
        raise RuntimeError(
            "portfolio calendars differ: " + ", ".join(mismatched)
        )
    return prepared, common_end


def _sample_equity(rows: tuple, maximum: int = 500) -> list[dict]:
    if maximum < 2:
        raise ValueError("equity sample maximum must be at least 2")
    if len(rows) <= maximum:
        selected = list(rows)
    else:
        final_index = len(rows) - 1
        indexes = [
            round(index * final_index / (maximum - 1))
            for index in range(maximum)
        ]
        selected = [rows[index] for index in indexes]
    return [asdict(row) for row in selected]


def portfolio_payload(strategy: str, params: dict) -> dict:
    if strategy not in PORTFOLIO_SUPPORTED_STRATEGIES:
        return _unsupported_payload(strategy, params)
    bars, common_end = _load_common_bars()
    config = PortfolioConfig()
    replay = simulate_portfolio(
        bars,
        strategy_name=strategy,
        params=params,
        classifications=PORTFOLIO_CLASSIFICATIONS,
        config=config,
    )
    metrics = portfolio_metrics(replay)
    primary_benchmark = simulate_passive_benchmark(
        bars,
        name="Passive ETF-12 v1",
        annual_rebalance=True,
        config=config,
    )
    spy_benchmark = simulate_passive_benchmark(
        {"SPY": bars["SPY"]},
        name="SPY buy-and-hold",
        annual_rebalance=False,
        config=config,
    )
    cash_reference = cash_benchmark(
        tuple(str(value) for value in bars["SPY"]["date"]),
        initial_cash=config.initial_cash,
        annual_cash_yield=0.0,
    )
    final = replay.equity[-1]
    positions = [
        {
            **asdict(position),
            "market_value": position.market_value,
            "unrealized_pnl": (
                (position.market_price - position.entry_price) * position.shares
                - position.entry_fee
            ),
        }
        for position in sorted(replay.state.positions.values(), key=lambda row: row.symbol)
    ]
    classifications = [
        {"symbol": symbol, **asdict(PORTFOLIO_CLASSIFICATIONS[symbol])}
        for symbol in PORTFOLIO_SYMBOLS
    ]
    return {
        "status": "halted" if replay.state.halted else "complete",
        "claim": PORTFOLIO_CLAIM,
        "strategy": strategy,
        "params": params,
        "universe": {
            "id": PORTFOLIO_UNIVERSE_ID,
            "symbols": list(PORTFOLIO_SYMBOLS),
            "classifications": classifications,
            "common_start": PORTFOLIO_COMMON_START,
            "common_end": common_end,
            "bars": len(replay.equity),
        },
        "assumptions": {
            **asdict(config),
            "signal_timing": "completed close",
            "fill_timing": "next shared-calendar open",
            "sale_settlement": "next shared-calendar session (T+1 approximation)",
            "priority": "equal locked score, then symbol ascending",
            "annual_cash_yield": 0.0,
        },
        "benchmark": {
            "contract": "ADR 0005",
            "primary": primary_benchmark.summary(),
            "secondary": {
                "spy_buy_and_hold": spy_benchmark.summary(),
                "cash": cash_reference,
            },
            "comparison": {
                "total_return_difference": (
                    metrics.total_return - primary_benchmark.metrics.total_return
                ),
                "cagr_difference": metrics.cagr - primary_benchmark.metrics.cagr,
                "max_drawdown_improvement": (
                    metrics.max_drawdown - primary_benchmark.metrics.max_drawdown
                ),
                "calmar_difference": (
                    metrics.calmar - primary_benchmark.metrics.calmar
                    if metrics.calmar is not None
                    and primary_benchmark.metrics.calmar is not None
                    else None
                ),
            },
        },
        "benchmark_note": (
            "Passive ETF-12 v1 is the primary same-universe comparison; SPY and "
            "cash answer different questions. Historical differences do not "
            "establish a durable edge"
        ),
        "metrics": asdict(metrics),
        "account": {
            "cash": replay.state.cash,
            "unsettled_cash": sum(item.amount for item in replay.state.settlements),
            "market_value": final.market_value,
            "equity": final.equity,
            "drawdown": final.drawdown,
            "halted": replay.state.halted,
            "open_positions": len(replay.state.positions),
            "pending_entries": len(replay.state.pending_orders),
            "pending_exits": len(replay.state.pending_exits),
        },
        "positions": positions,
        "trades": [asdict(row) for row in replay.trades[-100:]],
        "rejections": [asdict(row) for row in replay.state.rejected_orders[-100:]],
        "rejection_count": len(replay.state.rejected_orders),
        "risk_events": [asdict(row) for row in replay.risk_events],
        "equity": _sample_equity(replay.equity),
    }
