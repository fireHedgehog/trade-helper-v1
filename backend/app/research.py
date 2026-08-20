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


# --- SMA Cross v1 exposure-reduction / volatility-state placebo (Stage 9A Cycle 2) ---
# Implements docs/research-protocols/sma-cross-v1-exposure-reduction.md. Both
# trailing states are self-referential (no external target level); the
# volatility state is the locked comparator, not a separate candidate.

SMA_CROSS_WARM_UP_SESSIONS = 252
SMA_CROSS_FAST = 20
SMA_CROSS_SLOW = 50
SMA_CROSS_VOL_LOOKBACK = 20
SMA_CROSS_BLOCK_BARS = 20
SMA_CROSS_RESAMPLES = 5_000
SMA_CROSS_SEED = 17_291
SMA_CROSS_ANNUALIZATION = math.sqrt(252)


def _rolling_mean(values: np.ndarray, window: int) -> np.ndarray:
    """NaN-padded rolling mean; result[i] uses values[i-window+1:i+1]."""
    n = len(values)
    result = np.full(n, np.nan)
    if window > n:
        return result
    cumsum = np.concatenate([[0.0], np.cumsum(values)])
    result[window - 1 :] = (cumsum[window:] - cumsum[:-window]) / window
    return result


def _rolling_std(values: np.ndarray, window: int) -> np.ndarray:
    """NaN-padded rolling population standard deviation."""
    n = len(values)
    result = np.full(n, np.nan)
    if window > n:
        return result
    mean = _rolling_mean(values, window)
    cumsum_sq = np.concatenate([[0.0], np.cumsum(values**2)])
    mean_sq = np.full(n, np.nan)
    mean_sq[window - 1 :] = (cumsum_sq[window:] - cumsum_sq[:-window]) / window
    variance = np.clip(mean_sq - mean**2, a_min=0.0, a_max=None)
    result[window - 1 :] = np.sqrt(variance[window - 1 :])
    return result


def _expanding_median(values: np.ndarray) -> np.ndarray:
    """Expanding median from the first finite value onward; NaN before that."""
    series = pd.Series(values)
    valid = series[series.notna()]
    result = pd.Series(np.nan, index=series.index)
    if not valid.empty:
        result.loc[valid.index] = valid.expanding(min_periods=1).median()
    return result.to_numpy()


def log_returns_from_closes(closes: np.ndarray) -> np.ndarray:
    """Day-0-padded log returns; index i is the return realized arriving at closes[i]."""
    padded = np.empty(len(closes))
    padded[0] = 0.0
    padded[1:] = np.diff(np.log(closes))
    return padded


def sma_cross_state(log_returns_padded: np.ndarray) -> np.ndarray:
    """State_SMA(t) = 1{SMA_fast(t) > SMA_slow(t)} on a reconstructed price path.

    Scale-invariant: SMA_fast > SMA_slow does not depend on the arbitrary base
    used to reconstruct the path from returns, so this gives byte-identical
    results whether fed real closes' own returns or a resampled return path.
    """
    closes_proxy = np.exp(np.cumsum(log_returns_padded))
    fast = _rolling_mean(closes_proxy, SMA_CROSS_FAST)
    slow = _rolling_mean(closes_proxy, SMA_CROSS_SLOW)
    return np.where(np.isfinite(fast) & np.isfinite(slow), fast > slow, False)


def sma_cross_volatility_state(log_returns_padded: np.ndarray) -> np.ndarray:
    """State_Vol(t) = 1{trailing_vol_20(t) <= expanding_median(trailing_vol_20)(t)}."""
    trailing_vol = (
        _rolling_std(log_returns_padded, SMA_CROSS_VOL_LOOKBACK) * SMA_CROSS_ANNUALIZATION
    )
    expanding_med = _expanding_median(trailing_vol)
    return np.where(
        np.isfinite(trailing_vol) & np.isfinite(expanding_med),
        trailing_vol <= expanding_med,
        False,
    )


def _max_drawdown_magnitude(log_returns: np.ndarray) -> float:
    """Positive magnitude of the worst peak-to-trough decline; 0 if none."""
    wealth = np.exp(np.cumsum(log_returns))
    running_max = np.maximum.accumulate(wealth)
    drawdown = wealth / running_max - 1.0
    return float(-drawdown.min())


def sma_cross_delta_stats(
    log_returns_padded: np.ndarray, state: np.ndarray
) -> tuple[float, float]:
    """(delta_sigma, delta_mdd) on the post-warm-up region; negative is favourable.

    state[i] gates the return realized moving from close i to close i+1
    (state(t-1) gates return(t)); evaluation begins at close
    SMA_CROSS_WARM_UP_SESSIONS so both indicators are long stable.
    """
    n = len(log_returns_padded)
    start = SMA_CROSS_WARM_UP_SESSIONS
    raw = log_returns_padded[start:]
    gate = state[start - 1 : n - 1]
    gated = raw * gate
    delta_sigma = (float(np.std(gated)) - float(np.std(raw))) * SMA_CROSS_ANNUALIZATION
    delta_mdd = _max_drawdown_magnitude(gated) - _max_drawdown_magnitude(raw)
    return delta_sigma, delta_mdd


def sma_cross_bootstrap(
    closes: np.ndarray,
    state_fn,
    *,
    block_bars: int = SMA_CROSS_BLOCK_BARS,
    resamples: int = SMA_CROSS_RESAMPLES,
    seed: int = SMA_CROSS_SEED,
) -> dict:
    """One-sided p-values for a favourable (negative) delta_sigma/delta_mdd.

    Extends circular_block_bootstrap_p_value's scaffold to a state-recomputing
    variant: each resample reconstructs a synthetic price path and recomputes
    the trailing state on it, rather than resampling a precomputed statistic.
    The null is "no informative relationship between trailing state and
    subsequent regime beyond what block-preserved serial dependence produces" —
    returns are not centered/demeaned, unlike circular_block_bootstrap_p_value's
    zero-mean null, because that would remove the vol-clustering structure this
    test is specifically about.
    """
    log_returns_padded = log_returns_from_closes(closes)
    n = len(log_returns_padded)
    if n <= SMA_CROSS_WARM_UP_SESSIONS + SMA_CROSS_SLOW:
        raise ValueError("series too short for warm-up plus evaluation")

    observed_state = state_fn(log_returns_padded)
    observed_delta_sigma, observed_delta_mdd = sma_cross_delta_stats(
        log_returns_padded, observed_state
    )

    values = log_returns_padded[1:]
    if block_bars <= 0 or block_bars > len(values):
        raise ValueError("block_bars must be between 1 and the sample length")
    if resamples <= 0:
        raise ValueError("resamples must be positive")

    blocks_needed = (len(values) + block_bars - 1) // block_bars
    offsets = np.arange(block_bars)
    rng = np.random.default_rng(seed)
    at_least_sigma = 0
    at_least_mdd = 0
    for _ in range(resamples):
        starts = rng.integers(0, len(values), size=blocks_needed)
        indexes = (starts[:, None] + offsets) % len(values)
        resampled_values = values[indexes.ravel()[: len(values)]]
        resampled_padded = np.concatenate([[0.0], resampled_values])
        resampled_state = state_fn(resampled_padded)
        resampled_delta_sigma, resampled_delta_mdd = sma_cross_delta_stats(
            resampled_padded, resampled_state
        )
        if resampled_delta_sigma <= observed_delta_sigma:
            at_least_sigma += 1
        if resampled_delta_mdd <= observed_delta_mdd:
            at_least_mdd += 1
    return {
        "observed_delta_sigma": observed_delta_sigma,
        "p_delta_sigma": (at_least_sigma + 1) / (resamples + 1),
        "observed_delta_mdd": observed_delta_mdd,
        "p_delta_mdd": (at_least_mdd + 1) / (resamples + 1),
    }


# --- RSI(14) oversold-crossing short-horizon reversal (Stage 9A Cycle 3) ---
# Implements docs/research-protocols/rsi-oversold-reversal-v1.md. Reuses the
# block-resample-and-recompute scaffold proven by sma_cross_bootstrap, applied
# to a sparse event/forward-return statistic instead of a continuous gated
# exposure — deliberately avoids Cycle 1's caliper-matching failure mode by
# never constructing a separate matched control set.

RSI_PERIOD = 14
RSI_OVERSOLD = 30.0
RSI_WARM_UP_SESSIONS = 100
RSI_EVENT_COOLDOWN = 10
RSI_FORWARD_HORIZON = 10
RSI_PLACEBO_LOOKBACK = 14
RSI_PLACEBO_QUANTILE = 0.10
RSI_MIN_EVENT_COUNT = 15
RSI_BLOCK_BARS = 20
RSI_RESAMPLES = 5_000
RSI_SEED = 17_291


def _expanding_quantile(values: np.ndarray, quantile: float) -> np.ndarray:
    """Expanding quantile from the first finite value onward; NaN before that."""
    series = pd.Series(values)
    valid = series[series.notna()]
    result = pd.Series(np.nan, index=series.index)
    if not valid.empty:
        result.loc[valid.index] = valid.expanding(min_periods=1).quantile(quantile)
    return result.to_numpy()


def rsi_from_log_returns(log_returns_padded: np.ndarray, period: int = RSI_PERIOD) -> np.ndarray:
    """RSI(14) exactly as strategies.py::RsiReversion computes it: Wilder EWM
    on raw price differences (not log returns) reconstructed from the path."""
    closes_proxy = np.exp(np.cumsum(log_returns_padded))
    delta = np.diff(closes_proxy, prepend=np.nan)
    delta_series = pd.Series(delta)
    gain = delta_series.clip(lower=0).ewm(alpha=1 / period, adjust=False).mean()
    loss = (-delta_series.clip(upper=0)).ewm(alpha=1 / period, adjust=False).mean()
    rsi = 100 - 100 / (1 + gain / loss.replace(0, 1e-12))
    return rsi.to_numpy()


def rsi_crossing_events(rsi: np.ndarray, threshold: float = RSI_OVERSOLD) -> np.ndarray:
    """Event(t) = 1{RSI(t) < threshold and RSI(t-1) >= threshold}."""
    below = rsi < threshold
    prev_below = np.concatenate([[False], below[:-1]])
    return below & ~prev_below


def rsi_placebo_events(
    log_returns_padded: np.ndarray,
    lookback: int = RSI_PLACEBO_LOOKBACK,
    quantile: float = RSI_PLACEBO_QUANTILE,
) -> np.ndarray:
    """Placebo(t) = 1{trailing lookback-session return <= its own expanding
    quantile(t)} — self-referential, no full-sample calibration."""
    trailing_sum = _rolling_mean(log_returns_padded, lookback) * lookback
    expanding_q = _expanding_quantile(trailing_sum, quantile)
    return np.where(
        np.isfinite(trailing_sum) & np.isfinite(expanding_q),
        trailing_sum <= expanding_q,
        False,
    )


def _apply_cooldown(event_indices: np.ndarray, cooldown: int) -> np.ndarray:
    """Keep only events at least `cooldown` sessions after the previously kept one."""
    kept = []
    last = -cooldown - 1
    for idx in event_indices:
        if idx - last > cooldown:
            kept.append(idx)
            last = idx
    return np.asarray(kept, dtype=int)


def _mean_forward_return(
    log_returns_padded: np.ndarray, event_indices: np.ndarray, horizon: int
) -> tuple[float, int]:
    """Mean cumulative forward log return over `horizon` sessions after each
    event; events too close to the sample end (no full forward window) are
    excluded. Returns (mean, usable_event_count)."""
    n = len(log_returns_padded)
    cumsum = np.concatenate([[0.0], np.cumsum(log_returns_padded)])
    usable = event_indices[event_indices + horizon < n]
    if len(usable) == 0:
        return 0.0, 0
    forward = cumsum[usable + horizon + 1] - cumsum[usable + 1]
    return float(forward.mean()), len(usable)


def rsi_event_forward_return(
    log_returns_padded: np.ndarray,
    *,
    warm_up: int = RSI_WARM_UP_SESSIONS,
    cooldown: int = RSI_EVENT_COOLDOWN,
    horizon: int = RSI_FORWARD_HORIZON,
) -> tuple[float, int]:
    """Observed mean forward return and usable event count for the RSI event,
    on data at or after `warm_up`."""
    rsi = rsi_from_log_returns(log_returns_padded)
    raw_events = np.where(rsi_crossing_events(rsi))[0]
    raw_events = raw_events[raw_events >= warm_up]
    events = _apply_cooldown(raw_events, cooldown)
    return _mean_forward_return(log_returns_padded, events, horizon)


def rsi_placebo_forward_return(
    log_returns_padded: np.ndarray,
    *,
    warm_up: int = RSI_WARM_UP_SESSIONS,
    cooldown: int = RSI_EVENT_COOLDOWN,
    horizon: int = RSI_FORWARD_HORIZON,
) -> tuple[float, int]:
    """Observed mean forward return and usable event count for the placebo."""
    placebo = rsi_placebo_events(log_returns_padded)
    raw_events = np.where(placebo)[0]
    raw_events = raw_events[raw_events >= warm_up]
    events = _apply_cooldown(raw_events, cooldown)
    return _mean_forward_return(log_returns_padded, events, horizon)


def rsi_bootstrap(
    closes: np.ndarray,
    *,
    block_bars: int = RSI_BLOCK_BARS,
    resamples: int = RSI_RESAMPLES,
    seed: int = RSI_SEED,
    warm_up: int = RSI_WARM_UP_SESSIONS,
    cooldown: int = RSI_EVENT_COOLDOWN,
    horizon: int = RSI_FORWARD_HORIZON,
    min_event_count: int = RSI_MIN_EVENT_COUNT,
) -> dict:
    """One-sided p-values for a favourable (positive) mean forward return,
    for both the RSI event and its placebo, per
    docs/research-protocols/rsi-oversold-reversal-v1.md. Each resample
    reconstructs a synthetic price path and recomputes both event definitions
    on it, mirroring sma_cross_bootstrap's state-recomputing design."""
    log_returns_padded = log_returns_from_closes(closes)
    n = len(log_returns_padded)
    if n <= warm_up + RSI_PERIOD:
        raise ValueError("series too short for warm-up plus evaluation")

    observed_event_mean, event_count = rsi_event_forward_return(
        log_returns_padded, warm_up=warm_up, cooldown=cooldown, horizon=horizon
    )
    observed_placebo_mean, placebo_count = rsi_placebo_forward_return(
        log_returns_padded, warm_up=warm_up, cooldown=cooldown, horizon=horizon
    )

    result = {
        "observed_event_mean_forward_return": observed_event_mean,
        "event_count": event_count,
        "observed_placebo_mean_forward_return": observed_placebo_mean,
        "placebo_count": placebo_count,
        "p_event": None,
        "insufficient_events": event_count < min_event_count,
    }
    if event_count < min_event_count:
        return result

    values = log_returns_padded[1:]
    if block_bars <= 0 or block_bars > len(values):
        raise ValueError("block_bars must be between 1 and the sample length")
    if resamples <= 0:
        raise ValueError("resamples must be positive")

    blocks_needed = (len(values) + block_bars - 1) // block_bars
    offsets = np.arange(block_bars)
    rng = np.random.default_rng(seed)
    at_least = 0
    for _ in range(resamples):
        starts = rng.integers(0, len(values), size=blocks_needed)
        indexes = (starts[:, None] + offsets) % len(values)
        resampled_values = values[indexes.ravel()[: len(values)]]
        resampled_padded = np.concatenate([[0.0], resampled_values])
        resampled_mean, _ = rsi_event_forward_return(
            resampled_padded, warm_up=warm_up, cooldown=cooldown, horizon=horizon
        )
        if resampled_mean >= observed_event_mean:
            at_least += 1
    result["p_event"] = (at_least + 1) / (resamples + 1)
    return result


# --- TA Breakout v1: rejected-resistance breakout vs. raw new-high placebo ---
# Implements docs/research-protocols/ta-breakout-v1.md. Reuses the same
# event-recomputing bootstrap scaffold as RSI oversold reversal (_apply_cooldown,
# _mean_forward_return), applied to a resistance-breakout event/placebo pair
# instead. Close-price-only by deliberate scope decision; see the protocol.

BREAKOUT_WINDOW = 60
BREAKOUT_REJECTION_TOLERANCE = 0.01
BREAKOUT_BUFFER = 0.005
BREAKOUT_MIN_REJECTIONS = 2
BREAKOUT_WARM_UP_SESSIONS = 100
BREAKOUT_EVENT_COOLDOWN = 10
BREAKOUT_FORWARD_HORIZON = 10
BREAKOUT_MIN_EVENT_COUNT = 15
BREAKOUT_BLOCK_BARS = 20
BREAKOUT_RESAMPLES = 5_000
BREAKOUT_SEED = 17_291


def _rolling_max_excluding_today(values: np.ndarray, window: int) -> np.ndarray:
    """Rolling max over the window ending at t-1; NaN until enough history exists."""
    series = pd.Series(values)
    return series.rolling(window).max().shift(1).to_numpy()


def ta_breakout_events(
    closes: np.ndarray,
    *,
    window: int = BREAKOUT_WINDOW,
    tolerance: float = BREAKOUT_REJECTION_TOLERANCE,
    buffer: float = BREAKOUT_BUFFER,
    min_rejections: int = BREAKOUT_MIN_REJECTIONS,
) -> tuple[np.ndarray, np.ndarray]:
    """(event, placebo) boolean arrays. Event requires >= min_rejections prior
    near-miss touches of the rolling high; placebo is the same breakout with
    no rejection requirement (DonchianTrend's own raw breakout rule)."""
    resistance = _rolling_max_excluding_today(closes, window)
    valid = np.isfinite(resistance)
    near_but_below = np.where(
        valid,
        (closes < resistance) & (closes >= resistance * (1 - tolerance)),
        False,
    )
    rejection_count = _rolling_mean(near_but_below.astype(float), window) * window
    raw_breakout = np.where(valid, closes > resistance * (1 + buffer), False)
    event = raw_breakout & np.isfinite(rejection_count) & (rejection_count >= min_rejections)
    placebo = raw_breakout
    return event, placebo


def breakout_event_forward_return(
    log_returns_padded: np.ndarray,
    *,
    warm_up: int = BREAKOUT_WARM_UP_SESSIONS,
    cooldown: int = BREAKOUT_EVENT_COOLDOWN,
    horizon: int = BREAKOUT_FORWARD_HORIZON,
) -> tuple[float, int]:
    closes_proxy = np.exp(np.cumsum(log_returns_padded))
    event, _ = ta_breakout_events(closes_proxy)
    raw_events = np.where(event)[0]
    raw_events = raw_events[raw_events >= warm_up]
    events = _apply_cooldown(raw_events, cooldown)
    return _mean_forward_return(log_returns_padded, events, horizon)


def breakout_placebo_forward_return(
    log_returns_padded: np.ndarray,
    *,
    warm_up: int = BREAKOUT_WARM_UP_SESSIONS,
    cooldown: int = BREAKOUT_EVENT_COOLDOWN,
    horizon: int = BREAKOUT_FORWARD_HORIZON,
) -> tuple[float, int]:
    closes_proxy = np.exp(np.cumsum(log_returns_padded))
    _, placebo = ta_breakout_events(closes_proxy)
    raw_events = np.where(placebo)[0]
    raw_events = raw_events[raw_events >= warm_up]
    events = _apply_cooldown(raw_events, cooldown)
    return _mean_forward_return(log_returns_padded, events, horizon)


def ta_breakout_bootstrap(
    closes: np.ndarray,
    *,
    block_bars: int = BREAKOUT_BLOCK_BARS,
    resamples: int = BREAKOUT_RESAMPLES,
    seed: int = BREAKOUT_SEED,
    warm_up: int = BREAKOUT_WARM_UP_SESSIONS,
    cooldown: int = BREAKOUT_EVENT_COOLDOWN,
    horizon: int = BREAKOUT_FORWARD_HORIZON,
    min_event_count: int = BREAKOUT_MIN_EVENT_COUNT,
) -> dict:
    """One-sided p-value for a favourable (positive) mean forward return,
    for both the rejected-resistance breakout event and its raw-breakout
    placebo, per docs/research-protocols/ta-breakout-v1.md."""
    log_returns_padded = log_returns_from_closes(closes)
    n = len(log_returns_padded)
    if n <= warm_up + BREAKOUT_WINDOW:
        raise ValueError("series too short for warm-up plus evaluation")

    observed_event_mean, event_count = breakout_event_forward_return(
        log_returns_padded, warm_up=warm_up, cooldown=cooldown, horizon=horizon
    )
    observed_placebo_mean, placebo_count = breakout_placebo_forward_return(
        log_returns_padded, warm_up=warm_up, cooldown=cooldown, horizon=horizon
    )

    result = {
        "observed_event_mean_forward_return": observed_event_mean,
        "event_count": event_count,
        "observed_placebo_mean_forward_return": observed_placebo_mean,
        "placebo_count": placebo_count,
        "p_event": None,
        "insufficient_events": event_count < min_event_count,
    }
    if event_count < min_event_count:
        return result

    values = log_returns_padded[1:]
    if block_bars <= 0 or block_bars > len(values):
        raise ValueError("block_bars must be between 1 and the sample length")
    if resamples <= 0:
        raise ValueError("resamples must be positive")

    blocks_needed = (len(values) + block_bars - 1) // block_bars
    offsets = np.arange(block_bars)
    rng = np.random.default_rng(seed)
    at_least = 0
    for _ in range(resamples):
        starts = rng.integers(0, len(values), size=blocks_needed)
        indexes = (starts[:, None] + offsets) % len(values)
        resampled_values = values[indexes.ravel()[: len(values)]]
        resampled_padded = np.concatenate([[0.0], resampled_values])
        resampled_mean, _ = breakout_event_forward_return(
            resampled_padded, warm_up=warm_up, cooldown=cooldown, horizon=horizon
        )
        if resampled_mean >= observed_event_mean:
            at_least += 1
    result["p_event"] = (at_least + 1) / (resamples + 1)
    return result


# --- Wave Pull v1: impulse-pullback continuation vs. plain-breakout placebo ---
# Implements docs/research-protocols/wave-pull-v1.md. Reuses the same
# event-recomputing bootstrap scaffold as RSI/TA Breakout (_apply_cooldown,
# _mean_forward_return). Close-price-only by deliberate scope decision,
# substituting a close-based rolling extreme for the existing WavePull
# prototype's intraday high/low pullback range; see the protocol.

WAVE_PULL_IMPULSE_LOOKBACK = 8
WAVE_PULL_IMPULSE_MIN_MOVE = 0.06
WAVE_PULL_PULLBACK_WINDOW = 3
WAVE_PULL_WARM_UP_SESSIONS = 100
WAVE_PULL_EVENT_COOLDOWN = 10
WAVE_PULL_FORWARD_HORIZON = 10
WAVE_PULL_MIN_EVENT_COUNT = 15
WAVE_PULL_BLOCK_BARS = 20
WAVE_PULL_RESAMPLES = 5_000
WAVE_PULL_SEED = 17_291


def wave_pull_events(
    closes: np.ndarray,
    *,
    impulse_lookback: int = WAVE_PULL_IMPULSE_LOOKBACK,
    impulse_min_move: float = WAVE_PULL_IMPULSE_MIN_MOVE,
    pullback_window: int = WAVE_PULL_PULLBACK_WINDOW,
) -> tuple[np.ndarray, np.ndarray]:
    """(event, placebo) boolean arrays. Event requires a prior impulse;
    placebo is the same pullback-high breakout with no impulse precondition."""
    n = len(closes)
    impulse = np.full(n, False)
    if n > impulse_lookback:
        impulse[impulse_lookback:] = (
            closes[impulse_lookback:] / closes[:-impulse_lookback] - 1 >= impulse_min_move
        )
    pullback_high = _rolling_max_excluding_today(closes, pullback_window)
    valid = np.isfinite(pullback_high)
    placebo = np.where(valid, closes > pullback_high, False)
    event = impulse & placebo
    return event, placebo


def wave_pull_event_forward_return(
    log_returns_padded: np.ndarray,
    *,
    warm_up: int = WAVE_PULL_WARM_UP_SESSIONS,
    cooldown: int = WAVE_PULL_EVENT_COOLDOWN,
    horizon: int = WAVE_PULL_FORWARD_HORIZON,
) -> tuple[float, int]:
    closes_proxy = np.exp(np.cumsum(log_returns_padded))
    event, _ = wave_pull_events(closes_proxy)
    raw_events = np.where(event)[0]
    raw_events = raw_events[raw_events >= warm_up]
    events = _apply_cooldown(raw_events, cooldown)
    return _mean_forward_return(log_returns_padded, events, horizon)


def wave_pull_placebo_forward_return(
    log_returns_padded: np.ndarray,
    *,
    warm_up: int = WAVE_PULL_WARM_UP_SESSIONS,
    cooldown: int = WAVE_PULL_EVENT_COOLDOWN,
    horizon: int = WAVE_PULL_FORWARD_HORIZON,
) -> tuple[float, int]:
    closes_proxy = np.exp(np.cumsum(log_returns_padded))
    _, placebo = wave_pull_events(closes_proxy)
    raw_events = np.where(placebo)[0]
    raw_events = raw_events[raw_events >= warm_up]
    events = _apply_cooldown(raw_events, cooldown)
    return _mean_forward_return(log_returns_padded, events, horizon)


def wave_pull_bootstrap(
    closes: np.ndarray,
    *,
    block_bars: int = WAVE_PULL_BLOCK_BARS,
    resamples: int = WAVE_PULL_RESAMPLES,
    seed: int = WAVE_PULL_SEED,
    warm_up: int = WAVE_PULL_WARM_UP_SESSIONS,
    cooldown: int = WAVE_PULL_EVENT_COOLDOWN,
    horizon: int = WAVE_PULL_FORWARD_HORIZON,
    min_event_count: int = WAVE_PULL_MIN_EVENT_COUNT,
) -> dict:
    """One-sided p-value for a favourable (positive) mean forward return,
    for both the impulse-pullback event and its plain-breakout placebo, per
    docs/research-protocols/wave-pull-v1.md."""
    log_returns_padded = log_returns_from_closes(closes)
    n = len(log_returns_padded)
    if n <= warm_up + WAVE_PULL_IMPULSE_LOOKBACK:
        raise ValueError("series too short for warm-up plus evaluation")

    observed_event_mean, event_count = wave_pull_event_forward_return(
        log_returns_padded, warm_up=warm_up, cooldown=cooldown, horizon=horizon
    )
    observed_placebo_mean, placebo_count = wave_pull_placebo_forward_return(
        log_returns_padded, warm_up=warm_up, cooldown=cooldown, horizon=horizon
    )

    result = {
        "observed_event_mean_forward_return": observed_event_mean,
        "event_count": event_count,
        "observed_placebo_mean_forward_return": observed_placebo_mean,
        "placebo_count": placebo_count,
        "p_event": None,
        "insufficient_events": event_count < min_event_count,
    }
    if event_count < min_event_count:
        return result

    values = log_returns_padded[1:]
    if block_bars <= 0 or block_bars > len(values):
        raise ValueError("block_bars must be between 1 and the sample length")
    if resamples <= 0:
        raise ValueError("resamples must be positive")

    blocks_needed = (len(values) + block_bars - 1) // block_bars
    offsets = np.arange(block_bars)
    rng = np.random.default_rng(seed)
    at_least = 0
    for _ in range(resamples):
        starts = rng.integers(0, len(values), size=blocks_needed)
        indexes = (starts[:, None] + offsets) % len(values)
        resampled_values = values[indexes.ravel()[: len(values)]]
        resampled_padded = np.concatenate([[0.0], resampled_values])
        resampled_mean, _ = wave_pull_event_forward_return(
            resampled_padded, warm_up=warm_up, cooldown=cooldown, horizon=horizon
        )
        if resampled_mean >= observed_event_mean:
            at_least += 1
    result["p_event"] = (at_least + 1) / (resamples + 1)
    return result


# --- ETF-12 cross-sectional rotation v1: rank continuation vs. joint-panel null ---
# Implements docs/research-protocols/etf12-cross-sectional-rotation-v1.md.
# Unlike every prior candidate this session, this is a genuinely panel/
# cross-sectional design: ranks are computed jointly across all 12 assets at
# each rebalance date, and the null resamples the SAME calendar-time blocks
# across all 12 assets simultaneously (not independently per asset), which
# preserves real contemporaneous cluster correlation and is how "net of
# cluster membership" is achieved here instead of a per-asset residualization
# that would be degenerate for the four singleton-cluster assets.

ROTATION_FORMATION_WINDOW = 60
ROTATION_HOLDING_HORIZON = 20
ROTATION_WARM_UP_SESSIONS = 100
ROTATION_REBALANCE_SPACING = 20
ROTATION_BLOCK_BARS = 20
ROTATION_RESAMPLES = 2_000
ROTATION_SEED = 17_291
ROTATION_MIN_CORRELATION = 0.10


def _average_rank(values: np.ndarray) -> np.ndarray:
    """Cross-sectional average-rank, matching pandas' default tie-breaking."""
    return pd.Series(values).rank(method="average").to_numpy()


def rotation_rebalance_dates(
    n: int,
    *,
    warm_up: int = ROTATION_WARM_UP_SESSIONS,
    spacing: int = ROTATION_REBALANCE_SPACING,
    formation: int = ROTATION_FORMATION_WINDOW,
    holding: int = ROTATION_HOLDING_HORIZON,
) -> np.ndarray:
    """Session indices usable as rebalance dates: enough formation history
    behind them (>= formation) and enough forward history ahead (+ holding < n)."""
    start = max(warm_up, formation)
    stop = n - holding
    if stop <= start:
        return np.array([], dtype=int)
    return np.arange(start, stop, spacing)


def rotation_pooled_correlation(
    closes_matrix: np.ndarray,
    *,
    warm_up: int = ROTATION_WARM_UP_SESSIONS,
    spacing: int = ROTATION_REBALANCE_SPACING,
    formation: int = ROTATION_FORMATION_WINDOW,
    holding: int = ROTATION_HOLDING_HORIZON,
) -> tuple[float, int, dict]:
    """closes_matrix: (T, num_assets) aligned close prices, one column per
    asset. Returns (pooled Spearman correlation, rebalance date count,
    {date_index: array of formation ranks}) — the per-date ranks are returned
    for the cluster-breadth gate, computed once on the real (non-resampled)
    panel only."""
    n = closes_matrix.shape[0]
    dates = rotation_rebalance_dates(
        n, warm_up=warm_up, spacing=spacing, formation=formation, holding=holding
    )
    if len(dates) == 0:
        return 0.0, 0, {}

    formation_ranks_by_date: dict[int, np.ndarray] = {}
    pooled_formation = []
    pooled_forward = []
    for t in dates:
        f_returns = closes_matrix[t] / closes_matrix[t - formation] - 1
        g_returns = closes_matrix[t + holding] / closes_matrix[t] - 1
        f_rank = _average_rank(f_returns)
        formation_ranks_by_date[int(t)] = f_rank
        pooled_formation.append(f_rank)
        pooled_forward.append(_average_rank(g_returns))

    pooled_formation = np.concatenate(pooled_formation)
    pooled_forward = np.concatenate(pooled_forward)
    if np.std(pooled_formation) == 0 or np.std(pooled_forward) == 0:
        return 0.0, len(dates), formation_ranks_by_date
    correlation = float(np.corrcoef(pooled_formation, pooled_forward)[0, 1])
    return correlation, len(dates), formation_ranks_by_date


def etf12_rotation_bootstrap(
    closes_by_symbol: dict[str, np.ndarray],
    *,
    block_bars: int = ROTATION_BLOCK_BARS,
    resamples: int = ROTATION_RESAMPLES,
    seed: int = ROTATION_SEED,
    warm_up: int = ROTATION_WARM_UP_SESSIONS,
    spacing: int = ROTATION_REBALANCE_SPACING,
    formation: int = ROTATION_FORMATION_WINDOW,
    holding: int = ROTATION_HOLDING_HORIZON,
) -> dict:
    """One-sided p-value for a favourable (positive) pooled rank correlation,
    per docs/research-protocols/etf12-cross-sectional-rotation-v1.md. Each
    resample applies the SAME block-permuted date sequence to all assets
    simultaneously, preserving real contemporaneous cross-asset correlation."""
    symbols = sorted(closes_by_symbol)
    lengths = {len(closes_by_symbol[s]) for s in symbols}
    if len(lengths) != 1:
        raise ValueError("all assets must share the same aligned length")
    n = lengths.pop()
    if n <= warm_up + formation + holding:
        raise ValueError("series too short for warm-up plus evaluation")

    closes_matrix = np.column_stack([closes_by_symbol[s] for s in symbols])
    observed_corr, date_count, formation_ranks_by_date = rotation_pooled_correlation(
        closes_matrix, warm_up=warm_up, spacing=spacing, formation=formation, holding=holding
    )
    if date_count == 0:
        raise ValueError("no usable rebalance dates for this sample length")

    log_returns_by_symbol = {
        s: log_returns_from_closes(closes_by_symbol[s])[1:] for s in symbols
    }
    m = n - 1
    if block_bars <= 0 or block_bars > m:
        raise ValueError("block_bars must be between 1 and the sample length")
    if resamples <= 0:
        raise ValueError("resamples must be positive")

    blocks_needed = (m + block_bars - 1) // block_bars
    offsets = np.arange(block_bars)
    rng = np.random.default_rng(seed)
    at_least = 0
    for _ in range(resamples):
        starts = rng.integers(0, m, size=blocks_needed)
        indexes = (starts[:, None] + offsets) % m  # same indexes for every asset
        flat_indexes = indexes.ravel()[:m]
        resampled_columns = []
        for symbol in symbols:
            resampled_values = log_returns_by_symbol[symbol][flat_indexes]
            resampled_padded = np.concatenate([[0.0], resampled_values])
            resampled_columns.append(np.exp(np.cumsum(resampled_padded)))
        resampled_matrix = np.column_stack(resampled_columns)
        resampled_corr, _, _ = rotation_pooled_correlation(
            resampled_matrix, warm_up=warm_up, spacing=spacing, formation=formation, holding=holding
        )
        if resampled_corr >= observed_corr:
            at_least += 1

    return {
        "observed_correlation": observed_corr,
        "rebalance_date_count": date_count,
        "p_value": (at_least + 1) / (resamples + 1),
        "symbols": symbols,
        "formation_ranks_by_date": {
            str(date): rank.tolist() for date, rank in formation_ranks_by_date.items()
        },
    }


# --- Calendar Turn-of-Month v1: daily-return differential vs. block-resampled
# null --- Implements docs/research-protocols/calendar-turn-of-month-v1.md.
# Unlike every prior candidate this session, the event definition (turn-of-
# month calendar membership) depends only on the trading-day calendar, not on
# any price level -- it is computed once and held fixed, rather than
# recomputed from a resampled synthetic path on every iteration. The
# statistic is a group difference, so no mean-centering is applied before
# resampling (see the protocol's Scope decision for why that is sound).

TOM_LEADING_DAYS = 3
TOM_BLOCK_BARS = 20
TOM_RESAMPLES = 5_000
TOM_SEED = 17_291
TOM_MIN_EVENT_COUNT = 200
TOM_MATERIALITY_MIN = 0.0005


def tom_event_mask(dates) -> np.ndarray:
    """True at each trading day that is the last trading day of its month, or
    one of the first `TOM_LEADING_DAYS` trading days of a month -- the
    Lakonishok and Smidt (1988) turn-of-month window. Computed purely from
    the trading-day sequence in `dates` (assumed already ordered oldest
    first); carries no price information and no look-ahead risk."""
    parsed = pd.to_datetime(pd.Series(dates).reset_index(drop=True))
    month = parsed.dt.to_period("M")
    rank_from_start = month.groupby(month).cumcount()
    rank_from_end = month.groupby(month).cumcount(ascending=False)
    is_early = (rank_from_start < TOM_LEADING_DAYS).to_numpy()
    is_month_end = (rank_from_end == 0).to_numpy()
    return is_early | is_month_end


def tom_daily_differential(
    log_returns_padded: np.ndarray, event_mask: np.ndarray
) -> tuple[float, int, int]:
    """(event_mean - non_event_mean, event_count, non_event_count), excluding
    the synthetic index-0 padding entry."""
    values = log_returns_padded[1:]
    mask = event_mask[1:]
    event_values = values[mask]
    non_event_values = values[~mask]
    if len(event_values) == 0 or len(non_event_values) == 0:
        return 0.0, len(event_values), len(non_event_values)
    return (
        float(event_values.mean() - non_event_values.mean()),
        len(event_values),
        len(non_event_values),
    )


def tom_volatility_diagnostic(
    log_returns_padded: np.ndarray, event_mask: np.ndarray
) -> dict:
    """Non-gating diagnostic: realized volatility (std of daily log returns)
    on turn-of-month days vs. all other days, checking the alternative
    explanation that any effect is a volatility-timing artifact rather than
    a return-level one (the same lesson SMA Cross v1's confound taught)."""
    values = log_returns_padded[1:]
    mask = event_mask[1:]
    event_values = values[mask]
    non_event_values = values[~mask]
    return {
        "event_std": float(event_values.std(ddof=1)) if len(event_values) > 1 else None,
        "non_event_std": float(non_event_values.std(ddof=1)) if len(non_event_values) > 1 else None,
    }


def tom_bootstrap(
    closes: np.ndarray,
    dates,
    *,
    block_bars: int = TOM_BLOCK_BARS,
    resamples: int = TOM_RESAMPLES,
    seed: int = TOM_SEED,
    min_event_count: int = TOM_MIN_EVENT_COUNT,
) -> dict:
    """One-sided p-value for a favourable (positive) turn-of-month daily
    return differential, per
    docs/research-protocols/calendar-turn-of-month-v1.md. The event mask is
    computed once from the real calendar and held fixed across every
    resample -- only the return values at those fixed positions are
    resampled and re-differenced, unlike the price-derived candidates
    earlier this session whose event definitions must be recomputed on each
    synthetic path."""
    log_returns_padded = log_returns_from_closes(closes)
    event_mask = tom_event_mask(dates)
    if len(event_mask) != len(log_returns_padded):
        raise ValueError("dates and closes must have the same length")

    observed_diff, event_count, non_event_count = tom_daily_differential(
        log_returns_padded, event_mask
    )
    diagnostics = tom_volatility_diagnostic(log_returns_padded, event_mask)

    result = {
        "observed_daily_differential": observed_diff,
        "event_count": event_count,
        "non_event_count": non_event_count,
        "p_event": None,
        "insufficient_events": event_count < min_event_count,
        "diagnostics": diagnostics,
    }
    if event_count < min_event_count:
        return result

    values = log_returns_padded[1:]
    mask = event_mask[1:]
    if block_bars <= 0 or block_bars > len(values):
        raise ValueError("block_bars must be between 1 and the sample length")
    if resamples <= 0:
        raise ValueError("resamples must be positive")

    blocks_needed = (len(values) + block_bars - 1) // block_bars
    offsets = np.arange(block_bars)
    rng = np.random.default_rng(seed)
    at_least = 0
    for _ in range(resamples):
        starts = rng.integers(0, len(values), size=blocks_needed)
        indexes = (starts[:, None] + offsets) % len(values)
        resampled_values = values[indexes.ravel()[: len(values)]]
        resampled_diff = float(resampled_values[mask].mean() - resampled_values[~mask].mean())
        if resampled_diff >= observed_diff:
            at_least += 1
    result["p_event"] = (at_least + 1) / (resamples + 1)
    return result


# --- Calendar Day-of-Week v1: Monday daily-return differential vs.
# block-resampled null --- Implements
# docs/research-protocols/calendar-day-of-week-v1.md. Reuses
# tom_daily_differential and tom_volatility_diagnostic unchanged (both are
# generic, mask-based statistics with no turn-of-month-specific logic); only
# the event mask (weekday, not month-position) and the bootstrap's test
# direction (negative -- French 1980's claim is Monday underperformance, not
# outperformance) differ from Calendar Turn-of-Month v1.

DOW_TARGET_WEEKDAY = 0  # pandas .dt.weekday: Monday = 0
DOW_BLOCK_BARS = 20
DOW_RESAMPLES = 5_000
DOW_SEED = 17_291
DOW_MIN_EVENT_COUNT = 200
DOW_MATERIALITY_MAX = -0.0005


def dow_event_mask(dates, target_weekday: int = DOW_TARGET_WEEKDAY) -> np.ndarray:
    """True at each trading day whose calendar weekday matches
    `target_weekday` (default Monday). Computed purely from the trading-day
    calendar; carries no price information and no look-ahead risk, the same
    as `tom_event_mask`."""
    parsed = pd.to_datetime(pd.Series(dates).reset_index(drop=True))
    return (parsed.dt.weekday == target_weekday).to_numpy()


def dow_bootstrap(
    closes: np.ndarray,
    dates,
    *,
    target_weekday: int = DOW_TARGET_WEEKDAY,
    block_bars: int = DOW_BLOCK_BARS,
    resamples: int = DOW_RESAMPLES,
    seed: int = DOW_SEED,
    min_event_count: int = DOW_MIN_EVENT_COUNT,
) -> dict:
    """One-sided p-value for a favourable (negative -- underperformance)
    Monday daily return differential, per
    docs/research-protocols/calendar-day-of-week-v1.md. Structurally
    identical to `tom_bootstrap` except the event mask is weekday-based and
    the resampled comparison direction is flipped to match the claim being
    tested."""
    log_returns_padded = log_returns_from_closes(closes)
    event_mask = dow_event_mask(dates, target_weekday)
    if len(event_mask) != len(log_returns_padded):
        raise ValueError("dates and closes must have the same length")

    observed_diff, event_count, non_event_count = tom_daily_differential(
        log_returns_padded, event_mask
    )
    diagnostics = tom_volatility_diagnostic(log_returns_padded, event_mask)

    result = {
        "observed_daily_differential": observed_diff,
        "event_count": event_count,
        "non_event_count": non_event_count,
        "p_event": None,
        "insufficient_events": event_count < min_event_count,
        "diagnostics": diagnostics,
    }
    if event_count < min_event_count:
        return result

    values = log_returns_padded[1:]
    mask = event_mask[1:]
    if block_bars <= 0 or block_bars > len(values):
        raise ValueError("block_bars must be between 1 and the sample length")
    if resamples <= 0:
        raise ValueError("resamples must be positive")

    blocks_needed = (len(values) + block_bars - 1) // block_bars
    offsets = np.arange(block_bars)
    rng = np.random.default_rng(seed)
    at_least = 0
    for _ in range(resamples):
        starts = rng.integers(0, len(values), size=blocks_needed)
        indexes = (starts[:, None] + offsets) % len(values)
        resampled_values = values[indexes.ravel()[: len(values)]]
        resampled_diff = float(resampled_values[mask].mean() - resampled_values[~mask].mean())
        if resampled_diff <= observed_diff:
            at_least += 1
    result["p_event"] = (at_least + 1) / (resamples + 1)
    return result


# --- Overnight Gap Continuation v1: gap-conditioned signed forward return
# vs. joint-paired-resampled null --- Implements
# docs/research-protocols/overnight-gap-continuation-v1.md. The first
# candidate this session whose event depends on TWO return components
# (overnight, intraday) of the same asset. Every resample draws ONE shared
# block-index sequence and applies it to both components at once,
# preserving their real day-to-day pairing -- the same principle
# etf12_rotation_bootstrap used to preserve real cross-asset correlation
# (same resampled dates applied to all assets simultaneously), applied here
# across return components within one asset instead of across assets.
# Hardened by an independent pre-lock adversarial code review (2026-08-20,
# three lenses: statistical soundness, implementation correctness,
# adversarial coverage) before any market data was touched -- see the
# protocol's Pre-lock verification record for the full disposition.

GAP_QUANTILE = 0.90
GAP_WARM_UP_SESSIONS = 20
GAP_EVENT_COOLDOWN = 10
GAP_FORWARD_HORIZON = 10
GAP_MIN_EVENT_COUNT = 30
GAP_BLOCK_BARS = 20
GAP_RESAMPLES = 5_000
GAP_SEED = 17_291


def gap_and_intraday_returns(opens: np.ndarray, closes: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Day-0-padded (overnight, intraday) log-return pairs. g[t] is the
    overnight return arriving at open[t]; d[t] is the same day's open-to-
    close intraday return. g[t] + d[t] equals log_returns_from_closes(closes)[t]
    for t >= 1 -- the two components exactly partition the ordinary daily
    return.

    g[0] is padded NaN, not 0.0 (unlike every other candidate's zero-padded
    convention): a pre-lock review found that zero-padding g's undefined
    first entry (no prior close exists) let it silently enter
    `overnight_gap_event_mask`'s expanding-quantile threshold calibration as
    a spurious real observation, asymmetrically diluting the Gap track's
    threshold relative to the Placebo track's (d[0] is a genuinely observed
    value and was never affected). NaN is excluded by `_expanding_quantile`'s
    own NaN-skipping logic instead. d[0] needs no such treatment. Callers
    building the ordinary daily-return path for cumsum/forward-return
    purposes must use `np.nan_to_num(g, nan=0.0)` -- see
    `overnight_gap_bootstrap` -- since a bare NaN would poison every
    downstream cumulative sum."""
    n = len(closes)
    if len(opens) != n:
        raise ValueError("opens and closes must have the same length")
    if not (np.all(np.isfinite(opens)) and np.all(opens > 0)):
        raise ValueError("opens must be finite and strictly positive")
    if not (np.all(np.isfinite(closes)) and np.all(closes > 0)):
        raise ValueError("closes must be finite and strictly positive")
    log_opens = np.log(opens)
    log_closes = np.log(closes)
    g = np.empty(n)
    d = np.empty(n)
    g[0] = np.nan
    g[1:] = log_opens[1:] - log_closes[:-1]
    d[:] = log_closes - log_opens
    return g, d


def overnight_gap_event_mask(padded_component: np.ndarray, quantile: float = GAP_QUANTILE) -> np.ndarray:
    """True where |component[t]| >= the self-referential expanding quantile
    of |component[1..t]| -- reusing `_expanding_quantile` unchanged, the
    same "includes today's own value" convention already established and
    disclosed by RSI's placebo design, not a new leakage risk. Shared by
    both the Gap event (fed the overnight component) and the Placebo event
    (fed the intraday component).

    Requires a strictly positive threshold. A pre-lock review found that a
    near-degenerate trailing history (e.g. a long tied-at-zero stretch, such
    as stale or forward-filled opens) makes the quantile collapse to that
    tied value, and a non-strict `>=` comparison alone would then flag
    almost every day as an "event" instead of the intended top decile --
    excluded explicitly here rather than relying on real data happening not
    to trigger it. Not observed in the current 12-ETF universe (verified
    directly against data/market.db), but a genuine robustness gap without
    this guard."""
    abs_values = np.abs(padded_component)
    threshold = _expanding_quantile(abs_values, quantile)
    valid = np.isfinite(threshold) & (threshold > 0)
    return np.where(valid, abs_values >= threshold, False)


def _circular_block_resample_indexes(
    length: int, block_bars: int, rng: np.random.Generator
) -> np.ndarray:
    """One circular-block-resampled index sequence of the given length.
    Applying this SAME sequence to multiple arrays is what preserves real
    pairing/joint structure across those arrays -- used here for the
    (overnight, intraday) component pair, the same principle
    etf12_rotation_bootstrap uses across assets."""
    blocks_needed = (length + block_bars - 1) // block_bars
    offsets = np.arange(block_bars)
    starts = rng.integers(0, length, size=blocks_needed)
    indexes = (starts[:, None] + offsets) % length
    return indexes.ravel()[:length]


def _signed_mean_forward_return(
    log_returns_padded: np.ndarray,
    event_indices: np.ndarray,
    signs: np.ndarray,
    horizon: int,
) -> tuple[float, int]:
    """Like `_mean_forward_return`, but each event's forward return is
    multiplied by that event's own sign before averaging -- a continuation
    claim (does the market keep moving the way the event pointed), not a
    raw-direction claim. `signs` must be aligned 1:1 with `event_indices`."""
    n = len(log_returns_padded)
    cumsum = np.concatenate([[0.0], np.cumsum(log_returns_padded)])
    usable_mask = event_indices + horizon < n
    usable = event_indices[usable_mask]
    usable_signs = signs[usable_mask]
    if len(usable) == 0:
        return 0.0, 0
    forward = cumsum[usable + horizon + 1] - cumsum[usable + 1]
    return float((forward * usable_signs).mean()), len(usable)


def _gap_track_events_and_signs(
    component_padded: np.ndarray,
    *,
    warm_up: int,
    cooldown: int,
    quantile: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Shared by the Gap and Placebo tracks: build the expanding-quantile
    event mask for `component_padded`, apply warm-up and cooldown, and
    return the kept event indices with each one's own sign. warm_up always
    excludes index 0, so `component_padded[0]` being NaN (the Gap track's
    own convention) never reaches `np.sign`."""
    mask = overnight_gap_event_mask(component_padded, quantile)
    raw_events = np.where(mask)[0]
    raw_events = raw_events[raw_events >= warm_up]
    events = _apply_cooldown(raw_events, cooldown)
    signs = np.sign(component_padded[events])
    return events, signs


def _gap_track_forward_return(
    r_padded: np.ndarray,
    component_padded: np.ndarray,
    *,
    warm_up: int,
    cooldown: int,
    horizon: int,
    quantile: float,
) -> tuple[float, int]:
    """Signed mean forward return for the Gap or Placebo track, computed
    from the ordinary daily-return series `r_padded` -- see
    `_gap_track_events_and_signs` for the event/sign construction."""
    events, signs = _gap_track_events_and_signs(
        component_padded, warm_up=warm_up, cooldown=cooldown, quantile=quantile
    )
    return _signed_mean_forward_return(r_padded, events, signs, horizon)


def _split_by_gap_direction_forward_return(
    r_padded: np.ndarray,
    events: np.ndarray,
    signs: np.ndarray,
    horizon: int,
) -> dict:
    """Non-gating diagnostic: mean UNSIGNED forward return and count for the
    up-gap and down-gap subsets separately. A pooled signed-continuation
    statistic can mask a real, directionally asymmetric effect (e.g. up-gaps
    continuing while down-gaps revert) -- a pre-lock review's concern; this
    does not change the estimand or any gate, only what a closed result
    discloses, the same treatment already given to `tom_volatility_diagnostic`."""
    up_mean, up_count = _mean_forward_return(r_padded, events[signs > 0], horizon)
    down_mean, down_count = _mean_forward_return(r_padded, events[signs < 0], horizon)
    return {
        "up_gap_mean_forward_return": up_mean,
        "up_gap_count": up_count,
        "down_gap_mean_forward_return": down_mean,
        "down_gap_count": down_count,
    }


def overnight_gap_bootstrap(
    opens: np.ndarray,
    closes: np.ndarray,
    *,
    quantile: float = GAP_QUANTILE,
    block_bars: int = GAP_BLOCK_BARS,
    resamples: int = GAP_RESAMPLES,
    seed: int = GAP_SEED,
    warm_up: int = GAP_WARM_UP_SESSIONS,
    cooldown: int = GAP_EVENT_COOLDOWN,
    horizon: int = GAP_FORWARD_HORIZON,
    min_event_count: int = GAP_MIN_EVENT_COUNT,
) -> dict:
    """One-sided p-values for a favourable (positive) gap-conditioned signed
    forward return, per
    docs/research-protocols/overnight-gap-continuation-v1.md. Each resample
    draws ONE shared block-index sequence and applies it to both the
    overnight and intraday components at once, preserving their real
    day-to-day pairing, then reconstructs the synthetic daily-return path as
    their sum and recomputes BOTH the Gap and Placebo statistics fresh on
    the resampled path -- unlike every prior candidate's bare real-data-only
    placebo comparison (Wave Pull's, TA Breakout's convention), this also
    yields a genuine paired-null p-value for whether Gap's advantage over
    Placebo is itself distinguishable from chance, not just a point-estimate
    inequality; a pre-lock review found the bare inequality alone gives the
    placebo little real discriminating power against a generic
    large-one-day-move confound (SMA Cross v1's own failure mode). The
    computational cost of also recomputing Placebo each iteration is
    accepted as cheap relative to the correctness gained."""
    n = len(closes)
    if len(opens) != n:
        raise ValueError("opens and closes must have the same length")
    g, d = gap_and_intraday_returns(opens, closes)
    r_padded = np.nan_to_num(g, nan=0.0) + d

    observed_gap_mean, gap_count = _gap_track_forward_return(
        r_padded, g, warm_up=warm_up, cooldown=cooldown, horizon=horizon, quantile=quantile
    )
    observed_placebo_mean, placebo_count = _gap_track_forward_return(
        r_padded, d, warm_up=warm_up, cooldown=cooldown, horizon=horizon, quantile=quantile
    )
    gap_events, gap_signs = _gap_track_events_and_signs(
        g, warm_up=warm_up, cooldown=cooldown, quantile=quantile
    )
    diagnostics = _split_by_gap_direction_forward_return(r_padded, gap_events, gap_signs, horizon)

    result = {
        "observed_gap_mean_signed_forward_return": observed_gap_mean,
        "gap_event_count": gap_count,
        "observed_placebo_mean_signed_forward_return": observed_placebo_mean,
        "placebo_event_count": placebo_count,
        "p_event": None,
        "p_gap_vs_placebo": None,
        "insufficient_events": gap_count < min_event_count,
        "diagnostics": diagnostics,
    }
    if gap_count < min_event_count:
        return result

    m = n - 1
    if block_bars <= 0 or block_bars > m:
        raise ValueError("block_bars must be between 1 and the sample length")
    if resamples <= 0:
        raise ValueError("resamples must be positive")

    g_values = g[1:]  # never NaN: index 0 is excluded by this slice itself
    d_values = d[1:]
    observed_diff = observed_gap_mean - observed_placebo_mean
    rng = np.random.default_rng(seed)
    at_least_gap = 0
    at_least_diff = 0
    for _ in range(resamples):
        flat_indexes = _circular_block_resample_indexes(m, block_bars, rng)
        resampled_g = np.concatenate([[np.nan], g_values[flat_indexes]])
        resampled_d = np.concatenate([[0.0], d_values[flat_indexes]])
        resampled_r = np.nan_to_num(resampled_g, nan=0.0) + resampled_d
        resampled_gap_mean, _ = _gap_track_forward_return(
            resampled_r, resampled_g, warm_up=warm_up, cooldown=cooldown, horizon=horizon, quantile=quantile
        )
        resampled_placebo_mean, _ = _gap_track_forward_return(
            resampled_r, resampled_d, warm_up=warm_up, cooldown=cooldown, horizon=horizon, quantile=quantile
        )
        if resampled_gap_mean >= observed_gap_mean:
            at_least_gap += 1
        if (resampled_gap_mean - resampled_placebo_mean) >= observed_diff:
            at_least_diff += 1
    result["p_event"] = (at_least_gap + 1) / (resamples + 1)
    result["p_gap_vs_placebo"] = (at_least_diff + 1) / (resamples + 1)
    return result


# --- CTA v2: pooled vol-scaled trend overlay (Stage 9A Cycle 2, Candidate C,
# picked up 2026-08-20) --- Implements
# docs/research-protocols/cta-v2-pooled-trend-overlay.md. The estimand is a
# single pooled daily excess-return series -- structurally identical in shape
# to CTA v1's original per-symbol excess-return statistic, just computed from
# a portfolio-weighted series instead of a per-symbol one -- so
# circular_block_bootstrap_p_value and holm_adjust are reused completely
# unchanged; no state-recomputing bootstrap is required the way SMA Cross
# v1's Δσ/ΔMDD estimand needed, because nothing here depends on how a
# threshold state would look on a resampled path.

CTA_V2_VOL_LOOKBACK = 20  # shares SMA Cross v1's exact volatility estimator
CTA_V2_VARIANTS = {"A": 150, "B": 252, "C": 350}  # SMA lookback per variant
CTA_V2_PRIMARY_VARIANT = "B"
CTA_V2_WARM_UP_SESSIONS = 350  # widest variant lookback, so every variant is
# fully warmed up from the sample's first evaluated day
CTA_V2_BLOCK_BARS = 20
CTA_V2_RESAMPLES = 5_000
CTA_V2_SEED = 17_291
CTA_V2_MATERIALITY_ANNUALIZED_MIN = 0.01  # +1.0 percentage point
CTA_V2_REGIME_YEARS = (2008, 2020, 2022)


def cta_v2_trailing_vol(log_returns_padded: np.ndarray) -> np.ndarray:
    """Trailing 20-session close-to-close log-return std, annualized -- the
    exact estimator already locked for SMA Cross v1's volatility-state
    placebo, reused here as both the trend-signal normalizer and the
    vol-scaling weight denominator, so one volatility concept governs the
    whole candidate rather than two different ones."""
    return _rolling_std(log_returns_padded, CTA_V2_VOL_LOOKBACK) * SMA_CROSS_ANNUALIZATION


def cta_v2_signal_matrix(
    closes_by_symbol: dict[str, np.ndarray], *, sma_window: int
) -> dict[str, np.ndarray]:
    """Per-asset Trend(t) = (close(t) - SMA_n(t)) / sigma_20(t), close-only --
    the same close-price-only simplification every prior close-derived
    candidate this session made, to avoid a second, high/low-dependent
    volatility proxy alongside the one already locked for the placebo."""
    signals: dict[str, np.ndarray] = {}
    for symbol, closes in closes_by_symbol.items():
        log_returns = log_returns_from_closes(closes)
        sma = _rolling_mean(closes, sma_window)
        sigma = cta_v2_trailing_vol(log_returns)
        with np.errstate(invalid="ignore", divide="ignore"):
            trend = (closes - sma) / sigma
        signals[symbol] = np.where(np.isfinite(trend), trend, np.nan)
    return signals


def _normalized_score_weights(score: np.ndarray) -> np.ndarray:
    """Row-normalize a (dates x assets) non-negative score matrix to sum to
    at most 1.0 per row; an all-zero row (no eligible asset) stays all-zero
    (100% cash), never divides by zero."""
    totals = score.sum(axis=1)
    return np.divide(
        score, totals[:, None], out=np.zeros_like(score), where=totals[:, None] > 0
    )


def cta_v2_weight_matrix(
    closes_by_symbol: dict[str, np.ndarray], *, sma_window: int
) -> dict[str, np.ndarray]:
    """w_i(t): long-only, sum-normalized, vol-scaled trend weight. Zero
    weight where a signal is non-positive or unavailable (pre-warm-up); an
    all-non-positive-trend day yields an all-zero row, i.e. 100% cash at
    zero yield, matching ADR 0003's locked zero-cash-yield convention."""
    symbols = list(closes_by_symbol)
    n = len(closes_by_symbol[symbols[0]])
    trends = cta_v2_signal_matrix(closes_by_symbol, sma_window=sma_window)
    score = np.zeros((n, len(symbols)))
    for j, symbol in enumerate(symbols):
        trend = trends[symbol]
        sigma = cta_v2_trailing_vol(log_returns_from_closes(closes_by_symbol[symbol]))
        positive_trend = np.where(np.isfinite(trend) & (trend > 0), trend, 0.0)
        with np.errstate(invalid="ignore", divide="ignore"):
            score[:, j] = np.where(
                np.isfinite(sigma) & (sigma > 0), positive_trend / sigma, 0.0
            )
    weights = _normalized_score_weights(score)
    return {symbol: weights[:, j] for j, symbol in enumerate(symbols)}


def cta_v2_placebo_weight_matrix(
    closes_by_symbol: dict[str, np.ndarray],
) -> dict[str, np.ndarray]:
    """Direction-blind volatility-only weight: no trend information at all,
    only inverse-volatility scaling with the same sigma_20 estimator --
    every asset always receives a positive weight, so this is always fully
    invested, unlike the trend-weighted portfolio's possible all-cash days."""
    symbols = list(closes_by_symbol)
    n = len(closes_by_symbol[symbols[0]])
    score = np.zeros((n, len(symbols)))
    for j, symbol in enumerate(symbols):
        sigma = cta_v2_trailing_vol(log_returns_from_closes(closes_by_symbol[symbol]))
        with np.errstate(invalid="ignore", divide="ignore"):
            score[:, j] = np.where(np.isfinite(sigma) & (sigma > 0), 1.0 / sigma, 0.0)
    weights = _normalized_score_weights(score)
    return {symbol: weights[:, j] for j, symbol in enumerate(symbols)}


def cta_v2_portfolio_return(
    closes_by_symbol: dict[str, np.ndarray],
    weights_by_symbol: dict[str, np.ndarray],
) -> np.ndarray:
    """r_portfolio(t) = sum_i w_i(t-1) * r_i(t); day 0 has no prior weight,
    so portfolio return is 0 there, matching log_returns_from_closes's own
    day-0 padding convention. t-1 weights gating day t's return matches ADR
    0001 even though no position is opened in this no-trade test."""
    symbols = list(closes_by_symbol)
    n = len(closes_by_symbol[symbols[0]])
    portfolio = np.zeros(n)
    for symbol in symbols:
        r = log_returns_from_closes(closes_by_symbol[symbol])
        w = weights_by_symbol[symbol]
        lagged_w = np.concatenate([[0.0], w[:-1]])
        portfolio += lagged_w * r
    return portfolio


def cta_v2_benchmark_return(closes_by_symbol: dict[str, np.ndarray]) -> np.ndarray:
    """Continuous, no-cost, daily-rebalanced equal-weight benchmark: the
    simple cross-sectional mean of the 12 assets' daily log returns. A
    further deliberate simplification of ADR 0005's real annually-rebalanced,
    whole-share, costed Passive ETF-12 v1 -- used only for this no-trade
    comparison, where daily rebalancing needs no drift/position tracking and
    stays fully transparent and easy to verify."""
    returns = np.vstack(
        [log_returns_from_closes(closes) for closes in closes_by_symbol.values()]
    )
    return returns.mean(axis=0)


def cta_v2_bootstrap(
    closes_by_symbol: dict[str, np.ndarray],
    dates: np.ndarray,
    *,
    warm_up: int = CTA_V2_WARM_UP_SESSIONS,
    block_bars: int = CTA_V2_BLOCK_BARS,
    resamples: int = CTA_V2_RESAMPLES,
    seed: int = CTA_V2_SEED,
    materiality_annualized_min: float = CTA_V2_MATERIALITY_ANNUALIZED_MIN,
) -> dict:
    """Per-variant and placebo pooled-portfolio excess return over a
    daily-rebalanced equal-weight benchmark, Holm-corrected across the
    3-variant lookback family (the placebo is compared directly via the
    paired placebo test, not pooled into that family), per
    docs/research-protocols/cta-v2-pooled-trend-overlay.md."""
    symbols = list(closes_by_symbol)
    n = len(closes_by_symbol[symbols[0]])
    for symbol, closes in closes_by_symbol.items():
        if len(closes) != n:
            raise ValueError(f"{symbol} calendar differs from the shared pooled calendar")
    if len(dates) != n:
        raise ValueError("dates must match the shared pooled calendar")
    if n <= warm_up:
        raise ValueError("series too short for warm-up plus evaluation")

    benchmark = cta_v2_benchmark_return(closes_by_symbol)

    variant_results: dict[str, dict] = {}
    raw_p: dict[str, float] = {}
    excess_by_variant: dict[str, np.ndarray] = {}
    for label, sma_window in CTA_V2_VARIANTS.items():
        weights = cta_v2_weight_matrix(closes_by_symbol, sma_window=sma_window)
        portfolio = cta_v2_portfolio_return(closes_by_symbol, weights)
        excess = (portfolio - benchmark)[warm_up:]
        excess_by_variant[label] = excess
        observed_mean = float(excess.mean())
        p = circular_block_bootstrap_p_value(
            excess, block_bars=block_bars, resamples=resamples, seed=seed
        )
        raw_p[label] = p
        variant_results[label] = {
            "sma_window": sma_window,
            "observed_mean_daily_excess_return": observed_mean,
            "annualized_materiality": observed_mean * 252,
            "raw_p": p,
            "asset_weight_share": {
                symbol: float(np.nanmean(weights[symbol][warm_up:])) for symbol in symbols
            },
        }

    labels = list(CTA_V2_VARIANTS)
    adjusted = holm_adjust([raw_p[label] for label in labels])
    for label, holm_p in zip(labels, adjusted):
        variant_results[label]["holm_p"] = holm_p

    placebo_weights = cta_v2_placebo_weight_matrix(closes_by_symbol)
    placebo_portfolio = cta_v2_portfolio_return(closes_by_symbol, placebo_weights)
    placebo_excess = (placebo_portfolio - benchmark)[warm_up:]
    placebo_mean = float(placebo_excess.mean())

    primary = CTA_V2_PRIMARY_VARIANT
    primary_excess = excess_by_variant[primary]
    primary_mean = variant_results[primary]["observed_mean_daily_excess_return"]
    primary_annualized = variant_results[primary]["annualized_materiality"]
    primary_holm_p = variant_results[primary]["holm_p"]
    beats_placebo_point_estimate = primary_mean > placebo_mean
    difference_series = primary_excess - placebo_excess
    p_primary_vs_placebo = circular_block_bootstrap_p_value(
        difference_series, block_bars=block_bars, resamples=resamples, seed=seed
    )
    beats_placebo = beats_placebo_point_estimate and p_primary_vs_placebo <= 0.05

    material = primary_annualized >= materiality_annualized_min
    significant = primary_holm_p <= 0.05
    decision = (
        "material_and_consistent"
        if material and significant and beats_placebo
        else "not_material_or_not_consistent"
    )

    years = pd.to_datetime(dates[warm_up:]).year.to_numpy()
    regime_diagnostics = {
        f"excluding_{year}": float(primary_excess[years != year].mean())
        for year in CTA_V2_REGIME_YEARS
    }

    return {
        "variants": variant_results,
        "primary_variant": primary,
        "placebo": {
            "observed_mean_daily_excess_return": placebo_mean,
            "beats_primary_point_estimate": not beats_placebo_point_estimate,
            "p_primary_vs_placebo": p_primary_vs_placebo,
        },
        "decision": decision,
        "gates": {
            "materiality": material,
            "significance": significant,
            "placebo": beats_placebo,
        },
        "regime_diagnostics": regime_diagnostics,
    }


# --- Chapter 4: risk-budgeted ensemble eligibility scoring --- Implements
# docs/adr/0007-risk-budgeted-ensemble-acceptance.md. Distinct from every
# bootstrap above: those test a NULL hypothesis (center the data, then ask
# how often chance reproduces the observed statistic -- a p-value). This
# characterizes the plausible RANGE of the true effect size itself (no
# centering), which a p-value does not provide and Loss-based Quantity
# Determination sizing needs. Reuses _circular_block_resample_indexes
# unchanged (the same block-resampling primitive Overnight Gap Continuation
# v1 introduced), only the statistic collected per resample differs.

CHAPTER4_BLOCK_BARS = 20
CHAPTER4_RESAMPLES = 5_000
CHAPTER4_SEED = 17_291
CHAPTER4_LOWER_PERCENTILE = 16.0
CHAPTER4_UPPER_PERCENTILE = 84.0


def block_bootstrap_confidence_interval(
    values: list[float] | np.ndarray,
    *,
    block_bars: int = CHAPTER4_BLOCK_BARS,
    resamples: int = CHAPTER4_RESAMPLES,
    seed: int = CHAPTER4_SEED,
    lower_percentile: float = CHAPTER4_LOWER_PERCENTILE,
    upper_percentile: float = CHAPTER4_UPPER_PERCENTILE,
) -> dict:
    """Block-bootstrap confidence interval on the MEAN of `values` -- NOT a
    null-hypothesis test. Resamples the data exactly as observed (no
    centering, no permutation) to characterize the plausible range of the
    true mean itself. Default 16th/84th percentiles approximate a `68%`
    ("one-sigma") coverage interval, matching ADR 0007's own framing of
    lenient-but-real evidence -- deliberately not the `95%` bar Chapters
    1-3 require."""
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if len(values) < 2:
        raise ValueError("confidence interval requires at least two finite values")
    if block_bars <= 0 or block_bars > len(values):
        raise ValueError("block_bars must be between 1 and the sample length")
    if resamples <= 0:
        raise ValueError("resamples must be positive")

    observed = float(values.mean())
    rng = np.random.default_rng(seed)
    resampled_means = np.empty(resamples)
    for i in range(resamples):
        flat_indexes = _circular_block_resample_indexes(len(values), block_bars, rng)
        resampled_means[i] = values[flat_indexes].mean()

    return {
        "observed_mean": observed,
        "lower_bound": float(np.percentile(resampled_means, lower_percentile)),
        "upper_bound": float(np.percentile(resampled_means, upper_percentile)),
        "coverage_pct": upper_percentile - lower_percentile,
        "resamples": resamples,
    }


def chapter4_confidence_multiplier(observed_mean: float, lower_bound: float) -> float:
    """Loss-based Quantity Determination confidence multiplier, per ADR
    0007: the ratio of the confidence interval's lower bound to the point
    estimate, floored at `0` (a lower bound at or below zero means no
    confident positive edge to size at all -- the signal fails Chapter 4
    eligibility outright) and capped at `1` (a Chapter 4 signal may never
    be sized as large as a fully Chapter 1-3-validated one, by
    construction, since it has not cleared that bar)."""
    if observed_mean <= 0:
        return 0.0
    return float(np.clip(lower_bound / observed_mean, 0.0, 1.0))
