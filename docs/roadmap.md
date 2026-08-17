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

## Stage 5 — portfolio and risk model

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

## Stage 6 — UX, accessibility, and safety language

**Goal:** make uncertainty and system state obvious to a beginner.

- [ ] Show `data as of`, market timezone, fetch status, and stale/missing symbols
      beside every decision-oriented view.
- [ ] Distinguish `no signal`, `not enough history`, `stale data`, and
      `calculation failed`.
- [ ] Show signal time, intended order time, assumed fill time, and actual
      simulation fill as separate fields.
- [ ] Put the research-only warning and key bias/cost assumptions beside results,
      not only in documentation.
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

## Stage 8 — reliable daily operation (cron only after Stages 0–7)

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

## Stage 9 — AWS deployment (last)

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
7. Complete UX and security gates.
8. Revisit cron only after the earlier gates pass.
9. Revisit AWS only after cron is demonstrably reliable.

Adding new strategies, machine learning, broker integration, cron automation,
and AWS deployment is intentionally paused until the relevant gates above pass.
