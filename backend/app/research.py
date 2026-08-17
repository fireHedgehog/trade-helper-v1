"""Guard rails for chronological, out-of-sample research.

This module only defines data partitions and manifests. It deliberately does not
choose parameters or evaluate candidate holdout performance. Existing SPY history
has already been inspected, so a tail partition is a workflow rehearsal rather
than a statistically untouched confirmatory sample.
"""

from __future__ import annotations

import itertools
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .execution import simulate, validate_bars


@dataclass(frozen=True)
class CandidateHoldout:
    start: str
    end: str
    bars: int


@dataclass(frozen=True)
class WalkForwardFold:
    number: int
    train_start: str
    train_end: str
    validation_start: str
    validation_end: str
    test_start: str
    test_end: str
    train_bars: int
    validation_bars: int
    test_bars: int

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class WindowEvaluation:
    requested_start: str
    requested_end: str
    actual_start: str
    actual_end: str
    bars: int
    strategy_return: float
    benchmark_return: float
    exposure: float
    max_drawdown: float
    calmar: float | None
    closed_trades: int
    dates: tuple[str, ...]
    strategy_daily_returns: tuple[float, ...]
    benchmark_daily_returns: tuple[float, ...]
    excess_daily_returns: tuple[float, ...]

    def summary(self) -> dict:
        return {
            key: value
            for key, value in asdict(self).items()
            if not key.endswith("_daily_returns") and key != "dates"
        }


@dataclass(frozen=True)
class CandidateWindowEvaluation:
    candidate: str
    params: dict
    eligible_symbols: tuple[str, ...]
    excluded_symbols: tuple[tuple[str, str], ...]
    median_strategy_return: float
    median_benchmark_return: float
    median_excess_return: float
    median_calmar: float | None
    median_max_drawdown: float
    median_exposure: float
    total_closed_trades: int
    dates: tuple[str, ...]
    strategy_daily_returns: tuple[float, ...]
    benchmark_daily_returns: tuple[float, ...]
    excess_daily_returns: tuple[float, ...]

    def summary(self) -> dict:
        return {
            key: value
            for key, value in asdict(self).items()
            if key != "dates" and not key.endswith("_daily_returns")
        }


def partition_candidate_holdout(
    bars: pd.DataFrame, *, holdout_bars: int
) -> tuple[pd.DataFrame, CandidateHoldout]:
    """Hide a historical tail for workflow rehearsal, not confirmation."""
    validate_bars(bars)
    if holdout_bars <= 0:
        raise ValueError("holdout_bars must be positive")
    if len(bars) <= holdout_bars:
        raise ValueError("holdout must leave at least one development bar")
    boundary = len(bars) - holdout_bars
    development = bars.iloc[:boundary].reset_index(drop=True).copy()
    reserved = bars.iloc[boundary:]
    return development, CandidateHoldout(
        start=str(reserved["date"].iloc[0]),
        end=str(reserved["date"].iloc[-1]),
        bars=len(reserved),
    )


def walk_forward_folds(
    development: pd.DataFrame,
    *,
    train_bars: int,
    validation_bars: int,
    test_bars: int,
    step_bars: int | None = None,
) -> list[WalkForwardFold]:
    """Build expanding-window folds with strictly later validation/test slices."""
    validate_bars(development)
    sizes = {
        "train_bars": train_bars,
        "validation_bars": validation_bars,
        "test_bars": test_bars,
    }
    if any(value <= 0 for value in sizes.values()):
        raise ValueError("train, validation, and test sizes must be positive")
    step = test_bars if step_bars is None else step_bars
    if step <= 0:
        raise ValueError("step_bars must be positive")

    folds: list[WalkForwardFold] = []
    train_end = train_bars
    number = 1
    while train_end + validation_bars + test_bars <= len(development):
        validation_end = train_end + validation_bars
        test_end = validation_end + test_bars
        folds.append(
            WalkForwardFold(
                number=number,
                train_start=str(development["date"].iloc[0]),
                train_end=str(development["date"].iloc[train_end - 1]),
                validation_start=str(development["date"].iloc[train_end]),
                validation_end=str(development["date"].iloc[validation_end - 1]),
                test_start=str(development["date"].iloc[validation_end]),
                test_end=str(development["date"].iloc[test_end - 1]),
                train_bars=train_end,
                validation_bars=validation_bars,
                test_bars=test_bars,
            )
        )
        train_end += step
        number += 1
    if not folds:
        needed = train_bars + validation_bars + test_bars
        raise ValueError(f"development sample has {len(development)} bars; need at least {needed}")
    return folds


def fold_manifest(folds: list[WalkForwardFold]) -> pd.DataFrame:
    """Small reviewable table; contains boundaries, never performance results."""
    return pd.DataFrame([fold.to_dict() for fold in folds])


def evaluate_window(
    bars: pd.DataFrame,
    *,
    strategy_name: str,
    params: dict,
    start: str,
    end: str,
    initial_cash: float = 100_000.0,
    commission: float = 0.001,
    spread: float = 0.0002,
    slippage: float = 0.0005,
    annual_cash_yield: float = 0.0,
) -> WindowEvaluation:
    """Evaluate one later window using only bars available through its end.

    Earlier bars remain as legitimate indicator and position-state context. Bars
    after ``end`` are cut before rule construction, making the no-future boundary
    explicit and testable. The comparison is the ADR 0003 constant-exposure
    control, not a tradable timing replica.
    """
    validate_bars(bars)
    if start > end:
        raise ValueError("evaluation start must not be after end")
    history = bars[bars["date"] <= end].reset_index(drop=True)
    if history.empty:
        raise ValueError("no bars are available on or before evaluation end")
    simulation = simulate(
        history,
        strategy_name,
        params,
        initial_cash=initial_cash,
        commission=commission,
        spread=spread,
        slippage=slippage,
        annual_cash_yield=annual_cash_yield,
    )
    equity = pd.DataFrame(simulation.equity)
    equity["strategy_return"] = equity["equity"].pct_change()
    asset = history[["date", "close"]].copy()
    asset["asset_return"] = asset["close"].astype(float).pct_change()
    daily = equity.merge(asset[["date", "asset_return"]], on="date", how="inner")
    daily = daily[(daily["date"] >= start) & (daily["date"] <= end)].copy()
    daily = daily.dropna(subset=["strategy_return", "asset_return"])
    if len(daily) < 2:
        raise ValueError("evaluation window needs at least two return observations")

    exposure = float(daily["exposed"].mean())
    cash_daily = (1 + annual_cash_yield) ** (1 / 252) - 1
    daily["benchmark_return"] = (
        exposure * daily["asset_return"] + (1 - exposure) * cash_daily
    )
    daily["excess_return"] = daily["strategy_return"] - daily["benchmark_return"]
    strategy_return = float((1 + daily["strategy_return"]).prod() - 1)
    benchmark_return = float((1 + daily["benchmark_return"]).prod() - 1)
    wealth = pd.concat(
        [pd.Series([1.0]), (1 + daily["strategy_return"]).cumprod().reset_index(drop=True)],
        ignore_index=True,
    )
    max_drawdown = float((wealth / wealth.cummax() - 1).min())
    first = pd.Timestamp(daily["date"].iloc[0])
    last = pd.Timestamp(daily["date"].iloc[-1])
    years = max((last - first).days / 365.25, 1 / 252)
    cagr = (1 + strategy_return) ** (1 / years) - 1 if strategy_return > -1 else -1.0
    calmar = cagr / abs(max_drawdown) if max_drawdown < 0 else None
    closed_trades = sum(
        start <= str(trade["exit_date"]) <= end for trade in simulation.trades
    )
    return WindowEvaluation(
        requested_start=start,
        requested_end=end,
        actual_start=str(daily["date"].iloc[0]),
        actual_end=str(daily["date"].iloc[-1]),
        bars=len(daily),
        strategy_return=strategy_return,
        benchmark_return=benchmark_return,
        exposure=exposure,
        max_drawdown=max_drawdown,
        calmar=calmar,
        closed_trades=closed_trades,
        dates=tuple(str(value) for value in daily["date"]),
        strategy_daily_returns=tuple(float(value) for value in daily["strategy_return"]),
        benchmark_daily_returns=tuple(float(value) for value in daily["benchmark_return"]),
        excess_daily_returns=tuple(float(value) for value in daily["excess_return"]),
    )


def evaluate_candidate_window(
    bars_by_symbol: dict[str, pd.DataFrame],
    *,
    universe: list[str],
    strategy_name: str,
    params: dict,
    training_start: str,
    start: str,
    end: str,
    minimum_symbols: int,
    costs: dict,
) -> CandidateWindowEvaluation:
    """Aggregate one candidate across the locked universe on common dates."""
    evaluations: dict[str, WindowEvaluation] = {}
    excluded: list[tuple[str, str]] = []
    for symbol in universe:
        bars = bars_by_symbol.get(symbol)
        if bars is None or bars.empty:
            excluded.append((symbol, "missing"))
            continue
        if str(bars["date"].iloc[0]) > training_start:
            excluded.append((symbol, "history starts after fold training start"))
            continue
        if str(bars["date"].iloc[-1]) < end:
            excluded.append((symbol, "history ends before evaluation end"))
            continue
        try:
            evaluations[symbol] = evaluate_window(
                bars,
                strategy_name=strategy_name,
                params=params,
                start=start,
                end=end,
                commission=float(costs["commission_per_side"]),
                spread=float(costs["quoted_spread"]),
                slippage=float(costs["slippage_per_fill"]),
                annual_cash_yield=float(costs["annual_cash_yield"]),
            )
        except (KeyError, ValueError) as exc:
            excluded.append((symbol, f"evaluation failed: {exc}"))
    if len(evaluations) < minimum_symbols:
        raise ValueError(
            f"candidate has {len(evaluations)} eligible symbols; need {minimum_symbols}; "
            f"excluded={dict(excluded)}"
        )

    excess_series = {
        symbol: pd.Series(result.excess_daily_returns, index=result.dates, dtype=float)
        for symbol, result in evaluations.items()
    }
    strategy_series = {
        symbol: pd.Series(result.strategy_daily_returns, index=result.dates, dtype=float)
        for symbol, result in evaluations.items()
    }
    benchmark_series = {
        symbol: pd.Series(result.benchmark_daily_returns, index=result.dates, dtype=float)
        for symbol, result in evaluations.items()
    }
    aligned_excess = pd.concat(excess_series, axis=1, join="inner").sort_index()
    common_dates = aligned_excess.index
    if len(common_dates) < 2:
        raise ValueError("eligible symbols have fewer than two common return dates")
    equal_weight_excess = aligned_excess.mean(axis=1)
    equal_weight_strategy = pd.concat(strategy_series, axis=1).loc[common_dates].mean(axis=1)
    equal_weight_benchmark = pd.concat(benchmark_series, axis=1).loc[common_dates].mean(axis=1)
    symbol_excess = [
        result.strategy_return - result.benchmark_return
        for result in evaluations.values()
    ]
    calmars = [
        result.calmar
        for result in evaluations.values()
        if result.calmar is not None and np.isfinite(result.calmar)
    ]
    candidate = json.dumps(params, sort_keys=True, separators=(",", ":"))
    return CandidateWindowEvaluation(
        candidate=candidate,
        params=dict(params),
        eligible_symbols=tuple(evaluations),
        excluded_symbols=tuple(excluded),
        median_strategy_return=float(
            np.median([result.strategy_return for result in evaluations.values()])
        ),
        median_benchmark_return=float(
            np.median([result.benchmark_return for result in evaluations.values()])
        ),
        median_excess_return=float(np.median(symbol_excess)),
        median_calmar=float(np.median(calmars)) if calmars else None,
        median_max_drawdown=float(
            np.median([result.max_drawdown for result in evaluations.values()])
        ),
        median_exposure=float(
            np.median([result.exposure for result in evaluations.values()])
        ),
        total_closed_trades=sum(result.closed_trades for result in evaluations.values()),
        dates=tuple(str(value) for value in common_dates),
        strategy_daily_returns=tuple(float(value) for value in equal_weight_strategy),
        benchmark_daily_returns=tuple(float(value) for value in equal_weight_benchmark),
        excess_daily_returns=tuple(float(value) for value in equal_weight_excess),
    )


def load_experiment_spec(path: str | Path) -> dict:
    """Load and validate a preregistration without evaluating any returns."""
    spec = json.loads(Path(path).read_text())
    required = {
        "experiment_id", "status", "strategy", "universe", "parameter_grid",
        "candidate_count", "costs", "partitions", "multiple_testing", "selection",
    }
    missing = required - set(spec)
    if missing:
        raise ValueError(f"experiment spec missing: {', '.join(sorted(missing))}")
    if spec["status"] != "preregistered_no_results":
        raise ValueError("new evaluation requires preregistered_no_results status")
    universe = spec["universe"]
    if not universe or len(universe) != len(set(universe)):
        raise ValueError("universe must be non-empty and unique")
    grid = spec["parameter_grid"]
    if not grid or any(not isinstance(values, list) or not values for values in grid.values()):
        raise ValueError("every parameter grid dimension must be a non-empty list")
    combinations = list(itertools.product(*grid.values()))
    if len(combinations) != spec["candidate_count"]:
        raise ValueError("candidate_count does not match parameter grid")
    correction = spec["multiple_testing"]
    if correction.get("family_size") != len(combinations):
        raise ValueError("multiple-testing family must cover every candidate")
    if correction.get("adjustment") != "Holm family-wise error rate":
        raise ValueError("unsupported multiple-testing adjustment")
    partitions = spec["partitions"]
    if partitions.get("calendar_symbol") not in universe:
        raise ValueError("partition calendar symbol must belong to the locked universe")
    if not partitions.get("common_history_start"):
        raise ValueError("partitions must lock a common_history_start")
    if partitions.get("calendar_end_policy") != (
        "earliest latest-date across the locked universe"
    ):
        raise ValueError("unsupported calendar end policy")
    selection = spec["selection"]
    if selection.get("phase") != "validation":
        raise ValueError("candidate selection phase must be validation")
    if not 1 <= selection.get("minimum_symbols", 0) <= len(universe):
        raise ValueError("selection minimum_symbols must fit the locked universe")
    if selection.get("no_survivor") != "hold cash for the following test fold":
        raise ValueError("selection must define the conservative no-survivor action")
    return spec


def parameter_candidates(spec: dict) -> list[dict]:
    """Expand the locked grid in deterministic manifest order."""
    grid = spec["parameter_grid"]
    keys = list(grid)
    return [dict(zip(keys, values)) for values in itertools.product(*(grid[key] for key in keys))]


def holm_adjust(p_values: list[float]) -> list[float]:
    """Holm step-down adjusted p-values, preserving the caller's order."""
    if any(not 0 <= value <= 1 for value in p_values):
        raise ValueError("p-values must be between 0 and 1")
    count = len(p_values)
    ranked = sorted(enumerate(p_values), key=lambda item: item[1])
    adjusted = [0.0] * count
    running = 0.0
    for rank, (original, value) in enumerate(ranked):
        running = max(running, min(1.0, (count - rank) * value))
        adjusted[original] = running
    return adjusted


def circular_block_bootstrap_p_value(
    excess_returns: list[float] | pd.Series,
    *,
    block_bars: int = 20,
    resamples: int = 5_000,
    seed: int = 17_291,
) -> float:
    """One-sided p-value for positive mean excess return under serial dependence.

    Returns are centered to impose the zero-mean null, then sampled in circular
    contiguous blocks. The add-one correction prevents a misleading zero p-value.
    """
    values = np.asarray(excess_returns, dtype=float)
    values = values[np.isfinite(values)]
    if len(values) < 2:
        raise ValueError("bootstrap requires at least two finite returns")
    if block_bars <= 0 or block_bars > len(values):
        raise ValueError("block_bars must be between 1 and the sample length")
    if resamples <= 0:
        raise ValueError("resamples must be positive")

    observed = float(values.mean())
    centered = values - observed
    blocks_needed = (len(values) + block_bars - 1) // block_bars
    offsets = np.arange(block_bars)
    rng = np.random.default_rng(seed)
    at_least_observed = 0
    for _ in range(resamples):
        starts = rng.integers(0, len(values), size=blocks_needed)
        indexes = (starts[:, None] + offsets) % len(values)
        boot_mean = float(centered[indexes.ravel()[: len(values)]].mean())
        if boot_mean >= observed:
            at_least_observed += 1
    return (at_least_observed + 1) / (resamples + 1)


def multiple_testing_report(
    returns_by_candidate: dict[str, list[float] | pd.Series],
    *,
    block_bars: int,
    resamples: int,
    alpha: float,
    seed: int = 17_291,
) -> list[dict]:
    """Apply the locked bootstrap and Holm correction to one candidate family."""
    if not returns_by_candidate:
        raise ValueError("candidate family cannot be empty")
    if not 0 < alpha < 1:
        raise ValueError("alpha must be between 0 and 1")
    names = list(returns_by_candidate)
    raw = [
        circular_block_bootstrap_p_value(
            returns_by_candidate[name],
            block_bars=block_bars,
            resamples=resamples,
            seed=seed + index,
        )
        for index, name in enumerate(names)
    ]
    adjusted = holm_adjust(raw)
    return [
        {
            "candidate": name,
            "raw_p_value": raw[index],
            "holm_p_value": adjusted[index],
            "reject_zero_excess": adjusted[index] <= alpha,
        }
        for index, name in enumerate(names)
    ]


def select_validation_candidate(
    evaluations: list[CandidateWindowEvaluation],
    *,
    block_bars: int,
    resamples: int,
    alpha: float,
    expected_family_size: int | None = None,
    seed: int = 17_291,
) -> tuple[CandidateWindowEvaluation | None, list[dict]]:
    """Apply the locked significance gate and deterministic ranking contract."""
    if expected_family_size is not None and len(evaluations) != expected_family_size:
        raise ValueError(
            f"candidate family has {len(evaluations)} evaluations; "
            f"expected {expected_family_size}"
        )
    if len({item.candidate for item in evaluations}) != len(evaluations):
        raise ValueError("candidate identifiers must be unique")
    by_id = {item.candidate: item for item in evaluations}
    report = multiple_testing_report(
        {item.candidate: list(item.excess_daily_returns) for item in evaluations},
        block_bars=block_bars,
        resamples=resamples,
        alpha=alpha,
        seed=seed,
    )
    survivors = [
        by_id[row["candidate"]] for row in report if row["reject_zero_excess"]
    ]
    if not survivors:
        return None, report

    def ranking(item: CandidateWindowEvaluation) -> tuple:
        calmar = item.median_calmar if item.median_calmar is not None else -math.inf
        return (
            -item.median_excess_return,
            -calmar,
            -item.median_max_drawdown,
            item.candidate,
        )

    return sorted(survivors, key=ranking)[0], report
