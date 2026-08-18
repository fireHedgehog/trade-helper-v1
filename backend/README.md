[Project home](../README.md) · [Docs](../docs/README.md) · [Roadmap](../docs/roadmap.md) · [Changelog](../CHANGELOG.md)

# backend/

Python FastAPI app — the only server component of trade-helper-v1.

## What it does

- **Manual fetch** — pull adjusted daily histories from Yahoo Finance via
  `yfinance`; unattended scheduling is parked.
- **Store** — write fetched bars, saved strategy watchlists, and immutable
  completed strategy snapshots into SQLite under `../data/`.
- **REST API** — endpoints for symbols, price history, signal scans, single-symbol
  backtests, research statistics, watchlists, explicit strategy snapshots, and
  the locked shared-account replay.
- **Data operations** — inventory provider ownership/freshness and run one
  observable, rate-limited manual Yahoo refresh at a time.
- **Serve the frontend** — static files from `../frontend/`.

## Tech choices (keep it lean)

| Need | Choice | Notes |
| --- | --- | --- |
| Web framework | `fastapi` + `uvicorn` | One app, no extra services |
| Data source | `yfinance` | Free Yahoo Finance client |
| Storage | SQLite via stdlib `sqlite3` | No database server to run |
| Data frames | `pandas` | For bars and backtests |
| ML (later) | `scikit-learn` | Add **only when actually used** |

## Layout

    backend/
    ├── README.md
    ├── requirements.txt
    └── app/
        ├── __init__.py
        ├── main.py          # FastAPI entrypoint + REST API ✅
        ├── fetch.py         # manual yfinance fetch, idempotent upsert ✅
        ├── data_management.py # freshness + manual background refresh ✅
        ├── store.py         # SQLite bars, PK (symbol, date), adjusted closes ✅
        ├── universe.py      # SP500 ∪ NDX ∪ XL ETFs from Wikipedia ✅
        ├── strategies.py    # SMA Cross + Donchian Trend + RSI Reversion ✅
        ├── rules.py         # canonical vectorized strategy rules ✅
        ├── execution.py     # canonical next-open state machine ✅
        ├── portfolio.py     # capital, sizing, and entry-allocation contracts ✅
        ├── portfolio_execution.py # shared-cash multi-symbol daily replay ✅
        ├── portfolio_metrics.py # account-level return and risk metrics ✅
        ├── portfolio_benchmark.py # Passive ETF-12, SPY, and cash controls ✅
        ├── portfolio_universe.py # locked ETF/risk-classification manifest ✅
        ├── portfolio_api.py # validated JSON adapter for /api/portfolio ✅
        ├── workspace.py     # explicit strategy snapshot composition ✅
        ├── version.py       # application checkpoint version ✅
        └── engine.py        # API/CLI payloads + marked-to-market metrics ✅

## Commands

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements-dev.txt  # app + local test tools
pytest                                      # deterministic, no network/data fetch
python -m app.fetch SPY              # daily fetch (idempotent), full history
python -m app.fetch SPY GC=F CL=F    # more symbols
python -m app.universe               # build/refresh the watch universe
python -m app.fetch --universe       # batched fetch, enforced 2s+ delay, retry
python -m app.engine SPY             # backtest SMA Cross on local bars
python -m app.run_experiment         # resumable preregistered CTA experiment
uvicorn app.main:app --reload        # serve API + UI at http://127.0.0.1:8000
```

Experiment candidate caches are fingerprinted and written under ignored
`../data/`; the reviewable evidence record is written under `../output/research/`.
It remains exploratory development research, not prospective confirmation.

The local Data Management page is the normal refresh surface. It fetches full
adjusted histories because partial adjusted downloads can otherwise create an
inconsistent adjustment boundary. The fixed delay and backoff reduce Yahoo
request pressure but cannot guarantee access. `scripts/daily.sh` is intentionally
parked and exits without fetching.
