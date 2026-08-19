# Roadmap

The roadmap is gate-based. Completion means evidence exists, not that code was written. Current checkpoint: `0.55.0`; Stage 8 is closed, Stage 9A Cycle 1 is closed `not_evaluable`, and nine completed protocols are each closed `not_material_or_not_consistent` for nine different reasons: SMA Cross v1 (Cycle 2) on a confound, RSI oversold reversal (Cycle 3) on a power limitation, TA Breakout v1 on weak event/placebo separation by construction, Wave Pull v1 (Cycle 4) on a clean but null result, ETF-12 cross-sectional rotation v1 on a clean, decisive null with no caveat, Calendar Turn-of-Month v1 (Cycle 5) on a well-powered null in the first non-technical-pattern mechanism tested, Calendar Day-of-Week v1 (Cycle 5) on a well-powered null with a directionally consistent but statistically unconfirmed tilt, Overnight Gap Continuation v1 (Cycle 5) on the session's most decisive negative — every asset opposite-signed from the hypothesis — after a new joint-paired resampling design passed independent adversarial pre-lock code review, and CTA v2 (Cycle 2's Candidate C, picked up 2026-08-20) on materiality clearing but significance and a paired placebo test both failing, with the positive point estimate materially dependent on 2008. The cheap tier of the pending checklist is exhausted, one Tier 2 item is closed, and CTA v2 — the properly-powered pooled retest of CTA v1's own founding thesis — is closed.

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
found nothing.

An independent, adversarially verified next-priority evaluation (2026-08-20)
then scored five options for what to do next — building CTA v2's engine,
redesigning S/R Bounce, investing in Fed-put macro data infrastructure,
searching for genuinely new cheap candidates, or a structural retrospective
— and surfaced [Cycle 5](research-candidates/2026-08-20-cycle-5.md): the
first time-based, non-price-derived mechanism family this session. Turn-of-
month calendar effect (Lakonishok and Smidt 1988's window) scored `15/16`,
tied with RSI for the highest of any candidate this session, and used a
genuinely simpler bootstrap variant — the event mask is calendar-fixed and
computed once, not recomputed on each resampled synthetic path, since
calendar membership carries no price dependence or look-ahead risk. Executed
and [closed](research-results/calendar-turn-of-month-v1.md)
`not_material_or_not_consistent`: `987`-`1,612` turn-of-month days per asset
ruled out a power limitation, and a locked, non-gating volatility diagnostic
ruled out SMA Cross v1's confound story, but the daily differential was
small and inconsistent (`7`/`12` assets positive, `4`/`12` negative). `EEM`
reached raw `p=0.013` — the strongest single-asset raw significance this
session — but its Holm-adjusted `p=0.156` did not survive correction across
the `12`-asset family. Day-of-week (scored `12/16`) and overnight-gap
conditioning (scored `13/16`, but not implementable without a new
joint-resampling design step) remain eligible, unexecuted Cycle 5
candidates. The evaluation also corrected two prior claims: CTA v2's true
engineering cost is lower than previously stated (adjacent live-portfolio
infrastructure exists but isn't directly reusable), and a genuinely distinct
S/R Bounce construction (round-number price levels) is now known but blocked
on an adjusted-vs-nominal-price data gap under ADR 0002.

Day-of-week (Candidate B, `12/16`) was then picked up directly from the same
selection record — no new cycle minted, the same precedent as TA Breakout
v1 — testing Monday's underperformance claim (French 1980) only, not a
five-way weekday scan, to avoid a new multiple-comparisons dimension. Its
[locked protocol](research-protocols/calendar-day-of-week-v1.md) reused
Turn-of-Month v1's generic statistics functions unchanged, flipping only the
event mask and the test direction (negative, matching the actual literature
claim). Executed and
[closed](research-results/calendar-day-of-week-v1.md)
`not_material_or_not_consistent`: `969`-`1,588` Mondays per asset ruled out
a power limitation; `0`/`12` cleared materiality and Holm-corrected
significance together. Unlike turn-of-month's near-even split, the
direction was notably consistent (`9`/`12` assets negative, matching the
literature's predicted sign), and `DBC` reached raw `p=0.048` — the only
raw-significant single-asset result at the conventional `0.05` threshold
across both calendar experiments — but Holm correction (`p=0.578`) erased
it. A locked, non-gating diagnostic also found `8`/`12` assets have modestly
higher realized volatility on Mondays, disclosed but not further
interpreted.

Overnight-gap conditioning (Candidate C, `13/16`) was picked up last. Its
required joint-paired resampling design (same block-index sequence applied
to both the overnight and intraday return components at once, preserving
their real day-to-day pairing — the same principle rotation used across
assets, applied here across return components within one asset) was
completed, then put through independent adversarial pre-lock code review —
three lenses, three agents, zero shared context — before any market data
was touched. That review found six real, well-verified issues (none
catastrophic): a threshold-calibration asymmetry between the two
components, a placebo gate with no real statistical backing, signed-pooling
that could mask a directionally asymmetric effect, a missing test the
protocol's own checklist required, a degenerate all-tied-values threshold
collapse, and unguarded NaN/Inf propagation from bad prices — all fixed
before the specification hash was computed. Executed and
[closed](research-results/overnight-gap-continuation-v1.md)
`not_material_or_not_consistent`: the most decisive negative of the
session — `12`/`12` assets showed a *negative* signed forward return, the
opposite sign from the continuation hypothesis. The strengthened placebo
significance gate added during review correctly rejected `3` assets that
would have trivially passed the bare point-estimate comparison every prior
candidate used, directly validating the review's own concern. A disclosed,
non-gating diagnostic suggests a reversal-shaped pattern instead (down-gaps
tend to bounce back), which this protocol was not designed to test and
cannot claim. This closes Cycle 5 in full. The next step remains a
deliberate choice, not a default continuation.

An independent, solo-but-adversarially-self-checked next-priority evaluation
(2026-08-20) scored the remaining live options — CTA v2's engine, the
Fed-put macro data investment, a reversal-framed overnight-gap follow-up,
and a fresh candidate search — against the model-acceptance scorecard and
surfaced CTA v2, contrary to this session's own earlier shorthand that its
rationale was "pre-undermined" by the 2026-08-19 audit. Re-reading that
audit's actual finding (CTA v1's design was underpowered, not its thesis
false) showed CTA v2's own estimand — one pooled test across all 12
instruments and the full sample instead of 54 independent per-fold
candidates — exists specifically to fix that power problem, reinforcing
channel 1 rather than undermining it; channel 2 (vol-scaled de-risking) was
retained only as the already-required shared placebo, given SMA Cross v1's
confound finding. Picked up directly from
[Cycle 2](research-candidates/2026-08-19-cycle-2.md#update-2026-08-20-candidate-c-cta-v2-picked-up-directly)
without minting a new cycle. Its
[locked protocol](research-protocols/cta-v2-pooled-trend-overlay.md) needed
no new bootstrap machinery — the pooled excess-return series is
structurally identical in shape to CTA v1's own per-symbol statistic, so
`circular_block_bootstrap_p_value` and `holm_adjust` are reused unchanged —
and strengthened its placebo gate from a bare point-estimate comparison to
a paired significance test, the same fix Overnight-Gap's pre-lock review
already proved necessary. Executed and
[closed](research-results/cta-v2-pooled-trend-overlay.md)
`not_material_or_not_consistent`: the primary variant (`SMA_252`) cleared
materiality (`+2.18pp` annualized) and beat both the benchmark and the
required placebo on point estimate, with all three lookback variants
positive-signed, but failed Holm-corrected significance (`p=0.692`) and the
paired placebo test (`p=0.116`); a disclosed, non-gating diagnostic found
the positive point estimate depends materially on 2008. This is a properly
powered, informative null on CTA v1's own founding thesis — closing the
power-limitation gap the audit found, not a repair of CTA v1 itself. Fed
put is the clear #2 priority for the step after this; both a reversal-framed
overnight-gap follow-up and a fresh candidate search remain open but
unscheduled.

### 9B — Locked experiment and confirmation

Only after 9A, implement the finite experiment. Apply the preregistered suitable benchmark, estimand, universe, search budget, multiplicity control, validation topology, cost/risk stress, stability tests, and untouched confirmation data. Passing means eligible for the next validation stage, not safe or approved for trading. See [research-backlog.md](research-backlog.md).

This stage is deliberately business/research work, not parameter tuning. UI placeholders do not authorize model development.

## Stage 10: Unattended data operation — parked

Scheduling becomes eligible only after the Stage 8D pipeline is proven observable, throttled, idempotent, atomic, recoverable, and trustworthy. Cron or an equivalent scheduler is then only a timed trigger over the same manual pipeline: it waits for dependencies, skips current symbols and current model fingerprints, treats non-trading days as no-work outcomes, and retries only failed work. No scheduling-specific research logic is permitted.

## Stage 11: Deployment — parked

Cloud deployment becomes eligible only after local staging and security/operations review. Define authentication, secrets, network boundary, storage, backups, monitoring, cost controls, incident recovery, and explicit prohibition of broker connectivity unless separately approved.

## Global stop conditions

Stop and document rather than continue when data contracts fail, execution semantics diverge, evidence is contaminated, a result depends on retrospective tuning, UI wording overstates validation, or a change would silently alter a locked benchmark/protocol.
