# Research backlog

Status: parked until Stage 8 product work is complete and the user explicitly resumes heavy statistical research.

## Resume gate

Before proposing another model, read [hypothesis engineering](hypothesis-engineering.md), [the model acceptance standard](model-acceptance-standard.md), [CTA v1 protocol](research-protocol.md), [result](research-results/cta-trend-wf-v1.md), [audit](research-results/cta-trend-wf-v1-audit.md), and [benchmark ADR](adr/0005-product-objective-and-portfolio-benchmark.md). Audit benchmark/universe suitability before scoring. CTA v1 is closed; do not optimize it retrospectively.

## Candidate research programmes

[Daily Consolidation Zone v1](research-hypotheses/daily-consolidation-zone-v1.md) is a preserved design draft, not the next-design priority. It must compete with every other candidate under Stage 9A before implementation.

### CTA v2

Define a new economic hypothesis before choosing parameters. Candidate changes may include diversified trend horizons, volatility scaling, cross-asset allocation, alternative exits, or explicit regime conditioning. For every change specify causal rationale, expected failure mode, benchmark, estimand, search budget, multiplicity control, stability tests, and untouched confirmation data.

### SMA cross, breakout, and momentum horizons

These are product placeholders, not validated strategies. Each requires an independent protocol. Momentum may compare short/mid/long horizons; breakout may study channel definitions and volatility filters; SMA cross must distinguish exposure reduction from excess-return claims. UI availability must never imply statistical approval.

### Classical TA series

`S/R Bounce` is the existing quantified classical-TA prototype: prior rolling support/resistance, support-test recovery entry, resistance target, and ATR-buffered stop. It may be charted and backtested but has no accepted edge claim.

`TA Breakout v1` is a parked, distinct hypothesis for a short local resistance zone followed by a completed-close breakout and next-available-open entry. Before implementation, lock:

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
