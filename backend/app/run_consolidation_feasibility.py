"""Validate or run the structural-only consolidation feasibility stage.

Examples from ``backend/``:
    python -m app.run_consolidation_feasibility --validate-only
    python -m app.run_consolidation_feasibility --structure

The runner cannot calculate actual-event forward outcomes or a feasibility decision.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

from .consolidation_feasibility import scan_structure, variants_from_spec
from .consolidation_matching import FEATURES, match_events
from .run_experiment import _atomic_json
from .store import load_bars


ROOT = Path(__file__).parents[2]
SPEC_PATH = ROOT / "research/experiments/consolidation-support-feasibility-v1.json"
SPEC_SHA256 = "90d31fb192ca9f7864a2d2f2565ebf018483d7f620422b5d1accb2d1b027a62b"


def canonical_spec_sha256(spec: dict) -> str:
    encoded = json.dumps(
        spec, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def development_bars(spec: dict) -> dict:
    start = spec["data"]["development_first_date"]
    end = spec["data"]["development_last_date"]
    return {
        symbol: load_bars(symbol).query("date >= @start and date <= @end").reset_index(drop=True)
        for symbol in spec["universe"]
    }


def development_data_sha256(spec: dict, bars_by_symbol: dict) -> str:
    """Hash exact ordered values without locale or decimal-text dependence."""
    digest = hashlib.sha256()
    for symbol in sorted(spec["universe"]):
        for row in bars_by_symbol[symbol].itertuples(index=False):
            digest.update(symbol.encode() + b"\0" + str(row.date).encode() + b"\0")
            digest.update(
                struct.pack(
                    ">ddddq",
                    float(row.open),
                    float(row.high),
                    float(row.low),
                    float(row.close),
                    int(row.volume),
                )
            )
    return digest.hexdigest()


def validate_locked_inputs(spec: dict, bars_by_symbol: dict) -> dict:
    spec_sha = canonical_spec_sha256(spec)
    data_sha = development_data_sha256(spec, bars_by_symbol)
    rows = sum(len(frame) for frame in bars_by_symbol.values())
    checks = {
        "spec_sha256": spec_sha,
        "spec_matches": spec_sha == SPEC_SHA256,
        "data_sha256": data_sha,
        "data_matches": data_sha == spec["data"]["development_sha256"],
        "rows": rows,
        "rows_match": rows == int(spec["data"]["development_rows"]),
        "symbols": len(bars_by_symbol),
    }
    if not all(checks[key] for key in ("spec_matches", "data_matches", "rows_match")):
        raise RuntimeError(f"locked input validation failed: {checks}")
    return checks


def _atomic_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows)
    )
    temporary.replace(path)


def run_structure(spec: dict, bars_by_symbol: dict, checks: dict) -> Path:
    output = (
        ROOT
        / "output/research/consolidation-support-feasibility-v1"
        / SPEC_SHA256
    )
    event_path = output / "structural-events.jsonl"
    previous_event_sha = (
        hashlib.sha256(event_path.read_bytes()).hexdigest() if event_path.exists() else None
    )
    scans = {
        symbol: scan_structure(bars_by_symbol[symbol], symbol=symbol, spec=spec)
        for symbol in spec["universe"]
    }
    matches = match_events(
        bars_by_symbol,
        {symbol: scan.events for symbol, scan in scans.items()},
        matching_spec=spec["matching"],
    )
    match_by_event = {(match.symbol, match.event_date): match for match in matches}
    records = []
    for scan in scans.values():
        for event in scan.events:
            row = event.to_dict()
            match = match_by_event[(event.symbol, event.event_date)]
            row["pre_event_features"] = dict(zip(FEATURES, match.event_features))
            row["control_dates"] = match.control_dates
            row["control_distances"] = match.control_distances
            row["matching_eligible"] = match.matched
            row["matching_funnel"] = {
                "same_year": match.same_year_candidates,
                "after_event_exclusion": match.event_exclusion_candidates,
                "inside_caliper": match.caliper_candidates,
            }
            records.append(row)
    records.sort(key=lambda row: (row["event_date"], row["symbol"]))
    by_symbol = {
        symbol: sum(row["symbol"] == symbol for row in records)
        for symbol in spec["universe"]
    }
    by_year: dict[str, int] = {}
    for row in records:
        year = row["event_date"][:4]
        by_year[year] = by_year.get(year, 0) + 1
    zones_by_variant = {
        variant.variant_id: sum(
            zone.variant_id == variant.variant_id
            for scan in scans.values()
            for zone in scan.zones
        )
        for variant in variants_from_spec(spec)
    }
    eligible_by_variant = {
        variant.variant_id: sum(
            max(0, len(bars_by_symbol[symbol]) - (2 * variant.window - 1))
            for symbol in spec["universe"]
        )
        for variant in variants_from_spec(spec)
    }
    prevalence_by_variant = {
        variant_id: zones_by_variant[variant_id] / eligible_by_variant[variant_id]
        for variant_id in zones_by_variant
    }
    minimum_controls = int(spec["matching"]["controls_per_event_minimum"])
    matched = sum(len(match.control_dates) >= minimum_controls for match in matches)
    matching_coverage = matched / len(matches) if matches else 0.0
    matching_funnel = {
        "same_year_candidates": sum(match.same_year_candidates for match in matches),
        "after_event_exclusion": sum(match.event_exclusion_candidates for match in matches),
        "inside_caliper": sum(match.caliper_candidates for match in matches),
    }
    _atomic_jsonl(event_path, records)
    event_sha = hashlib.sha256(event_path.read_bytes()).hexdigest()
    schema_keys = set(records[0]) if records else set()
    forbidden = {"forward_return", "drawdown", "pnl", "rank", "signal"}
    _atomic_json(
        output / "manifest.json",
        {
            "experiment_id": spec["experiment_id"],
            "stage": "structural_only",
            "spec_sha256": SPEC_SHA256,
            "data_sha256": checks["data_sha256"],
            "actual_event_forward_outcomes_accessed": False,
            "decision_authorized": False,
        },
    )
    _atomic_json(
        output / "audit.json",
        {
            "locked_inputs": checks,
            "structural_schema_keys": sorted(schema_keys),
            "forbidden_forward_fields_present": bool(schema_keys & forbidden),
            "structural_events_sha256": event_sha,
            "byte_identical_structural_rerun": (
                previous_event_sha == event_sha if previous_event_sha else None
            ),
            "status": "structural_stage_complete",
        },
    )
    _atomic_json(
        output / "feasibility.json",
        {
            "status": "incomplete_structural_only",
            "decision": None,
            "deduplicated_events": len(records),
            "events_by_symbol": by_symbol,
            "events_by_year": dict(sorted(by_year.items())),
            "zones_by_variant": zones_by_variant,
            "eligible_completion_dates_by_variant": eligible_by_variant,
            "detector_prevalence_by_variant": prevalence_by_variant,
            "matching_coverage": matching_coverage,
            "matched_events": matched,
            "matching_funnel_totals": matching_funnel,
            "prospective_power": None,
        },
    )
    return output


def finalize_existing(spec: dict, checks: dict) -> tuple[Path, dict]:
    output = ROOT / "output/research/consolidation-support-feasibility-v1" / SPEC_SHA256
    feasibility_path = output / "feasibility.json"
    if not feasibility_path.exists():
        raise RuntimeError("run --structure before finalizing feasibility")
    feasibility = json.loads(feasibility_path.read_text())
    lower = float(spec["gates"]["minimum_detector_prevalence"])
    upper = float(spec["gates"]["maximum_detector_prevalence"])
    prevalence = feasibility["detector_prevalence_by_variant"]
    retained = sorted(
        variant for variant, value in prevalence.items() if lower <= value <= upper
    )
    excluded = sorted(set(prevalence) - set(retained))
    event_total = int(feasibility["deduplicated_events"])
    maximum_asset = max(feasibility["events_by_symbol"].values(), default=0)
    maximum_year = max(feasibility["events_by_year"].values(), default=0)
    gates = {
        "locked_inputs": all(
            checks[key] for key in ("spec_matches", "data_matches", "rows_match")
        ),
        "detector_variants_retained": len(retained) > 0,
        "asset_breadth": sum(value > 0 for value in feasibility["events_by_symbol"].values())
        >= int(spec["gates"]["minimum_assets_with_events"]),
        "calendar_breadth": len(feasibility["events_by_year"])
        >= int(spec["gates"]["minimum_calendar_years_with_events"]),
        "asset_concentration": bool(event_total) and maximum_asset / event_total
        <= float(spec["gates"]["maximum_asset_event_fraction"]),
        "year_concentration": bool(event_total) and maximum_year / event_total
        <= float(spec["gates"]["maximum_year_event_fraction"]),
        "matching_coverage": feasibility["matching_coverage"]
        >= float(spec["gates"]["minimum_matching_coverage"]),
        "prospective_power": None,
    }
    if not gates["locked_inputs"]:
        decision, reason = "invalid", "locked input identity failed"
    elif not gates["detector_variants_retained"]:
        decision, reason = "not_evaluable", "every detector variant is degenerate"
    elif not gates["matching_coverage"]:
        decision, reason = (
            "not_evaluable",
            "locked matching coverage is below 90%; power was not run because the comparison set is infeasible",
        )
    elif feasibility.get("prospective_power") is None:
        raise RuntimeError("matching passed; prospective power implementation is required")
    elif feasibility["prospective_power"] < float(spec["gates"]["minimum_power"]):
        decision, reason = "not_evaluable", "prospective adjusted power is below 80%"
    else:
        decision, reason = "feasible", "every locked feasibility gate passed"
    payload = {
        "decision": decision,
        "reason": reason,
        "gates": gates,
        "retained_variants": retained,
        "excluded_sparse_or_degenerate_variants": excluded,
        "actual_event_forward_outcomes_accessed": False,
        "spec_sha256": SPEC_SHA256,
        "data_sha256": checks["data_sha256"],
    }
    feasibility.update(
        {
            "status": "complete",
            "decision": decision,
            "retained_variants": retained,
            "excluded_sparse_or_degenerate_variants": excluded,
        }
    )
    _atomic_json(feasibility_path, feasibility)
    _atomic_json(output / "decision.json", payload)
    return output, payload


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--validate-only", action="store_true")
    mode.add_argument("--structure", action="store_true")
    mode.add_argument("--finalize", action="store_true")
    args = parser.parse_args()
    spec = json.loads(SPEC_PATH.read_text())
    bars = development_bars(spec)
    checks = validate_locked_inputs(spec, bars)
    if args.validate_only:
        print(json.dumps(checks, sort_keys=True))
        return
    if args.structure:
        print(run_structure(spec, bars, checks))
        return
    output, decision = finalize_existing(spec, checks)
    print(json.dumps({"output": str(output), **decision}, sort_keys=True))


if __name__ == "__main__":
    main()
