# trade-helper-v1

A simple stock-data helper app: pull US stock daily closing prices once a day from the free Yahoo Finance API, store the history locally, and run backtests against the local data — with a small web UI on top.

> **Status: planning.** This README is a **living document**. Every idea we confirm or change is recorded here and versioned. See [Versioning](#versioning) and [Changelog](#changelog).

---

## 1. The idea (what we know so far)

- **Data source:** Yahoo Finance free API (via Python `yfinance`), US stocks, daily closing prices.
- **Fetch frequency:** once per day — either a cron/scheduled job or a manual button.
- **Storage:** persist the history **locally on disk**, so backtests read local data instead of re-fetching from the API every time.
- **Backend:** Python (FastAPI) — good open-source ML stack: `pandas`, `scikit-learn`, etc.
- **Frontend:** simple web UI to view data, trigger a fetch, and kick off backtests.
- **Deployment (later):** AWS.

## 2. Open questions (decide later — none of these block starting)

- AWS shape: one small **EC2** instance (simple) vs **Lambda + S3** (more moving parts)?
- Storage format: **SQLite** (start here) vs Parquet vs DuckDB?
- Frontend hosting: served by the backend (start here) vs separate S3 + CloudFront?
- Which symbols to track? Watchlist / portfolio / a fixed universe?
- Backtest engine: hand-rolled vs existing libs (`backtrader`, `vectorbt`)?
- Which ML models matter first? (start with plain stats, ML later)

## 3. Architecture (current plan)

### Phase 1 — local (start here)

```
┌──────────────┐   fetch once/day          ┌─────────────────────────┐
│ yfinance     │  (cron OR manual click)   │ backend/ (Python FastAPI)│
│ (Yahoo API)  │ ────────────────────────▶ │  • fetch job             │
└──────────────┘                           │  • REST API              │
                                           └────────────┬────────────┘
                                                        │ read/write
                                           ┌────────────▼────────────┐
                                           │ data/  (SQLite,         │
                                           │  gitignored, local disk)│
                                           └────────────┬────────────┘
                                                        │ read
                                           ┌────────────▼────────────┐
                                           │ frontend/ (static UI,   │
                                           │  served by the backend) │
                                           └─────────────────────────┘
```

### Phase 2 — AWS (later, same code)

- Small EC2 instance running the same backend + a daily cron job.
- SQLite file on the instance's EBS disk (or moved to S3/Parquet if we outgrow it).
- Optionally move the frontend to S3 + CloudFront.

## 4. Repo structure

```
trade-helper-v1/
├── README.md            # this living document
├── .gitignore
├── backend/             # Python FastAPI app
│   ├── README.md
│   └── app/             # (planned: main.py, fetch.py, store.py)
├── frontend/            # static UI, no build step (planned: index.html)
│   └── README.md
├── scripts/             # cron wrapper (planned, not created yet)
└── data/                # local market data (gitignored)
    └── README.md
```

## 5. Local dev environment (planned)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

Planned commands (once implemented):

```bash
python -m app.fetch            # manual daily fetch
uvicorn app.main:app --reload  # run backend + UI locally
```

## 6. Roadmap

1. **v0.1** — README + decisions documented. ✅
2. **v0.2** — folder structure + per-folder READMEs. ✅
3. **v0.3** — backend skeleton: venv, FastAPI hello, `yfinance` fetch script, SQLite schema.
4. **v0.4** — frontend skeleton: view data, manual fetch button.
5. **v0.5** — backtest basics against local data.
6. **v0.6** — AWS deployment (phase 2).

---

## Versioning

Doc version: `v<major>.<minor>.<patch>`.

| Change | Bump |
| --- | --- |
| Typo / small wording fix | patch |
| New section or plan change | minor |
| Architecture reset / rewrite | major |

Every version gets a dated entry in the [Changelog](#changelog).

## Changelog

### v0.2.1 — 2026-08-17

- Expanded `.gitignore`: data file formats (`*.sqlite*`, `*.db`, `*.csv`, `*.parquet`, `*.pkl`, `*.pickle`, `*.feather`) ignored wherever they appear, plus macOS `.DS_Store`.
- Stated the rule in `.gitignore`: commit data-handling **code**, never the **data**.

### v0.2.0 — 2026-08-17

- Created folder structure: `backend/`, `frontend/`, `data/`, each with its own README.
- Decision recorded: lean-first — plain static frontend (no build step), FastAPI monolith, SQLite via stdlib `sqlite3`.
- Build order: data pipeline first, then viewer UI, then backtest, then AWS.

### v0.1.0 — 2026-08-17

- Initial README: project idea, open questions, local + AWS architecture plan, repo layout, roadmap.
- Added `data/` to `.gitignore` for the local market-data store.