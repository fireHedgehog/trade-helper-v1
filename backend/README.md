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

## Layout (planned)

    backend/
    ├── README.md
    ├── requirements.txt
    └── app/
        ├── main.py        # FastAPI entrypoint
        ├── fetch.py       # daily yfinance fetch job
        ├── store.py       # SQLite read/write
        └── backtest.py    # backtest logic (later)

## Commands (planned)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn app.main:app --reload
```
