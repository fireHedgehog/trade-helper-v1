# trade-helper-v1

An educational, local-first quantitative research application for daily US
market data, reproducible strategy simulation, and honest comparison with
passive benchmarks.

[Documentation](docs/README.md) · [Roadmap](docs/roadmap.md) · [Product](docs/product.md) · [Research protocol](docs/research-protocol.md) · [Changelog](CHANGELOG.md)

> [!WARNING]
> **Research prototype—not ready for live trading.** This is not investment
> advice or a brokerage system. Backtests can be wrong because of defects,
> biased data, overfitting, unrealistic execution assumptions, and regime
> changes. Do not risk real money based on this application.

## Current status

Stages 0–3 and the Stage 5 engineering gate of the
[validation roadmap](docs/roadmap.md) are complete. The Stage 4 CTA v1
experiment is complete and rejected, while genuinely untouched confirmation
data remains an open research gate. Stage 6, UX and safety clarity, is next.

- One canonical state machine drives backtests, signals, chart markers, and the
  simulated ledger: completed-close signal → next-available-open fill.
- The deterministic test suite currently contains 148 passing tests.
- Trading costs, spread, slippage, gaps, idle-cash yield, uncertainty intervals,
  and benchmark limitations are explicit.
- The CTA walk-forward experiment is preregistered with a 12-ETF universe and
  54 parameter candidates. The completed development run rejected v1: no
  candidate survived validation in any of 14 folds, so every test fold held cash.
- The portfolio engine now replays multiple symbols on one shared-cash account,
  with cost-aware sizing, gap-time limit checks, deterministic concurrent orders,
  concentration caps, next-session sale settlement, common-close equity, and
  explicit rejection reasons. A 15% close-based drawdown now halts entries and
  creates next-open liquidation orders without hiding further gap losses.
  Account-level return, risk, exposure, concentration, turnover, and trade
  metrics are exposed through a locked-universe API and the Today view without
  inventing an undefined benchmark. The active UI no longer displays fictional
  fixed-100-share dollar P&L. Strategies without a protective stop are refused
  explicitly instead of receiving an invented fallback.
- Existing historical SPY results are exploratory and contaminated by prior
  inspection. Valid confirmation requires genuinely unseen future or otherwise
  uninspected point-in-time data.
- Cron, AWS, machine learning, and brokerage integration remain paused until
  their prerequisite gates pass.

The honest baseline is poor as an “edge”: full-history SPY CTA returned roughly
276.5% net versus roughly 3,119.6% buy-and-hold. Lower drawdown does not by itself
prove that the strategy adds value.

The stricter [walk-forward result](docs/research-results/cta-trend-wf-v1.md) is
more negative: after costs and multiple-testing correction, CTA Trend v1 produced
no validated candidate and is rejected for insufficient evidence.

## Quick start

Requires Python 3.12.3.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements-dev.txt
pytest
```

Fetch local adjusted daily bars:

```bash
cd backend
python -m app.fetch SPY
```

Run the application:

```bash
cd backend
uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000>.

Run a command-line backtest:

```bash
cd backend
python -m app.engine SPY --strategy "CTA Trend"
```

Run the test suite without downloading market data:

```bash
pytest
```

> [!CAUTION]
> Full-universe historical scans are intentionally opt-in and can be expensive
> on a laptop. The default post-signal calculation is limited to 16 symbols and
> approximately one trading year.

## Architecture

```text
yfinance / FRED
       │ validated daily fetch
       ▼
FastAPI backend ──────► SQLite local store
       │                       │
       ├── canonical engine ◄──┘
       ├── research statistics
       └── static browser UI
```

- Backend: Python, FastAPI, pandas, SQLite.
- Frontend: static HTML/CSS/JavaScript with TradingView Lightweight Charts.
- Data: adjusted Yahoo OHLC for securities; FRED macro series are context only
  and never treated as executable instruments.
- Deployment: local only. AWS is the final roadmap stage, not the current goal.

## Repository map

```text
backend/                 API, storage, strategies, execution, research primitives
frontend/                static user interface
data/                    local database and generated data (not committed)
docs/                    roadmap, product design, protocol, and ADRs
research/                experiment specifications and attempt ledger
output/jupyter-notebook/ reproducible research notebooks
scripts/                 operational scripts; unattended scheduling is paused
```

## Documentation

| Document | Purpose |
| --- | --- |
| [Documentation index](docs/README.md) | Navigation for all project documents |
| [Validation roadmap](docs/roadmap.md) | Stages 0–9, exit gates, and current work |
| [Product and research design](docs/product.md) | Views, trading rules, and design notes |
| [Research protocol](docs/research-protocol.md) | Locked Stage 4 hypothesis and methodology |
| [Architecture decisions](docs/README.md#architecture-decisions) | Execution, data, and statistics contracts |
| [Changelog](CHANGELOG.md) | Full version history |

Component-specific commands and responsibilities are documented in
[backend/README.md](backend/README.md), [frontend/README.md](frontend/README.md),
and [data/README.md](data/README.md).

## License

See [LICENSE](LICENSE).
