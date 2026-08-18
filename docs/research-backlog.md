# Research backlog

Status: parked until Stage 8 product work is complete and the user explicitly resumes heavy statistical research.

## Resume gate

Before proposing another model, read [the CTA v1 protocol](research-protocol.md), [result](research-results/cta-trend-wf-v1.md), [audit](research-results/cta-trend-wf-v1-audit.md), and [benchmark ADR](adr/0005-product-objective-and-portfolio-benchmark.md). CTA v1 is closed; do not optimize it retrospectively.

## Candidate research programmes

### CTA v2

Define a new economic hypothesis before choosing parameters. Candidate changes may include diversified trend horizons, volatility scaling, cross-asset allocation, alternative exits, or explicit regime conditioning. For every change specify causal rationale, expected failure mode, benchmark, estimand, search budget, multiplicity control, stability tests, and untouched confirmation data.

### SMA cross, breakout, and momentum horizons

These are product placeholders, not validated strategies. Each requires an independent protocol. Momentum may compare short/mid/long horizons; breakout may study channel definitions and volatility filters; SMA cross must distinguish exposure reduction from excess-return claims. UI availability must never imply statistical approval.

### Model selection and machine learning

ML is justified only if the sample, target, leakage controls, turnover/cost model, nested validation, feature stability, and interpretability constraints are specified first. It is not a substitute for an economic hypothesis, and unrestricted feature search increases false discovery risk.

## Required outputs for any new hypothesis

- immutable specification and fingerprint;
- point-in-time universe and data provenance;
- executable timing and portfolio contract;
- passive benchmark and decision threshold;
- train/validation/test separation with multiplicity control;
- sensitivity, regime, and cost stress tests;
- explicit `reject`, `revise`, or `continue` decision;
- durable artifact sufficient for independent reproduction.
