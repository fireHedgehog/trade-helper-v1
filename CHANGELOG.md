[Home](README.md) · [Docs index](docs/README.md) · [Roadmap](docs/roadmap.md) · [Product](docs/product.md)

# Changelog

## v0.19.4 — 2026-08-18

- Implemented locked-universe candidate aggregation on common dates, including
  explicit symbol exclusions and a hard minimum-coverage failure.
- Implemented complete-family validation selection using the preregistered
  bootstrap/Holm gate and deterministic score/Calmar/drawdown/parameter ties.
- A family with no significant survivor now returns cash rather than promoting
  the least-bad candidate. **91 tests pass. No real candidate run occurred.**

## v0.19.3 — 2026-08-18

- Locked fold-local selection before candidate evaluation: validation-only
  scoring, at least 8 of 12 ETFs, common-date equal-weight aggregation, median
  benchmark-relative return, Holm significance gate, deterministic tie breakers,
  and a cash fallback when nothing survives.
- Recorded the amendment in the append-only attempt ledger. No candidate
  performance was calculated before this checkpoint.

## v0.19.2 — 2026-08-18

- Added fold-local strategy, constant-exposure benchmark, and excess daily-return
  construction using the canonical costed execution engine.
- Explicitly removes every bar after a window's declared end before constructing
  rules. Tests mutate future prices and prove earlier evaluation is unchanged.
- Added aligned-date, configured-cost, invalid-window, drawdown, exposure, trade-
  count, and compact-summary outputs. **86 tests pass.**
- Candidate ranking remains intentionally disabled until fold-local selection is
  implemented and reviewed.

## v0.19.1 — 2026-08-18

- Implemented the preregistered one-sided circular moving-block bootstrap for
  mean excess returns, including null centering, deterministic seeds, circular
  blocks, and a non-zero add-one p-value correction.
- Added complete-family Holm adjustment reporting without running it on strategy
  candidates yet. Fold-local return construction remains a separate review gate.
- Verified **82 tests pass**.

## v0.19.0 — 2026-08-18

- Replaced the 787-line root README with a concise project landing page focused
  on status, safety, setup, architecture, and documentation navigation.
- Moved the complete validation checklist to `docs/roadmap.md`, product/trading
  notes to `docs/product.md`, and version history to this file without discarding
  the original audit evidence or legacy entries.
- Added `docs/README.md` as the documentation index and consistent navigation to
  component guides, the research protocol, and all architecture decisions.

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
