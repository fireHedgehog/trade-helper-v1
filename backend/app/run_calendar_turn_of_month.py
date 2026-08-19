"""Run the Calendar Turn-of-Month v1 daily-return-differential experiment.

Usage (from backend/):
    python -m app.run_calendar_turn_of_month

Implements docs/research-protocols/calendar-turn-of-month-v1.md. This is a
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
from .research import holm_adjust, tom_bootstrap
from .run_experiment import _atomic_json
from .store import load_bars

ROOT = Path(__file__).parents[2]
SPEC_PATH = ROOT / "research/experiments/calendar-turn-of-month-v1.json"
SPEC_SHA256 = "e961ffd26eb65b77b51ef397a603507aead215a4c9748a3073d4cc2e4bd01e92"


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
        bars = bars_by_symbol[symbol]
        closes = bars["close"].to_numpy(dtype=float)
        dates = bars["date"]
        per_asset[symbol] = tom_bootstrap(
            closes,
            dates,
            block_bars=spec["bootstrap"]["block_bars"],
            resamples=spec["bootstrap"]["resamples"],
            seed=spec["bootstrap"]["seed"],
            min_event_count=spec["gates"]["minimum_event_count"],
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
    materiality_min = float(spec["gates"]["materiality"]["daily_differential_minimum"])
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
                "qualifies": False,
            }
            continue
        event_material = (
            result["observed_daily_differential"] >= materiality_min
            and result["holm_p_event"] is not None
            and result["holm_p_event"] <= alpha
        )
        materiality_by_asset[symbol] = {
            "eligible": True,
            "event_material": event_material,
            "qualifies": event_material,
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

    output = ROOT / "output/research/calendar-turn-of-month-v1" / SPEC_SHA256
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
