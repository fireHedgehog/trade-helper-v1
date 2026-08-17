# trade-helper-v1

A simple stock-data helper app: pull US stock daily closing prices once a day from the free Yahoo Finance API, store the history locally, and run backtests against the local data — with a small web UI on top.

> **Status: research prototype — not ready for live trading.** This README is a
> **living document**. Every material decision, limitation, and completed change
> is recorded here and versioned. See [Pre-deployment hardening plan](#6-pre-deployment-hardening-plan),
> [Versioning](#versioning), and [Changelog](#changelog).

> [!WARNING]
> This project is educational research software, not investment advice or a
> brokerage system. Backtests and simulated positions can be wrong because of
> implementation defects, biased data, overfitting, transaction assumptions, or
> market regime changes. Do not risk real money based on this app until the
> validation gates in Section 6 are complete and independently reviewed.

---

## 1. The idea (what we know so far)

- **Data source:** Yahoo Finance free API (via Python `yfinance`), US stocks, daily closing prices.
- **Fetch frequency:** once per day — either a cron/scheduled job or a manual button.
- **Storage:** persist the history **locally on disk**, so backtests read local data instead of re-fetching from the API every time.
- **Backend:** Python (FastAPI) — good open-source ML stack: `pandas`, `scikit-learn`, etc.
- **Frontend:** simple web UI to view data, trigger a fetch, and kick off backtests.
- **Deployment (later):** AWS.

## 2. Deferred decisions

- AWS shape: one small **EC2** instance (simple) vs **Lambda + S3** (more moving parts)?
  **Paused until Stage 9.**
- Storage format: **SQLite** (start here) vs Parquet vs DuckDB?
- Frontend hosting: served by the backend (start here) vs separate S3 + CloudFront?
- Which symbols to track? ✅ decided — S&P 500 ∪ Nasdaq-100 ∪ XL sector ETFs (~530 symbols, deduped, survivorship-bias caveat applies).
- Backtest engine: ✅ canonical in-repo daily execution state machine (v0.15.0);
  `backtesting.py` is retained only as a frozen legacy comparison baseline.
- Which ML models matter first? **Paused until Stages 1–4 establish a valid
  non-ML research baseline.**

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

### Phase 2 — AWS (paused until the Stage 9 gates)

- Small EC2 instance running the same backend + a daily cron job.
- SQLite file on the instance's EBS disk (or moved to S3/Parquet if we outgrow it).
- Optionally move the frontend to S3 + CloudFront.

## 4. Repo structure

```
trade-helper-v1/
├── README.md            # this living document
├── .gitignore
├── backend/             # Python FastAPI app + tested research primitives
│   ├── README.md
│   └── app/             # main.py, fetch.py, store.py, universe.py, strategies.py, engine.py
├── docs/                # architecture decisions + locked research protocol
├── output/
│   └── jupyter-notebook/ # reproducible research notebooks
├── frontend/            # static UI, no build step (index.html)
│   └── README.md
├── scripts/             # daily cron wrapper (created; unattended use paused)
└── data/                # local market data (gitignored)
    └── README.md
```

## 5. Local dev environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements-dev.txt
pytest
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
minutes of CPU — laptop fans will complain). Locally, confidence is
sample-limited by default (**16 symbols × 1 year**) and the Today view keeps
that default. Larger symbol/history selections in Strategy Lab are opt-in and
intended for cloud compute — do not trigger it on a laptop.

## 6. Pre-deployment hardening plan

### 6.1 Audit baseline (Codex review, 2026-08-17)

The repository was reviewed across the backend, frontend, data flow, strategy
logic, documentation, and current validation setup. The review found a useful
educational prototype with unusually honest caveats, but not yet a trustworthy
trading decision system.

The principal blockers are:

- The backtest, Today scanner, historical confidence calculation, and simulated
  ledger do not yet share one canonical position/execution engine.
- The simulated ledger documents next-open exits but currently records some
  exits at the signal day's close.
- The Today scanner can confuse a condition that is true now with a position
  that was actually entered and remains open.
- "Confidence" measures a fixed 20-day forward return after an entry signal; it
  does not measure the strategy's realized trade result or a calibrated
  probability.
- Parameter selection is in-sample. There is no untouched holdout, walk-forward
  evaluation, uncertainty estimate, or multiple-testing control yet.
- There is no automated test suite, and calculation failures can be silently
  skipped by broad exception handlers.
- The frontend does not yet make data freshness, execution timing, missing data,
  and research-only status prominent enough for a money-related product.
- Security, accessibility, reproducibility, and deployment controls need to be
  completed before cron or AWS work.

The stages below deliberately put correctness before new strategies, automation,
or deployment. Each stage should be completed in a small pull request or commit,
with tests and README evidence, so changes can be reviewed one at a time.

### Stage 0 — freeze the research baseline

**Goal:** preserve today's behaviour before refactoring it.

- [x] Record the Python version and pin direct dependency versions.
- [x] Add a deterministic small OHLC fixture covering gaps, trends, reversals,
      stops, and missing bars.
- [x] Save baseline outputs for each strategy on that fixture.
- [x] Add `pytest` and a documented test command without downloading market data.
- [x] Separate generated data, caches, logs, and research artifacts from source.
- [x] Add a short decision record explaining close signal → next-open fill.

**Exit gate:** a fresh clone can install dependencies and reproduce the same
fixture results locally.

### Stage 1 — one canonical execution model (highest priority)

**Goal:** every view reports the same entries, exits, fills, and position state.

- [x] Define explicit states: `flat`, `entry_pending`, `long`, and
      `exit_pending`.
- [x] Define fill rules for normal opens, overnight gaps, missing next bars, and
      the final bar of a dataset.
- [x] Move each strategy's entry and exit rules into one reusable signal source.
- [x] Make the backtest, Today scan, ledger, and chart markers consume that source.
- [x] Use the configured ATR period consistently; do not hardcode 14 in one path.
- [x] Decide whether stops are close-based or intraday OHLC-based and implement
      that decision consistently.
- [x] Remove forced end-of-window exits from headline statistics, or label them
      separately from genuine strategy exits.
- [x] Add parity tests proving that identical bars and parameters produce
      identical trades in all code paths.

**Exit gate:** for every strategy and fixture, the API, ledger, and backtest have
the same position state and fill dates/prices.

### Stage 2 — automated correctness and data-quality tests

**Goal:** turn trading assumptions into executable checks.

- [x] Unit-test every entry rule, exit rule, ATR calculation, indicator warm-up,
      and parameter boundary.
- [x] Test next-open fills, overnight gaps through stops, no-next-bar cases, and
      open trades at the end of a sample.
- [x] Test SQLite idempotency, duplicate bars, invalid OHLC, zero/negative prices,
      missing volume, and non-monotonic dates.
- [x] Test split/dividend-adjusted price handling and document its benchmark
      implications.
- [x] Replace broad silent exception handling with structured errors containing
      the symbol, strategy, and failed calculation.
- [x] Return scan coverage: requested, processed, missing, and failed. Explicit
      stale-data classification remains in Stage 6, where market timezone and
      trading-calendar semantics are defined.
- [x] Add API integration tests for bad strategies, bad parameters, missing
      symbols, empty samples, and oversized requests.

**Exit gate:** the deterministic suite passes locally and a deliberately broken
rule produces a failing test.

### Stage 3 — honest research statistics and benchmarks

**Goal:** make the displayed evidence answer the right questions.

- [x] Rename "Confidence" to "Historical post-signal statistics" unless a
      probability model is later calibrated and validated.
- [x] Clearly separate fixed-horizon signal analysis from full-trade performance.
- [x] Show the sample start/end dates; never label a one-year window "all-time".
- [x] Report CAGR, annualized volatility, downside deviation, Sortino, Calmar,
      maximum drawdown duration, exposure, turnover, and trade expectancy.
- [x] Compare against buy-and-hold and a constant-exposure/cash-yield benchmark;
      document that it is a simple control rather than a tradable replication.
- [x] Include commission, spread, slippage, overnight gaps, and configurable cash
      yield in net results.
- [x] Prevent within-symbol overlap and use calendar-month clusters to retain
      contemporaneous cross-symbol outcomes when estimating uncertainty; disclose
      the remaining adjacent-month dependence.
- [x] Add deterministic cluster-bootstrap confidence intervals, not only point
      estimates, with a disclosed small-cluster fallback.
- [x] Display insufficient-sample warnings at the predefined 30-observation
      threshold.

**Exit gate:** every headline metric states its window, sample, benchmark, cost
assumptions, and uncertainty or limitation.

### Stage 4 — out-of-sample research protocol

**Goal:** test hypotheses without advertising in-sample winners as proven edges.

- [x] Write the initial CTA hypothesis and acceptance metrics before any new
      parameter search (`docs/research-protocol.md`).
- [x] Divide data chronologically into training, validation, and untouched test
      periods.
- [ ] Implement rolling walk-forward evaluation with parameters selected only
      from information available at that time.
- [ ] Reserve an untouched holdout universe and period.
- [ ] Plot parameter stability and reject isolated "best" combinations.
- [x] Start an append-only attempt ledger, including the contaminated legacy
      14-configuration CTA tuning run and the preregistered 54-candidate run.
- [ ] Apply a suitable multiple-comparison or false-discovery adjustment.
- [ ] Prefer point-in-time membership data; until available, limit claims and use
      long-lived broad ETFs to reduce survivorship bias.
- [ ] Test bear, bull, sideways, high-volatility, and rising-rate regimes
      separately without tuning to each result after inspection.

**Exit gate:** the final test set remains untouched until a written model is
locked, and results are reported even when they fail.

**Current checkpoint (v0.18.1 correction):** partition mechanics and the
preregistered hypothesis are complete, but Stage 4 is not. The hidden 504-bar
SPY tail is only a workflow rehearsal, not an untouched holdout: earlier versions
already tuned and displayed full-history SPY results. Parameter ranking remains
blocked until the universe, finite grid, attempt ledger, and multiple-testing
treatment are committed. Valid confirmation must use genuinely unseen future or
otherwise uninspected point-in-time data.

### Stage 5 — portfolio and risk model

**Goal:** stop presenting independent fixed-share trades as a portfolio.

- [ ] Replace the fixed 100-share convention with explicit capital and sizing.
- [ ] Add maximum position, sector, correlated-asset, and portfolio exposure.
- [ ] Model concurrent signals, available cash, turnover, and rejected orders.
- [ ] Separate per-trade stop distance from portfolio risk limits.
- [ ] Add portfolio equity, drawdown, concentration, and daily return history.
- [ ] Add a hard kill switch and maximum-loss controls for any future paper/live
      integration.
- [ ] Keep paper and live data stores physically and visually distinct.

**Exit gate:** no displayed dollar P&L can imply capital that the portfolio did
not actually have.

### Stage 6 — UX, accessibility, and safety language

**Goal:** make uncertainty and system state obvious to a beginner.

- [ ] Show `data as of`, market timezone, fetch status, and stale/missing symbols
      beside every decision-oriented view.
- [ ] Distinguish `no signal`, `not enough history`, `stale data`, and
      `calculation failed`.
- [ ] Show signal time, intended order time, assumed fill time, and actual
      simulation fill as separate fields.
- [ ] Put the research-only warning and key bias/cost assumptions beside results,
      not only in this README.
- [ ] Replace hover-only explanations with keyboard/touch-accessible disclosures.
- [ ] Add labels/ARIA, visible focus states, responsive layouts, and accessible
      table/card alternatives.
- [ ] Confirm destructive actions such as deleting saved parameter sets.
- [ ] Break the single frontend file into testable modules when doing so reduces
      risk rather than merely changing technology.
- [ ] Add Playwright smoke tests for Today, Explorer, Strategy Lab, Macro, error
      states, and narrow-screen layouts.

**Exit gate:** a new user can identify data freshness, assumptions, current
position state, and failure conditions without relying on a tooltip.

### Stage 7 — API and local security hardening

**Goal:** make local operation safe before exposing any endpoint externally.

- [ ] Validate parameters server-side using typed request models, declared ranges,
      and cross-field rules such as fast periods being below slow periods.
- [ ] Escape or safely render saved names and external calendar content instead
      of inserting untrusted strings with `innerHTML`.
- [ ] Add request size and compute limits; reject accidental full-universe/full-
      history jobs unless explicitly authorized.
- [ ] Add structured logging without secrets or sensitive account data.
- [ ] Define authentication, authorization, CSRF/CORS, rate limiting, TLS, secret
      storage, and dependency-scanning requirements for any non-local deployment.
- [ ] Run the security-best-practices review and record accepted risks.
- [ ] Back up and test restoration of SQLite before schema migrations.

**Exit gate:** the application has a documented threat model and no endpoint is
internet-exposed by default.

### Stage 8 — reliable daily operation (cron only after Stages 0–7)

**Goal:** make an unattended update observable, idempotent, and recoverable.

- [ ] Fetch into a staging transaction and validate before publishing new bars.
- [ ] Handle market holidays, early closes, timezones, partial downloads, revised
      macro data, and provider schema changes.
- [ ] Use a lock so two fetch jobs cannot run concurrently.
- [ ] Add retry limits, timeouts, run IDs, per-symbol results, and non-zero failure
      status when coverage is incomplete.
- [ ] Alert on stale data, abnormal row counts, missing core symbols, and failed
      backups.
- [ ] Recompute derived results only after a successful validated data update.
- [ ] Document rollback and manual recovery procedures.

**Exit gate:** repeated scheduled runs cannot corrupt or silently partially
publish the dataset, and a failed run produces a visible alert.

### Stage 9 — AWS deployment (last)

**Goal:** deploy a validated research application, not move unresolved risk to
the cloud.

- [ ] Choose the architecture from measured workload and recovery requirements.
- [ ] Separate application, persistent data, backups, and secrets.
- [ ] Add TLS, authentication, least-privilege IAM, network restrictions, patching,
      monitoring, budgets, and log retention.
- [ ] Create reproducible infrastructure/deployment configuration and a rollback.
- [ ] Test restore, dependency failure, provider outage, disk exhaustion, and
      process restart.
- [ ] Keep brokerage connectivity explicitly out of scope until a separate,
      independently reviewed live-trading safety project is approved.

**Exit gate:** deployment and disaster recovery are repeatable, monitored, and
cost-bounded. AWS completion does not imply that a strategy is profitable.

### Recommended implementation order

Work one small slice at a time:

1. Stage 0 test foundation.
2. CTA Trend canonical state machine and parity tests.
3. Apply the same engine to the remaining strategies.
4. Correct/rename confidence and benchmark statistics.
5. Build the walk-forward research notebook and protocol.
6. Add portfolio/risk semantics.
7. Complete UX and security gates.
8. Revisit cron only after the earlier gates pass.
9. Revisit AWS only after cron is demonstrably reliable.

Adding new strategies, machine learning, broker integration, cron automation,
and AWS deployment is intentionally paused until the relevant gates above pass.

## 7. Product spec — the three views

### A. Today (dashboard)

- Tabs per strategy ("Momentum v1", ...); each tab lists today's picks.
- Pick card: symbol, entry, suggested exit (ATR/target), rule score, historical
  post-signal statistics, and a "why" one-liner generated by the rule that fired.
- Rule agreement is a ranking heuristic; post-signal hit rate is descriptive
  historical evidence. Neither is a calibrated probability.

### B. Symbol Explorer (chart viewer)

- Dropdown of fetched symbols (start with SPY).
- Chart: candles, volume, technicals (MA, RSI), algorithm-drawn support/resistance with a strength score (touches, recency, volume at level).
- Auto-suggestions from rules: "exit — ATR stop hit", "hold — trend intact".
- Strategy selector: run a backtest on this symbol → results rail: win rate, profit factor, max drawdown, trade count, equity curve.

### C. Strategy Lab

- Engine: canonical close-signal/next-open execution state machine shared by the
  API, Today, simulated ledger, and chart markers. `backtesting.py` remains only
  for the frozen pre-refactor comparison tests.
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
- **Win rate alone lies:** always report expectancy, profit factor, drawdown,
  exposure, turnover, trade count, costs, and the comparison benchmark.
- **Post-signal statistics ≠ probability:** rule scores are ranking heuristics;
  historical hit rates are descriptive and carry uncertainty and selection bias.
- **Survivorship bias:** index lists are today's members only — backtests ignore delisted names and look better than reality.
- **Over-tuning:** few trades + great stats = suspicious. Walk-forward testing later.

## 9. Design notes (recorded, mostly future work)

- **Saved params ("tuned models"):** ✅ built v0.7.1 — the Lab saves a tuned param set (name, params, date) into SQLite and Explorer applies saved sets from a dropdown. Next slice: let the Today scan use a saved set too.
- **Daily signal state machine:** ✅ canonical engine completed v0.15.0 — the
  product uses `flat → entry_pending → long → exit_pending`, completed-close
  signals, and next-available-open fills. Today, Explorer, chart markers, and
  the 100-share ledger consume the same replay. Flat rows retain their last exit.
- **Rule-based ranking & post-signal statistics:** ✅ corrected in v0.17.0 — rule
  rank = momentum + trend + volatility score; the separate research panel reports
  non-overlapping 20-day forward outcomes for the selected window, sample dates,
  baseline, low-sample warnings, and cluster-bootstrap intervals. It is not
  strategy P&L or a probability. Full-universe research remains cloud-only.
- **CTA Trend (managed-futures style):** ✅ built v0.12.0 — breakout above an N-day high confirmed by a trend average; exits: M-day low (trend changed), trailing ATR stop, optional ATR TP. Defaults tuned on a 15-symbol curated basket (14 configs): `100/40/100, 5×ATR, no TP` → median PF 2.53, Sharpe 0.36, +228% all-time; SPY +286% / −20% maxDD. Honest caveat: trails 30-year buy & hold total return on this survivorship-biased basket — the value is drawdown control (~41% exposure) and positive expectancy, not beating the index. Backtest first, believe later.
- **Classic TA validity lab:** ✅ S/R Bounce, Fib Retrace, Wave Pull built (v0.8.0–v0.9.0), each with params and an on-chart explanation. First honest measurement: Fib Retrace +6.7% vs +3,109% buy & hold on SPY over 33 years — the classic levels do not add value as implemented. Backtest first, believe later.
- **Macro beat/miss:** last actuals come from FRED, next dates + forecasts from Trading Economics. Each event also gets a **Read** interpretation (good/bad for equities + why, per-event direction semantics) — a rule-of-thumb, not a forecast. Consensus history for past releases (needed for beat/miss badges) still needs a source — pending.
- **Model simulation ledger (sector ETFs)** — built v0.9.0, last-exit tracking added v0.11.2, renamed v0.12.2:
  - Replaces the "Holding" section and moves to the top of the Today view, above Entries/Exits.
  - One simulated position per symbol per strategy, fixed size **100 shares**.
  - Entry: next open after an entry signal. Exit: the strategy rule, configured
    close-based stop, or configured take-profit becomes pending at the close and
    fills at the following available open.
  - Columns: Symbol | Entry date | Entry px | Now | P&L % | P&L $ (100 sh) | ATR stop | Take profit | Note.
  - ATR stop/target settings come from the selected strategy parameters. Initial
    levels use ATR known on the signal bar, never the not-yet-complete fill bar.
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

### v0.18.2 — 2026-08-17

- Preregistered the exact 12-ETF universe, 54-candidate CTA grid, costs,
  partitions, and prospective-confirmation requirement in a machine-validated
  experiment specification.
- Started the attempt ledger with both the contaminated legacy 14-configuration
  run and the new no-results preregistration; failed work now counts too.
- Locked a dependence-aware testing plan before ranking: one-sided circular
  20-bar block bootstrap with 5,000 resamples, followed by Holm family-wise error
  control across all 54 candidates.
- Added deterministic grid expansion, specification validation, Holm adjustment,
  and tests. **79 tests pass. No new performance result was calculated.**

### v0.18.1 — 2026-08-17

- Corrected an overclaim in v0.18.0: the hidden 504-bar SPY tail is not a valid
  untouched holdout because prior app versions and research inspected full-history
  SPY, including that period. Renamed the code boundary to `CandidateHoldout` and
  labeled it as a workflow rehearsal.
- A valid confirmatory result now explicitly requires prospectively collected
  post-lock data or another genuinely uninspected point-in-time dataset. Prior
  exposure cannot be repaired by hiding the same observations later.

### v0.18.0 — 2026-08-17

- **Stage 4 foundation only — not a strategy result:** preregistered the CTA
  hypothesis, primary benchmark-relative metric, stability/risk/evidence gates,
  failure rule, and final-holdout unlock boundary.
- Added tested expanding 756/252/252-bar train/validation/test manifests and hid
  the latest 504 SPY bars without evaluating them in the new notebook. See the
  v0.18.1 correction: this tail was already exposed by older full-history work.
- Added a reproducible Jupyter experiment under `output/jupyter-notebook/`. It
  runs from repository-local data, exposes partition dates rather than holdout
  returns, and stops before parameter ranking.
- The next slice must lock the broad-ETF universe, finite parameter grid,
  append-only attempt ledger, and multiple-testing treatment. Stage 4 remains
  incomplete and no edge claim is permitted.
- Verified **76 tests passed** and executed all notebook code cells top-to-bottom.

### v0.17.0 — 2026-08-17

- **Stage 3 complete — honest research statistics and benchmarks:** renamed the
  confidence UI to historical post-signal statistics and separated its fixed
  20-day close-to-close outcomes from canonical full-trade performance.
- Post-signal samples are 20 bars apart within each symbol. The API reports the
  exact sample window, a 30-observation warning, and deterministic 95% calendar-
  month cluster-bootstrap intervals that retain contemporaneous symbol outcomes.
- Expanded net performance reporting with CAGR, annual volatility, downside
  deviation, Sortino, Calmar, drawdown duration, exposure, turnover, and dollar/
  percentage expectancy.
- Added adjusted-price buy-and-hold and a documented constant-exposure/cash-yield
  comparison. Performance is labeled as one historical path, not proof.
- Added configurable commission, quoted spread, adverse slippage, and cash yield;
  default round-trip friction is 20 bps commission plus 2 bps spread plus 10 bps
  slippage. Next-open execution includes overnight gaps.
- Added ADR 0003 documenting definitions and unresolved limitations including
  adjacent-month dependence, selection bias, survivorship bias, and overfitting.
- Verified **71 tests passed** with no warnings.

### v0.16.0 — 2026-08-17

- **Stage 2 complete — correctness, data-quality, and API tests:** expanded the
  deterministic suite to entry/exit rules, ATR/RSI warm-up, next-open execution,
  final-bar pending orders, fixed-share accounting, SQLite, scan coverage, and
  FastAPI contracts.
- Market-data storage now rejects an entire malformed batch before writing any
  row: missing/non-finite values, non-positive OHLC, impossible candles, negative
  volume, duplicate dates, and non-monotonic dates are errors.
- Added ADR 0002 documenting adjusted Yahoo OHLC semantics, total-return-like
  benchmark implications, FRED non-tradability, provider revisions, and the
  remaining data-lineage limitations.
- API strategy parameters now enforce declared types/ranges and cross-field rules;
  unknown parameters and invalid date windows return explicit 400 responses.
- Scan and historical-signal calculations now return requested/processed/missing/
  failed coverage instead of silently discarding calculation failures. Today
  displays the coverage counts.
- Canonical RSI and ATR require their full configured warm-up periods.
- Verified **63 tests passed** with no warnings.

### v0.15.0 — 2026-08-17

- **Stage 1 complete — canonical execution model:** added one deterministic
  `flat → entry_pending → long → exit_pending` engine and one reusable vectorized
  rules source for all seven strategies.
- Backtest API, Today scanner, position ledger, signal endpoint, and chart markers
  now consume the same replay. Added all-strategy parity tests.
- Corrected exits to become pending at the completed close and fill at the next
  available open. Overnight gaps fill at that open; final-bar pending orders are
  not fabricated as completed trades.
- Corrected ATR lookahead: initial stop/target levels use the ATR known on the
  signal bar, not high/low/close from the fill day that did not yet exist at its
  open.
- Removed forced final-bar liquidation from headline results. Explorer now shows
  closed-trade count, an explicit OPEN position metric, and a marker for the open
  entry.
- Corrected the simulated ledger to calculate closed P&L with the displayed fixed
  100-share size.
- Verified **27 tests passed** and exercised Today and Explorer in a real browser
  on an isolated server. The existing port-8000 VS Code process was left intact;
  verification used port 8001.

### v0.14.0 — 2026-08-17

- **Stage 0 complete — reproducible research baseline:** pinned Python 3.12.3 and
  all direct runtime dependencies, added a pinned development requirements file,
  and documented the network-free `pytest` command.
- Added deterministic synthetic OHLC data containing trends, reversals,
  overnight gaps, and missing sessions; no local market database or live provider
  is required by the tests.
- Captured characterization metrics for all seven default strategies. These are
  regression baselines, not profitability claims.
- Added ADR 0001 defining completed-close signals, next-available-open fills,
  pending final-bar orders, and close-based stops until an intraday ordering model
  exists.
- Verified the complete suite in both the project environment and a clean
  temporary virtual environment: **9 tests passed**.

### v0.13.0 — 2026-08-17

- **Codex audit and pre-deployment hardening plan:** reviewed the repository's
  backend, frontend, data flow, strategy logic, documentation, and validation
  setup. Recorded the principal correctness, quant-research, UX, security, and
  operational risks without claiming they are already fixed.
- Changed the project status from "planning" to **research prototype — not ready
  for live trading**, with a prominent educational-use warning.
- Replaced the feature-oriented roadmap with staged validation gates: freeze the
  baseline; unify execution; add automated tests; correct research statistics;
  implement out-of-sample evaluation; define portfolio risk; harden UX/security;
  then revisit cron and AWS.
- Paused new strategies, machine learning, brokerage integration, cron
  automation, and cloud deployment until their prerequisite gates pass.

### v0.12.4 — 2026-08-17

- Exit-plan cells reverted to the compact chips (`trend 716.58`, `stop 738.42` — hover for the rule); the line-broken legend with bracketed explanations stays below the table.

### v0.12.3 — 2026-08-17

- **Exit plan, plain English:** each open row now lists every exit trigger on its own line with the rule in brackets, e.g. `trend 716.58 (close below the 40-day low → trend changed)` / `stop 738.42 (close below trailing stop → stop loss)` — no more guessing what each number means. The legend under the table is the same format: one line per trigger with the explanation in parentheses.
- **Scoreboard returns vs buy & hold:** two new columns, **Ret med** and **B&H med** — the median strategy return vs the median buy & hold return across the selected symbols and window (new `/api/score-return`). Honest result on the default 1-year sample: every strategy trails buy & hold in this bull window; RSI Reversion comes closest.
- **Default button** in the Lab symbol picker restores the pre-ticked 16-name liquid basket — Clear no longer means "reload the page to get it back".
- Lab row computations now run in a 3-way pool instead of all at once, keeping the laptop's CPU calm.

### v0.12.2 — 2026-08-17

- **Strategy Lab sample control:** the blind "5 symbols × 1 year" dropdown is gone. There is now a **symbol picker with All / Clear** buttons and a **year selector** (1/3/5/10 years, all history). Default selection is a deliberate 16-name liquid basket — SPY, QQQ, MAGS, SOXX, IGV, XLK, XLE, XLF, XLU, AAPL, NVDA, MSFT, JPM, CAT, KO, LLY — chosen for liquidity and diversity, so you always know exactly which names are being tested.
- Selections above 40 symbols or "All history" show an explicit heavy-compute warning (cloud recommended) instead of silently spinning the fan.
- `/api/confidence` now takes an explicit symbol list (`symbols=SPY,QQQ,XLK`); the default is the liquid basket, and the response includes the sampled names.
- **Today confidence panel** reformatted from a run-on sentence into compact labeled stat boxes (win rate, avg 20d, signals, market base, 3Y win, 3Y signals) with the sample list on hover.
- "Paper Trading" renamed **Model Simulation — Sector ETFs** (no paper-trading framing; it's a quick simulation of the selected model across the sector/core ETF list).

### v0.12.1 — 2026-08-17

- Paper Trading table reworked so you always know **when and why** a position exits:
  - Open rows show an **Exit plan** column: the strategy's trend level, the trailing ATR stop, and the take-profit (when set), each with the exact rule as a hover tooltip (e.g. "close below the 40-day low → trend changed").
  - Closed rows say `exited <date> @ <price>` plus the reason chip (`take profit` / `stop loss` / `trend changed`) and realized P&L.
  - A legend under the table explains the chips; `/api/positions` now resolves saved-set params so the plan matches the selected model.

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
