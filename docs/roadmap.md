# Roadmap

The roadmap is gate-based. Completion means evidence exists, not that code was written. Current checkpoint: `0.31.0`, Stage 8C in progress.

## Completed foundation

| Stages | Outcome |
|---|---|
| 0–3 | Repository, data, API, frontend, symbol research, and initial strategies established |
| 4 | Execution timing, data contracts, costs, and deterministic backtests corrected |
| 5 | Portfolio cash, capacity, settlement, sector/cluster limits, and drawdown halt implemented |
| 6 | Data freshness, explicit refresh, failure states, safety language, responsive baseline, and browser smoke coverage added |
| 7 | CTA v1 preregistered, executed, rejected, and independently audited; Passive ETF-12 v1 implemented |

Historical detail is retained in [CHANGELOG.md](../CHANGELOG.md), ADRs, and research results.

## Stage 8: Product research workspace

Purpose: make the validated state and research workflow usable without importing unvalidated legacy claims.

### 8A — State and workflow foundation: complete

- Persist user watchlists per strategy.
- Expose lifecycle state, last entry/exit, holding state, and evaluation session.
- Separate watchlists from full-universe entry candidates.
- Provide model tabs and intersections.
- Read persisted state on navigation; keep refresh/run as explicit actions.
- Version checkpoint `0.26.0`; verification `176 passed`.

### 8B — Semantic visual system and Today: complete

- Define semantic tokens for positive, negative, warning, stale, neutral, price, date, metric, and evidence strength.
- Replace debug labels with concise market language while preserving uncertainty.
- Use spacious hierarchy, readable type, coloured key numbers/phrases, and accessible redundant status cues.
- Rebuild Today as a command centre: freshness, refresh/run actions, watchlist lifecycle, candidates by model, intersections, warnings, and last-run provenance.
- Distinguish `not run`, `running`, `stale`, `no candidates`, `failed`, and `complete`.
- Add regression tests for state-to-copy and state-to-colour mappings.

Gate: a user can determine current data state, portfolio/watchlist state, candidate set, required action, and evidential status without reading implementation terminology.

Evidence: semantic CSS/state mapping, explicit four-step Today workflow, market-oriented table copy, responsive layout, three static contract tests, `179 passed`, and headless Playwright navigation/visual verification.

### 8C — Productise remaining surfaces: next

- Symbol Research: strategy accordions with summary, signal, risk, evidence, sector context, and comparable time horizons.
- Strategy Lab: explicit hypothesis/version, configuration, benchmark, run progress, results, rejection reasons, and artifacts.
- Data Management: coverage/freshness table, selected refresh, hard-coded provider delay, durable progress, retryable failures, and last successful update.
- Replace fixed data assumptions with the product-contract dataset registry: provenance, information class, schema, cadence, point-in-time/revision status, coverage, freshness, licence, quality, lineage, and fingerprint.
- Represent strategy families and typed parameters through versioned metadata rather than adding one UI column per future factor.
- Bring Macro presentation into ADR 0006 compliance: label current FRED observations as final-revised/display-only, distinguish observation from release time, remove causal `good/bad for equities` styling, and expose point-in-time capability as unavailable until implemented.
- Preserve empty placeholders for CTA, SMA cross, breakout, and momentum until each has an executed valid protocol.

Completed slices: `0.28.0` added multi-model Symbol Research accordions, readable guide/dossier hierarchy, explicit refresh semantics, and watchlist-snapshot recovery; `0.30.0` added bounded dataset and strategy metadata; `0.31.0` separates Strategy Lab definition/configuration/evidence from its non-durable descriptive calculation, preserves immutable decisions/artifacts, exposes calculation state and partial failures, and forbids silent default-basket substitution after an empty selection. Remaining: durable Data Management job presentation, Macro ADR 0006 presentation, and full asynchronous browser coverage.

Gate: browser smoke tests cover primary workflows and every asynchronous state; no page load triggers data or strategy computation.

### 8D — Durable local staging

- Persist active jobs and progress across reloads.
- Add recovery from interrupted refresh/run operations.
- Build one dependency-aware daily pipeline: freshness check → selective refresh → validation/promotion → fingerprint-selective strategy runs → persisted snapshot.
- Make manual completion and later scheduled invocation idempotent: current work is recorded as `skipped_current`; partial failures retry only failed dependencies.
- Validate desktop and narrow layouts.
- Conduct a task-based usability pass and resolve high-severity ambiguity.
- Update screenshots and operating notes only after behaviour stabilises.

Gate: the local product is reliable enough for repeated daily research use, with no implication of live readiness.

## Stage 9: New strategy research — parked

Resume only by explicit decision after Stage 8.

### 9A — Acceptance standard and candidate priority

Before selecting a strategy, operationalize each thesis under [hypothesis engineering](hypothesis-engineering.md), audit benchmark/universe suitability under ADR 0005, then apply the [model acceptance and candidate-priority standard](model-acceptance-standard.md). Score all serious candidates before viewing comparative results, preserve the complete selection record, and preregister model-specific evidence thresholds. Consolidation, CTA v2, momentum, breakout, SMA cross, and future ideas compete under the same process; none is the default next model.

Candidate search and promotion follow the [exploration protocol](exploration-protocol.md): search is non-evidential, logged in `research/attempts.jsonl`, and only promoted survivors enter 9A scoring. Macro candidates additionally require [ADR 0006](adr/0006-macro-data-contract.md) point-in-time data before scoring.

Gate: one candidate has earned priority on rationale, product relevance, distinct information, data readiness, implementability, falsifiability, research restraint, and diversification; its immutable protocol defines what will cause `reject`, `revise`, or `continue research`.

### 9B — Locked experiment and confirmation

Only after 9A, implement the finite experiment. Apply the preregistered suitable benchmark, estimand, universe, search budget, multiplicity control, validation topology, cost/risk stress, stability tests, and untouched confirmation data. Passing means eligible for the next validation stage, not safe or approved for trading. See [research-backlog.md](research-backlog.md).

This stage is deliberately business/research work, not parameter tuning. UI placeholders do not authorize model development.

## Stage 10: Unattended data operation — parked

Scheduling becomes eligible only after the Stage 8D pipeline is proven observable, throttled, idempotent, atomic, recoverable, and trustworthy. Cron or an equivalent scheduler is then only a timed trigger over the same manual pipeline: it waits for dependencies, skips current symbols and current model fingerprints, treats non-trading days as no-work outcomes, and retries only failed work. No scheduling-specific research logic is permitted.

## Stage 11: Deployment — parked

Cloud deployment becomes eligible only after local staging and security/operations review. Define authentication, secrets, network boundary, storage, backups, monitoring, cost controls, incident recovery, and explicit prohibition of broker connectivity unless separately approved.

## Global stop conditions

Stop and document rather than continue when data contracts fail, execution semantics diverge, evidence is contaminated, a result depends on retrospective tuning, UI wording overstates validation, or a change would silently alter a locked benchmark/protocol.
