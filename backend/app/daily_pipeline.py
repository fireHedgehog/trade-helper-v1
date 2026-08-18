"""Deterministic planning contract for the future shared daily pipeline.

This module is read-only: it decides dependencies and currency but performs no
refresh or strategy work. A later executor must consume this same plan.
"""

from __future__ import annotations

import hashlib
import json


def strategy_input_fingerprint(
    *,
    strategy_id: str,
    strategy_version: str,
    params: dict,
    scope: str,
    symbols: list[str],
    inventory: list[dict],
) -> str:
    by_symbol = {row["symbol"]: row for row in inventory}
    payload = {
        "strategy_id": strategy_id,
        "strategy_version": strategy_version,
        "params": params,
        "scope": scope,
        "inputs": [
            {
                "symbol": symbol,
                "dataset_id": by_symbol.get(symbol, {}).get("dataset_id"),
                "rows": by_symbol.get(symbol, {}).get("rows"),
                "latest_date": by_symbol.get(symbol, {}).get("latest_date"),
            }
            for symbol in sorted(set(symbols))
        ],
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def plan_strategy_job(
    *,
    strategy: str,
    metadata: dict,
    params: dict,
    scope: str,
    symbols: list[str],
    inventory: list[dict],
    latest_run: dict | None,
) -> dict:
    by_symbol = {row["symbol"]: row for row in inventory}
    missing = [symbol for symbol in symbols if symbol not in by_symbol]
    non_current = [
        symbol
        for symbol in symbols
        if symbol in by_symbol and by_symbol[symbol].get("freshness") != "fresh"
    ]
    fingerprint = strategy_input_fingerprint(
        strategy_id=metadata["strategy_id"],
        strategy_version=metadata["version"],
        params=params,
        scope=scope,
        symbols=symbols,
        inventory=inventory,
    )
    previous = (latest_run or {}).get("result", {}).get("pipeline_fingerprint")
    if not symbols:
        status, reason = "skipped_empty", "scope has no selected symbols"
    elif missing or non_current:
        status, reason = "blocked_data", "required inputs are missing or not current"
    elif previous == fingerprint:
        status, reason = "skipped_current", "input, model, parameters, and scope are unchanged"
    else:
        status, reason = "ready", "dependencies are current and fingerprint changed"
    return {
        "strategy": strategy,
        "strategy_id": metadata["strategy_id"],
        "strategy_version": metadata["version"],
        "set": "defaults",
        "scope": scope,
        "status": status,
        "reason": reason,
        "symbols": len(set(symbols)),
        "missing": missing,
        "non_current": non_current,
        "fingerprint": fingerprint,
        "previous_run_id": (latest_run or {}).get("id"),
    }


def plan_daily_pipeline(
    *,
    expected_session: str,
    inventory: list[dict],
    strategy_specs: list[dict],
) -> dict:
    yahoo = [row for row in inventory if row.get("provider") == "yahoo"]
    refresh_symbols = [
        row["symbol"] for row in yahoo if row.get("freshness") != "fresh"
    ]
    jobs = [plan_strategy_job(inventory=inventory, **spec) for spec in strategy_specs]
    return {
        "expected_session": expected_session,
        "status": "refresh_required" if refresh_symbols else "ready",
        "refresh": {
            "status": "ready" if refresh_symbols else "skipped_current",
            "symbols": sorted(refresh_symbols),
            "count": len(refresh_symbols),
        },
        "strategy_jobs": jobs,
        "summary": {
            "ready": sum(job["status"] == "ready" for job in jobs),
            "blocked_data": sum(job["status"] == "blocked_data" for job in jobs),
            "skipped_current": sum(job["status"] == "skipped_current" for job in jobs),
            "skipped_empty": sum(job["status"] == "skipped_empty" for job in jobs),
        },
    }
