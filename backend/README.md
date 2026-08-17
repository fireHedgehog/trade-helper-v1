[Project home](../README.md) · [Docs](../docs/README.md) · [Roadmap](../docs/roadmap.md) · [Changelog](../CHANGELOG.md)

# backend/

Python FastAPI app — the only server component of trade-helper-v1.

## What it does (planned)

- **Daily fetch** — pull US stock daily closing prices from Yahoo Finance via `yfinance`.
- **Store** — write fetched bars into SQLite under `../data/`.
- **REST API** — endpoints for the frontend: list symbols, get price history, trigger a fetch, run a backtest (later).
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
        ├── fetch.py         # daily yfinance fetch, idempotent upsert ✅
        ├── store.py         # SQLite bars, PK (symbol, date), adjusted closes ✅
        ├── universe.py      # SP500 ∪ NDX ∪ XL ETFs from Wikipedia ✅
        ├── strategies.py    # SMA Cross + Donchian Trend + RSI Reversion ✅
        ├── rules.py         # canonical vectorized strategy rules ✅
        ├── execution.py     # canonical next-open state machine ✅
        └── engine.py        # API/CLI payloads + marked-to-market metrics ✅

## Commands

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements-dev.txt  # app + local test tools
pytest                                      # deterministic, no network/data fetch
python -m app.fetch SPY              # daily fetch (idempotent), full history
python -m app.fetch SPY GC=F CL=F    # more symbols
python -m app.universe               # build/refresh the watch universe
python -m app.fetch --universe       # batched fetch, 1s delay, retry on 429
python -m app.engine SPY             # backtest SMA Cross on local bars
uvicorn app.main:app --reload        # serve API + UI at http://127.0.0.1:8000
```
