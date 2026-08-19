# Trade Research

Local, long-only systematic-research workspace for testing whether a strategy adds value over explicit passive benchmarks after costs. It is a research decision aid, not an execution system or investment recommendation.

## Current state

Version `0.53.0`. Stage 9A Cycle 1 closed `not_evaluable` in `0.40.0`: the locked consolidation detector found 274 broad, non-concentrated events, but its exact matcher admitted zero controls; power and actual-event outcomes were therefore not run. This is not a rejection of consolidation support recovery. Eight subsequent protocols each closed `not_material_or_not_consistent`, each for a different reason: SMA Cross v1 (`0.45.0`) on a confound; RSI(14) oversold reversal (`0.46.0`) on a power limitation; TA Breakout v1 (`0.47.0`) on a disclosed design weakness; Wave Pull v1 (`0.49.0`) on a clean-separation-but-null result with one small-sample near-miss; ETF-12 cross-sectional rotation v1 (`0.50.0`) on a clean, decisive null with no caveat at all — pooled rank correlation 0.045 against a 0.10 floor; Calendar Turn-of-Month v1 (`0.51.0`), the first time-based (not price-derived) mechanism tested, on a well-powered null — `987`-`1,612` events per asset ruled out a power limitation; Calendar Day-of-Week v1 (`0.52.0`) on a well-powered, directionally consistent (`9`/`12` assets negative) but statistically uncorrected null — `DBC`'s raw `p=0.048` did not survive Holm correction; Overnight Gap Continuation v1 (`0.53.0`), the first candidate whose event depends on two return components resampled jointly, on the session's most decisive negative — `12`/`12` assets showed a signed forward return opposite the continuation hypothesis, after a new joint-paired resampling design passed independent adversarial pre-lock code review. This closes Cycle 5 in full, every Tier 0/1 item, and one Tier 2 item on the pending checklist. CTA v2 remains eligible but parked pending a pooled-portfolio engine. CTA v1 remains rejected under its locked protocol; no paper trading, broker integration, unattended refresh, or deployment is enabled.

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
