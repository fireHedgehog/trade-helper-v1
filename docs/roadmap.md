# Roadmap

The roadmap is gate-based. Completion means evidence exists, not that code was written. Current checkpoint: `0.50.0`; Stage 8 is closed, Stage 9A Cycle 1 is closed `not_evaluable`, and five completed protocols are each closed `not_material_or_not_consistent` for five different reasons: SMA Cross v1 (Cycle 2) on a confound, RSI oversold reversal (Cycle 3) on a power limitation, TA Breakout v1 on weak event/placebo separation by construction, Wave Pull v1 (Cycle 4) on a clean but null result, and ETF-12 cross-sectional rotation v1 on a clean, decisive null with no caveat — the cheap tier of the pending checklist is exhausted and one Tier 2 item is closed.

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

TA Breakout v1 (Cycle 2's Candidate E, scored `10/16`, never disqualified)
was picked up next from the checklist: its
[protocol](research-protocols/ta-breakout-v1.md) locked a close-price-only
rejected-resistance breakout against the exact placebo Cycle 2's own
verification named — a raw new-high breakout with no rejection requirement —
reusing RSI's proven event-recomputing bootstrap rather than Cycle 1's
caliper-matching design. Executed and
[closed](research-results/ta-breakout-v1.md) `not_material_or_not_consistent`:
`0/12` assets reached raw significance despite `1,477` events, far more than
RSI's `508`. The result also discloses a design weakness rather than hiding
it — the `≥2`-rejection filter barely separated event from placebo on any
asset, so the placebo comparison here is weaker evidence than SMA Cross v1's
clean sweep or RSI's genuinely mixed split. MACD and full Elliott Wave
counting were assessed against the checklist and not recommended: MACD is
mechanically the same shape as SMA Cross v1 and would very likely reproduce
its exact confound; Elliott Wave counting is not objectively definable
without discretionary judgment, in tension with this project's falsifiability
requirement — the existing `WavePull` prototype remains the honest,
already-scoped stand-in, currently blocked by a known bug.

`WavePull`'s `IndexError` was fixed in `0.48.0`, unblocking it; Cycle 4
scored it (`13/16`) as impulse-pullback continuation and prioritised it —
[selection record](research-candidates/2026-08-19-cycle-4.md). Its
[protocol](research-protocols/wave-pull-v1.md) locked a close-price-only
impulse-then-breakout event against a plain-breakout placebo stripping the
impulse precondition, reusing the same event-recomputing bootstrap a third
time. Executed and [closed](research-results/wave-pull-v1.md)
`not_material_or_not_consistent`: `IEF` had zero qualifying events
(disclosed, anticipated in the protocol's own risk section); `0/11` eligible
assets survived Holm correction. Unlike TA Breakout, the event/placebo
separation was clean (events ran `5`–`20×` fewer than placebo occurrences).
`TLT` reached raw `p=0.032` — the closest any single asset has come to raw
significance across all four experiments this session — but failed
correction on only `20` events, and several equity assets showed a
negative-direction effect, disclosed rather than omitted. This closes every
Tier 0/1 item on the pending checklist.

ETF-12 cross-sectional rotation (Cycle 2's Candidate D, scored `13/16`,
parked pending statistics infrastructure) was picked up next: its
[protocol](research-protocols/etf12-cross-sectional-rotation-v1.md) resolved
the infrastructure gap by redesign rather than a new dependency — Spearman
rank correlation instead of a panel regression, and a joint-panel
block-resampling null (the same resampled calendar-time blocks applied to
all 12 assets simultaneously) instead of per-asset cluster residualization,
which would have been degenerate for the four singleton-cluster assets
(`TLT`, `IEF`, `GLD`, `DBC`). Executed and
[closed](research-results/etf12-cross-sectional-rotation-v1.md)
`not_material_or_not_consistent`: pooled rank correlation `0.045` against a
locked `0.10` floor, `p=0.266` across `253` rebalance dates — the cleanest
negative of the session's five experiments, with no confound, power
limitation, or design weakness attached. Cluster breadth passed cleanly
(`6/6`), so the null is not a concentration artifact. This closes the last
Tier 0/1/2-ready item on the pending checklist; CTA v2's overlap concern
with rotation is now moot in the other direction, since rotation ran and
found nothing. The next step is a deliberate choice, not a default
continuation.

### 9B — Locked experiment and confirmation

Only after 9A, implement the finite experiment. Apply the preregistered suitable benchmark, estimand, universe, search budget, multiplicity control, validation topology, cost/risk stress, stability tests, and untouched confirmation data. Passing means eligible for the next validation stage, not safe or approved for trading. See [research-backlog.md](research-backlog.md).

This stage is deliberately business/research work, not parameter tuning. UI placeholders do not authorize model development.

## Stage 10: Unattended data operation — parked

Scheduling becomes eligible only after the Stage 8D pipeline is proven observable, throttled, idempotent, atomic, recoverable, and trustworthy. Cron or an equivalent scheduler is then only a timed trigger over the same manual pipeline: it waits for dependencies, skips current symbols and current model fingerprints, treats non-trading days as no-work outcomes, and retries only failed work. No scheduling-specific research logic is permitted.

## Stage 11: Deployment — parked

Cloud deployment becomes eligible only after local staging and security/operations review. Define authentication, secrets, network boundary, storage, backups, monitoring, cost controls, incident recovery, and explicit prohibition of broker connectivity unless separately approved.

## Global stop conditions

Stop and document rather than continue when data contracts fail, execution semantics diverge, evidence is contaminated, a result depends on retrospective tuning, UI wording overstates validation, or a change would silently alter a locked benchmark/protocol.
