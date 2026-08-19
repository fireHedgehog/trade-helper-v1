# Roadmap

The roadmap is gate-based. Completion means evidence exists, not that code was written. Current checkpoint: `0.46.0`; Stage 8 is closed, Stage 9A Cycle 1 is closed `not_evaluable`, Cycle 2's chosen protocol (SMA Cross v1) is closed `not_material_or_not_consistent` on a confound (a volatility-only placebo explained it away), and Cycle 3's chosen protocol (RSI oversold reversal) is closed `not_material_or_not_consistent` on a power limitation (36–56 events per asset was not enough to distinguish signal from noise) — two completed, differently-shaped negative results.

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

Completed slices: `0.28.0` added multi-model Symbol Research accordions, readable guide/dossier hierarchy, explicit refresh semantics, and watchlist-snapshot recovery; `0.30.0` added bounded dataset and strategy metadata; `0.31.0` separated Strategy Lab evidence from its non-durable descriptive calculation; `0.32.0` persisted Data Management refresh identity/progress/outcomes; `0.33.0` made Macro display-only under ADR 0006; `0.34.0` added deterministic browser coverage of primary read-only and asynchronous states without external mutations. Stage 8C gate: complete.

Gate: browser smoke tests cover primary workflows and every asynchronous state; no page load triggers data or strategy computation.

### 8D — Durable local staging

Completed in `0.35.0`: read-only dependency preflight and deterministic input/model/scope fingerprints. Completed in `0.36.0`: confirmed durable execution through the existing refresh/snapshot paths, dependency re-planning after partial publication, persisted restart-visible state, and idempotent retry-by-replanning.

Completed in `0.37.0`: task-based ambiguity audit; explicit manual-vs-batch and portfolio boundaries; fixed provider-delay estimate; responsive primary views at 390 px; expanded deterministic browser regression and operating notes.

Acceptance repair in `0.37.1`: separate Yahoo market context from the equity/ETF strategy universe; asset-appropriate context validation; a disclosed 90% operational daily-discovery coverage floor; persisted exclusions. Formal research coverage remains protocol-specific. The repaired real run produced or reused all seven full-universe model snapshots with zero failed/blocked jobs. Version `0.38.0` adds visible per-job/run provenance, collapses infrequent controls, and closes the gate.

Anti-toy exit rule: after the layout/usability and smoke-test items above, stop Stage 8 infrastructure work and enter Stage 9A. Do not add dashboards, schedulers, providers, or strategy decoration merely because the pipeline can support them.

Gate: the repaired real workflow must complete with model snapshots or explain any remaining block correctly. The user must then explicitly accept it before 9A. This is not live-readiness approval.

## Stage 9: New strategy research — active

Resume only by explicit decision after Stage 8.

### 9A — Acceptance standard and candidate priority

Before selecting a strategy, operationalize each thesis under [hypothesis engineering](hypothesis-engineering.md), audit benchmark/universe suitability under ADR 0005, then apply the [model acceptance and candidate-priority standard](model-acceptance-standard.md). Score all serious candidates before viewing comparative results, preserve the complete selection record, and preregister model-specific evidence thresholds. Consolidation, CTA v2, momentum, breakout, SMA cross, and future ideas compete under the same process; none is the default next model.

Candidate search and promotion follow the [exploration protocol](exploration-protocol.md): search is non-evidential, logged in `research/attempts.jsonl`, and only promoted survivors enter 9A scoring. Macro candidates additionally require [ADR 0006](adr/0006-macro-data-contract.md) point-in-time data before scoring.

Gate: one candidate has earned priority on rationale, product relevance, distinct information, data readiness, implementability, falsifiability, research restraint, and diversification; its immutable protocol defines what will cause `reject`, `revise`, or `continue research`.

Cycle 1 selected [consolidation support recovery](research-candidates/2026-08-19-cycle-1.md) only for a bounded [detector/event-feasibility protocol](research-protocols/daily-consolidation-support-recovery-feasibility-v1.md). Its [result](research-results/consolidation-support-feasibility-v1.md) is `not_evaluable`: breadth and prevalence passed, but the locked matcher admitted zero controls for 274 events. Power and actual-event outcomes were correctly skipped. This does not reject the hypothesis.

Cycle 2 scored five new candidates before any result: [selection
record](research-candidates/2026-08-19-cycle-2.md). SMA Cross v1's
exposure-reduction claim was prioritised, jointly designed against a
volatility-state placebo (recast from Candidate B's raw operationalization into a
second self-referential trailing state, avoiding any new portfolio-weighting
engine) so the two are not scored as independent evidence of the same question.
CTA v2 and ETF-12 cross-sectional rotation are eligible but parked pending
infrastructure this codebase does not have — a pooled multi-instrument portfolio
engine and panel/permutation statistical tooling respectively — not pending data.
TA Breakout v1 was not prioritised. The chosen protocol was
[locked](research-protocols/sma-cross-v1-exposure-reduction.md), executed, and
[closed](research-results/sma-cross-v1-exposure-reduction.md)
`not_material_or_not_consistent`: 0/12 assets survived Holm correction on both
statistics at once, and the volatility-state placebo matched or beat the SMA
state's variance reduction on all 12 assets, directly triggering the
protocol's own falsifier. This is a real negative result on the specific
locked claim, not a blocked test. A materially different consolidation
matcher, a different SMA window, or a pooled/panel version of this same claim
may compete only as a new, independently justified protocol — none is a
default next task. Cycle 1 thresholds cannot be relaxed retrospectively.
Futures trend and cross-sectional equity momentum on the ~500-symbol list
remain parked until their point-in-time data path exists.

Cycle 3 scored two Tier 0/1 candidates from the [pending candidate
checklist](brainstorm/2026-08-19-pending-candidate-checklist.md): [selection
record](research-candidates/2026-08-19-cycle-3.md). RSI(14) oversold-crossing
short-horizon reversal scored `15/16`, the highest of any candidate so far,
and was prioritised as a genuinely different mechanism family (contrarian, not
trend) from every candidate tested to date. S/R Bounce formalization scored
`0` on distinct information — too close in shape to Cycle 1's already-closed
consolidation work — and was not prioritised. The chosen protocol was
[locked](research-protocols/rsi-oversold-reversal-v1.md), executed, and
[closed](research-results/rsi-oversold-reversal-v1.md)
`not_material_or_not_consistent`: 0/12 assets reached raw significance even
before Holm correction (smallest raw p `0.138`), and the placebo comparison
was genuinely mixed (`6/12` each way) rather than a clean sweep. This reads as
a power limitation at the available event count (`36`–`56` per asset), not a
confound explanation like Cycle 2's result — a materially different reading
that a future attempt must not blur into the same conclusion. No parameter,
cooldown, or horizon grid was run; any such change is a new, independently
justified protocol.

### 9B — Locked experiment and confirmation

Only after 9A, implement the finite experiment. Apply the preregistered suitable benchmark, estimand, universe, search budget, multiplicity control, validation topology, cost/risk stress, stability tests, and untouched confirmation data. Passing means eligible for the next validation stage, not safe or approved for trading. See [research-backlog.md](research-backlog.md).

This stage is deliberately business/research work, not parameter tuning. UI placeholders do not authorize model development.

## Stage 10: Unattended data operation — parked

Scheduling becomes eligible only after the Stage 8D pipeline is proven observable, throttled, idempotent, atomic, recoverable, and trustworthy. Cron or an equivalent scheduler is then only a timed trigger over the same manual pipeline: it waits for dependencies, skips current symbols and current model fingerprints, treats non-trading days as no-work outcomes, and retries only failed work. No scheduling-specific research logic is permitted.

## Stage 11: Deployment — parked

Cloud deployment becomes eligible only after local staging and security/operations review. Define authentication, secrets, network boundary, storage, backups, monitoring, cost controls, incident recovery, and explicit prohibition of broker connectivity unless separately approved.

## Global stop conditions

Stop and document rather than continue when data contracts fail, execution semantics diverge, evidence is contaminated, a result depends on retrospective tuning, UI wording overstates validation, or a change would silently alter a locked benchmark/protocol.
