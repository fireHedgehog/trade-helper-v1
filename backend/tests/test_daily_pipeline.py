"""Dependency and idempotency contract for the read-only daily planner."""

import time

from app.daily_pipeline import (
    DailyPipelineManager,
    plan_daily_pipeline,
    plan_strategy_job,
    strategy_input_fingerprint,
)


META = {"strategy_id": "cta-trend", "version": "v2-candidate"}
PARAMS = {"n_entry": 100}


def _inventory(state: str = "fresh") -> list[dict]:
    return [
        {
            "symbol": "SPY",
            "provider": "yahoo",
            "dataset_id": "yahoo-adjusted-daily-ohlcv-v1",
            "rows": 100,
            "latest_date": "2026-08-18",
            "freshness": state,
        }
    ]


def test_fingerprint_is_order_independent_but_changes_with_inputs() -> None:
    kwargs = {
        "strategy_id": "cta-trend",
        "strategy_version": "v2",
        "params": PARAMS,
        "scope": "all",
        "inventory": _inventory(),
    }
    assert strategy_input_fingerprint(symbols=["SPY", "SPY"], **kwargs) == strategy_input_fingerprint(symbols=["SPY"], **kwargs)
    assert strategy_input_fingerprint(symbols=["SPY"], **kwargs) != strategy_input_fingerprint(
        symbols=["SPY"], **{**kwargs, "strategy_version": "v3"}
    )


def test_strategy_job_blocks_data_then_skips_matching_fingerprint() -> None:
    base = {
        "strategy": "CTA Trend",
        "metadata": META,
        "params": PARAMS,
        "scope": "all",
        "symbols": ["SPY"],
    }
    blocked = plan_strategy_job(inventory=_inventory("stale"), latest_run=None, **base)
    assert blocked["status"] == "blocked_data"
    ready = plan_strategy_job(inventory=_inventory(), latest_run=None, **base)
    assert ready["status"] == "ready"
    current = plan_strategy_job(
        inventory=_inventory(),
        latest_run={"id": 7, "result": {"pipeline_fingerprint": ready["fingerprint"]}},
        **base,
    )
    assert current["status"] == "skipped_current"
    assert current["previous_run_id"] == 7


def test_pipeline_records_refresh_noop_and_empty_scope() -> None:
    plan = plan_daily_pipeline(
        expected_session="2026-08-18",
        inventory=_inventory(),
        strategy_specs=[
            {
                "strategy": "CTA Trend",
                "metadata": META,
                "params": PARAMS,
                "scope": "watchlist",
                "symbols": [],
                "latest_run": None,
            }
        ],
    )
    assert plan["status"] == "ready"
    assert plan["refresh"] == {"status": "skipped_current", "symbols": [], "count": 0}
    assert plan["strategy_jobs"][0]["status"] == "skipped_empty"


def _wait(manager: DailyPipelineManager) -> dict:
    for _ in range(200):
        result = manager.snapshot()
        if result["state"] != "running":
            return result
        time.sleep(0.005)
    raise AssertionError("pipeline did not finish")


def test_executor_runs_ready_jobs_and_persists_transitions() -> None:
    saved = []
    runs = []
    plan = {
        "expected_session": "2026-08-18",
        "refresh": {"status": "skipped_current", "count": 0, "symbols": []},
        "strategy_jobs": [
            {"strategy": "CTA Trend", "set": "defaults", "scope": "all", "status": "ready"},
            {"strategy": "SMA Cross", "set": "defaults", "scope": "watchlist", "status": "skipped_empty"},
        ],
    }
    manager = DailyPipelineManager(
        planner=lambda: plan,
        start_refresh=lambda _: {},
        refresh_snapshot=lambda: {},
        run_strategy=lambda job: runs.append(job) or {"id": 42},
        save_job=saved.append,
    )
    manager.start()
    result = _wait(manager)
    assert result["state"] == "complete"
    assert result["strategy_jobs"][0]["run_id"] == 42
    assert result["strategy_jobs"][1]["state"] == "skipped_empty"
    assert len(runs) == 1
    assert len(saved) >= 4


def test_executor_replans_after_partial_refresh_and_runs_independent_job() -> None:
    calls = 0
    refresh_states = iter([{"state": "complete_with_errors", "failed": 1}])
    initial = {
        "expected_session": "2026-08-18",
        "refresh": {"status": "ready", "count": 2, "symbols": ["QQQ", "SPY"]},
        "strategy_jobs": [],
    }
    replanned = {
        "expected_session": "2026-08-18",
        "refresh": {"status": "ready", "count": 1, "symbols": ["QQQ"]},
        "strategy_jobs": [
            {"strategy": "CTA Trend", "set": "defaults", "scope": "watchlist", "status": "ready"},
            {"strategy": "CTA Trend", "set": "defaults", "scope": "all", "status": "blocked_data"},
        ],
    }

    def planner():
        nonlocal calls
        calls += 1
        return initial if calls == 1 else replanned

    manager = DailyPipelineManager(
        planner=planner,
        start_refresh=lambda symbols: {"symbols": symbols},
        refresh_snapshot=lambda: next(refresh_states),
        run_strategy=lambda _: {"id": 8},
        sleeper=lambda _: None,
    )
    manager.start()
    result = _wait(manager)
    assert result["state"] == "complete_with_errors"
    assert [job["state"] for job in result["strategy_jobs"]] == ["complete", "blocked_data"]


def test_recovered_running_pipeline_is_marked_interrupted() -> None:
    recovered = {
        "state": "running",
        "strategy_jobs": [{"state": "running"}, {"state": "complete"}],
    }
    manager = DailyPipelineManager(
        planner=lambda: {}, start_refresh=lambda _: {}, refresh_snapshot=lambda: {},
        run_strategy=lambda _: {}, load_job=lambda: recovered,
    )
    result = manager.snapshot()
    assert result["state"] == "interrupted"
    assert result["strategy_jobs"][0]["state"] == "interrupted"
