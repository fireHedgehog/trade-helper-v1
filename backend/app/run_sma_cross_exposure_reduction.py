"""Run the SMA Cross v1 exposure-reduction / volatility-state placebo experiment.

Usage (from backend/):
    python -m app.run_sma_cross_exposure_reduction

Implements docs/research-protocols/sma-cross-v1-exposure-reduction.md. This is a
no-trade characterization and significance test; it may output only
material_and_consistent / not_material_or_not_consistent / invalid. No cost,
execution, or portfolio simulation is authorised by this run.
"""

from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

from .portfolio_universe import PORTFOLIO_CLASSIFICATIONS
from .research import (
    holm_adjust,
    sma_cross_bootstrap,
    sma_cross_state,
    sma_cross_volatility_state,
)
from .run_experiment import _atomic_json
from .store import load_bars

ROOT = Path(__file__).parents[2]
SPEC_PATH = ROOT / "research/experiments/sma-cross-v1-exposure-reduction.json"
SPEC_SHA256 = "3c7e8be2a5fb636a8234bf982e42862412143213f9f42f592a93babcc9956238"

STATE_FUNCTIONS = {
    "sma_state": sma_cross_state,
    "volatility_state_placebo": sma_cross_volatility_state,
}


def canonical_spec_sha256(spec: dict) -> str:
    encoded = json.dumps(
        spec, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def load_universe_bars(spec: dict) -> dict:
    return {symbol: load_bars(symbol) for symbol in spec["universe"]}


def data_sha256(spec: dict, bars_by_symbol: dict) -> str:
    """Ordered-binary hash; same method as run_consolidation_feasibility.py."""
    digest = hashlib.sha256()
    for symbol in sorted(spec["universe"]):
        for row in bars_by_symbol[symbol].itertuples(index=False):
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


def run_bootstrap(spec: dict, bars_by_symbol: dict) -> dict:
    order = sorted(spec["universe"])
    per_asset: dict[str, dict] = {symbol: {} for symbol in order}
    raw_p_by_state: dict[str, list[float]] = {name: [] for name in STATE_FUNCTIONS}

    for symbol in order:
        closes = bars_by_symbol[symbol]["close"].to_numpy(dtype=float)
        for state_name, state_fn in STATE_FUNCTIONS.items():
            result = sma_cross_bootstrap(
                closes,
                state_fn,
                block_bars=spec["bootstrap"]["block_bars"],
                resamples=spec["bootstrap"]["resamples"],
                seed=spec["bootstrap"]["seed"],
            )
            per_asset[symbol][state_name] = result
            raw_p_by_state[state_name].append(result["p_delta_sigma"])
            raw_p_by_state[state_name].append(result["p_delta_mdd"])

    holm_by_state = {name: holm_adjust(values) for name, values in raw_p_by_state.items()}
    cursor = {name: 0 for name in STATE_FUNCTIONS}
    for symbol in order:
        for state_name in STATE_FUNCTIONS:
            i = cursor[state_name]
            per_asset[symbol][state_name]["holm_p_delta_sigma"] = holm_by_state[state_name][i]
            per_asset[symbol][state_name]["holm_p_delta_mdd"] = holm_by_state[state_name][i + 1]
            cursor[state_name] += 2

    return per_asset


def evaluate_gates(spec: dict, per_asset: dict) -> dict:
    alpha = float(spec["bootstrap"]["correction"]["alpha"])
    sigma_threshold = float(spec["gates"]["materiality"]["delta_sigma_max_percentage_points"]) / 100.0
    mdd_threshold = float(spec["gates"]["materiality"]["delta_mdd_max_percentage_points"]) / 100.0
    order = sorted(spec["universe"])

    materiality_by_asset = {}
    for symbol in order:
        sma = per_asset[symbol]["sma_state"]
        placebo = per_asset[symbol]["volatility_state_placebo"]
        sma_material = (
            sma["observed_delta_sigma"] <= sigma_threshold
            and sma["observed_delta_mdd"] <= mdd_threshold
            and sma["holm_p_delta_sigma"] <= alpha
            and sma["holm_p_delta_mdd"] <= alpha
        )
        beats_placebo = (
            sma["observed_delta_sigma"] < placebo["observed_delta_sigma"]
            and sma["observed_delta_mdd"] < placebo["observed_delta_mdd"]
        )
        materiality_by_asset[symbol] = {
            "sma_material": sma_material,
            "beats_placebo": beats_placebo,
            "qualifies": sma_material and beats_placebo,
        }

    qualifying = [symbol for symbol in order if materiality_by_asset[symbol]["qualifies"]]
    breadth_met = len(qualifying) >= int(spec["gates"]["breadth_minimum_assets"])
    clusters = sorted({PORTFOLIO_CLASSIFICATIONS[symbol].cluster for symbol in qualifying})
    concentration_met = len(clusters) >= int(spec["gates"]["concentration_minimum_clusters"])

    if breadth_met and concentration_met:
        decision = "material_and_consistent"
    else:
        decision = "not_material_or_not_consistent"

    return {
        "materiality_by_asset": materiality_by_asset,
        "qualifying_assets": qualifying,
        "breadth_met": breadth_met,
        "breadth_count": len(qualifying),
        "clusters_represented": clusters,
        "concentration_met": concentration_met,
        "decision": decision,
    }


def main() -> None:
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    validate_locked_spec(spec)
    bars_by_symbol = load_universe_bars(spec)
    data_sha = data_sha256(spec, bars_by_symbol)

    per_asset = run_bootstrap(spec, bars_by_symbol)
    gates = evaluate_gates(spec, per_asset)

    output = ROOT / "output/research/sma-cross-v1-exposure-reduction" / SPEC_SHA256
    _atomic_json(
        output / "manifest.json",
        {
            "experiment_id": spec["experiment_id"],
            "spec_sha256": SPEC_SHA256,
            "data_sha256": data_sha,
            "universe": sorted(spec["universe"]),
            "no_trade": True,
            "actual_costs_or_execution_accessed": False,
        },
    )
    _atomic_json(output / "per-asset-results.json", per_asset)
    _atomic_json(
        output / "decision.json",
        {
            "decision": gates["decision"],
            "spec_sha256": SPEC_SHA256,
            "data_sha256": data_sha,
            **{k: v for k, v in gates.items() if k != "materiality_by_asset"},
        },
    )
    print(json.dumps({"output": str(output), "data_sha256": data_sha, **gates}, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
