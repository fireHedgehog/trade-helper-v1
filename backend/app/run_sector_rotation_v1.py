"""Run sector-level cross-sectional momentum v1 (GICS sector rotation).

Usage (from backend/):
    python -m app.run_sector_rotation_v1

Implements docs/research-protocols/sector-rotation-v1.md. Reuses
research.py:etf12_rotation_bootstrap completely unmodified -- a
sector-aggregation step (this file) turns the 501-symbol point-in-time
equity panel into an 11-column synthetic GICS-sector-index panel first.
May output only material_and_consistent / not_material_or_not_consistent /
invalid. No cost, execution, position, or sleeve is authorised by this run.
"""

from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

import numpy as np
import pandas as pd

from .research import etf12_rotation_bootstrap
from .run_experiment import _atomic_json
from .run_cross_sectional_momentum_v1 import _membership_intervals
from .store import load_bars, load_equity_sectors

ROOT = Path(__file__).parents[2]
SPEC_PATH = ROOT / "research/experiments/sector-rotation-v1.json"
SPEC_SHA256 = "bad8d34725bbd62f9bd77ce660d81150aac52623e47b06eb8ee29fd5dc49465a"
CS01_SPEC_PATH = ROOT / "research/experiments/cross-sectional-momentum-v1.json"


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


def _symbol_universe() -> list[str]:
    """The same 501-symbol universe cross-sectional-momentum-v1.json locked."""
    cs01_spec = json.loads(CS01_SPEC_PATH.read_text(encoding="utf-8"))
    return list(cs01_spec["universe"])


def build_sector_panel(spec: dict) -> tuple[dict[str, np.ndarray], pd.Index, dict]:
    """Returns (sector_index_levels, date_index, coverage_stats)."""
    symbols = _symbol_universe()
    start = spec["universe_construction"]["alignment_start_date"]

    spy = load_bars("SPY")
    calendar = spy[spy["date"] >= start]["date"].reset_index(drop=True)
    date_index = pd.Index(calendar)
    date_values = date_index.to_numpy()
    n = len(date_index)

    closes_by_symbol: dict[str, np.ndarray] = {}
    for symbol in symbols:
        bars = load_bars(symbol)
        bars = bars[bars["date"] >= start]
        series = bars.set_index("date")["close"].reindex(date_index)
        closes_by_symbol[symbol] = series.to_numpy(dtype=float)

    intervals = _membership_intervals()
    by_symbol = {symbol: group for symbol, group in intervals.groupby("symbol")}
    membership_mask: dict[str, np.ndarray] = {}
    for symbol in symbols:
        mask = np.zeros(n, dtype=bool)
        group = by_symbol.get(symbol)
        if group is not None:
            for row in group.itertuples(index=False):
                end = "9999-12-31" if pd.isna(row.end_date) else row.end_date
                mask |= (date_values >= row.start_date) & (date_values <= end)
        membership_mask[symbol] = mask

    sectors = load_equity_sectors()
    symbols_by_sector: dict[str, list[str]] = {}
    for symbol in symbols:
        info = sectors.get(symbol)
        if info is None:
            continue
        symbols_by_sector.setdefault(info["gics_sector"], []).append(symbol)

    # Daily simple returns per symbol (NaN where price is missing on either day).
    daily_returns: dict[str, np.ndarray] = {}
    for symbol in symbols:
        closes = closes_by_symbol[symbol]
        ret = np.full(n, np.nan)
        ret[1:] = closes[1:] / closes[:-1] - 1
        daily_returns[symbol] = ret

    sector_names = sorted(symbols_by_sector)
    sector_levels: dict[str, np.ndarray] = {}
    coverage = {}
    for sector in sector_names:
        members = symbols_by_sector[sector]
        member_returns = np.column_stack([daily_returns[s] for s in members])  # (n, m)
        member_mask = np.column_stack([membership_mask[s] for s in members])  # (n, m)
        has_return = ~np.isnan(member_returns)
        eligible = member_mask & has_return
        sector_return = np.zeros(n)
        eligible_counts = eligible.sum(axis=1)
        with np.errstate(invalid="ignore"):
            masked_returns = np.where(eligible, member_returns, 0.0)
            summed = masked_returns.sum(axis=1)
            averaged = np.divide(
                summed, eligible_counts, out=np.zeros(n), where=eligible_counts >= 2
            )
        sector_return[1:] = averaged[1:]
        level = 100.0 * np.cumprod(1.0 + sector_return)
        sector_levels[sector] = level
        coverage[sector] = {
            "member_count": len(members),
            "min_eligible_on_any_date": int(eligible_counts[1:].min()),
            "sparse_date_count": int((eligible_counts[1:] < 2).sum()),
        }

    return sector_levels, date_index, coverage


def data_sha256(sector_levels: dict[str, np.ndarray], date_index: pd.Index) -> str:
    digest = hashlib.sha256()
    date_bytes = [str(d).encode() for d in date_index]
    for sector in sorted(sector_levels):
        digest.update(sector.encode() + b"\0")
        levels = sector_levels[sector]
        for i, date_b in enumerate(date_bytes):
            digest.update(date_b + b"\0")
            digest.update(struct.pack(">d", levels[i]))
    return digest.hexdigest()


def evaluate_gates(spec: dict, result: dict) -> dict:
    minimum_correlation = float(spec["gates"]["materiality"]["minimum_correlation"])
    alpha = float(spec["gates"]["materiality"]["alpha"])
    materiality_met = (
        result["observed_correlation"] >= minimum_correlation and result["p_value"] <= alpha
    )
    decision = "material_and_consistent" if materiality_met else "not_material_or_not_consistent"
    return {"materiality_met": materiality_met, "decision": decision}


def main() -> None:
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    validate_locked_spec(spec)

    sector_levels, date_index, coverage = build_sector_panel(spec)
    data_sha = data_sha256(sector_levels, date_index)

    result = etf12_rotation_bootstrap(
        sector_levels,
        block_bars=spec["bootstrap"]["block_bars"],
        resamples=spec["bootstrap"]["resamples"],
        seed=spec["bootstrap"]["seed"],
        warm_up=spec["rebalance_grid"]["warm_up_sessions"],
        spacing=spec["rebalance_grid"]["spacing_sessions"],
        formation=spec["formation"]["window_sessions"],
        holding=spec["holding"]["horizon_sessions"],
    )
    gates = evaluate_gates(spec, result)

    output = ROOT / "output/research/sector-rotation-v1" / SPEC_SHA256
    _atomic_json(
        output / "manifest.json",
        {
            "experiment_id": spec["experiment_id"],
            "spec_sha256": SPEC_SHA256,
            "data_sha256": data_sha,
            "sector_count": len(sector_levels),
            "sectors": sorted(sector_levels),
            "aligned_calendar_start": str(date_index[0]),
            "aligned_calendar_end": str(date_index[-1]),
            "aligned_session_count": len(date_index),
            "coverage": coverage,
            "no_trade": True,
            "actual_costs_or_execution_accessed": False,
            "today_classification_not_point_in_time_disclosed": True,
        },
    )
    _atomic_json(
        output / "rebalance-results.json",
        {
            "observed_correlation": result["observed_correlation"],
            "rebalance_date_count": result["rebalance_date_count"],
            "p_value": result["p_value"],
            "sectors": result["symbols"],
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
            "materiality_met": gates["materiality_met"],
            "today_classification_not_point_in_time_disclosed": True,
        },
    )
    print(
        json.dumps(
            {
                "output": str(output),
                "data_sha256": data_sha,
                "decision": gates["decision"],
                "observed_correlation": result["observed_correlation"],
                "p_value": result["p_value"],
                "rebalance_date_count": result["rebalance_date_count"],
                "sector_count": len(sector_levels),
                "coverage": coverage,
            },
            sort_keys=True,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
