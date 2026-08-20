"""Formulaic alpha factor zoo -- Chapter 4 production input, not Chapter 1-3.

Cross-sectional operator vocabulary (rank, delay, correlation, ts_rank,
decay_linear, ...) and a curated, portable subset of the published
WorldQuant "101 Formulaic Alphas" (Kakushadze 2015) -- verified against
https://github.com/popbo/alphas/blob/main/alphas101.py, not reconstructed
from memory. Selected for portability: OHLCV + volume only, no vwap/amount/
turnover/industry fields this project's free Yahoo data doesn't have (rules
out most of alpha191, a China-A-share set with different required fields).

None of these 17 are individually validated -- that is the point of a zoo:
breadth over interpretability, screened cheaply, with the strongest, most
orthogonal survivors proposed individually into Chapter 4 (each then needs
its own stated mechanism per ADR 0007 clause 1 -- this module only screens).

Panel convention throughout: DataFrame indexed by date (str, ascending),
columns = symbol. `rank` is cross-sectional (axis=1, per date, across
symbols); `ts_*` operators are time-series (rolling, per symbol).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Operators
# ---------------------------------------------------------------------------


def rank(df: pd.DataFrame) -> pd.DataFrame:
    """Cross-sectional percentile rank, per date, across symbols."""
    return df.rank(axis=1, method="min", pct=True)


def delay(df: pd.DataFrame, period: int) -> pd.DataFrame:
    return df.shift(period)


def delta(df: pd.DataFrame, period: int) -> pd.DataFrame:
    return df.diff(period)


def ts_sum(df: pd.DataFrame, window: int) -> pd.DataFrame:
    return df.rolling(window).sum()


def sma(df: pd.DataFrame, window: int) -> pd.DataFrame:
    return df.rolling(window).mean()


def stddev(df: pd.DataFrame, window: int) -> pd.DataFrame:
    return df.rolling(window).std()


def ts_min(df: pd.DataFrame, window: int) -> pd.DataFrame:
    return df.rolling(window).min()


def ts_max(df: pd.DataFrame, window: int) -> pd.DataFrame:
    return df.rolling(window).max()


def correlation(x: pd.DataFrame, y: pd.DataFrame, window: int) -> pd.DataFrame:
    result = x.rolling(window).corr(y)
    return result.replace([np.inf, -np.inf], 0.0).fillna(0.0)


def covariance(x: pd.DataFrame, y: pd.DataFrame, window: int) -> pd.DataFrame:
    result = x.rolling(window).cov(y)
    return result.replace([np.inf, -np.inf], 0.0).fillna(0.0)


def sign(df: pd.DataFrame) -> pd.DataFrame:
    return np.sign(df)


def log(df: pd.DataFrame) -> pd.DataFrame:
    return np.log(df.clip(lower=1e-12))


def signed_power(df: pd.DataFrame, exponent: float) -> pd.DataFrame:
    return np.sign(df) * df.abs() ** exponent


def _last_ordinal_rank(window: np.ndarray) -> float:
    last = window[-1]
    return 1.0 + float(np.sum(window < last))


def ts_rank(df: pd.DataFrame, window: int) -> pd.DataFrame:
    """Ordinal rank (ties -> minimum rank) of the last value in a trailing window."""
    return df.rolling(window).apply(_last_ordinal_rank, raw=True)


def _last_argmax(window: np.ndarray) -> float:
    return float(np.argmax(window) + 1)


def ts_argmax(df: pd.DataFrame, window: int) -> pd.DataFrame:
    return df.rolling(window).apply(_last_argmax, raw=True)


def decay_linear(df: pd.DataFrame, period: int) -> pd.DataFrame:
    weights = np.arange(1, period + 1, dtype=float)
    weight_sum = weights.sum()
    return df.rolling(period).apply(lambda x: np.dot(weights, x) / weight_sum, raw=True)


def scale(df: pd.DataFrame, k: float = 1.0) -> pd.DataFrame:
    """Cross-sectional rescale, per date, so sum(abs(row)) == k."""
    denom = df.abs().sum(axis=1).replace(0.0, np.nan)
    return df.mul(k).div(denom, axis=0).fillna(0.0)


# ---------------------------------------------------------------------------
# Panel
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Panel:
    open: pd.DataFrame
    high: pd.DataFrame
    low: pd.DataFrame
    close: pd.DataFrame
    volume: pd.DataFrame
    returns: pd.DataFrame

    @classmethod
    def build(
        cls,
        open_: pd.DataFrame,
        high: pd.DataFrame,
        low: pd.DataFrame,
        close: pd.DataFrame,
        volume: pd.DataFrame,
    ) -> "Panel":
        return cls(
            open=open_, high=high, low=low, close=close, volume=volume,
            returns=close.pct_change(),
        )


# ---------------------------------------------------------------------------
# Formulas -- 17 of WorldQuant's 101, chosen for OHLCV-only portability.
# Each docstring carries the published formula verbatim for auditability.
# ---------------------------------------------------------------------------


def alpha001(p: Panel) -> pd.DataFrame:
    """rank(Ts_ArgMax(SignedPower(((returns<0) ? stddev(returns,20) : close), 2.), 5)) - 0.5"""
    inner = p.close.where(p.returns >= 0, stddev(p.returns, 20))
    return rank(ts_argmax(signed_power(inner, 2.0), 5)) - 0.5


def alpha002(p: Panel) -> pd.DataFrame:
    """-1 * correlation(rank(delta(log(volume),2)), rank((close-open)/open), 6)"""
    return -1 * correlation(rank(delta(log(p.volume), 2)), rank((p.close - p.open) / p.open), 6)


def alpha003(p: Panel) -> pd.DataFrame:
    """-1 * correlation(rank(open), rank(volume), 10)"""
    return -1 * correlation(rank(p.open), rank(p.volume), 10)


def alpha004(p: Panel) -> pd.DataFrame:
    """-1 * Ts_Rank(rank(low), 9)"""
    return -1 * ts_rank(rank(p.low), 9)


def alpha006(p: Panel) -> pd.DataFrame:
    """-1 * correlation(open, volume, 10)"""
    return -1 * correlation(p.open, p.volume, 10)


def alpha009(p: Panel) -> pd.DataFrame:
    """(0<ts_min(delta(close,1),5)) ? delta(close,1) : ((ts_max(delta(close,1),5)<0) ? delta(close,1) : -delta(close,1))"""
    diff = delta(p.close, 1)
    condition = (ts_min(diff, 5) > 0) | (ts_max(diff, 5) < 0)
    return diff.where(condition, -1 * diff)


def alpha012(p: Panel) -> pd.DataFrame:
    """sign(delta(volume,1)) * (-1 * delta(close,1))"""
    return sign(delta(p.volume, 1)) * (-1 * delta(p.close, 1))


def alpha013(p: Panel) -> pd.DataFrame:
    """-1 * rank(covariance(rank(close), rank(volume), 5))"""
    return -1 * rank(covariance(rank(p.close), rank(p.volume), 5))


def alpha014(p: Panel) -> pd.DataFrame:
    """(-1 * rank(delta(returns,3))) * correlation(open, volume, 10)"""
    return -1 * rank(delta(p.returns, 3)) * correlation(p.open, p.volume, 10)


def alpha017(p: Panel) -> pd.DataFrame:
    """(-1*rank(Ts_Rank(close,10))) * rank(delta(delta(close,1),1)) * rank(Ts_Rank(volume/adv20,5))"""
    adv20 = sma(p.volume, 20)
    return -1 * (
        rank(ts_rank(p.close, 10))
        * rank(delta(delta(p.close, 1), 1))
        * rank(ts_rank(p.volume / adv20, 5))
    )


def alpha020(p: Panel) -> pd.DataFrame:
    """(-1*rank(open-delay(high,1))) * rank(open-delay(close,1)) * rank(open-delay(low,1))"""
    return -1 * (
        rank(p.open - delay(p.high, 1))
        * rank(p.open - delay(p.close, 1))
        * rank(p.open - delay(p.low, 1))
    )


def alpha023(p: Panel) -> pd.DataFrame:
    """((sum(high,20)/20) < high) ? (-1*delta(high,2)) : 0"""
    condition = sma(p.high, 20) < p.high
    return (-1 * delta(p.high, 2)).where(condition, p.high * 0.0)


def alpha026(p: Panel) -> pd.DataFrame:
    """-1 * ts_max(correlation(Ts_Rank(volume,5), Ts_Rank(high,5), 5), 3)"""
    return -1 * ts_max(correlation(ts_rank(p.volume, 5), ts_rank(p.high, 5), 5), 3)


def alpha028(p: Panel) -> pd.DataFrame:
    """scale(correlation(adv20, low, 5) + ((high+low)/2) - close)"""
    adv20 = sma(p.volume, 20)
    return scale(correlation(adv20, p.low, 5) + (p.high + p.low) / 2 - p.close)


def alpha033(p: Panel) -> pd.DataFrame:
    """rank(-1 * (1 - open/close))"""
    return rank(-1 + p.open / p.close)


def alpha034(p: Panel) -> pd.DataFrame:
    """rank((1-rank(stddev(returns,2)/stddev(returns,5))) + (1-rank(delta(close,1))))"""
    ratio = (stddev(p.returns, 2) / stddev(p.returns, 5)).replace([np.inf, -np.inf], 1.0).fillna(1.0)
    return rank(2 - rank(ratio) - rank(delta(p.close, 1)))


def alpha035(p: Panel) -> pd.DataFrame:
    """Ts_Rank(volume,32) * (1-Ts_Rank((close+high-low),16)) * (1-Ts_Rank(returns,32))"""
    return (
        ts_rank(p.volume, 32)
        * (1 - ts_rank(p.close + p.high - p.low, 16))
        * (1 - ts_rank(p.returns, 32))
    )


ALPHAS: dict[str, Callable[[Panel], pd.DataFrame]] = {
    "alpha001": alpha001,
    "alpha002": alpha002,
    "alpha003": alpha003,
    "alpha004": alpha004,
    "alpha006": alpha006,
    "alpha009": alpha009,
    "alpha012": alpha012,
    "alpha013": alpha013,
    "alpha014": alpha014,
    "alpha017": alpha017,
    "alpha020": alpha020,
    "alpha023": alpha023,
    "alpha026": alpha026,
    "alpha028": alpha028,
    "alpha033": alpha033,
    "alpha034": alpha034,
    "alpha035": alpha035,
}


# ---------------------------------------------------------------------------
# Evaluation -- rank-IC and a daily-rebalanced quintile-spread return series.
# ---------------------------------------------------------------------------


def factor_return_metrics(daily_returns: pd.Series) -> dict:
    """Sharpe/CAGR/drawdown from a raw daily return series.

    Deliberately parallels portfolio_metrics.py's formulas (same math, a
    different input shape -- a factor spread series, not a portfolio
    replay). Unifying the two into one engine is the still-open idea in
    docs/brainstorm/2026-08-21-shared-metrics-and-charting-engine.md; this
    is a disclosed, intentional duplicate in the meantime, not a silent one.
    """
    if daily_returns.empty:
        raise ValueError("factor_return_metrics requires at least one daily return")
    equity = (1.0 + daily_returns).cumprod()
    total_return = float(equity.iloc[-1] - 1.0)
    years = max(len(daily_returns) / 252.0, 1 / 252)
    cagr = (1.0 + total_return) ** (1.0 / years) - 1.0 if total_return > -1 else -1.0
    std = float(daily_returns.std())
    annual_volatility = std * math.sqrt(252) if std > 0 else None
    sharpe = float(daily_returns.mean() / std * math.sqrt(252)) if std > 0 else None
    running_max = equity.cummax()
    drawdown = equity / running_max - 1.0
    max_drawdown = float(drawdown.min())
    calmar = cagr / abs(max_drawdown) if max_drawdown < 0 else None
    win_rate = float((daily_returns > 0).mean())
    return {
        "total_return": total_return,
        "cagr": cagr,
        "annual_volatility": annual_volatility,
        "sharpe": sharpe,
        "max_drawdown": max_drawdown,
        "calmar": calmar,
        "win_rate": win_rate,
    }


@dataclass(frozen=True)
class FactorEvaluation:
    name: str
    n_days: int
    n_symbols_median: float
    ic_mean: float
    ic_std: float
    ic_ir: float
    daily_spread_returns: pd.Series
    sharpe: float | None
    cagr: float
    annual_volatility: float | None
    max_drawdown: float
    calmar: float | None
    win_rate: float
    total_return: float


def evaluate_factor(
    name: str, factor: pd.DataFrame, close: pd.DataFrame, min_symbols: int = 30
) -> FactorEvaluation:
    """Screening pass: 1-session forward close-to-close return, no cost/
    slippage modeled. Rank-IC per date (Pearson correlation of ranks) and a
    daily-rebalanced, equal-weight top-quintile-minus-bottom-quintile spread
    return, both non-evidential -- see run_factor_zoo_scan.py's module
    docstring for the full disclosure (overlapping-draw IC t-stats, no
    multiple-comparisons correction across the zoo)."""
    forward_return = close.shift(-1) / close - 1.0
    ic_values: list[float] = []
    spread_returns: dict[str, float] = {}
    symbol_counts: list[int] = []
    for current_date in factor.index[:-1]:
        factor_row = factor.loc[current_date]
        forward_row = forward_return.loc[current_date]
        valid = factor_row.notna() & forward_row.notna()
        symbols = factor_row.index[valid]
        if len(symbols) < min_symbols:
            continue
        f = factor_row[symbols]
        r = forward_row[symbols]
        f_rank = f.rank(pct=True)
        r_rank = r.rank(pct=True)
        if f_rank.std() > 0 and r_rank.std() > 0:
            ic = float(np.corrcoef(f_rank.to_numpy(), r_rank.to_numpy())[0, 1])
            if math.isfinite(ic):
                ic_values.append(ic)
        quintile_size = max(int(len(symbols) * 0.2), 1)
        ordered = f.sort_values()
        bottom = ordered.index[:quintile_size]
        top = ordered.index[-quintile_size:]
        spread_returns[str(current_date)] = float(r[top].mean() - r[bottom].mean())
        symbol_counts.append(len(symbols))

    if len(ic_values) < 2 or len(spread_returns) < 2:
        raise ValueError(f"{name}: insufficient valid cross-sections to evaluate")

    ic_array = np.array(ic_values)
    daily_returns = pd.Series(spread_returns).sort_index()
    metrics = factor_return_metrics(daily_returns)

    return FactorEvaluation(
        name=name,
        n_days=len(daily_returns),
        n_symbols_median=float(np.median(symbol_counts)),
        ic_mean=float(ic_array.mean()),
        ic_std=float(ic_array.std()),
        ic_ir=float(ic_array.mean() / ic_array.std()) if ic_array.std() > 0 else 0.0,
        daily_spread_returns=daily_returns,
        sharpe=metrics["sharpe"],
        cagr=metrics["cagr"],
        annual_volatility=metrics["annual_volatility"],
        max_drawdown=metrics["max_drawdown"],
        calmar=metrics["calmar"],
        win_rate=metrics["win_rate"],
        total_return=metrics["total_return"],
    )


def pairwise_orthogonality(
    evaluations: list[FactorEvaluation], threshold: float = 0.5
) -> list[dict]:
    """Same disclosed rule-of-thumb as score_chapter4_orthogonality.py:
    |correlation| >= 0.5 on overlapping dates flags a redundant pair."""
    results = []
    for i in range(len(evaluations)):
        for j in range(i + 1, len(evaluations)):
            a, b = evaluations[i], evaluations[j]
            aligned = pd.concat(
                {"a": a.daily_spread_returns, "b": b.daily_spread_returns}, axis=1
            ).dropna()
            if len(aligned) < 30:
                continue
            corr = float(aligned["a"].corr(aligned["b"]))
            results.append({
                "pair": [a.name, b.name],
                "correlation": corr,
                "n_overlap_days": len(aligned),
                "redundant": abs(corr) >= threshold,
            })
    return results


def render_charts(evaluations: list[FactorEvaluation], output_dir: Path, top_n: int = 6) -> list[Path]:
    """Real matplotlib PNGs, not placeholders -- written once per scan run."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    ranked = sorted(evaluations, key=lambda e: e.ic_ir, reverse=True)

    fig, ax = plt.subplots(figsize=(9, 6))
    names = [e.name for e in ranked]
    values = [e.ic_ir for e in ranked]
    colors = ["#2a6f4f" if v >= 0 else "#8f3b3b" for v in values]
    ax.barh(names, values, color=colors)
    ax.invert_yaxis()
    ax.set_xlabel("Rank-IC IR (1-session forward return, screening scan, non-evidential)")
    ax.set_title("Factor zoo v1 -- Rank-IC IR by formula")
    ax.axvline(0, color="black", linewidth=0.8)
    fig.tight_layout()
    ic_path = output_dir / "ic-ir-ranking.png"
    fig.savefig(ic_path, dpi=150)
    plt.close(fig)
    paths.append(ic_path)

    fig, ax = plt.subplots(figsize=(9, 6))
    for evaluation in ranked[:top_n]:
        equity = (1.0 + evaluation.daily_spread_returns).cumprod()
        dates = pd.to_datetime(equity.index)
        label = evaluation.name
        if evaluation.sharpe is not None:
            label = f"{evaluation.name} (Sharpe {evaluation.sharpe:.2f})"
        ax.plot(dates, equity.to_numpy(), label=label, linewidth=1.2)
    ax.axhline(1.0, color="black", linewidth=0.6, linestyle="--")
    ax.set_title(f"Factor zoo v1 -- top {top_n} quintile-spread equity curves (no costs modeled)")
    ax.set_ylabel("Growth of $1 (top-quintile minus bottom-quintile, equal-weight)")
    ax.legend(fontsize=8)
    fig.autofmt_xdate()
    fig.tight_layout()
    equity_path = output_dir / "top-factor-equity-curves.png"
    fig.savefig(equity_path, dpi=150)
    plt.close(fig)
    paths.append(equity_path)

    return paths
