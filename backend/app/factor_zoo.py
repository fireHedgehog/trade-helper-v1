"""Formulaic alpha factor zoo -- Chapter 4 production input, not Chapter 1-3.

Cross-sectional operator vocabulary (rank, delay, correlation, ts_rank,
decay_linear, ...) and a curated, portable subset of the published
WorldQuant "101 Formulaic Alphas" (Kakushadze 2015) -- verified against
https://github.com/popbo/alphas/blob/main/alphas101.py, not reconstructed
from memory. Selected for portability: OHLCV + volume only, no vwap/amount/
turnover/industry fields this project's free Yahoo data doesn't have (rules
out most of alpha191, a China-A-share set with different required fields).

Also includes CLASSIC_INDICATORS: 10 hand-implemented classic technical
indicators (RSI, MACD, Bollinger %B, Stochastic, CCI, Williams %R, ROC,
ATR, OBV flow, MFI) -- the most battle-tested OHLCV-only factor family in
the ecosystem, not previously in this codebase.

Also includes ACADEMIC_ANOMALIES: 5 named, real-citation price/volume-only
cross-sectional anomalies (Amihud illiquidity, MAX/lottery-demand,
low-volatility, Corwin-Schultz spread, expected idiosyncratic skewness) --
deliberately a *different* family from the reversal-shaped WQ101/classic-
indicator cluster already screened, not more variants of it. Two of these
(MAX, skewness) are expected to score a NEGATIVE IC-IR under this module's
"high reading = long" rank-IC convention -- that is each paper's own
predicted sign (lottery-demand overpricing), not a misdirection needing
correction the way the classic indicators needed one.

See docs/brainstorm/2026-08-21-open-source-factor-source-backlog.md for
the source survey behind all three batches and what's queued/excluded
next (Qlib Alpha158 is the next queued batch, not yet built).

None of these are individually validated -- that is the point of a zoo:
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


def rsi14(p: Panel) -> pd.DataFrame:
    """RSI(14), Wilder smoothing (EMA with alpha=1/14): 100 - 100/(1+RS)."""
    diff = p.close.diff()
    gain = diff.clip(lower=0.0)
    loss = -diff.clip(upper=0.0)
    avg_gain = gain.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    avg_loss = loss.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    rs = avg_gain / avg_loss.replace(0.0, np.nan)
    return (100 - 100 / (1 + rs)).fillna(100.0)


def macd_histogram(p: Panel) -> pd.DataFrame:
    """MACD(12,26) histogram normalized by close: (macd_line - signal_line) / close."""
    ema12 = p.close.ewm(span=12, adjust=False).mean()
    ema26 = p.close.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    return (macd_line - signal_line) / p.close


def bollinger_pct_b(p: Panel) -> pd.DataFrame:
    """Bollinger %B(20, 2sigma): (close - lower_band) / (upper_band - lower_band)."""
    mid = sma(p.close, 20)
    band = 2 * stddev(p.close, 20)
    upper, lower = mid + band, mid - band
    return (p.close - lower) / (upper - lower).replace(0.0, np.nan)


def stochastic_k(p: Panel) -> pd.DataFrame:
    """Stochastic %K(14): (close - low_14) / (high_14 - low_14)."""
    low14 = ts_min(p.low, 14)
    high14 = ts_max(p.high, 14)
    return (p.close - low14) / (high14 - low14).replace(0.0, np.nan)


def _mean_abs_deviation(window: np.ndarray) -> float:
    return float(np.mean(np.abs(window - window.mean())))


def cci20(p: Panel) -> pd.DataFrame:
    """CCI(20): (typical_price - sma(typical_price,20)) / (0.015 * mean_abs_deviation)."""
    typical = (p.high + p.low + p.close) / 3
    sma_tp = sma(typical, 20)
    mad = typical.rolling(20).apply(_mean_abs_deviation, raw=True)
    return (typical - sma_tp) / (0.015 * mad.replace(0.0, np.nan))


def williams_r(p: Panel) -> pd.DataFrame:
    """Williams %R(14): -100 * (high_14 - close) / (high_14 - low_14)."""
    low14 = ts_min(p.low, 14)
    high14 = ts_max(p.high, 14)
    return -100 * (high14 - p.close) / (high14 - low14).replace(0.0, np.nan)


def roc12(p: Panel) -> pd.DataFrame:
    """Rate of change(12): close / close.shift(12) - 1."""
    return p.close / delay(p.close, 12) - 1.0


def atr_normalized(p: Panel) -> pd.DataFrame:
    """ATR(14) / close -- true range averaged over 14 sessions, scaled by price."""
    prior_close = delay(p.close, 1)
    true_range = (p.high - p.low).abs()
    true_range = true_range.combine((p.high - prior_close).abs(), np.maximum)
    true_range = true_range.combine((p.low - prior_close).abs(), np.maximum)
    return sma(true_range, 14) / p.close


def obv_flow(p: Panel) -> pd.DataFrame:
    """On-balance-volume net change over 20 sessions, normalized by trailing volume sum."""
    signed_volume = sign(delta(p.close, 1)) * p.volume
    obv = signed_volume.cumsum()
    return delta(obv, 20) / ts_sum(p.volume, 20).replace(0.0, np.nan)


def mfi14(p: Panel) -> pd.DataFrame:
    """Money Flow Index(14): volume-weighted RSI analog on typical price."""
    typical = (p.high + p.low + p.close) / 3
    money_flow = typical * p.volume
    typical_diff = delta(typical, 1)
    positive_flow = money_flow.where(typical_diff > 0, 0.0)
    negative_flow = money_flow.where(typical_diff < 0, 0.0)
    positive_sum = ts_sum(positive_flow, 14)
    negative_sum = ts_sum(negative_flow, 14)
    money_ratio = positive_sum / negative_sum.replace(0.0, np.nan)
    return (100 - 100 / (1 + money_ratio)).fillna(100.0)


# ---------------------------------------------------------------------------
# ACADEMIC_ANOMALIES -- 5 named, real-citation anomalies, a different family
# from the reversal-shaped clusters above. See module docstring.
# ---------------------------------------------------------------------------


def amihud_illiquidity(p: Panel) -> pd.DataFrame:
    """Amihud (2002) illiquidity: 21-session mean of |daily return| /
    dollar volume. Expected direction: HIGHER illiquidity predicts HIGHER
    forward return (a compensation-for-risk premium), the same sign
    convention as this module's other factors -- no direction flip needed."""
    dollar_volume = p.close * p.volume
    daily_illiquidity = p.returns.abs() / dollar_volume.replace(0.0, np.nan)
    return sma(daily_illiquidity, 21)


def _mean_of_top5(window: np.ndarray) -> float:
    return float(np.sort(window)[-5:].mean())


def max_effect(p: Panel) -> pd.DataFrame:
    """MAX effect (Bali-Cakici-Whitelaw 2011): mean of the 5 highest daily
    returns in the trailing 21 sessions. Expected direction: HIGH MAX
    predicts LOWER forward returns (lottery-demand overpricing) -- a
    negative IC-IR here is the paper's own predicted sign, not a
    misdirection the way the classic indicators needed correcting."""
    return p.returns.rolling(21).apply(_mean_of_top5, raw=True)


def low_volatility(p: Panel) -> pd.DataFrame:
    """Low-volatility anomaly proxy (Blitz-van Vliet 2007 / Frazzini-
    Pedersen 2014's Betting-Against-Beta, simplified to realized
    volatility -- a true rolling beta needs a benchmark return series this
    Panel does not carry): 21-session realized volatility of daily
    returns. Expected direction: HIGH volatility predicts LOWER forward
    returns -- again the literature's own predicted sign."""
    return stddev(p.returns, 21)


def corwin_schultz_spread(p: Panel) -> pd.DataFrame:
    """Corwin-Schultz (2012) high-low spread estimator, paired with the
    prior session (not the next one) to use only already-known data. The
    standard daily-OHLC-only liquidity proxy, more refined than a raw
    high-low range. Expected direction: same as Amihud -- higher
    estimated spread (more illiquid) predicts higher forward return."""
    prior_high, prior_low = delay(p.high, 1), delay(p.low, 1)
    beta = np.log(p.high / p.low) ** 2 + np.log(prior_high / prior_low) ** 2
    two_day_high = p.high.combine(prior_high, np.maximum)
    two_day_low = p.low.combine(prior_low, np.minimum)
    gamma = np.log(two_day_high / two_day_low) ** 2
    denom = 3 - 2 * math.sqrt(2)
    alpha = (np.sqrt(2 * beta) - np.sqrt(beta)) / denom - np.sqrt(gamma / denom)
    spread = 2 * (np.exp(alpha) - 1) / (1 + np.exp(alpha))
    return spread.clip(lower=0.0)  # conventionally floored -- negative estimates are noise, not real


def expected_skewness_proxy(p: Panel) -> pd.DataFrame:
    """Idiosyncratic skewness, simplified (Boyer-Mitton-Vorkink 2010's
    economic story -- lottery-demand overpricing of positively-skewed
    stocks -- via a persistence-based proxy, not the paper's own fitted
    cross-sectional expected-skewness model, which needs lagged
    characteristics and a benchmark series this OHLCV-only project does
    not have): 60-session rolling skewness of raw daily returns. Expected
    direction: HIGH skewness predicts LOWER forward returns, same story
    as MAX."""
    return p.returns.rolling(60).skew()


CLASSIC_INDICATORS: dict[str, Callable[[Panel], pd.DataFrame]] = {
    "rsi14": rsi14,
    "macd_histogram": macd_histogram,
    "bollinger_pct_b": bollinger_pct_b,
    "stochastic_k": stochastic_k,
    "cci20": cci20,
    "williams_r": williams_r,
    "roc12": roc12,
    "atr_normalized": atr_normalized,
    "obv_flow": obv_flow,
    "mfi14": mfi14,
}


ACADEMIC_ANOMALIES: dict[str, Callable[[Panel], pd.DataFrame]] = {
    "amihud_illiquidity": amihud_illiquidity,
    "max_effect": max_effect,
    "low_volatility": low_volatility,
    "corwin_schultz_spread": corwin_schultz_spread,
    "expected_skewness_proxy": expected_skewness_proxy,
}

# Factors whose literature-predicted direction is a negative IC-IR under
# this module's "high reading = long" convention -- disclosed here once so
# every consumer (scan script, tests, result docs) reads the same list
# instead of re-deriving it.
NEGATIVE_EXPECTED_DIRECTION = {"max_effect", "expected_skewness_proxy"}


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
    name: str, factor: pd.DataFrame, close: pd.DataFrame, min_symbols: int = 30,
    round_trip_cost_bps: float = 0.0,
) -> FactorEvaluation:
    """Screening pass: 1-session forward close-to-close return. Rank-IC per
    date (Pearson correlation of ranks) and a daily-rebalanced, equal-weight
    top-quintile-minus-bottom-quintile spread return, both non-evidential --
    see run_factor_zoo_scan.py's module docstring for the full disclosure
    (overlapping-draw IC t-stats, no multiple-comparisons correction across
    the zoo).

    round_trip_cost_bps: charged on quintile turnover, not a flat daily drag
    -- each day, the fraction of the top/bottom quintile whose membership
    changed since yesterday pays this rate once (one full buy+sell on that
    slot's capital); the first valid day of any run is always turnover-free
    (nothing to compare against yet). Default 0.0 reproduces the original
    zero-cost screen exactly, unchanged -- every existing factor-zoo-v1
    number stays reproducible. See
    docs/research-results/factor-zoo-cost-sensitivity-v1.md for this
    project's own standard rate (derived from engine.py's own
    COMMISSION/SPREAD/SLIPPAGE, not invented fresh) and the reversal-cluster
    result it produced. Reusable by any future factor, WQ101 or new."""
    forward_return = close.shift(-1) / close - 1.0
    ic_values: list[float] = []
    spread_returns: dict[str, float] = {}
    symbol_counts: list[int] = []
    previous_top: frozenset | None = None
    previous_bottom: frozenset | None = None
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
        bottom_index = ordered.index[:quintile_size]
        top_index = ordered.index[-quintile_size:]
        raw_spread = float(r[top_index].mean() - r[bottom_index].mean())
        cost_drag = 0.0
        if round_trip_cost_bps:
            top_set = frozenset(top_index)
            bottom_set = frozenset(bottom_index)
            if previous_top is not None:
                top_turnover = len(top_set - previous_top) / quintile_size
                bottom_turnover = len(bottom_set - previous_bottom) / quintile_size
                cost_drag = (top_turnover + bottom_turnover) * (round_trip_cost_bps / 10_000.0)
            previous_top, previous_bottom = top_set, bottom_set
        spread_returns[str(current_date)] = raw_spread - cost_drag
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


def regime_concentration_by_year(daily_returns: pd.Series) -> dict:
    """ADR 0007 clause 5's regime-concentration check -- the same
    calculation already disclosed in cta-v2-pooled-trend-overlay.md
    ("excluding 2008 ... flips its mean daily excess return ... negative"),
    generalized to sweep every calendar year in the sample rather than a
    few hand-picked ones. For each year present: the mean daily return
    with that year excluded, and whether excluding it flips the sign of
    the full-sample mean. Reusable by any future Chapter 4 candidate, not
    specific to one factor."""
    if daily_returns.empty:
        raise ValueError("regime_concentration_by_year requires at least one daily return")
    year_labels = pd.Series(
        [str(idx)[:4] for idx in daily_returns.index], index=daily_returns.index
    )
    full_mean = float(daily_returns.mean())
    by_year = []
    for year in sorted(year_labels.unique()):
        in_year = daily_returns[year_labels == year]
        excluding = daily_returns[year_labels != year]
        mean_excluding = float(excluding.mean()) if len(excluding) else None
        flips_sign = (
            mean_excluding is not None
            and full_mean != 0
            and (mean_excluding > 0) != (full_mean > 0)
        )
        by_year.append({
            "year": year,
            "n_days": int(len(in_year)),
            "year_mean": float(in_year.mean()),
            "mean_excluding_year": mean_excluding,
            "flips_sign": flips_sign,
        })
    return {
        "full_sample_mean": full_mean,
        "n_days": len(daily_returns),
        "by_year": by_year,
        "any_year_flips_sign": any(row["flips_sign"] for row in by_year),
    }


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
