"""Run the ETF-12 cross-sectional rotation v1 rank-continuation experiment.

Usage (from backend/):
    python -m app.run_etf12_rotation

Implements docs/research-protocols/etf12-cross-sectional-rotation-v1.md.
This is a no-trade rank-continuation study and significance test; it may
output only material_and_consistent / not_material_or_not_consistent /
invalid. No cost, execution, position, or sleeve is authorised by this run.
"""

from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

from .portfolio_universe import PORTFOLIO_CLASSIFICATIONS
from .research import etf12_rotation_bootstrap
from .run_experiment import _atomic_json
from .store import load_bars

ROOT = Path(__file__).parents[2]
SPEC_PATH = ROOT / "research/experiments/etf12-cross-sectional-rotation-v1.json"
SPEC_SHA256 = "ce80d2e15bfdc3a644289e6e762d9c041193fba1366c2e2c0faa1d1b87e5d358"


def canonical_spec_sha256(spec: dict) -> str:
    encoded = json.dumps(
        spec, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def load_aligned_closes(spec: dict) -> tuple[dict, dict]:
    """Load bars per symbol, restrict to the shared date range every symbol
    covers, and return (aligned close arrays, aligned full bars DataFrames)
    for fingerprinting."""
    symbols = sorted(spec["universe"])
    bars = {symbol: load_bars(symbol) for symbol in symbols}
    common_start = max(bars[symbol]["date"].iloc[0] for symbol in symbols)
    common_end = min(bars[symbol]["date"].iloc[-1] for symbol in symbols)
    aligned_bars = {
        symbol: bars[symbol][
            (bars[symbol]["date"] >= common_start) & (bars[symbol]["date"] <= common_end)
        ].reset_index(drop=True)
        for symbol in symbols
    }
    lengths = {len(aligned_bars[symbol]) for symbol in symbols}
    if len(lengths) != 1:
        raise RuntimeError(f"aligned bars are not equal length: {lengths}")
    closes = {
        symbol: aligned_bars[symbol]["close"].to_numpy(dtype=float) for symbol in symbols
    }
    return closes, aligned_bars


def data_sha256(spec: dict, aligned_bars: dict) -> str:
    digest = hashlib.sha256()
    for symbol in sorted(spec["universe"]):
        for row in aligned_bars[symbol].itertuples(index=False):
            digest.update(symbol.encode() + b"\0" + str(row.date).encode() + b"\0")
            digest.update(struct.pack(">dddd", row.open, row.high, row.low, row.close))
            digest.update(struct.pack(">q", int(row.volume)))
    return digest.hexdigest()


def validate_locked_spec(spec: dict) -> None:
    spec_sha = canonical_spec_sha256(spec)
    if spec_sha != SPEC_SHA256:
        raise RuntimeError(
            f"locked specification identity failed: expected {SPEC_SHA256}, got {spec_sha}"
        )


def evaluate_cluster_breadth(spec: dict, formation_ranks_by_date: dict, symbols: list[str]) -> dict:
    """At least cluster_breadth_minimum_clusters of the 6 cluster values must
    each contribute an asset to the top-third formation-rank group at least
    once across all rebalance dates."""
    top_third_count = max(1, len(symbols) // 3)
    ever_top_third: set[str] = set()
    for ranks in formation_ranks_by_date.values():
        order = sorted(range(len(symbols)), key=lambda i: -ranks[i])
        for i in order[:top_third_count]:
            ever_top_third.add(symbols[i])
    clusters = sorted({PORTFOLIO_CLASSIFICATIONS[symbol].cluster for symbol in ever_top_third})
    minimum = int(spec["gates"]["cluster_breadth_minimum_clusters"])
    return {
        "ever_top_third_assets": sorted(ever_top_third),
        "clusters_represented": clusters,
        "cluster_breadth_met": len(clusters) >= minimum,
    }


def evaluate_gates(spec: dict, result: dict, breadth: dict) -> dict:
    alpha = float(spec["gates"]["alpha"])
    minimum_correlation = float(spec["gates"]["materiality"]["minimum_correlation"])
    materiality_met = (
        result["observed_correlation"] >= minimum_correlation and result["p_value"] <= alpha
    )
    if materiality_met and breadth["cluster_breadth_met"]:
        decision = "material_and_consistent"
    else:
        decision = "not_material_or_not_consistent"
    return {
        "materiality_met": materiality_met,
        "cluster_breadth_met": breadth["cluster_breadth_met"],
        "clusters_represented": breadth["clusters_represented"],
        "ever_top_third_assets": breadth["ever_top_third_assets"],
        "decision": decision,
    }


def main() -> None:
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    validate_locked_spec(spec)
    closes, aligned_bars = load_aligned_closes(spec)
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
    formation_ranks_by_date = {
        int(date): ranks for date, ranks in result["formation_ranks_by_date"].items()
    }
    breadth = evaluate_cluster_breadth(spec, formation_ranks_by_date, result["symbols"])
    gates = evaluate_gates(spec, result, breadth)

    output = ROOT / "output/research/etf12-cross-sectional-rotation-v1" / SPEC_SHA256
    _atomic_json(
        output / "manifest.json",
        {
            "experiment_id": spec["experiment_id"],
            "spec_sha256": SPEC_SHA256,
            "data_sha256": data_sha,
            "universe": result["symbols"],
            "aligned_common_start": str(aligned_bars[result["symbols"][0]]["date"].iloc[0]),
            "aligned_common_end": str(aligned_bars[result["symbols"][0]]["date"].iloc[-1]),
            "no_trade": True,
            "actual_costs_or_execution_accessed": False,
        },
    )
    _atomic_json(
        output / "rebalance-results.json",
        {
            "observed_correlation": result["observed_correlation"],
            "rebalance_date_count": result["rebalance_date_count"],
            "p_value": result["p_value"],
            "symbols": result["symbols"],
            "formation_ranks_by_date": result["formation_ranks_by_date"],
        },
    )
    _atomic_json(
        output / "decision.json",
        {
            "decision": gates["decision"],
            "spec_sha256": SPEC_SHA256,
            "data_sha256": data_sha,
            "observed_correlation": result["observed_correlation"],
            "p_value": result["p_value"],
            "rebalance_date_count": result["rebalance_date_count"],
            **{k: v for k, v in gates.items() if k != "decision"},
        },
    )
    print(
        json.dumps(
            {
                "output": str(output),
                "data_sha256": data_sha,
                "observed_correlation": result["observed_correlation"],
                "p_value": result["p_value"],
                "rebalance_date_count": result["rebalance_date_count"],
                **gates,
            },
            sort_keys=True,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
