# Trade Research

Local, long-only systematic-research workspace for testing whether a strategy adds value over explicit passive benchmarks after costs. It is a research decision aid, not an execution system or investment recommendation.

## Current state

Version `0.42.0`. Stage 9A Cycle 1 closed `not_evaluable` in `0.40.0`: the locked consolidation detector found 274 broad, non-concentrated events, but its exact matcher admitted zero controls; power and actual-event outcomes were therefore not run. This is not a rejection of consolidation support recovery. Cycle 2 (in `0.42.0`) prioritised SMA Cross v1's exposure-reduction claim for a joint protocol against a volatility-managed-exposure control; two other candidates are eligible but parked pending infrastructure this codebase does not yet have. CTA v1 remains rejected under its locked protocol; no paper trading, broker integration, unattended refresh, or deployment is enabled.

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

- Historical and local only; no order routing or broker credentials.
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
