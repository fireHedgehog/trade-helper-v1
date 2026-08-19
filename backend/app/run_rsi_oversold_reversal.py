"""Run the RSI(14) oversold-crossing short-horizon reversal experiment.

Usage (from backend/):
    python -m app.run_rsi_oversold_reversal

Implements docs/research-protocols/rsi-oversold-reversal-v1.md. This is a
no-trade event study and significance test; it may output only
material_and_consistent / not_material_or_not_consistent / invalid. No cost,
execution, or portfolio simulation is authorised by this run.
"""

from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

from .portfolio_universe import PORTFOLIO_CLASSIFICATIONS
from .research import holm_adjust, rsi_bootstrap
from .run_experiment import _atomic_json
from .store import load_bars

ROOT = Path(__file__).parents[2]
SPEC_PATH = ROOT / "research/experiments/rsi-oversold-reversal-v1.json"
SPEC_SHA256 = "4e99621b45867b5ed7431d77f8bf642f6988ac48d3972ff9143548099cd5e0f8"


def canonical_spec_sha256(spec: dict) -> str:
    encoded = json.dumps(
        spec, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def load_universe_bars(spec: dict) -> dict:
    return {symbol: load_bars(symbol) for symbol in spec["universe"]}


def data_sha256(spec: dict, bars_by_symbol: dict) -> str:
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
    per_asset: dict[str, dict] = {}
    for symbol in order:
        closes = bars_by_symbol[symbol]["close"].to_numpy(dtype=float)
        per_asset[symbol] = rsi_bootstrap(
            closes,
            block_bars=spec["bootstrap"]["block_bars"],
            resamples=spec["bootstrap"]["resamples"],
            seed=spec["bootstrap"]["seed"],
            warm_up=spec["indicator"]["warm_up_sessions"],
            cooldown=spec["event"]["cooldown_sessions"],
            horizon=spec["forward_return"]["horizon_sessions"],
            min_event_count=spec["event"]["minimum_event_count_per_asset"],
        )

    eligible = [s for s in order if not per_asset[s]["insufficient_events"]]
    raw_p = [per_asset[s]["p_event"] for s in eligible]
    if raw_p:
        holm_p = holm_adjust(raw_p)
        for symbol, adjusted in zip(eligible, holm_p):
            per_asset[symbol]["holm_p_event"] = adjusted
    for symbol in order:
        per_asset[symbol].setdefault("holm_p_event", None)

    return per_asset


def evaluate_gates(spec: dict, per_asset: dict) -> dict:
    alpha = float(spec["bootstrap"]["correction"]["alpha"])
    materiality_min = float(spec["gates"]["materiality"]["mean_forward_return_minimum"])
    order = sorted(spec["universe"])

    materiality_by_asset = {}
    excluded_insufficient_events = []
    for symbol in order:
        result = per_asset[symbol]
        if result["insufficient_events"]:
            excluded_insufficient_events.append(symbol)
            materiality_by_asset[symbol] = {
                "eligible": False,
                "event_material": False,
                "beats_placebo": False,
                "qualifies": False,
            }
            continue
        event_material = (
            result["observed_event_mean_forward_return"] >= materiality_min
            and result["holm_p_event"] is not None
            and result["holm_p_event"] <= alpha
        )
        beats_placebo = (
            result["observed_event_mean_forward_return"]
            > result["observed_placebo_mean_forward_return"]
        )
        materiality_by_asset[symbol] = {
            "eligible": True,
            "event_material": event_material,
            "beats_placebo": beats_placebo,
            "qualifies": event_material and beats_placebo,
        }

    qualifying = [symbol for symbol in order if materiality_by_asset[symbol]["qualifies"]]
    eligible_count = len(order) - len(excluded_insufficient_events)
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
        "eligible_asset_count": eligible_count,
        "excluded_insufficient_events": excluded_insufficient_events,
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

    output = ROOT / "output/research/rsi-oversold-reversal-v1" / SPEC_SHA256
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
