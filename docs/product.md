[Home](../README.md) · [Docs index](README.md) · [Roadmap](roadmap.md) · [Product](product.md) · [Research protocol](research-protocol.md) · [Changelog](../CHANGELOG.md)

# Product and research design

## Product objective

The first product is a **local research decision assistant**, not a trading
signal service. Its purpose is to turn one prewritten hypothesis into a
reproducible `reject`, `revise`, or `continue` decision and to make weak evidence
obvious. Preventing a false belief in an edge counts as product success; trade
frequency and attractive historical charts do not.

Portfolio strategies will use Passive ETF-12 v1 as their primary benchmark,
with SPY buy-and-hold and cash as secondary references. The exact contract is
fixed in [ADR 0005](adr/0005-product-objective-and-portfolio-benchmark.md).

## A. Today (dashboard)

- Opening Today reads immutable stored state; it does not scan or replay a
  portfolio. Updating watched lifecycles, running the selected model across the
  full universe, and running the portfolio comparison are separate actions.
- Each strategy has a persistent user-managed observation list. Watched symbols
  remain present when flat and show their latest entry or exit event.
- Only explicitly saved symbols appear in that table; defaults are suggestions,
  not silently adopted user choices.
- The watched table is the complete per-symbol lifecycle view: holding/flat or
  pending status, last entry, last exit, next action, current stop, and data date.
- Model tabs show every entry-pending candidate from the latest completed
  full-universe run for that algorithm. A watchlist-only run never populates the
  model tab.
- Rule agreement is a ranking heuristic; post-signal hit rate is descriptive
  historical evidence. Neither is a calibrated probability.
- A model-discovery board provides separate Intersections, Momentum, New
  Breakouts, and per-algorithm tabs. It reads stored full-universe runs only. The
  Momentum facility remains empty until a model is preregistered; New Breakouts
  combines entry-pending states from existing runs rather than inventing an
  untested algorithm.

## B. Symbol Research (chart viewer)

- Searchable picker of fetched symbols (start with SPY). Selecting a symbol,
  strategy, parameter set, or chart range does not start a backtest.
- Chart: candles, volume, technicals (MA, RSI), algorithm-drawn support/resistance with a strength score (touches, recency, volume at level).
- Auto-suggestions from rules: "exit — ATR stop hit", "hold — trend intact".
- The explicit Run Backtest action fills the results rail: win rate, profit
  factor, max drawdown, trade count, and equity curve.
- Expandable strategy dossiers expose the current evidence label, rules, risks,
  and pending research rather than presenting every algorithm as validated.

## C. Strategy Lab

- Engine: canonical close-signal/next-open execution state machine shared by the
  API, Today, simulated ledger, and chart markers. `backtesting.py` remains only
  for the frozen pre-refactor comparison tests.
- Starter ladder: SMA cross → Donchian breakout (Turtle, the "hello world") → RSI mean reversion → Bollinger bands.
- Default params + editable params + reset; run on any fetched symbol / date range.
- Guard rails: cost/slippage assumptions; flag over-tuned results (too few trades).
- Save an ordered symbol selection as the chosen strategy's persistent
  observation list. “Compute / refresh” remains a separate explicit action.

## D. Macro (market context)

- Event calendar: next macro dates (FOMC, Jackson Hole, CPI, NFP) — hardcoded JSON first, sourced later.
- Cards: closing prices of macro instruments — gold (`GC=F`), crude (`CL=F`), US 2Y / 10Y yields (Treasury ETFs or `^TNX`).
- **Global regime filter:** blunt veto conditions (e.g. US10Y > 5% → no new trades). Applied on top of the whole app: Today picks are flagged/suppressed, Lab runs show the filter state.
- Keep filters few and blunt — event-day-level filtering tends to whipsaw backtests.

## E. Data Management

- Inventory every stored series with provider ownership, first/latest dates,
  row count, expected completed US weekday, and a visible freshness state.
- Keep Yahoo securities and FRED economic series separate. FRED identifiers must
  never appear in strategy selectors or Yahoo refresh jobs.
- Refresh manually from the local UI: core, aging/stale, or all Yahoo-managed
  symbols. Only one job may run at once.
- Fetch full adjusted Yahoo history so an incremental update cannot mix old and
  new adjustment bases. Apply a fixed two-second delay between symbols and retry
  backoff. These controls reduce pressure; they cannot guarantee provider access.
- Show job progress and each symbol's published/failed result. Published SQLite
  rows survive a server restart, but the in-memory progress record does not.
- Unattended cron remains parked until persistent run records, staging,
  exchange-calendar handling, alerts, backup/restore, and recovery are tested.

## Trading ground rules

- **No lookahead bias:** signals at close execute next open — backtest and live must agree.
- **Adjusted prices:** split/dividend-adjusted closes (`yfinance auto_adjust=True`).
- **Exits are half the strategy:** every strategy ships with explicit exits (ATR trail, time stop, take-profit).
- **Win rate alone lies:** always report expectancy, profit factor, drawdown,
  exposure, turnover, trade count, costs, and the comparison benchmark.
- **Post-signal statistics ≠ probability:** rule scores are ranking heuristics;
  historical hit rates are descriptive and carry uncertainty and selection bias.
- **Survivorship bias:** index lists are today's members only — backtests ignore delisted names and look better than reality.
- **Over-tuning:** few trades + great stats = suspicious. Walk-forward testing later.

## Design notes

- **Research workspace:** ✅ first slice built v0.26.0 — menu navigation is
  read-only, per-strategy observation lists and completed snapshots persist in
  SQLite, Today separates watched lifecycle from full-universe new-entry scans,
  and every expensive view has its own explicit run action. The workflow and
  product-usability target are in the
  [workspace redesign](workspace-redesign.md).

- **Saved params ("tuned models"):** ✅ built v0.7.1 — the Lab saves a named
  parameter set with its date in SQLite; Explorer and Today can replay it. A
  saved set records inputs, not evidence that they are optimal or validated.
- **Daily signal state machine:** ✅ canonical engine completed v0.15.0 — the
  product uses `flat → entry_pending → long → exit_pending`, completed-close
  signals, and next-available-open fills. Today signals, Explorer, chart markers,
  and the legacy diagnostic ledger consume the same single-symbol replay. The
  shared-account simulator reuses those rules and execution decisions while
  applying portfolio cash and risk constraints.
- **Rule-based ranking & post-signal statistics:** ✅ corrected in v0.17.0 — rule
  rank = momentum + trend + volatility score; the separate research panel reports
  non-overlapping 20-day forward outcomes for the selected window, sample dates,
  baseline, low-sample warnings, and cluster-bootstrap intervals. It is not
  strategy P&L or a probability. Full-universe research remains cloud-only.
- **CTA Trend (managed-futures style):** ✅ built v0.12.0 — breakout above an N-day high confirmed by a trend average; exits: M-day low (trend changed), trailing ATR stop, optional ATR TP. Defaults tuned on a 15-symbol curated basket (14 configs): `100/40/100, 5×ATR, no TP` → median PF 2.53, Sharpe 0.36, +228% all-time; SPY +286% / −20% maxDD. Honest caveat: trails 30-year buy & hold total return on this survivorship-biased basket — the value is drawdown control (~41% exposure) and positive expectancy, not beating the index. Backtest first, believe later.
- **Classic TA validity lab:** ✅ S/R Bounce, Fib Retrace, Wave Pull built (v0.8.0–v0.9.0), each with params and an on-chart explanation. First honest measurement: Fib Retrace +6.7% vs +3,109% buy & hold on SPY over 33 years — the classic levels do not add value as implemented. Backtest first, believe later.
- **Macro beat/miss:** last actuals come from FRED, next dates + forecasts from Trading Economics. Each event also gets a **Read** interpretation (good/bad for equities + why, per-event direction semantics) — a rule-of-thumb, not a forecast. Consensus history for past releases (needed for beat/miss badges) still needs a source — pending.
- **Shared-capital portfolio replay** — ✅ replaced the active fixed-share view in
  v0.22.0:
  - One historical $100,000 account covers a locked 12-ETF universe on one exact
    common calendar; it never treats independent symbols as separately funded.
  - Completed-close signals fill at the next shared-calendar open. Whole-share
    sizing, costs, cash, sector/cluster caps, settlement, rejected orders, and a
    15% drawdown kill switch follow [ADR 0004](adr/0004-portfolio-risk-contract.md).
  - Today displays account equity, return, drawdown, exposure, turnover, trade
    and rejection counts, plus actual open-position value and dollar P&L.
  - Passive ETF-12 v1 is implemented under ADR 0005: equal-weight locked ETFs,
    annual rebalancing, whole shares, canonical costs, residual cash, and T+1
    settlement. Today also shows SPY and cash as secondary references and warns
    that historical differences do not establish a durable edge.
  - SMA Cross and RSI Reversion are unavailable in this view because they have
    no explicit protective stop. The product refuses them rather than inventing
    a risk rule after seeing results.
  - The older `/api/positions` fixed-share response remains a compatibility and
    signal-parity diagnostic; the Today UI does not render it.

---

## Versioning

Doc version: `v<major>.<minor>.<patch>`.

| Change | Bump |
| --- | --- |
| Typo / small wording fix | patch |
| New section or plan change | minor |
| Architecture reset / rewrite | major |

Every version gets a dated entry in the [Changelog](../CHANGELOG.md).
