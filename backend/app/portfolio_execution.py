"""Multi-symbol daily portfolio replay on one cash-constrained account.

Signals use completed closes and fill at the following shared-calendar open.
Sale proceeds settle on the next recorded session and cannot finance same-day
entries. The module is deterministic, performs no I/O, and does not yet trigger
the portfolio drawdown kill switch.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace

import pandas as pd

from .execution import close_exit_decision, entry_levels, validate_bars
from .portfolio import (
    CandidateOrder,
    CashSettlement,
    PendingExit,
    PortfolioConfig,
    PortfolioPosition,
    PortfolioState,
    RejectedOrder,
    allocate_entries,
    initial_portfolio,
    size_entry,
)
from .rules import RuleSet, build_rules


@dataclass(frozen=True)
class AssetClassification:
    sector: str
    cluster: str


@dataclass(frozen=True)
class PortfolioFill:
    side: str
    signal_date: str
    fill_date: str
    symbol: str
    requested_shares: int
    shares: int
    price: float
    fee: float
    net_amount: float


@dataclass(frozen=True)
class PortfolioTrade:
    symbol: str
    entry_date: str
    entry_price: float
    exit_date: str
    exit_price: float
    shares: int
    entry_fee: float
    exit_fee: float
    pnl: float
    return_pct: float
    exit_reason: str


@dataclass(frozen=True)
class PortfolioSnapshot:
    date: str
    cash: float
    unsettled_cash: float
    market_value: float
    equity: float
    peak_equity: float
    drawdown: float
    gross_exposure: float
    position_count: int
    sector_values: dict[str, float]
    cluster_values: dict[str, float]


@dataclass(frozen=True)
class PortfolioReplay:
    strategy: str
    state: PortfolioState
    fills: tuple[PortfolioFill, ...]
    trades: tuple[PortfolioTrade, ...]
    equity: tuple[PortfolioSnapshot, ...]


def _prepared_inputs(
    bars_by_symbol: dict[str, pd.DataFrame],
    classifications: dict[str, AssetClassification],
    priority_scores: dict[str, float] | None,
) -> tuple[
    tuple[str, ...],
    tuple[str, ...],
    dict[str, pd.DataFrame],
    dict[str, float],
]:
    if not bars_by_symbol:
        raise ValueError("portfolio replay requires at least one symbol")
    symbols = tuple(sorted(bars_by_symbol))
    missing_classifications = set(symbols) - set(classifications)
    if missing_classifications:
        raise ValueError(
            "missing classifications: " + ", ".join(sorted(missing_classifications))
        )

    prepared: dict[str, pd.DataFrame] = {}
    calendar: tuple[str, ...] | None = None
    for symbol in symbols:
        bars = bars_by_symbol[symbol].reset_index(drop=True).copy()
        validate_bars(bars)
        if bars.empty:
            raise ValueError(f"{symbol} has no bars")
        dates = tuple(str(value) for value in bars["date"])
        if calendar is None:
            calendar = dates
        elif dates != calendar:
            raise ValueError(
                f"{symbol} calendar differs from the shared portfolio calendar"
            )
        classification = classifications[symbol]
        if not classification.sector.strip() or not classification.cluster.strip():
            raise ValueError(f"{symbol} classification must be explicit")
        prepared[symbol] = bars

    assert calendar is not None
    scores = dict(priority_scores or {symbol: 0.0 for symbol in symbols})
    missing_scores = set(symbols) - set(scores)
    if missing_scores:
        raise ValueError("missing priority scores: " + ", ".join(sorted(missing_scores)))
    for symbol in symbols:
        if not math.isfinite(scores[symbol]):
            raise ValueError(f"{symbol} priority score must be finite")
    return symbols, calendar, prepared, scores


def _fill_rejection(
    *, date: str, symbol: str, requested_shares: int, cash: float, reason: str
) -> RejectedOrder:
    return RejectedOrder(
        date=date,
        symbol=symbol,
        requested_shares=requested_shares,
        available_cash=max(0.0, cash),
        reason=reason,
    )


def _snapshot(
    date: str,
    *,
    cash: float,
    settlements: list[CashSettlement],
    positions: dict[str, PortfolioPosition],
    previous_peak: float,
) -> PortfolioSnapshot:
    unsettled = sum(item.amount for item in settlements)
    market_value = sum(position.market_value for position in positions.values())
    equity = cash + unsettled + market_value
    peak = max(previous_peak, equity)
    drawdown = equity / peak - 1
    sectors: dict[str, float] = {}
    clusters: dict[str, float] = {}
    for position in positions.values():
        sectors[position.sector] = sectors.get(position.sector, 0.0) + position.market_value
        clusters[position.cluster] = clusters.get(position.cluster, 0.0) + position.market_value
    return PortfolioSnapshot(
        date=date,
        cash=cash,
        unsettled_cash=unsettled,
        market_value=market_value,
        equity=equity,
        peak_equity=peak,
        drawdown=drawdown,
        gross_exposure=market_value / equity if equity > 0 else 0.0,
        position_count=len(positions),
        sector_values=sectors,
        cluster_values=clusters,
    )


def simulate_portfolio(
    bars_by_symbol: dict[str, pd.DataFrame],
    *,
    strategy_name: str,
    params: dict,
    classifications: dict[str, AssetClassification],
    priority_scores: dict[str, float] | None = None,
    config: PortfolioConfig | None = None,
) -> PortfolioReplay:
    """Replay one rule set across symbols using shared capital and daily marks.

    ``priority_scores`` are immutable, predeclared symbol priorities for the
    entire replay. Their default is equal priority, resolved by symbol order.
    Dynamic full-history ranks are intentionally not accepted here because they
    can introduce future leakage unless separately specified and tested.
    """
    resolved = config or PortfolioConfig()
    symbols, dates, bars, scores = _prepared_inputs(
        bars_by_symbol, classifications, priority_scores
    )
    rules: dict[str, RuleSet] = {
        symbol: build_rules(bars[symbol], strategy_name, params) for symbol in symbols
    }
    date_indexes = {date: index for index, date in enumerate(dates)}
    state = initial_portfolio(resolved)
    fills: list[PortfolioFill] = []
    trades: list[PortfolioTrade] = []
    snapshots: list[PortfolioSnapshot] = []

    for index, date in enumerate(dates):
        next_date = dates[index + 1] if index + 1 < len(dates) else None
        cash = state.cash
        positions = dict(state.positions)
        settlements = list(state.settlements)
        rejected = list(state.rejected_orders)

        matured = [item for item in settlements if item.available_date == date]
        cash += sum(item.amount for item in matured)
        settlements = [item for item in settlements if item.available_date != date]

        remaining_exits: list[PendingExit] = []
        for order in state.pending_exits:
            if order.order_date != date:
                remaining_exits.append(order)
                continue
            position = positions.pop(order.symbol, None)
            if position is None:
                raise RuntimeError(f"exit order has no position: {order.symbol}")
            raw_open = float(bars[order.symbol]["open"].iloc[index])
            fill_price = raw_open * (1 - resolved.spread / 2 - resolved.slippage)
            gross_proceeds = position.shares * fill_price
            exit_fee = gross_proceeds * resolved.commission
            net_proceeds = gross_proceeds - exit_fee
            settlements.append(
                CashSettlement(
                    trade_date=date,
                    available_date=next_date,
                    symbol=order.symbol,
                    amount=net_proceeds,
                )
            )
            pnl = (
                (fill_price - position.entry_price) * position.shares
                - position.entry_fee
                - exit_fee
            )
            basis = position.entry_price * position.shares + position.entry_fee
            fills.append(
                PortfolioFill(
                    side="exit",
                    signal_date=order.signal_date,
                    fill_date=date,
                    symbol=order.symbol,
                    requested_shares=position.shares,
                    shares=position.shares,
                    price=fill_price,
                    fee=exit_fee,
                    net_amount=net_proceeds,
                )
            )
            trades.append(
                PortfolioTrade(
                    symbol=order.symbol,
                    entry_date=position.entry_date,
                    entry_price=position.entry_price,
                    exit_date=date,
                    exit_price=fill_price,
                    shares=position.shares,
                    entry_fee=position.entry_fee,
                    exit_fee=exit_fee,
                    pnl=pnl,
                    return_pct=pnl / basis * 100,
                    exit_reason=order.reason,
                )
            )

        for symbol, position in tuple(positions.items()):
            positions[symbol] = replace(
                position, market_price=float(bars[symbol]["open"].iloc[index])
            )

        remaining_entries = []
        for order in state.pending_orders:
            if order.order_date != date:
                remaining_entries.append(order)
                continue
            signal_index = date_indexes[order.signal_date]
            raw_open = float(bars[order.symbol]["open"].iloc[index])
            fill_price = raw_open * (1 + resolved.spread / 2 + resolved.slippage)
            stop, target = entry_levels(
                strategy_name,
                rules[order.symbol],
                params,
                signal_index,
                fill_price,
            )
            if stop is None or not math.isfinite(stop) or stop <= 0 or stop >= raw_open:
                rejected.append(
                    _fill_rejection(
                        date=date,
                        symbol=order.symbol,
                        requested_shares=order.shares,
                        cash=cash,
                        reason="invalid_stop_at_fill",
                    )
                )
                continue
            unsettled = sum(item.amount for item in settlements)
            opening_equity = cash + unsettled + sum(
                position.market_value for position in positions.values()
            )
            if opening_equity <= 0:
                rejected.append(
                    _fill_rejection(
                        date=date,
                        symbol=order.symbol,
                        requested_shares=order.shares,
                        cash=cash,
                        reason="fill_nonpositive_equity",
                    )
                )
                continue
            actual_sizing = size_entry(
                expected_open=raw_open,
                stop=stop,
                equity=opening_equity,
                config=resolved,
            )
            cash_per_share = actual_sizing.estimated_cash_per_share
            affordable = math.floor(cash / cash_per_share)
            classification = classifications[order.symbol]
            sector_value = sum(
                position.market_value
                for position in positions.values()
                if position.sector == classification.sector
            )
            cluster_value = sum(
                position.market_value
                for position in positions.values()
                if position.cluster == classification.cluster
            )
            sector_remaining = max(
                0.0, opening_equity * resolved.max_sector_fraction - sector_value
            )
            cluster_remaining = max(
                0.0, opening_equity * resolved.max_cluster_fraction - cluster_value
            )
            sector_shares = math.floor(sector_remaining / fill_price)
            cluster_shares = math.floor(cluster_remaining / fill_price)
            shares = min(
                order.shares,
                actual_sizing.requested_shares,
                affordable,
                sector_shares,
                cluster_shares,
            )
            if shares <= 0:
                if affordable <= 0:
                    reason = "fill_insufficient_cash"
                elif sector_shares <= 0:
                    reason = "fill_sector_limit"
                elif cluster_shares <= 0:
                    reason = "fill_cluster_limit"
                else:
                    reason = "fill_size_below_one_share"
                rejected.append(
                    _fill_rejection(
                        date=date,
                        symbol=order.symbol,
                        requested_shares=order.shares,
                        cash=cash,
                        reason=reason,
                    )
                )
                continue
            gross_cost = shares * fill_price
            entry_fee = gross_cost * resolved.commission
            cash_required = gross_cost + entry_fee
            cash -= cash_required
            if cash < -1e-8:
                raise RuntimeError("entry fill exceeded available settled cash")
            cash = max(0.0, cash)
            positions[order.symbol] = PortfolioPosition(
                symbol=order.symbol,
                shares=shares,
                entry_date=date,
                entry_price=fill_price,
                entry_fee=entry_fee,
                stop=stop,
                sector=classification.sector,
                cluster=classification.cluster,
                # Later orders at this same open must not see today's close.
                market_price=raw_open,
                target=target,
            )
            fills.append(
                PortfolioFill(
                    side="entry",
                    signal_date=order.signal_date,
                    fill_date=date,
                    symbol=order.symbol,
                    requested_shares=order.shares,
                    shares=shares,
                    price=fill_price,
                    fee=entry_fee,
                    net_amount=-cash_required,
                )
            )

        for symbol, position in tuple(positions.items()):
            positions[symbol] = replace(
                position, market_price=float(bars[symbol]["close"].iloc[index])
            )

        snapshot = _snapshot(
            date,
            cash=cash,
            settlements=settlements,
            positions=positions,
            previous_peak=state.peak_equity,
        )
        snapshots.append(snapshot)

        pending_exits = list(remaining_exits)
        exiting_symbols = {order.symbol for order in pending_exits}
        for symbol in symbols:
            position = positions.get(symbol)
            if position is None or symbol in exiting_symbols:
                continue
            updated_stop, reason = close_exit_decision(
                strategy_name,
                rules[symbol],
                params,
                index,
                float(bars[symbol]["close"].iloc[index]),
                position.stop,
                position.target,
            )
            positions[symbol] = replace(position, stop=updated_stop)
            if reason:
                pending_exits.append(
                    PendingExit(
                        signal_date=date,
                        order_date=next_date,
                        symbol=symbol,
                        reason=reason,
                    )
                )
                exiting_symbols.add(symbol)

        pending_entries = list(remaining_entries)
        candidates: list[CandidateOrder] = []
        occupied = set(positions) | {order.symbol for order in pending_entries}
        for symbol in symbols:
            if symbol in occupied or not bool(rules[symbol].entries.iloc[index]):
                continue
            close = float(bars[symbol]["close"].iloc[index])
            stop, _ = entry_levels(
                strategy_name, rules[symbol], params, index, close
            )
            classification = classifications[symbol]
            candidates.append(
                CandidateOrder(
                    signal_date=date,
                    order_date=next_date,
                    symbol=symbol,
                    expected_open=close,
                    stop=stop,
                    score=scores[symbol],
                    sector=classification.sector,
                    cluster=classification.cluster,
                )
            )

        allocation_state = PortfolioState(
            cash=cash,
            peak_equity=snapshot.peak_equity,
            halted=state.halted,
            positions=positions,
            pending_orders=tuple(pending_entries),
            pending_exits=tuple(pending_exits),
            settlements=tuple(settlements),
            rejected_orders=tuple(rejected),
        )
        allocation = allocate_entries(
            candidates,
            state=allocation_state,
            equity=snapshot.equity,
            config=resolved,
        )
        pending_entries.extend(allocation.accepted)
        rejected.extend(allocation.rejected)
        state = replace(
            allocation_state,
            pending_orders=tuple(pending_entries),
            rejected_orders=tuple(rejected),
        )

    return PortfolioReplay(
        strategy=strategy_name,
        state=state,
        fills=tuple(fills),
        trades=tuple(trades),
        equity=tuple(snapshots),
    )
