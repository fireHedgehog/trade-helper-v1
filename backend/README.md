# Backend

FastAPI is the sole server. It owns local data access, deterministic research logic, SQLite persistence, explicit long-running jobs, and static frontend delivery.

## Responsibilities

- Download adjusted daily Yahoo history only through explicit manual actions.
- Validate and persist bars, watchlists, lifecycle state, and immutable completed strategy snapshots.
- Expose symbols, history, signals, backtests, statistics, experiments, portfolio benchmarks, data jobs, and workspace state through REST.
- Enforce canonical next-open execution and portfolio/risk contracts.
- Serve `frontend/` at the application root.

Core modules include `execution.py`, `rules.py`, `engine.py`, `portfolio*.py`, `workspace.py`, `data_management.py`, `store.py`, and `main.py`. SQLite and generated candidate caches live under ignored `data/`; reviewable evidence lives under `output/research/`.

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
