[Home](../README.md) · [Docs index](README.md) · [Roadmap](roadmap.md) · [Product](product.md) · [Research protocol](research-protocol.md) · [Changelog](../CHANGELOG.md)

# Validation roadmap

## Audit baseline (Codex review, 2026-08-17)

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

## Stage 0 — freeze the research baseline

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

## Stage 1 — one canonical execution model (highest priority)

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

## Stage 2 — automated correctness and data-quality tests

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

## Stage 3 — honest research statistics and benchmarks

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

## Stage 4 — out-of-sample research protocol

**Goal:** test hypotheses without advertising in-sample winners as proven edges.

- [x] Write the initial CTA hypothesis and acceptance metrics before any new
      parameter search ([research protocol](research-protocol.md)).
- [x] Divide data chronologically into training, validation, and untouched test
      periods.
- [x] Implement rolling walk-forward evaluation with parameters selected only
      from information available at that time.
- [ ] Reserve an untouched holdout universe and period.
- [x] Report parameter stability: no configuration survived any validation fold,
      so there is no selected-parameter series to plot and v1 is rejected.
- [x] Start an append-only attempt ledger, including the contaminated legacy
      14-configuration CTA tuning run and the preregistered 54-candidate run.
- [x] Apply the preregistered 20-bar bootstrap and Holm family-wise correction to
      all 54 candidates in every fold.
- [x] Limit claims to the 12 locked long-lived ETFs because point-in-time index
      membership is unavailable.
      long-lived broad ETFs to reduce survivorship bias.
- [x] Record regime results as not estimable: the locked selector held cash in
      every test fold, so post-hoc regime tuning would be misleading.

**Exit gate:** the final test set remains untouched until a written model is
locked, and results are reported even when they fail.

**Current checkpoint (v0.20.0):** the development experiment is complete and CTA
Trend v1 is rejected. No candidate survived any validation fold after Holm
correction; all 14 test folds held cash, producing zero trades and insufficient
evidence. The hidden 504-bar SPY tail was not evaluated and remains contaminated.
A revised strategy requires a new preregistered experiment; valid confirmation
still requires genuinely unseen future or uninspected point-in-time data.

## Stage 5 — portfolio and risk model

**Goal:** stop presenting independent fixed-share trades as a portfolio.

**Current checkpoint (v0.22.0):** the multi-symbol replay now uses one shared
cash ledger and exact shared calendar. It processes completed-close signals at
the next open, rechecks sizing and every cap after gaps, charges canonical costs,
holds sale proceeds until the next session, marks common-close equity and
concentration, and preserves final pending orders. The 15% drawdown kill switch
now records its trigger, blocks entries, and submits next-open liquidations while
retaining any gap loss. Daily account return, risk, concentration, turnover,
trade, rejection, and pending-state metrics are calculated without inventing an
undefined multi-asset benchmark. `/api/portfolio` locks the replay to 12 declared
ETFs and their operational sector/cluster labels, fails closed on missing or
mismatched calendars, and exposes the account contract. The Today view now shows
actual shared-account equity, risk metrics, positions, and dollar P&L. SMA Cross
and RSI Reversion are explicitly unavailable because they do not define the
protective stop required by risk sizing; no fallback stop is invented. The full
deterministic suite has 148 tests, and supported/refusal UI paths pass a headless
browser smoke check with no console errors.

- [x] Add explicit $100k account state and conservative validated defaults.
- [x] Add cost-aware stop-risk and maximum-notional entry sizing.
- [x] Add deterministic entry allocation, pending-cash reservation, and rejection
      records for cash, classification, concentration, duplicate, and halt gates.
- [x] Process multi-symbol next-open fills and exits against one cash ledger.
- [x] Mark all positions on a strict common daily calendar and record equity,
      exposure, concentration, peak, and drawdown.
- [x] Keep sale proceeds unavailable until the next shared-calendar session.
- [x] Trigger and execute next-open drawdown kill-switch liquidations, including
      final-bar pending state and gap-loss evidence.
- [x] Calculate portfolio-level return, volatility, turnover, and risk metrics.
- [x] Integrate tested portfolio results into the API and UI.

- [x] Replace the active UI's fixed 100-share convention with explicit capital
      and sizing. The legacy `/api/positions` route remains diagnostic only and
      is not rendered.
- [x] Add maximum position, sector, correlated-asset, and portfolio exposure.
- [x] Model concurrent signals, available cash, turnover, and rejected orders.
- [x] Separate per-trade stop distance from portfolio risk limits.
- [x] Add portfolio equity, drawdown, concentration, and daily return history.
- [x] Add a hard kill switch and maximum-loss controls for any future paper/live
      integration.
- [x] Keep this historical replay explicitly separate from future paper/live
      state: there is no broker connection or paper/live store, and the API/UI
      state that the replay does not authorize either.

**Exit gate:** no displayed dollar P&L can imply capital that the portfolio did
not actually have.

**Gate status:** passed for the active Today view at v0.22.0. Stage 5 does not
claim a validated edge and does not authorize paper or live trading.

## Stage 6 — operator clarity and safety language

**Goal:** make uncertainty, data state, and failures obvious before a user
interprets any research output.

**Current checkpoint (v0.23.0):** Data Management lists all 554 stored series
with explicit Yahoo/FRED ownership, coverage dates, row counts, expected latest
completed US weekday, and per-symbol freshness. Manual Yahoo refreshes run one
observable in-process job at a time, publish each validated symbol
transactionally, refresh full adjusted history, apply a non-configurable
two-second inter-symbol delay plus existing retry backoff, and expose progress
and failures. FRED series cannot enter Yahoo jobs. Today, Explorer, Lab, and
Macro now show freshness/date context, while Today distinguishes no signal from
coverage failures and carries a research-only warning. Symbol Explorer already
uses typeahead; Strategy Lab and Data Management now filter 500+ symbols by
typing. No real provider refresh was started during implementation or testing.

- [x] Show `data as of`, expected US session, fetch status, and stale/missing symbols
      beside every decision-oriented view.
- [x] Distinguish `no signal`, `not enough history`, `stale data`, and
      `calculation failed`.
- [ ] Show signal time, intended order time, assumed fill time, and actual
      simulation fill as separate fields.
- [x] Put the research-only warning and key bias/cost assumptions beside results,
      not only in documentation.
- [x] Add an explicit Data Management view with provider-separated inventory,
      manual refresh controls, progress, and per-symbol outcomes.
- [x] Add typeahead/filtering for large symbol collections instead of requiring
      users to scan hundreds of names.
- [ ] Replace hover-only explanations with keyboard/touch-accessible disclosures
      (parked behind the current data-integrity work).
- [ ] Add labels/ARIA, visible focus states, and accessible table/card alternatives
      (parked; still required before any broader external use).
- [ ] Complete the broad responsive-layout pass (parked; targeted overflow and
      large-list usability are handled in the current slice).
- [ ] Confirm destructive actions such as deleting saved parameter sets.
- [ ] Break the single frontend file into testable modules when doing so reduces
      risk rather than merely changing technology.
- [ ] Add Playwright smoke tests for Today, Explorer, Strategy Lab, Macro, error
      states, and narrow-screen layouts.

**Exit gate:** a new user can identify data freshness, assumptions, current
position state, and failure conditions without relying on a tooltip.

## Stage 7 — API and local security hardening

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

## Stage 8 — local strategy validation and product decision gate

**Goal:** decide locally whether a strategy is useful enough to continue before
automating or deploying it.

This stage is not “fine-tuning until the strategy wins.” Every attempt starts
with a written economic reason, fixed comparison rules, declared costs, a
limited set of permitted choices, and pass/fail thresholds. Failed and
uninteresting results are retained. CTA Trend v1 remains rejected and cannot be
rescued by changing its rules after seeing its result.

- [x] Choose the product goal before judging results: a research assistant, a
      lower-risk alternative, or a strategy intended to beat a benchmark. Do
      not switch goals after seeing performance. The accepted goal is a local
      research decision assistant ([ADR 0005](adr/0005-product-objective-and-portfolio-benchmark.md)).
- [x] Define the fair portfolio benchmark, its rebalancing rule, and treatment
      of idle cash before making any excess-return claim. Passive ETF-12 v1 is
      the primary comparator; SPY and cash are secondary references.
- [x] Independently audit the surprising CTA v1 experiment result before using
      it to design CTA v2. Reconcile one fold outside the runner and verify data
      boundaries, returns, costs, statistical direction, correction, and power
      ([audit result](research-results/cta-trend-wf-v1-audit.md)). No material
      defect was found; the rejection remains valid under its locked rules.
- [ ] Select one next hypothesis for an economic reason and write its rules and
      rejection criteria before running it.
- [ ] Freeze the investment universe, research periods, trading costs,
      execution assumptions, portfolio limits, and permitted parameter choices.
- [ ] Run repeatable local walk-forward experiments and retain every attempted
      setup and outcome, including failures.
- [ ] Judge net excess return, drawdown and recovery, capital use, turnover,
      number of independent trades, and stability across periods and assets—not
      headline return alone.
- [ ] Stress higher costs, worse fills, gaps, and small changes in assumptions;
      reject an advantage that disappears under reasonable conditions.
- [ ] Compare with buy-and-hold, cash yield, and the accepted portfolio
      benchmark on the same dates and capital basis.
- [ ] Record a `reject`, `revise`, or `continue` decision using the thresholds
      written before the result was known.
- [ ] Confirm that a non-programmer can understand the data used, the decision
      rule, the assumed trade timing, the risk taken, and why no action may be
      the correct result.
- [ ] If a candidate passes development, lock it for later observation on
      genuinely unseen data. Do not begin paper or live trading in this stage.

**Exit gate:** an independently readable decision record either rejects the
hypothesis or locks exactly one candidate for future unseen-data observation.
Working software or an attractive historical chart is not enough to pass.

## Stage 9 — reliable daily operation (parked; cron only after Stages 0–8)

**Goal:** make an unattended update observable, idempotent, and recoverable.

**Current status:** no crontab is installed for this user and `scripts/daily.sh`
is a guarded parked stub. Manual Data Management is not a substitute for the
staging, locks, persistent run history, alerts, and recovery controls below.

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

## Stage 10 — AWS deployment (last)

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

## Recommended implementation order

Work one small slice at a time:

1. Stage 0 test foundation.
2. CTA Trend canonical state machine and parity tests.
3. Apply the same engine to the remaining strategies.
4. Correct/rename confidence and benchmark statistics.
5. Build the walk-forward research notebook and protocol.
6. Add portfolio/risk semantics.
7. Complete the local safety work needed for honest experimentation; keep the
   broader external-use UX and security requirements recorded.
8. Run one hypothesis at a time through the local strategy-validation and
   product decision gate.
9. Complete every external-use UX and security gate, then revisit cron only if
   unattended operation still has a clear product purpose.
10. Revisit AWS only after cron is demonstrably reliable and deployment has a
    justified user need.

Adding new strategies, machine learning, broker integration, cron automation,
and AWS deployment is intentionally paused until the relevant gates above pass.
