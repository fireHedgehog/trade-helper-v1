"""Dependency and idempotency contract for the read-only daily planner."""

from app.daily_pipeline import (
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
