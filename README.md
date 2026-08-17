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
- Which symbols to track? ✅ decided — S&P 500 ∪ Nasdaq-100 ∪ XL sector ETFs (~530 symbols, deduped, survivorship-bias caveat applies).
- Backtest engine: ✅ decided — `backtesting.py` as skeleton (v0.3.0).
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
│   └── app/             # main.py, fetch.py, store.py, universe.py, strategies.py, engine.py
├── frontend/            # static UI, no build step (index.html)
│   └── README.md
├── scripts/             # cron wrapper (planned, not created yet)
└── data/                # local market data (gitignored)
    └── README.md
```

## 5. Local dev environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

Daily fetch (idempotent — safe for cron or manual runs):

```bash
cd backend
python -m app.fetch SPY              # default symbol, full history
python -m app.fetch SPY GC=F CL=F    # more symbols
```

Backtest a strategy on local data (no network needed):

```bash
cd backend
python -m app.engine SPY                    # SMA Cross on SPY
python -m app.engine SPY --strategy "SMA Cross"
```

Build the watch universe (S&P 500 ∪ Nasdaq-100 ∪ XL sector ETFs, deduped, cached in `data/universe.csv`):

```bash
cd backend
python -m app.universe               # refresh list + print counts
python -m app.fetch --universe       # polite batched fetch (~530 symbols, 1s delay)
python -m app.fetch --universe --delay 2   # slower = safer vs Yahoo rate limits
```

Run backend + UI, then open http://127.0.0.1:8000 in a browser:

```bash
cd backend
uvicorn app.main:app --reload
```

⚠ **Local compute safety (important):** the confidence engine scans
symbols × bars, and a full-universe run is heavy (hundreds of MB of bars,
minutes of CPU — laptop fans will complain). Locally, confidence is ALWAYS
sample-limited by default (**5 symbols × 1 year**) and the Today view keeps
that default. The "Full universe" option in Strategy Lab is opt-in and
intended for cloud compute — do not trigger it on a laptop.

## 6. Roadmap (build order)

1. Docs + decisions ✅
2. Folder structure ✅
3. Data pipeline: fetch SPY → SQLite (idempotent daily job) ✅
4. First strategy (SMA cross) + minimal backtest → metrics ✅
5. Chart viewer: candles + entry/exit markers + algorithm lines ✅
5. Today view: scan ✅, paper trading ✅, rule rank ✅, confidence ✅, saved sets ✅, pick cards ✅
6. Strategy Lab: params ✅, symbols ✅, saved param sets ✅, scoreboard ✅, batch runs (later)
7. Macro view: event-driven calendar ✅ (beat/miss history later)
9. Classic TA series: S/R bounce ✅, Fib retrace ✅, wave pull ✅
10. CTA trend-following (tuned default) ✅
11. Daily cron script ✅ (`scripts/daily.sh`)
12. AWS deployment (phase 2)

## 7. Product spec — the three views

### A. Today (dashboard)

- Tabs per strategy ("Momentum v1", ...); each tab lists today's picks.
- Pick card: symbol, entry, suggested exit (ATR/target), confidence bar, and a "why" one-liner generated by the rule that fired.
- Confidence = rule-agreement score and/or historical hit rate — not a subjective feeling.

### B. Symbol Explorer (chart viewer)

- Dropdown of fetched symbols (start with SPY).
- Chart: candles, volume, technicals (MA, RSI), algorithm-drawn support/resistance with a strength score (touches, recency, volume at level).
- Auto-suggestions from rules: "exit — ATR stop hit", "hold — trend intact".
- Strategy selector: run a backtest on this symbol → results rail: win rate, profit factor, max drawdown, trade count, equity curve.

### C. Strategy Lab

- Engine skeleton: `backtesting.py` (open source) — not from scratch.
- Starter ladder: SMA cross → Donchian breakout (Turtle, the "hello world") → RSI mean reversion → Bollinger bands.
- Default params + editable params + reset; run on any fetched symbol / date range.
- Guard rails: cost/slippage assumptions; flag over-tuned results (too few trades).

### D. Macro (market context)

- Event calendar: next macro dates (FOMC, Jackson Hole, CPI, NFP) — hardcoded JSON first, sourced later.
- Cards: closing prices of macro instruments — gold (`GC=F`), crude (`CL=F`), US 2Y / 10Y yields (Treasury ETFs or `^TNX`).
- **Global regime filter:** blunt veto conditions (e.g. US10Y > 5% → no new trades). Applied on top of the whole app: Today picks are flagged/suppressed, Lab runs show the filter state.
- Keep filters few and blunt — event-day-level filtering tends to whipsaw backtests.

## 8. Trading ground rules

- **No lookahead bias:** signals at close execute next open — backtest and live must agree.
- **Adjusted prices:** split/dividend-adjusted closes (`yfinance auto_adjust=True`).
- **Exits are half the strategy:** every strategy ships with explicit exits (ATR trail, time stop, take-profit).
- **Win rate alone lies:** always report expectancy, profit factor, max drawdown, trade count.
- **Confidence ≠ probability:** rule-based scores are agreement scores, not calibrated probabilities.
- **Survivorship bias:** index lists are today's members only — backtests ignore delisted names and look better than reality.
- **Over-tuning:** few trades + great stats = suspicious. Walk-forward testing later.

## 9. Design notes (recorded, mostly future work)

- **Saved params ("tuned models"):** ✅ built v0.7.1 — the Lab saves a tuned param set (name, params, date) into SQLite and Explorer applies saved sets from a dropdown. Next slice: let the Today scan use a saved set too.
- **Daily signal state machine:** ✅ core watchlist built v0.9.0 — the `positions` ledger persists flat → entry_pending → long per symbol+strategy. Since v0.11.2 it is replayed from full history on every Today fetch (vectorized signals + ATR, cheap scalar loop) and flat rows keep their **last exit** (date, price, take-profit/stop-loss/trend-changed, realized P&L). Remaining: the daily cron job and a snapshot table for all symbols.
- **Rule-based ranking & confidence:** ✅ both built (v0.9.0–v0.10.0) — rule rank = momentum + trend + volatility score; confidence = per-strategy historical hit rate and avg 20-day return with all-time and 3Y slices. Sample-limited by default locally (deliberate curated list first, v0.12.0); full universe is a cloud-only trigger. Remaining: per-symbol slices.
- **CTA Trend (managed-futures style):** ✅ built v0.12.0 — breakout above an N-day high confirmed by a trend average; exits: M-day low (trend changed), trailing ATR stop, optional ATR TP. Defaults tuned on a 15-symbol curated basket (14 configs): `100/40/100, 5×ATR, no TP` → median PF 2.53, Sharpe 0.36, +228% all-time; SPY +286% / −20% maxDD. Honest caveat: trails 30-year buy & hold total return on this survivorship-biased basket — the value is drawdown control (~41% exposure) and positive expectancy, not beating the index. Backtest first, believe later.
- **Classic TA validity lab:** ✅ S/R Bounce, Fib Retrace, Wave Pull built (v0.8.0–v0.9.0), each with params and an on-chart explanation. First honest measurement: Fib Retrace +6.7% vs +3,109% buy & hold on SPY over 33 years — the classic levels do not add value as implemented. Backtest first, believe later.
- **Macro beat/miss:** last actuals come from FRED, next dates + forecasts from Trading Economics. Each event also gets a **Read** interpretation (good/bad for equities + why, per-event direction semantics) — a rule-of-thumb, not a forecast. Consensus history for past releases (needed for beat/miss badges) still needs a source — pending.
- **Paper trading ledger** — built v0.9.0, last-exit tracking added v0.11.2:
  - Replaces the "Holding" section and moves to the top of the Today view, above Entries/Exits.
  - One simulated position per symbol per strategy, fixed size **100 shares**.
  - Entry: next open after an entry signal (NDO). Exit: ATR trailing stop or take-profit, whichever first — exit at the following open.
  - Columns: Symbol | Entry date | Entry px | Now | P&L % | P&L $ (100 sh) | ATR stop | Take profit | Note.
  - ATR stop: starts at entry − 3×ATR(14), ratchets up to close − 3×ATR (never moves down). Take profit: entry + 2×ATR(14).
  - Flat rows show the **last exit** (date, price, `stop`/`target`, realized P&L) so an empty section always explains itself.
  - Default scope dropdown: SPY, QQQ, MAGS, SOXX, IGV, then all XLs in that order; "All symbols" option.
  - For the core watchlist, position state is computed from full history (entry never lost); for "All symbols", from the 300-bar lookback.

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

### v0.12.0 — 2026-08-17

- **CTA Trend** — a managed-futures-style trend follower: N-day high breakout above a trend average, exit on the M-day low (trend changed), trailing ATR stop, optional ATR take-profit. It is now the **default strategy everywhere** (Today, Explorer, Lab, API defaults) and it does enter at all-time highs by design.
- **Tuned defaults, not a toy:** swept 14 configs across 15 deliberate symbols (sector ETFs + megacaps + cyclicals + defensives). Winner: `n_entry=100, n_exit=40, trend_ma=100, 5×ATR stop, no TP` — median Profit Factor **2.53**, median Sharpe **0.36**, +228% all-time; SPY +286% at −20% max drawdown. Honest caveats: total return still trails 30-year buy & hold on this survivorship-biased basket (~41% exposure; the value is drawdown control + positive expectancy), win rate ~53%.
- **Curated prior-probability list** (`CURATED_SYMBOLS`): sector/core ETFs + AAPL, NVDA, MSFT, AMZN, GOOGL, META, AVGO, TSLA, JPM, XOM, CAT, UNH, LLY, HD, KO, V, MA, GS — confidence samples now draw from this deliberate list instead of a random draw.
- **Closed rows say WHY:** the paper ledger now also exits on the strategy's own exit rule, and flat rows show `take profit` / `stop loss` / `trend changed` with the realized P&L. The ledger honors each strategy's `atr_mult`/`atr_tp_mult` so paper matches backtest.
- **Macro Read column:** each calendar event interprets the latest change for equities (e.g. cooling CPI = good, falling NFP = bad) with a plain-language why — labeled as a rule-of-thumb, not a forecast.

### v0.11.2 — 2026-08-17

- The Today positions section is renamed **Paper Trading — Sector ETFs** (a quick paper simulation of the selected model across all sector/core ETFs).
- **Last exit tracking:** the ledger is now replayed from full history on every fetch (vectorized signal/ATR series + a cheap scalar loop — laptop-safe, no per-bar signal recomputation), and flat rows show their **last exit**: date, price, `stop` or `target`, and realized P&L. An empty row no longer hides why it's empty.

### v0.11.1 — 2026-08-17

- Confidence now shows the **market baseline** next to every hit rate (% of ALL sampled windows that were up) — a 100% win rate on 11 signals in a trending sample is exposed for what it is.
- Small samples (<30) get a visible "n=…" noise chip in the scoreboard.
- Fixed: FRED series with zero values produced `inf` forward returns → JSON 500; non-finite returns are now filtered.

### v0.11.0 — 2026-08-17

- Macro calendar is now **event-driven**: a curated US catalog (FOMC, CPI, Core PCE, NFP, unemployment, jobless claims, GDP, retail sales, ISM) where each event shows the next release date + forecast (Trading Economics) and the last actual vs previous (FRED), with category icons. Beat/miss vs consensus is honestly marked n/a until a forecast-history source exists.
- Real US 2Y yield (`DGS2`) from FRED replaces the SHY price proxy; FRED series joined the bars pipeline and `scripts/daily.sh`.
- Saved param sets are wired into the Today scan (`Params: <set>` dropdown); the simulated-positions ledger is tracked per set.
- Loading dimmer + disabled buttons prevent double-clicks that spin up the laptop; the confidence cache is now date-aware (recomputes when new bars arrive, not on a timer).
- Today picks are now cards with ENTRY/EXIT chips, color accents, and rank tooltips.

### v0.10.1 — 2026-08-17

- **Today is now the default view** on load (the daily workflow: confidence, simulated positions, picks).
- **URL routing:** the browser URL now reflects the active view via hash (`/#today`, `/#explorer`, `/#lab`, `/#macro`), including browser back/forward buttons and shareable links.
- Symbol Explorer loads lazily on first visit instead of on startup.

### v0.10.0 — 2026-08-17

- **Historical hit-rate confidence** (per strategy): win rate + avg 20-day forward return over past entry signals, all-time and 3Y slices — honest statistics, not probabilities.
- **Sample-limited by default** for local dev (5 symbols × 1 year); the full-universe run is opt-in via the Strategy Lab trigger and marked "cloud only".
- Strategy Lab scoreboard shows all strategies side by side; Today view shows the selected strategy's confidence with its sample size.
- Regime filter now suppresses Today picks when US10Y ≥ 5%.
- Added `scripts/daily.sh` cron script for the daily universe fetch.
- Fixed: Strategy Lab was a blank page (now the scoreboard).

### v0.9.0 — 2026-08-17

- Strategy guide panel under the chart: plain-language description, entry/exit rules, chart legend, param tooltips, and a live "now" line explaining the current signal with indicator values and the rule-rank breakdown.
- Two classic-TA strategies with params: **Fib Retrace** (n_swing, m_pullback, fib level) and **Wave Pull** (impulse_bars, impulse_pct, pullback_bars), with chart overlays.
- **Simulated Positions** (design note built): state machine ledger per symbol+strategy on the core watchlist — 100 shares, entry at next open, exit on 3×ATR trailing stop or 2×ATR take-profit. Table shows all 16 watchlist rows in order, "—" for flat symbols.
- **Rule-based ranking**: momentum + trend agreement + volatility penalty, labeled as a score with its breakdown shown.
- First honest measurements (SPY, full history): Fib Retrace +6.7% vs +3,109% buy & hold; Wave Pull +121% vs +3,057%.

### v0.8.1 — 2026-08-17

- Recorded the **Simulated Positions** design (100-share paper ledger, ATR stop + take-profit levels, default watchlist order) in the design notes. Reviewed the parking lot — no ideas lost.

### v0.8.0 — 2026-08-17

- Fixed: switching strategy left the previous strategy's entry/exit markers on the chart. Root cause: short windows produced NaN metrics → 500 → markers never refreshed. NaN now serializes as null ("—" in the UI), and markers/overlays are cleared at the start of every run.
- Added classic **S/R Bounce** strategy: long when price tests and holds the N-day support, exit at the N-day resistance or on an ATR stop breakdown. The chart draws the algorithm-computed support/resistance bands.
- Today scan supports S/R Bounce.

### v0.7.1 — 2026-08-17

- Today view polished: human-readable signal reasons, since-entry P&L (entry at next open, green/red %), watchlist scope dropdown (default: SPY, QQQ, MAGS, SOXX, IGV + XL ETFs; "All symbols" option).
- Saved param sets (design note #1): save/apply/delete tuned params per strategy, stored in SQLite `param_sets` table.
- Removed the "later" badges from the sidebar.

### v0.7.0 — 2026-08-17

- Today view (raw): per-strategy scan of all fetched symbols — entries today / holding / exits today, ranked by a momentum placeholder, with a refresh button.
- Macro view (raw): cards for SPY, gold (`GC=F`), crude (`CL=F`), US 10Y (`^TNX`), 2Y proxy (`SHY`); sample event calendar (clearly marked — real source later); blunt regime filter (US10Y ≥ 5% → caution banner).
- Recorded design notes: saved/tuned param sets, daily signal state machine, rule-based ranking + confidence.

### v0.6.0 — 2026-08-17

- Metrics are now **range-aware**: selecting 3M…ALL re-runs the backtest on that window, so per-regime performance is visible instead of one constant full-history number.
- Strategy Lab first slice: editable params per strategy (with defaults + reset) and an equity curve chart.
- Added two strategies: **Donchian Trend** (Turtle-style breakout, Donchian exit + ATR trailing stop) and **RSI Reversion**.
- Chart overlays now switch per strategy: SMA lines / Donchian bands + ATR stop floor.

### v0.5.2 — 2026-08-17

- Replaced the symbol dropdown with a searchable typeahead combobox (type to filter, arrows + Enter, click to pick).
- Hardened the pipeline: Yahoo NaN rows dropped before storing; a bad symbol no longer kills a fetch run.
- Added `--missing-only` flag to resume interrupted backfills without re-downloading.

### v0.5.1 — 2026-08-17

- Explorer now loads full history (was truncated to ~3 years) and adds TradingView-style controls: 3M/6M/1Y/2Y/3Y/5Y/10Y/ALL range buttons + zoom in/out/fit.
- Daily resolution only by design — NDO strategies only need daily closes.
- Fixed via in-browser testing: controls overflowed under the results rail at narrow widths; time-scale ranges were clamped by `minBarSpacing` (lowered to 0.1).

### v0.5.0 — 2026-08-17

- Added `main.py`: FastAPI server — `/api/symbols`, `/api/bars/{symbol}`, `/api/backtest/{symbol}`, serves the static frontend.
- Built the first real UI (`frontend/index.html`): sidebar with Today/Lab/Macro stubs, Symbol Explorer with Lightweight Charts — candles, volume, SMA 20/50 overlays, entry/exit markers, metrics rail, trades table.
- Verified in the built-in browser: page load, chart pixels, SPY → AAPL switching, API payloads.
- Fixed: `backtesting.py` 0.6.6 exposes trades as a DataFrame (`stats._trades`), not Trade objects.

### v0.4.0 — 2026-08-17

- Added `strategies.py`: SMA Cross (20/50) on `backtesting.py` — signal at close, execution at next open, explicit exit on cross-back.
- Added `engine.py`: backtest CLI with honest assumptions — $100k cash, 0.1% commission per side, `finalize_trades=True`.
- Metrics reported: return, buy & hold, max drawdown, win rate, profit factor, Sharpe, # trades, exposure.
- First honest result (SPY, 1993→2026): +550% vs +3,035% buy & hold, PF 2.40, MaxDD −36.6%, 87 trades — the hello-world strategy whipsaws and underperforms buy & hold, as expected.

### v0.3.2 — 2026-08-17

- Added `universe.py`: builds the watch universe from Wikipedia (S&P 500 ∪ Nasdaq-100 ∪ XL ETFs, deduped, Yahoo-normalized), cached in `data/universe.csv`.
- Extended `fetch.py`: `--universe` mode, `--delay` pacing, retry with backoff on Yahoo rate limits (429).
- Fetched 11 XL sector ETFs as a polite-fetch smoke test.
- Added survivorship-bias warning to the trading ground rules.

### v0.3.1 — 2026-08-17

- Implemented the data pipeline: `backend/app/store.py` (SQLite `bars` table, PK (symbol, date), idempotent upsert) and `backend/app/fetch.py` (yfinance, adjusted prices, multi-symbol CLI).
- Set up `.venv` with `fastapi`, `uvicorn`, `yfinance`, `pandas`.
- Fetched SPY: 8,443 daily bars (1993-01-29 → 2026-08-14) into `data/market.db`; re-run verified duplicate-free.

### v0.3.0 — 2026-08-17

- Evaluated the three-menu idea and wrote the product spec: Today (dashboard), Symbol Explorer (chart viewer), Strategy Lab.
- Decided engine: `backtesting.py` as open-source skeleton (not from scratch).
- Added trading ground rules: no lookahead bias, adjusted prices, explicit exits, full metrics set (not win rate alone), confidence ≠ probability.
- Added 4th view: Macro (event calendar + macro instrument cards + global regime filter, e.g. US10Y > 5% → no trade).
- Roadmap renumbered to a build order (data → one strategy → chart → Today view → Lab).

### v0.2.2 — 2026-08-17

- Decided charting: **TradingView Lightweight Charts** (CDN, no build step).
- Backtest visualization plan: entry/exit via series markers, ATR exit / support / resistance as algorithm-drawn price lines. Backend computes, frontend draws.

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