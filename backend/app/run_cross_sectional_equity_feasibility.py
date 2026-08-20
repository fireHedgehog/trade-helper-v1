"""Run the cross-sectional equity momentum feasibility v1 engine check.

Usage (from backend/):
    python -m app.run_cross_sectional_equity_feasibility

Implements
docs/research-protocols/cross-sectional-equity-momentum-feasibility-v1.md.
This is NOT a Stage 9A candidate and produces NO evidential claim about
real cross-sectional equity momentum -- see the protocol's section 1 for
why (survivorship bias in the universe; a disclosed pre-lock parameter
peek). It answers one question only: does the panel-bootstrap engine
already proven at ETF-12 scale (N=12) also run correctly at real equity
scale (N=495)? Output is engine_feasible / engine_not_feasible only.
"""

from __future__ import annotations

import hashlib
import json
import math
import struct
from pathlib import Path

from .research import etf12_rotation_bootstrap
from .run_experiment import _atomic_json
from .store import load_bars

ROOT = Path(__file__).parents[2]
SPEC_PATH = ROOT / "research/experiments/cross-sectional-equity-momentum-feasibility-v1.json"
SPEC_SHA256 = "482b84aef0479dff15b2ac489a82ab9cf542d9c59fe23bc82f9cca0fbc03f9b4"


def canonical_spec_sha256(spec: dict) -> str:
    encoded = json.dumps(
        spec, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def validate_locked_spec(spec: dict) -> None:
    spec_sha = canonical_spec_sha256(spec)
    if spec_sha != SPEC_SHA256:
        raise RuntimeError(
            f"locked specification identity failed: expected {SPEC_SHA256}, got {spec_sha}"
        )


def load_aligned_closes(spec: dict) -> tuple[dict, dict, list[str]]:
    """Load bars per symbol, restrict to the true common trading-date
    intersection (not a min/max range -- individual equities can have
    idiosyncratic single-day gaps a range filter would miss), and return
    (aligned close arrays, aligned full bars DataFrames, common dates)."""
    symbols = list(spec["universe"])
    cutoff = spec["universe_construction"]["cutoff_date"]
    bars = {symbol: load_bars(symbol) for symbol in symbols}
    common_end = min(bars[symbol]["date"].iloc[-1] for symbol in symbols)
    filtered = {
        symbol: bars[symbol][
            (bars[symbol]["date"] >= cutoff) & (bars[symbol]["date"] <= common_end)
        ]
        for symbol in symbols
    }
    common_dates = sorted(set.intersection(*(set(df["date"]) for df in filtered.values())))
    aligned_bars = {
        symbol: filtered[symbol].set_index("date").loc[common_dates].reset_index()
        for symbol in symbols
    }
    lengths = {len(aligned_bars[symbol]) for symbol in symbols}
    if len(lengths) != 1:
        raise RuntimeError(f"aligned bars are not equal length: {lengths}")
    closes = {
        symbol: aligned_bars[symbol]["close"].to_numpy(dtype=float) for symbol in symbols
    }
    return closes, aligned_bars, common_dates


def data_sha256(spec: dict, aligned_bars: dict) -> str:
    digest = hashlib.sha256()
    for symbol in list(spec["universe"]):
        for row in aligned_bars[symbol].itertuples(index=False):
            digest.update(symbol.encode() + b"\0" + str(row.date).encode() + b"\0")
            digest.update(struct.pack(">dddd", row.open, row.high, row.low, row.close))
            digest.update(struct.pack(">q", int(row.volume)))
    return digest.hexdigest()


def evaluate_engine_feasibility(spec: dict, result: dict) -> dict:
    """engine_feasible iff the bootstrap produced a well-formed output --
    NOT a claim about the correlation's real-world meaning. See protocol
    section 6."""
    checks = {
        "rebalance_date_count_positive": result["rebalance_date_count"] > 0,
        "observed_correlation_finite": math.isfinite(result["observed_correlation"]),
        "p_value_finite_and_in_range": (
            math.isfinite(result["p_value"]) and 0.0 <= result["p_value"] <= 1.0
        ),
        "resample_count_matches_spec": True,  # etf12_rotation_bootstrap raises on any failure mid-loop
    }
    decision = "engine_feasible" if all(checks.values()) else "engine_not_feasible"
    return {"checks": checks, "decision": decision}


def main() -> None:
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    validate_locked_spec(spec)
    closes, aligned_bars, common_dates = load_aligned_closes(spec)
    data_sha = data_sha256(spec, aligned_bars)

    result = etf12_rotation_bootstrap(
        closes,
        block_bars=spec["bootstrap"]["block_bars"],
        resamples=spec["bootstrap"]["resamples"],
        seed=spec["bootstrap"]["seed"],
        warm_up=spec["rebalance_grid"]["warm_up_sessions"],
        spacing=spec["rebalance_grid"]["spacing_sessions"],
        formation=spec["formation"]["window_sessions"],
        holding=spec["holding"]["horizon_sessions"],
    )
    feasibility = evaluate_engine_feasibility(spec, result)

    output = ROOT / "output/research/cross-sectional-equity-momentum-feasibility-v1" / SPEC_SHA256
    _atomic_json(
        output / "manifest.json",
        {
            "experiment_id": spec["experiment_id"],
            "spec_sha256": SPEC_SHA256,
            "data_sha256": data_sha,
            "universe_size": len(result["symbols"]),
            "common_date_start": common_dates[0],
            "common_date_end": common_dates[-1],
            "common_date_count": len(common_dates),
            "no_trade": True,
            "actual_costs_or_execution_accessed": False,
            "evidential_status": "non-evidential -- engine feasibility check only, see protocol section 1",
        },
    )
    _atomic_json(
        output / "rebalance-results.json",
        {
            "observed_correlation": result["observed_correlation"],
            "rebalance_date_count": result["rebalance_date_count"],
            "p_value": result["p_value"],
            "universe_size": len(result["symbols"]),
        },
    )
    _atomic_json(
        output / "decision.json",
        {
            "decision": feasibility["decision"],
            "spec_sha256": SPEC_SHA256,
            "data_sha256": data_sha,
            "checks": feasibility["checks"],
            "observed_correlation_reported_non_evidentially": result["observed_correlation"],
            "p_value_reported_non_evidentially": result["p_value"],
            "rebalance_date_count": result["rebalance_date_count"],
        },
    )
    print(
        json.dumps(
            {
                "output": str(output),
                "data_sha256": data_sha,
                "decision": feasibility["decision"],
                "checks": feasibility["checks"],
                "observed_correlation": result["observed_correlation"],
                "p_value": result["p_value"],
                "rebalance_date_count": result["rebalance_date_count"],
                "universe_size": len(result["symbols"]),
            },
            sort_keys=True,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
