# Research backlog

Status: active Stage 9A. Cycle 1 consolidation feasibility closed `not_evaluable`
because the locked matcher admitted no controls; see the [selection
record](research-candidates/2026-08-19-cycle-1.md) and [result](research-results/consolidation-support-feasibility-v1.md). Cycle 2 selected SMA Cross v1's
exposure-reduction claim, jointly designed against a volatility-state placebo;
see the [selection record](research-candidates/2026-08-19-cycle-2.md). Its
[locked protocol](research-protocols/sma-cross-v1-exposure-reduction.md) executed
and [closed](research-results/sma-cross-v1-exposure-reduction.md)
`not_material_or_not_consistent` — a real, properly-powered negative result: 0/12
assets survived Holm correction on both statistics, and a volatility-only placebo
matched or beat the SMA state's variance reduction on every asset. No follow-up
research task is queued; the next Stage 9A step, if any, is a new cycle.

## Resume gate

Before proposing another model, read [hypothesis engineering](hypothesis-engineering.md), [the model acceptance standard](model-acceptance-standard.md), [CTA v1 protocol](research-protocol.md), [result](research-results/cta-trend-wf-v1.md), [audit](research-results/cta-trend-wf-v1-audit.md), and [benchmark ADR](adr/0005-product-objective-and-portfolio-benchmark.md). Audit benchmark/universe suitability before scoring. CTA v1 is closed; do not optimize it retrospectively.

## Candidate research programmes

[Daily Consolidation Zone v1](research-hypotheses/daily-consolidation-zone-v1.md)
competed in the Cycle 1 Stage 9A scorecard. Support recovery—not breakout or failed
breakout—was prioritised for detector/event feasibility only. The detector was
structurally viable, but matching feasibility failed. This does not authorise a
strategy implementation or outcome calculation, and it does not reject the claim.

### CTA v2

Operationalized and scored in Cycle 2 as a pooled, volatility-scaled trend overlay
across the 12-ETF universe — see [Candidate C](research-candidates/2026-08-19-cycle-2.md). Eligible (score 13) but parked: its estimand needs a
multi-instrument pooled-portfolio weighting engine that exists nowhere in this
codebase today, and it overlaps materially with cross-sectional rotation and
volatility-managed exposure. Park is an infrastructure gate, not a data or
rationale gate; do not choose parameters until that engine is scoped and a
distinct, non-overlapping mechanism is confirmed.

### SMA cross, breakout, and momentum horizons

SMA cross was operationalized, scored, and prioritised in Cycle 2 as an
exposure-reduction claim, jointly designed against a volatility-state placebo —
see [Candidate A](research-candidates/2026-08-19-cycle-2.md). Its
[locked protocol](research-protocols/sma-cross-v1-exposure-reduction.md) is
closed `not_material_or_not_consistent`: the volatility-only placebo matched or
beat it on every asset, and no asset survived Holm correction on both statistics
at once — see the [result](research-results/sma-cross-v1-exposure-reduction.md).
A different window pair or a pooled/panel version would be a new, independently
justified attempt, not a repair of this one. Momentum
horizons was operationalized as ETF-12 cross-sectional relative-strength rotation
— see [Candidate D](research-candidates/2026-08-19-cycle-2.md) — eligible (score
13) but parked: its estimand needs panel/permutation statistical tooling this
codebase does not have (no `scipy`/`statsmodels` dependency, no panel-regression or
permutation-null machinery in `research.py`), and it overlaps with CTA v2's trend
family. Generic breakout is covered under Classical TA series below. UI
availability must never imply statistical approval.

### Classical TA series

`S/R Bounce` is the existing quantified classical-TA prototype: prior rolling support/resistance, support-test recovery entry, resistance target, and ATR-buffered stop. It may be charted and backtested but has no accepted edge claim.

`TA Breakout v1` was operationalized and scored in Cycle 2 — see [Candidate
E](research-candidates/2026-08-19-cycle-2.md). Not prioritised: lowest score of
its cycle (10), an explicit zero on diversification, and its own record concedes
that its distinguishing multi-touch-zone mechanic degenerates to a CTA v1 retest
once stripped out. Before any future implementation attempt, lock:

- resistance/support construction: rolling extremes versus confirmed pivots/zones, including pivot confirmation delay so no future bars leak into the signal;
- horizon and zone tolerance;
- breakout qualification: close penetration, time acceptance, volume/relative-strength filters, or none;
- initial stop: failed-breakout close, breakout-zone buffer, confirmed swing support, or ATR distance;
- trailing/target/timeout exit and gap treatment;
- parameter-search budget, benchmark, costs, multiplicity control, and untouched confirmation data.

No `NDO entry` marker is permitted until these choices define an executable rule. Descriptive support/resistance lines may be shown as chart context but must be labelled non-signal.

### Model selection and machine learning

ML is justified only if the sample, target, leakage controls, turnover/cost model, nested validation, feature stability, and interpretability constraints are specified first. It is not a substitute for an economic hypothesis, and unrestricted feature search increases false discovery risk.

## Required outputs for any new hypothesis

- pre-result candidate scorecard and selection record;
- immutable specification and fingerprint;
- point-in-time universe and data provenance;
- executable timing and portfolio contract;
- passive benchmark and decision threshold;
- train/validation/test separation with multiplicity control;
- sensitivity, regime, and cost stress tests;
- explicit `reject`, `revise`, or `continue` decision;
- durable artifact sufficient for independent reproduction.
