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

from .consolidation_feasibility import structural_events
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
    records = [
        event.to_dict()
        for symbol in spec["universe"]
        for event in structural_events(bars_by_symbol[symbol], symbol=symbol, spec=spec)
    ]
    records.sort(key=lambda row: (row["event_date"], row["symbol"]))
    by_symbol = {
        symbol: sum(row["symbol"] == symbol for row in records)
        for symbol in spec["universe"]
    }
    by_year: dict[str, int] = {}
    for row in records:
        year = row["event_date"][:4]
        by_year[year] = by_year.get(year, 0) + 1
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
            "matching_coverage": None,
            "prospective_power": None,
        },
    )
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--validate-only", action="store_true")
    mode.add_argument("--structure", action="store_true")
    args = parser.parse_args()
    spec = json.loads(SPEC_PATH.read_text())
    bars = development_bars(spec)
    checks = validate_locked_inputs(spec, bars)
    if args.validate_only:
        print(json.dumps(checks, sort_keys=True))
        return
    print(run_structure(spec, bars, checks))


if __name__ == "__main__":
    main()
