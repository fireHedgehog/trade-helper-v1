"""Run the CTA v2 pooled vol-scaled trend overlay experiment.

Usage (from backend/):
    python -m app.run_cta_v2

Implements docs/research-protocols/cta-v2-pooled-trend-overlay.md. This is a
no-trade, no-cost characterization and significance test; it may output only
material_and_consistent / not_material_or_not_consistent / invalid. No cost,
execution, or portfolio simulation is authorised by this run.
"""

from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

import pandas as pd

from .research import cta_v2_bootstrap
from .run_experiment import _atomic_json
from .store import load_bars

ROOT = Path(__file__).parents[2]
SPEC_PATH = ROOT / "research/experiments/cta-v2-pooled-trend-overlay.json"
SPEC_SHA256 = "958a3c838778f32cfb562090309b21f42826394517f0f5f68020ac0067f2382e"


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


def common_calendar_bars(spec: dict) -> dict[str, pd.DataFrame]:
    """Load each symbol's full history, then restrict every symbol to the
    intersection of dates present in all 12 -- the common pooled calendar."""
    universe = spec["universe"]
    raw = {symbol: load_bars(symbol) for symbol in universe}
    missing = [symbol for symbol in universe if raw[symbol].empty]
    if missing:
        raise RuntimeError(f"locked symbols missing data: {', '.join(missing)}")
    common_dates = None
    for symbol in universe:
        dates = set(raw[symbol]["date"])
        common_dates = dates if common_dates is None else common_dates & dates
    common_dates = sorted(common_dates)
    return {
        symbol: raw[symbol][raw[symbol]["date"].isin(common_dates)]
        .sort_values("date")
        .reset_index(drop=True)
        for symbol in universe
    }


def data_sha256(spec: dict, bars_by_symbol: dict[str, pd.DataFrame]) -> str:
    """Ordered-binary hash; same method as run_consolidation_feasibility.py."""
    digest = hashlib.sha256()
    for symbol in sorted(spec["universe"]):
        for row in bars_by_symbol[symbol].itertuples(index=False):
            digest.update(symbol.encode() + b"\0" + str(row.date).encode() + b"\0")
            digest.update(struct.pack(">dddd", row.open, row.high, row.low, row.close))
            digest.update(struct.pack(">q", int(row.volume)))
    return digest.hexdigest()


def main() -> None:
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    validate_locked_spec(spec)

    bars_by_symbol = common_calendar_bars(spec)
    data_sha = data_sha256(spec, bars_by_symbol)

    universe = sorted(spec["universe"])
    dates = bars_by_symbol[universe[0]]["date"].to_numpy()
    closes_by_symbol = {
        symbol: bars_by_symbol[symbol]["close"].to_numpy(dtype=float) for symbol in universe
    }

    result = cta_v2_bootstrap(
        closes_by_symbol,
        dates,
        warm_up=spec["warm_up_sessions"],
        block_bars=spec["bootstrap"]["block_bars"],
        resamples=spec["bootstrap"]["resamples"],
        seed=spec["bootstrap"]["seed"],
        materiality_annualized_min=spec["gates"]["materiality_annualized_min_percentage_points"] / 100.0,
    )

    output = ROOT / "output/research/cta-v2-pooled-trend-overlay" / SPEC_SHA256
    _atomic_json(
        output / "manifest.json",
        {
            "experiment_id": spec["experiment_id"],
            "spec_sha256": SPEC_SHA256,
            "data_sha256": data_sha,
            "universe": universe,
            "common_start": str(dates[0]),
            "common_end": str(dates[-1]),
            "pooled_calendar_length": len(dates),
            "no_trade": True,
            "actual_costs_or_execution_accessed": False,
        },
    )
    _atomic_json(
        output / "variant-results.json",
        {"variants": result["variants"], "placebo": result["placebo"]},
    )
    _atomic_json(output / "diagnostics.json", result["regime_diagnostics"])
    _atomic_json(
        output / "decision.json",
        {
            "decision": result["decision"],
            "spec_sha256": SPEC_SHA256,
            "data_sha256": data_sha,
            "primary_variant": result["primary_variant"],
            "gates": result["gates"],
        },
    )
    print(
        json.dumps(
            {
                "output": str(output),
                "data_sha256": data_sha,
                "decision": result["decision"],
                "gates": result["gates"],
                "primary": result["variants"][result["primary_variant"]],
                "placebo": result["placebo"],
            },
            sort_keys=True,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
