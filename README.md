# Trade Research

Local, long-only systematic-research workspace for testing whether a strategy adds value over explicit passive benchmarks after costs. It is a research decision aid, not an execution system or investment recommendation.

## Current state

This file is not the version source of truth and is not bumped every release — start every new work session at [docs/README.md](docs/README.md). It contains the authoritative checkpoint (current version, active research, next task) and document map.

As a fixed landmark rather than a live status: research is organized into a chaptered, living program (Chapters 1-3 falsification, Chapter 4 risk-budgeted ensemble sizing, Chapter 5 the operational bridge to bounded paper trading, Chapter 6 discussion) — see [docs/research-program.md](docs/research-program.md). No paper trading, broker integration, unattended refresh, or deployment is enabled yet; ADR 0008 (accepted) defines the design for bounded paper trading, not its implementation. CTA v1 remains rejected under its locked protocol.

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

With the backend running, execute the deterministic browser smoke suite:

```bash
scripts/browser-smoke.sh
```

It uses local/injected API states and never starts data refresh or strategy computation.

## Repository

| Path | Responsibility |
|---|---|
| `backend/app/` | FastAPI routes, research engines, persistence, portfolio simulation |
| `frontend/` | Browser application served by the backend |
| `data/` | Local market data and metadata |
| `docs/` | Product, research, decisions, roadmap, and evidence |
| `output/research/` | Generated experiment artifacts; not source-of-truth prose |

## Safety boundary

- Historical and local only; no order routing or broker credentials — a sandboxed paper-trading design is accepted ([ADR 0008](docs/adr/0008-bounded-paper-trading.md)) but not implemented.
- Adjusted Yahoo OHLCV is suitable for research, not execution-grade accounting.
- A backtest result is conditional on its data, universe, costs, timing, and statistical design.
- Strategy changes require a new preregistered hypothesis; retrospective tuning cannot rehabilitate CTA v1.

## Documentation

- [Resume checkpoint and index](docs/README.md)
- [Product contract](docs/product.md)
- [Workspace redesign](docs/workspace-redesign.md)
- [Research protocol](docs/research-protocol.md)
- [Hypothesis engineering](docs/hypothesis-engineering.md)
- [Model acceptance and candidate priority](docs/model-acceptance-standard.md)
- [Roadmap](docs/roadmap.md)
- [Decision records](docs/adr/)
- [Version ledger](CHANGELOG.md)
