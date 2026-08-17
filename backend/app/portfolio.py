"""Deterministic, strategy-independent portfolio sizing and order allocation.

This module contains no market-data or broker I/O. It converts already-created
entry candidates into cash-constrained pending orders under the contract in ADR
0004. A later replay engine will own fills, exits, marking, and the drawdown kill
switch.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass(frozen=True)
class PortfolioConfig:
    initial_cash: float = 100_000.0
    risk_per_trade: float = 0.005
    max_position_fraction: float = 0.10
    max_sector_fraction: float = 0.25
    max_cluster_fraction: float = 0.30
    drawdown_limit: float = 0.15
    commission: float = 0.001
    spread: float = 0.0002
    slippage: float = 0.0005

    def __post_init__(self) -> None:
        if not math.isfinite(self.initial_cash) or self.initial_cash <= 0:
            raise ValueError("initial_cash must be finite and positive")
        for name in (
            "risk_per_trade",
            "max_position_fraction",
            "max_sector_fraction",
            "max_cluster_fraction",
            "drawdown_limit",
        ):
            value = getattr(self, name)
            if not math.isfinite(value) or not 0 < value <= 1:
                raise ValueError(f"{name} must be finite and in (0, 1]")
        for name in ("commission", "spread", "slippage"):
            value = getattr(self, name)
            if not math.isfinite(value) or not 0 <= value < 1:
                raise ValueError(f"{name} must be finite and in [0, 1)")
        if self.spread / 2 + self.slippage >= 1:
            raise ValueError("combined spread and slippage must leave a positive exit price")


@dataclass(frozen=True)
class PortfolioPosition:
    symbol: str
    shares: int
    entry_date: str
    entry_price: float
    entry_fee: float
    stop: float
    sector: str
    cluster: str
    market_price: float

    @property
    def market_value(self) -> float:
        return self.shares * self.market_price


@dataclass(frozen=True)
class CandidateOrder:
    signal_date: str
    order_date: str
    symbol: str
    expected_open: float
    stop: float | None
    score: float
    sector: str | None
    cluster: str | None


@dataclass(frozen=True)
class EntrySizing:
    requested_shares: int
    estimated_fill_price: float
    estimated_cash_per_share: float
    estimated_loss_per_share: float
    risk_budget: float
    notional_budget: float


@dataclass(frozen=True)
class PendingOrder:
    signal_date: str
    order_date: str
    symbol: str
    requested_shares: int
    shares: int
    estimated_fill_price: float
    estimated_cash_required: float
    stop: float
    score: float
    sector: str
    cluster: str

    @property
    def estimated_market_value(self) -> float:
        return self.shares * self.estimated_fill_price


@dataclass(frozen=True)
class RejectedOrder:
    date: str
    symbol: str
    requested_shares: int
    available_cash: float
    reason: str


@dataclass(frozen=True)
class PortfolioState:
    cash: float
    peak_equity: float
    halted: bool = False
    positions: dict[str, PortfolioPosition] = field(default_factory=dict)
    pending_orders: tuple[PendingOrder, ...] = ()
    rejected_orders: tuple[RejectedOrder, ...] = ()


@dataclass(frozen=True)
class AllocationResult:
    accepted: tuple[PendingOrder, ...]
    rejected: tuple[RejectedOrder, ...]
    remaining_cash: float


def initial_portfolio(config: PortfolioConfig | None = None) -> PortfolioState:
    """Create the explicit account state used by future portfolio replays."""
    resolved = config or PortfolioConfig()
    return PortfolioState(cash=resolved.initial_cash, peak_equity=resolved.initial_cash)


def size_entry(
    *,
    expected_open: float,
    stop: float,
    equity: float,
    config: PortfolioConfig,
) -> EntrySizing:
    """Size an entry from stop loss and notional budgets, including modeled costs.

    The risk budget estimates a next-open entry followed by a stop-price exit,
    charging adverse spread/slippage and commission on both sides. This is more
    conservative than treating ``expected_open - stop`` as the complete loss.
    """
    for name, value in {"expected_open": expected_open, "stop": stop, "equity": equity}.items():
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite")
    if expected_open <= 0:
        raise ValueError("expected_open must be positive")
    if equity <= 0:
        raise ValueError("equity must be positive")
    if stop <= 0 or stop >= expected_open:
        raise ValueError("stop must be positive and below expected_open")

    entry_fill = expected_open * (1 + config.spread / 2 + config.slippage)
    stop_fill = stop * (1 - config.spread / 2 - config.slippage)
    cash_per_share = entry_fill * (1 + config.commission)
    stop_proceeds_per_share = stop_fill * (1 - config.commission)
    loss_per_share = cash_per_share - stop_proceeds_per_share
    risk_budget = equity * config.risk_per_trade
    notional_budget = equity * config.max_position_fraction
    risk_shares = math.floor(risk_budget / loss_per_share)
    notional_shares = math.floor(notional_budget / entry_fill)

    return EntrySizing(
        requested_shares=max(0, min(risk_shares, notional_shares)),
        estimated_fill_price=entry_fill,
        estimated_cash_per_share=cash_per_share,
        estimated_loss_per_share=loss_per_share,
        risk_budget=risk_budget,
        notional_budget=notional_budget,
    )


def _candidate_error(candidate: CandidateOrder) -> str | None:
    if not candidate.symbol.strip():
        return "invalid_symbol"
    if not math.isfinite(candidate.expected_open) or candidate.expected_open <= 0:
        return "invalid_price"
    if candidate.stop is None or not math.isfinite(candidate.stop):
        return "invalid_stop"
    if candidate.stop <= 0 or candidate.stop >= candidate.expected_open:
        return "invalid_stop"
    if not math.isfinite(candidate.score):
        return "invalid_score"
    if not candidate.sector or not candidate.sector.strip():
        return "missing_classification"
    if not candidate.cluster or not candidate.cluster.strip():
        return "missing_classification"
    return None


def _rejection(
    candidate: CandidateOrder,
    *,
    requested_shares: int,
    available_cash: float,
    reason: str,
) -> RejectedOrder:
    return RejectedOrder(
        date=candidate.order_date,
        symbol=candidate.symbol,
        requested_shares=requested_shares,
        available_cash=max(0.0, available_cash),
        reason=reason,
    )


def allocate_entries(
    candidates: list[CandidateOrder],
    *,
    state: PortfolioState,
    equity: float,
    config: PortfolioConfig,
) -> AllocationResult:
    """Allocate concurrent entry candidates without exceeding account limits.

    Valid candidates are processed by descending locked score and then ascending
    symbol. Orders can be reduced to the largest whole-share quantity that fits;
    a zero-share result is rejected with a stable machine-readable reason.
    """
    if not math.isfinite(equity) or equity <= 0:
        raise ValueError("equity must be finite and positive")
    if not math.isfinite(state.cash) or state.cash < 0:
        raise ValueError("portfolio cash must be finite and non-negative")

    accepted: list[PendingOrder] = []
    rejected: list[RejectedOrder] = []
    reserved_cash = sum(order.estimated_cash_required for order in state.pending_orders)
    available_cash = max(0.0, state.cash - reserved_cash)
    occupied_symbols = set(state.positions) | {
        order.symbol for order in state.pending_orders
    }
    sector_value: dict[str, float] = {}
    cluster_value: dict[str, float] = {}

    for position in state.positions.values():
        if (
            position.shares <= 0
            or not math.isfinite(position.market_value)
            or position.market_value <= 0
        ):
            raise ValueError("portfolio positions must have finite positive exposure")
        sector_value[position.sector] = sector_value.get(position.sector, 0.0) + position.market_value
        cluster_value[position.cluster] = cluster_value.get(position.cluster, 0.0) + position.market_value
    for order in state.pending_orders:
        sector_value[order.sector] = sector_value.get(order.sector, 0.0) + order.estimated_market_value
        cluster_value[order.cluster] = cluster_value.get(order.cluster, 0.0) + order.estimated_market_value

    def priority(candidate: CandidateOrder) -> tuple[float, str]:
        score = candidate.score if math.isfinite(candidate.score) else -math.inf
        return (-score, candidate.symbol)

    for candidate in sorted(candidates, key=priority):
        error = _candidate_error(candidate)
        if error:
            rejected.append(
                _rejection(
                    candidate,
                    requested_shares=0,
                    available_cash=available_cash,
                    reason=error,
                )
            )
            continue

        assert candidate.stop is not None
        assert candidate.sector is not None
        assert candidate.cluster is not None
        sizing = size_entry(
            expected_open=candidate.expected_open,
            stop=candidate.stop,
            equity=equity,
            config=config,
        )
        requested = sizing.requested_shares
        if state.halted:
            rejected.append(
                _rejection(
                    candidate,
                    requested_shares=requested,
                    available_cash=available_cash,
                    reason="portfolio_halted",
                )
            )
            continue
        if candidate.symbol in occupied_symbols:
            rejected.append(
                _rejection(
                    candidate,
                    requested_shares=requested,
                    available_cash=available_cash,
                    reason="position_exists",
                )
            )
            continue
        if requested == 0:
            rejected.append(
                _rejection(
                    candidate,
                    requested_shares=0,
                    available_cash=available_cash,
                    reason="size_below_one_share",
                )
            )
            continue

        cash_shares = math.floor(available_cash / sizing.estimated_cash_per_share)
        sector_remaining = max(
            0.0,
            equity * config.max_sector_fraction - sector_value.get(candidate.sector, 0.0),
        )
        cluster_remaining = max(
            0.0,
            equity * config.max_cluster_fraction - cluster_value.get(candidate.cluster, 0.0),
        )
        sector_shares = math.floor(sector_remaining / sizing.estimated_fill_price)
        cluster_shares = math.floor(cluster_remaining / sizing.estimated_fill_price)
        shares = min(requested, cash_shares, sector_shares, cluster_shares)

        if shares <= 0:
            if cash_shares <= 0:
                reason = "insufficient_cash"
            elif sector_shares <= 0:
                reason = "sector_limit"
            else:
                reason = "cluster_limit"
            rejected.append(
                _rejection(
                    candidate,
                    requested_shares=requested,
                    available_cash=available_cash,
                    reason=reason,
                )
            )
            continue

        cash_required = shares * sizing.estimated_cash_per_share
        pending = PendingOrder(
            signal_date=candidate.signal_date,
            order_date=candidate.order_date,
            symbol=candidate.symbol,
            requested_shares=requested,
            shares=shares,
            estimated_fill_price=sizing.estimated_fill_price,
            estimated_cash_required=cash_required,
            stop=candidate.stop,
            score=candidate.score,
            sector=candidate.sector,
            cluster=candidate.cluster,
        )
        accepted.append(pending)
        occupied_symbols.add(candidate.symbol)
        available_cash = max(0.0, available_cash - cash_required)
        sector_value[candidate.sector] = sector_value.get(candidate.sector, 0.0) + pending.estimated_market_value
        cluster_value[candidate.cluster] = cluster_value.get(candidate.cluster, 0.0) + pending.estimated_market_value

    return AllocationResult(
        accepted=tuple(accepted),
        rejected=tuple(rejected),
        remaining_cash=available_cash,
    )
