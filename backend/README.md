# Backend

FastAPI is the sole server. It owns local data access, deterministic research logic, SQLite persistence, explicit long-running jobs, and static frontend delivery.

## Responsibilities

- Download adjusted daily Yahoo history only through explicit manual actions.
- Validate and persist bars, watchlists, lifecycle state, and immutable completed strategy snapshots.
- Expose symbols, history, signals, backtests, statistics, experiments, portfolio benchmarks, data jobs, and workspace state through REST.
- Enforce canonical next-open execution and portfolio/risk contracts.
- Serve `frontend/` at the application root.

Core modules include `execution.py`, `rules.py`, `engine.py`, `portfolio*.py`, `workspace.py`, `data_management.py`, `research_catalog.py`, `store.py`, and `main.py`. The catalog describes only data products and executable strategies that really exist; it is not a speculative universal schema. SQLite and generated candidate caches live under ignored `data/`; reviewable evidence lives under `output/research/`.

`daily_pipeline.py` owns the pure dependency planner and explicit durable executor. `/api/daily-pipeline/plan` is read-only; `/api/daily-pipeline` requires confirmation, refreshes dependencies, re-plans, and runs only changed snapshots. `/api/daily-pipeline/status` reconstructs persisted state. Retry is a fresh plan, so completed current work is skipped. Scheduling remains out of scope.

`macro_pit.py` ingests point-in-time macro vintage history (every historical FRED revision, not the final-revised series `fred.py` stores for display) per [ADR 0006](../docs/adr/0006-macro-data-contract.md); live-verified against the real FRED API (`0.61.0`). Requires a free `FRED_API_KEY`, either as an env var or stored once via `app.store.set_key` into the local, gitignored `key_library` table. `treasury_buybacks.py` (`0.63.0`) ingests Treasury buyback operations (`fiscaldata.treasury.gov`, free, keyless, not on FRED); settled operations only. Neither is wired into any strategy, endpoint, or scheduled job — standalone ingestion paths a future macro protocol calls explicitly.

## Commands

From the repository root:

```bash
source .venv/bin/activate
pytest -q
cd backend
python -m uvicorn app.main:app --reload
python -m app.fetch SPY
python -m app.universe
python -m app.engine SPY
python -m app.run_experiment
```

Install with `pip install -r backend/requirements-dev.txt` if the environment is absent. Tests are deterministic and must not fetch network data.

## Constraints

The Data Management UI is the normal refresh surface. Full adjusted histories avoid adjustment-boundary inconsistency; fixed delay/backoff reduces provider pressure but cannot guarantee access. `scripts/daily.sh` is intentionally disabled. Cron, brokers, and live execution are out of scope.

[Project](../README.md) · [Checkpoint](../docs/README.md) · [Contracts](../docs/adr/)
