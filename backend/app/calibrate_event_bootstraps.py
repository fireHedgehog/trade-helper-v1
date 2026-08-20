"""Monte Carlo Type-I error calibration for the event-recomputing bootstrap
variants: SMA Cross v1, RSI oversold reversal, TA Breakout v1, Wave Pull v1,
and Overnight Gap Continuation v1.

Usage (from backend/):
    python -m app.calibrate_event_bootstraps [--replications N]

This is methodology validation, not a market hypothesis test: no real data
is touched, no research-candidate scorecard applies, and this is not a
Stage 9A protocol. Synthetic null return series (zero true mean, GARCH(1,1)
volatility clustering, so realistic serial dependence in variance with no
genuine directional predictability by construction) are generated many
times; each candidate's own production bootstrap function is run
unmodified against each synthetic series, and the empirical fraction of
p <= 0.05 draws is compared to the nominal 5%. A well-calibrated test
should reject a true null at approximately its nominal rate; a materially
higher empirical rate means the test is anti-conservative (more likely to
report a false positive than advertised).

Flagged in docs/brainstorm/2026-08-20-ensemble-factor-vocabulary.md as a
gap specific to the event-RECOMPUTING extensions tested here. ETF-12
rotation, Calendar Turn-of-Month, Calendar Day-of-Week, and CTA v2 do not
share this exposure -- they resample an already-realized series with no
per-resample state/event recomputation, much closer to textbook
Politis-Romano usage, and are not tested here.

Deliberate deviations from each candidate's own locked production
parameters, both disclosed rather than silently applied:
  - resamples reduced from each candidate's locked 5,000 to 1,000 per call.
    Checking the empirical REJECTION RATE across many replications does not
    need the same inner precision as computing one real decision's p-value;
    the minimum achievable p-value only moves from ~1/5001 to ~1/1001,
    which does not materially affect whether values cross the 0.05
    threshold being measured here.
  - series length fixed at 3,000 bars. Shorter than most real per-asset
    histories used by the actual closed results (5,165-8,445 rows for the
    12 locked ETFs) -- if anything conservative for the event-count-
    sensitive candidates (Wave Pull, TA Breakout), which would see more
    qualifying events on a real, longer history than they do here.
block_bars and each candidate's own event-definition parameters (RSI
period/threshold, breakout window, impulse threshold, gap quantile, etc.)
are unchanged from production.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np

from . import research
from .run_experiment import _atomic_json

ROOT = Path(__file__).parents[2]
OUTPUT_DIR = ROOT / "output/research/event-bootstrap-calibration-v1"

GARCH_ALPHA = 0.08
GARCH_BETA = 0.90
GARCH_TARGET_DAILY_VOL = 0.01
GARCH_OMEGA = GARCH_TARGET_DAILY_VOL**2 * (1 - GARCH_ALPHA - GARCH_BETA)
SERIES_LENGTH = 3_000
CALIBRATION_RESAMPLES = 1_000
CALIBRATION_BLOCK_BARS = 20
ALPHA = 0.05
DEFAULT_REPLICATIONS = 300


def garch_log_returns(
    n: int, *, omega: float = GARCH_OMEGA, alpha: float = GARCH_ALPHA,
    beta: float = GARCH_BETA, seed: int,
) -> np.ndarray:
    """Zero-mean GARCH(1,1) log returns: realistic volatility clustering,
    no genuine directional predictability by construction (mean is exactly
    zero at every step, independent of history)."""
    rng = np.random.default_rng(seed)
    sigma2 = np.empty(n)
    eps = np.empty(n)
    sigma2[0] = omega / (1 - alpha - beta)
    eps[0] = math.sqrt(sigma2[0]) * rng.standard_normal()
    for t in range(1, n):
        sigma2[t] = omega + alpha * eps[t - 1] ** 2 + beta * sigma2[t - 1]
        eps[t] = math.sqrt(sigma2[t]) * rng.standard_normal()
    return eps


def closes_from_returns(log_returns: np.ndarray, base: float = 100.0) -> np.ndarray:
    return base * np.exp(np.concatenate([[0.0], np.cumsum(log_returns[1:])]))


def opens_closes_from_independent_components(n: int, *, seed: int) -> tuple[np.ndarray, np.ndarray]:
    """Independent overnight/intraday GARCH components: two separate RNG
    streams, half the target variance each -- zero true relationship
    between gap direction/magnitude and subsequent price action by
    construction, the null Overnight Gap Continuation v1 is meant to test
    against."""
    overnight = garch_log_returns(n, omega=GARCH_OMEGA / 2, seed=seed)
    intraday = garch_log_returns(n, omega=GARCH_OMEGA / 2, seed=seed + 10_000_000)
    opens = np.empty(n)
    closes = np.empty(n)
    opens[0] = 100.0
    closes[0] = 100.0
    for t in range(1, n):
        opens[t] = closes[t - 1] * math.exp(overnight[t])
        closes[t] = opens[t] * math.exp(intraday[t])
    return opens, closes


def _wilson_interval(successes: int, n: int, z: float = 1.959963985) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    phat = successes / n
    denom = 1 + z**2 / n
    center = (phat + z**2 / (2 * n)) / denom
    half = z * math.sqrt(phat * (1 - phat) / n + z**2 / (4 * n**2)) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def run_sma_cross(closes: np.ndarray, seed: int) -> dict[str, float]:
    result = research.sma_cross_bootstrap(
        closes, research.sma_cross_state,
        block_bars=CALIBRATION_BLOCK_BARS, resamples=CALIBRATION_RESAMPLES, seed=seed,
    )
    return {"p_delta_sigma": result["p_delta_sigma"], "p_delta_mdd": result["p_delta_mdd"]}


def run_rsi(closes: np.ndarray, seed: int) -> dict[str, float] | None:
    result = research.rsi_bootstrap(closes, resamples=CALIBRATION_RESAMPLES, seed=seed)
    if result["insufficient_events"]:
        return None
    return {"p_event": result["p_event"]}


def run_ta_breakout(closes: np.ndarray, seed: int) -> dict[str, float] | None:
    result = research.ta_breakout_bootstrap(closes, resamples=CALIBRATION_RESAMPLES, seed=seed)
    if result["insufficient_events"]:
        return None
    return {"p_event": result["p_event"]}


def run_wave_pull(closes: np.ndarray, seed: int) -> dict[str, float] | None:
    result = research.wave_pull_bootstrap(closes, resamples=CALIBRATION_RESAMPLES, seed=seed)
    if result["insufficient_events"]:
        return None
    return {"p_event": result["p_event"]}


def run_overnight_gap(opens: np.ndarray, closes: np.ndarray, seed: int) -> dict[str, float] | None:
    result = research.overnight_gap_bootstrap(opens, closes, resamples=CALIBRATION_RESAMPLES, seed=seed)
    if result["insufficient_events"]:
        return None
    return {"p_event": result["p_event"], "p_gap_vs_placebo": result["p_gap_vs_placebo"]}


def run(replications: int) -> dict:
    p_values: dict[str, dict[str, list[float]]] = {
        "sma_cross": {"p_delta_sigma": [], "p_delta_mdd": []},
        "rsi": {"p_event": []},
        "ta_breakout": {"p_event": []},
        "wave_pull": {"p_event": []},
        "overnight_gap": {"p_event": [], "p_gap_vs_placebo": []},
    }
    insufficient = {"rsi": 0, "ta_breakout": 0, "wave_pull": 0, "overnight_gap": 0}

    start = time.time()
    for i in range(replications):
        seed = 900_000 + i
        r = garch_log_returns(SERIES_LENGTH, seed=seed)
        closes = closes_from_returns(r)

        for k, v in run_sma_cross(closes, seed).items():
            p_values["sma_cross"][k].append(v)

        for name, fn in (("rsi", run_rsi), ("ta_breakout", run_ta_breakout), ("wave_pull", run_wave_pull)):
            stats = fn(closes, seed)
            if stats is None:
                insufficient[name] += 1
            else:
                for k, v in stats.items():
                    p_values[name][k].append(v)

        opens, gap_closes = opens_closes_from_independent_components(SERIES_LENGTH, seed=seed)
        stats = run_overnight_gap(opens, gap_closes, seed)
        if stats is None:
            insufficient["overnight_gap"] += 1
        else:
            for k, v in stats.items():
                p_values["overnight_gap"][k].append(v)

        if (i + 1) % 10 == 0:
            elapsed = time.time() - start
            print(f"{i + 1}/{replications} replications, {elapsed:.0f}s elapsed", flush=True)

    report: dict = {}
    for name, stat_dict in p_values.items():
        report[name] = {}
        for stat_name, values in stat_dict.items():
            n_used = len(values)
            rejections = sum(1 for p in values if p <= ALPHA)
            rate = rejections / n_used if n_used else None
            lo, hi = _wilson_interval(rejections, n_used) if n_used else (None, None)
            report[name][stat_name] = {
                "replications_used": n_used,
                "rejections_at_alpha_0.05": rejections,
                "empirical_type1_rate": rate,
                "wilson_95_ci": [lo, hi],
            }
        if name in insufficient:
            report[name]["insufficient_event_replications"] = insufficient[name]

    return {
        "replications_attempted": replications,
        "series_length": SERIES_LENGTH,
        "calibration_resamples": CALIBRATION_RESAMPLES,
        "calibration_block_bars": CALIBRATION_BLOCK_BARS,
        "nominal_alpha": ALPHA,
        "null_generator": (
            f"GARCH(1,1), zero mean, alpha={GARCH_ALPHA}, beta={GARCH_BETA}, "
            f"target unconditional daily vol {GARCH_TARGET_DAILY_VOL}"
        ),
        "wall_clock_seconds": time.time() - start,
        "results": report,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replications", type=int, default=DEFAULT_REPLICATIONS)
    args = parser.parse_args()

    report = run(args.replications)
    output_path = OUTPUT_DIR / "calibration-report.json"
    _atomic_json(output_path, report)
    print(json.dumps(report, sort_keys=True, indent=2, default=str))
    print(f"\nWritten to {output_path}")


if __name__ == "__main__":
    main()
