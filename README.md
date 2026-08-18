# Trade Research

Local, long-only systematic-research workspace for testing whether a strategy adds value over explicit passive benchmarks after costs. It is a research decision aid, not an execution system or investment recommendation.

## Current state

Version `0.27.0` adds the semantic visual system and Today command centre to the durable research workspace: historical backtests, portfolio simulation, data management, persistent watchlists, lifecycle signals, and full-universe candidate views. CTA v1 was rejected under its preregistered test; Passive ETF-12 v1 is the primary benchmark. No paper trading, broker integration, unattended refresh, or deployment is enabled.

Start every new work session at [docs/README.md](docs/README.md). It contains the authoritative checkpoint, next task, and document map.

## Run locally

```bash
source .venv/bin/activate
cd backend
python -m uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000>. If port `8000` is occupied, stop the existing process or use `--port 8001` and open that port.

Run verification from the repository root:

```bash
source .venv/bin/activate
pytest -q
```

## Repository

| Path | Responsibility |
|---|---|
| `backend/app/` | FastAPI routes, research engines, persistence, portfolio simulation |
| `frontend/` | Browser application served by the backend |
| `data/` | Local market data and metadata |
| `docs/` | Product, research, decisions, roadmap, and evidence |
| `output/research/` | Generated experiment artifacts; not source-of-truth prose |

## Safety boundary

- Historical and local only; no order routing or broker credentials.
- Adjusted Yahoo OHLCV is suitable for research, not execution-grade accounting.
- A backtest result is conditional on its data, universe, costs, timing, and statistical design.
- Strategy changes require a new preregistered hypothesis; retrospective tuning cannot rehabilitate CTA v1.

## Documentation

- [Resume checkpoint and index](docs/README.md)
- [Product contract](docs/product.md)
- [Workspace redesign](docs/workspace-redesign.md)
- [Research protocol](docs/research-protocol.md)
- [Roadmap](docs/roadmap.md)
- [Decision records](docs/adr/)
- [Version ledger](CHANGELOG.md)
