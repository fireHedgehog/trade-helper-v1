"""Run cross-sectional equity momentum v1 (CS-01) -- point-in-time re-baseline.

Usage (from backend/):
    python -m app.run_cross_sectional_momentum_v1

Implements docs/research-protocols/cross-sectional-momentum-v1.md. Unlike
cross-sectional-equity-momentum-feasibility-v1 (engine-only, non-evidential),
this is a confirmatory Stage 9B test -- subject to the residual
survivorship-bias caveat disclosed in the protocol's section 2. May output
only material_and_consistent / not_material_or_not_consistent / invalid.
No cost, execution, position, or sleeve is authorised by this run.
"""

from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

import numpy as np
import pandas as pd

from .research import cross_sectional_momentum_bootstrap
from .run_experiment import _atomic_json
from .store import connect, load_bars

ROOT = Path(__file__).parents[2]
SPEC_PATH = ROOT / "research/experiments/cross-sectional-momentum-v1.json"
SPEC_SHA256 = "46cdf4b44aed563a15cac53b9c9b2fdc22c4be4f2ca6bec5b94243fd044d5ce5"


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


def _membership_intervals(index_name: str = "SP500") -> pd.DataFrame:
    """Load the whole membership-interval table once, instead of calling
    `members_asof` per date (one DB connection per call -- prohibitively
    slow across thousands of rebalance-calendar dates)."""
    with connect() as conn:
        return pd.read_sql_query(
            "SELECT symbol, start_date, end_date FROM universe_membership WHERE index_name = ?",
            conn,
            params=(index_name,),
        )


def build_panel(spec: dict) -> tuple[dict, dict, list[str], pd.DatetimeIndex]:
    """Reindex every universe symbol's close onto SPY's own trading-date
    calendar (restricted to the locked start date), producing ragged NaN
    gaps outside each symbol's real stored coverage -- deliberately not a
    true set-intersection (protocol section 3). Returns
    (closes_by_symbol, membership_mask_by_symbol, symbols, date_index)."""
    symbols = list(spec["universe"])
    start = spec["universe_construction"]["alignment_start_date"]

    spy = load_bars("SPY")
    calendar = spy[spy["date"] >= start]["date"].reset_index(drop=True)
    date_index = pd.Index(calendar)
    date_values = date_index.to_numpy()

    closes_by_symbol: dict[str, np.ndarray] = {}
    for symbol in symbols:
        bars = load_bars(symbol)
        bars = bars[bars["date"] >= start]
        series = bars.set_index("date")["close"].reindex(date_index)
        closes_by_symbol[symbol] = series.to_numpy(dtype=float)

    intervals = _membership_intervals()
    membership_mask_by_symbol: dict[str, np.ndarray] = {}
    by_symbol = {symbol: group for symbol, group in intervals.groupby("symbol")}
    for symbol in symbols:
        mask = np.zeros(len(date_index), dtype=bool)
        group = by_symbol.get(symbol)
        if group is not None:
            for row in group.itertuples(index=False):
                end = "9999-12-31" if pd.isna(row.end_date) else row.end_date
                mask |= (date_values >= row.start_date) & (date_values <= end)
        membership_mask_by_symbol[symbol] = mask

    return closes_by_symbol, membership_mask_by_symbol, symbols, date_index


def combined_eligibility_mask(
    closes_by_symbol: dict[str, np.ndarray],
    membership_mask_by_symbol: dict[str, np.ndarray],
    symbols: list[str],
    formation: int,
    holding: int,
) -> dict[str, np.ndarray]:
    """Membership AND real (non-NaN) price data at t, t-formation, t+holding."""
    n = len(next(iter(closes_by_symbol.values())))
    combined: dict[str, np.ndarray] = {}
    for symbol in symbols:
        closes = closes_by_symbol[symbol]
        has_price = ~np.isnan(closes)
        eligible = membership_mask_by_symbol[symbol] & has_price
        # Also require the formation-lag and holding-lead observations to be
        # real prices -- shift-and-AND, with out-of-range positions False.
        formation_ok = np.zeros(n, dtype=bool)
        formation_ok[formation:] = has_price[formation:] & has_price[:-formation]
        holding_ok = np.zeros(n, dtype=bool)
        holding_ok[:-holding] = has_price[:-holding] & has_price[holding:]
        combined[symbol] = eligible & formation_ok & holding_ok
    return combined


def data_sha256(
    spec: dict,
    closes_by_symbol: dict,
    eligibility_by_symbol: dict,
    date_index: pd.Index,
) -> str:
    """Fingerprint exactly the aligned data the bootstrap consumes -- the
    reindexed close series and the combined eligibility mask, both on the
    same SPY-anchored calendar -- not the raw per-symbol bars rows. Raw bars
    can carry dates outside the aligned calendar (a stray row the reindex
    silently drops), which made an earlier version of this fingerprint
    non-reproducible despite the actual computation being deterministic
    (caught by an independent rerun, per this protocol's own reproducibility
    gate)."""
    digest = hashlib.sha256()
    date_bytes = [str(d).encode() for d in date_index]
    for symbol in sorted(spec["universe"]):
        closes = closes_by_symbol[symbol]
        eligible = eligibility_by_symbol[symbol]
        digest.update(symbol.encode() + b"\0")
        for i, date_b in enumerate(date_bytes):
            value = closes[i]
            packed = struct.pack(">d", 0.0 if np.isnan(value) else value)
            digest.update(date_b + b"\0" + (b"\1" if np.isnan(value) else b"\0") + packed)
        digest.update(np.packbits(eligible).tobytes())
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

    closes_by_symbol, membership_mask_by_symbol, symbols, date_index = build_panel(spec)
    formation = spec["formation"]["window_sessions"]
    holding = spec["holding"]["horizon_sessions"]
    eligibility = combined_eligibility_mask(
        closes_by_symbol, membership_mask_by_symbol, symbols, formation, holding
    )
    data_sha = data_sha256(spec, closes_by_symbol, eligibility, date_index)

    # NaN closes cannot be fed to the bootstrap's log-return machinery even
    # at masked-out positions (log of NaN/negative propagates); forward-fill
    # AFTER computing the real eligibility mask above, so the mask alone
    # gates what actually counts -- the filled value at an ineligible
    # position is never read because eligibility[t] is False there.
    filled_closes = {
        symbol: pd.Series(closes_by_symbol[symbol]).ffill().bfill().to_numpy()
        for symbol in symbols
    }

    result = cross_sectional_momentum_bootstrap(
        filled_closes,
        eligibility,
        block_bars=spec["bootstrap"]["block_bars"],
        resamples=spec["bootstrap"]["resamples"],
        seed=spec["bootstrap"]["seed"],
        warm_up=spec["rebalance_grid"]["warm_up_sessions"],
        spacing=spec["rebalance_grid"]["spacing_sessions"],
        formation=formation,
        holding=holding,
    )
    gates = evaluate_gates(spec, result)

    missing_from_bars = spec["universe_construction"].get("missing_from_bars_count")

    output = ROOT / "output/research/cross-sectional-momentum-v1" / SPEC_SHA256
    _atomic_json(
        output / "manifest.json",
        {
            "experiment_id": spec["experiment_id"],
            "spec_sha256": SPEC_SHA256,
            "data_sha256": data_sha,
            "universe_size": len(symbols),
            "missing_from_bars_count": missing_from_bars,
            "aligned_calendar_start": str(date_index[0]),
            "aligned_calendar_end": str(date_index[-1]),
            "aligned_session_count": len(date_index),
            "no_trade": True,
            "actual_costs_or_execution_accessed": False,
            "residual_survivorship_bias_disclosed": True,
        },
    )
    _atomic_json(
        output / "rebalance-results.json",
        {
            "observed_correlation": result["observed_correlation"],
            "rebalance_date_count": result["rebalance_date_count"],
            "p_value": result["p_value"],
            "universe_size": len(symbols),
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
            "residual_survivorship_bias_disclosed": True,
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
                "universe_size": len(symbols),
            },
            sort_keys=True,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
