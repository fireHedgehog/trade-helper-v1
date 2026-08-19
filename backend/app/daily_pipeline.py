"""Deterministic planning and durable execution for the daily pipeline."""

from __future__ import annotations

import copy
import hashlib
import json
import threading
import time
import uuid
from datetime import datetime, timezone
from typing import Callable


MIN_FULL_UNIVERSE_COVERAGE = 0.90


class PipelineAlreadyRunning(RuntimeError):
    pass


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
    eligible = [
        symbol
        for symbol in symbols
        if symbol in by_symbol and by_symbol[symbol].get("freshness") == "fresh"
    ]
    excluded_data = [
        {
            "symbol": symbol,
            "reason": "missing" if symbol in missing else "not_current",
        }
        for symbol in symbols
        if symbol in missing or symbol in non_current
    ]
    requested_count = len(set(symbols))
    coverage_ratio = len(set(eligible)) / requested_count if requested_count else 0.0
    execution_symbols = eligible if scope == "all" else symbols
    fingerprint = strategy_input_fingerprint(
        strategy_id=metadata["strategy_id"],
        strategy_version=metadata["version"],
        params=params,
        scope=scope,
        symbols=execution_symbols,
        inventory=inventory,
    )
    previous = (latest_run or {}).get("result", {}).get("pipeline_fingerprint")
    if not symbols:
        status, reason = "skipped_empty", "scope has no selected symbols"
    elif scope == "all" and coverage_ratio < MIN_FULL_UNIVERSE_COVERAGE:
        status, reason = (
            "blocked_data",
            f"current universe coverage {coverage_ratio:.1%} is below "
            f"the {MIN_FULL_UNIVERSE_COVERAGE:.0%} daily-snapshot floor",
        )
    elif scope != "all" and (missing or non_current):
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
        "symbols": requested_count,
        "eligible_symbols": len(set(execution_symbols)),
        "execution_symbols": sorted(set(execution_symbols)),
        "excluded_data": excluded_data,
        "coverage_ratio": coverage_ratio,
        "minimum_coverage_ratio": (
            MIN_FULL_UNIVERSE_COVERAGE if scope == "all" else 1.0
        ),
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
    exclusions = sorted(
        {
            row["symbol"]
            for job in jobs
            if job["scope"] == "all"
            for row in job["excluded_data"]
        }
    )
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
            "excluded_symbols": exclusions,
            "excluded_count": len(exclusions),
        },
    }


class DailyPipelineManager:
    """Run one dependency-aware pipeline; retries always re-plan current state."""

    def __init__(
        self,
        *,
        planner: Callable[[], dict],
        start_refresh: Callable[[list[str]], dict],
        refresh_snapshot: Callable[[], dict],
        run_strategy: Callable[[dict], dict],
        load_job: Callable[[], dict | None] | None = None,
        save_job: Callable[[dict], None] | None = None,
        sleeper: Callable[[float], None] = time.sleep,
        poll_seconds: float = 0.25,
    ) -> None:
        self._planner = planner
        self._start_refresh = start_refresh
        self._refresh_snapshot = refresh_snapshot
        self._run_strategy = run_strategy
        self._save_job = save_job
        self._sleeper = sleeper
        self._poll_seconds = poll_seconds
        self._lock = threading.Lock()
        self._job = load_job() if load_job else None
        if self._job and self._job.get("state") == "running":
            self._job["state"] = "interrupted"
            self._job["finished_at"] = datetime.now(timezone.utc).isoformat()
            self._job["message"] = "server stopped before the pipeline completed"
            for item in self._job.get("strategy_jobs", []):
                if item.get("state") in {"pending", "running"}:
                    item["state"] = "interrupted"
            self._persist_locked()

    def _persist_locked(self) -> None:
        if self._save_job and self._job is not None:
            self._save_job(copy.deepcopy(self._job))

    def snapshot(self) -> dict:
        with self._lock:
            return copy.deepcopy(self._job) if self._job else {
                "state": "idle", "job_id": None, "strategy_jobs": []
            }

    def _update(self, **changes) -> None:
        with self._lock:
            assert self._job is not None
            self._job.update(changes)
            self._persist_locked()

    def start(self) -> dict:
        plan = self._planner()
        with self._lock:
            if self._job and self._job.get("state") == "running":
                raise PipelineAlreadyRunning("a daily pipeline is already running")
            now = datetime.now(timezone.utc).isoformat()
            self._job = {
                "state": "running",
                "job_id": uuid.uuid4().hex,
                "started_at": now,
                "finished_at": None,
                "message": "starting reviewed pipeline",
                "expected_session": plan["expected_session"],
                "initial_plan": plan,
                "refresh": {"state": "pending", "count": plan["refresh"]["count"]},
                "strategy_jobs": [],
            }
            self._persist_locked()
            snapshot = copy.deepcopy(self._job)
        threading.Thread(
            target=self._run,
            args=(plan,),
            name=f"daily-pipeline-{snapshot['job_id'][:8]}",
            daemon=True,
        ).start()
        return snapshot

    def _run(self, initial_plan: dict) -> None:
        errors = 0
        try:
            refresh_plan = initial_plan["refresh"]
            if refresh_plan["status"] == "ready":
                self._update(
                    refresh={"state": "running", "count": refresh_plan["count"]},
                    message="refreshing market data",
                )
                self._start_refresh(refresh_plan["symbols"])
                while True:
                    refresh = self._refresh_snapshot()
                    if refresh.get("state") != "running":
                        break
                    self._sleeper(self._poll_seconds)
                errors += int(refresh.get("failed", 0))
                self._update(
                    refresh={
                        "state": refresh.get("state", "failed"),
                        "count": refresh_plan["count"],
                        "failed": refresh.get("failed", 0),
                    }
                )
            else:
                self._update(refresh={"state": "skipped_current", "count": 0})

            # Refresh can partially succeed. Re-planning lets independent jobs run
            # while jobs whose own inputs remain stale stay explicitly blocked.
            plan = self._planner()
            jobs = [{**job, "state": "pending"} for job in plan["strategy_jobs"]]
            self._update(strategy_jobs=jobs, message="running current strategy jobs")
            for index, job in enumerate(jobs):
                if job["status"] != "ready":
                    state = job["status"]
                    if state == "blocked_data":
                        errors += 1
                    with self._lock:
                        self._job["strategy_jobs"][index]["state"] = state
                        self._persist_locked()
                    continue
                with self._lock:
                    self._job["strategy_jobs"][index]["state"] = "running"
                    self._persist_locked()
                try:
                    result = self._run_strategy(job)
                    changes = {"state": "complete", "run_id": result.get("id")}
                except Exception as exc:
                    errors += 1
                    changes = {
                        "state": "failed",
                        "error": f"{type(exc).__name__}: {exc}"[:300],
                    }
                with self._lock:
                    self._job["strategy_jobs"][index].update(changes)
                    self._persist_locked()
            final = "complete_with_errors" if errors else "complete"
            self._update(
                state=final,
                finished_at=datetime.now(timezone.utc).isoformat(),
                message="pipeline finished",
            )
        except Exception as exc:
            self._update(
                state="failed",
                finished_at=datetime.now(timezone.utc).isoformat(),
                message=f"{type(exc).__name__}: {exc}"[:300],
            )
