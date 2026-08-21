"""Ensemble-construction engine v1 -- alpha model, risk model, optimizer.

Implements docs/ensemble-construction-engine-v1.md exactly: the ADR
0010-accepted design for combining Chapter-4-eligible signals into one
long-short, risk-controlled book. Three stages, each independently
testable:

    composite_alpha_scores  -- alpha model (cross-sectional z-score + confidence weight)
    shrinkage_covariance     -- risk model (fixed-intensity Ledoit-Wolf-style shrinkage)
    construct_portfolio      -- optimizer (rank-and-weight, ADR 0004 position cap)

No new dependency (numpy/pandas only), per this project's own repeated
preference (see ETF-12 rotation's own scope decision) and the design
doc's own stated v1 choice.
"""
from __future__ import annotations

import numpy as np


def composite_alpha_scores(
    raw_scores: dict[str, np.ndarray],
    confidence_multipliers: dict[str, float],
    symbols: list[str],
) -> np.ndarray:
    """Per-symbol composite score, per
    ensemble-construction-engine-v1.md section 1: each signal's raw score
    is cross-sectionally z-scored (mean/std taken over symbols with a
    finite value for that signal, not full history -- no look-ahead
    through the standardization statistics), then combined per symbol as
    a confidence-multiplier-weighted average using only the signals that
    have a finite value for that specific symbol. A symbol with no valid
    signal at all gets NaN (excluded from that date's ranking), not zero.
    """
    n = len(symbols)
    weighted_sum = np.zeros(n)
    weight_total = np.zeros(n)
    for signal_name, scores in raw_scores.items():
        c = confidence_multipliers.get(signal_name, 0.0)
        if c <= 0:
            continue
        scores = np.asarray(scores, dtype=float)
        valid = np.isfinite(scores)
        if not valid.any():
            continue
        sigma = scores[valid].std()
        if sigma == 0:
            continue
        mu = scores[valid].mean()
        z = (scores[valid] - mu) / sigma
        weighted_sum[valid] += c * z
        weight_total[valid] += c

    composite = np.full(n, np.nan)
    has_weight = weight_total > 0
    composite[has_weight] = weighted_sum[has_weight] / weight_total[has_weight]
    return composite


def shrinkage_covariance(returns: np.ndarray, delta: float = 0.3) -> np.ndarray:
    """Fixed-intensity shrinkage toward a constant-correlation target, per
    ensemble-construction-engine-v1.md section 2 (Ledoit & Wolf 2004's
    target structure, a fixed disclosed intensity rather than their
    automatic-intensity formula). `returns`: (W, N) trailing daily returns.
    Returns the (N, N) shrunk covariance matrix -- symmetric, diagonal
    exactly equal to each asset's own sample variance by construction."""
    sample_cov = np.cov(returns, rowvar=False)
    sample_cov = np.atleast_2d(sample_cov)
    n = sample_cov.shape[0]
    variances = np.diag(sample_cov).copy()
    std = np.sqrt(np.clip(variances, 0.0, None))
    outer_std = np.outer(std, std)
    with np.errstate(invalid="ignore", divide="ignore"):
        corr = np.where(outer_std > 0, sample_cov / outer_std, 0.0)
    np.fill_diagonal(corr, 0.0)
    num_pairs = n * (n - 1)
    avg_corr = corr.sum() / num_pairs if num_pairs > 0 else 0.0
    target = avg_corr * outer_std
    np.fill_diagonal(target, variances)
    shrunk = delta * target + (1 - delta) * sample_cov
    # Symmetry can drift by floating-point epsilon; enforce it exactly.
    return (shrunk + shrunk.T) / 2.0


def construct_portfolio(
    composite_scores: np.ndarray,
    covariance: np.ndarray,
    symbols: list[str],
    equity: float,
    prices: np.ndarray,
    stop_distances: np.ndarray,
    long_short_fraction: float = 0.20,
    min_names_per_side: int = 5,
) -> dict[str, float]:
    """Rank-and-weight optimizer, per
    ensemble-construction-engine-v1.md section 3: rank eligible symbols by
    composite score, take the top/bottom `long_short_fraction` (floored at
    `min_names_per_side`) as the long/short groups, weight within each
    side inversely to that asset's own shrinkage-covariance volatility,
    scale to 50% gross long / 50% gross short (market-neutral, 100% total
    gross -- no added leverage), then cap every position at ADR 0004's
    stop-distance/notional ceiling: `q_i = floor(min(0.005E/d_i, 0.10E/P_i))`.
    The optimizer proposes a target weight; the ADR 0004 cap is the
    absolute ceiling regardless of what the optimizer wants.

    Returns {symbol: signed target size in shares}. Returns {} (no trade)
    if fewer than `min_names_per_side` eligible names exist on either
    side -- per ADR 0007's minimum-breadth reasoning, a no-trade outcome,
    not a smaller book.
    """
    composite_scores = np.asarray(composite_scores, dtype=float)
    eligible_idx = np.where(np.isfinite(composite_scores))[0]
    if len(eligible_idx) < 2 * min_names_per_side:
        return {}

    order = eligible_idx[np.argsort(-composite_scores[eligible_idx])]
    group_size = max(int(len(eligible_idx) * long_short_fraction), min_names_per_side)
    group_size = min(group_size, len(eligible_idx) // 2)
    if group_size < min_names_per_side:
        return {}

    long_idx = order[:group_size]
    short_idx = order[-group_size:]

    diag_var = np.diag(covariance)
    vol = np.sqrt(np.clip(diag_var, 1e-12, None))

    def _side_weights(idx: np.ndarray) -> np.ndarray:
        inv_vol = 1.0 / vol[idx]
        return inv_vol / inv_vol.sum()

    long_weights = _side_weights(long_idx)
    short_weights = _side_weights(short_idx)

    targets: dict[str, float] = {}
    for idx, weight in zip(long_idx, long_weights):
        targets[symbols[idx]] = weight * 0.5
    for idx, weight in zip(short_idx, short_weights):
        targets[symbols[idx]] = -weight * 0.5

    sized: dict[str, float] = {}
    for symbol, weight in targets.items():
        i = symbols.index(symbol)
        price = prices[i]
        d = stop_distances[i]
        if price <= 0 or d <= 0:
            continue
        target_notional = weight * equity
        cap_shares = np.floor(min(0.005 * equity / d, 0.10 * equity / price))
        target_shares = target_notional / price
        capped = np.sign(target_shares) * min(abs(target_shares), cap_shares)
        sized[symbol] = float(capped)
    return sized
