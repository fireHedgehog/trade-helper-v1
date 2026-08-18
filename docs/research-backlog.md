[Home](../README.md) · [Docs index](README.md) · [Roadmap](roadmap.md) · [CTA v1 result](research-results/cta-trend-wf-v1.md)

# Parked research backlog

This file preserves research questions for a future session. It is not an
approved experiment, a parameter grid, or evidence that any proposed change will
work. A new model may begin only after the current priority gates are complete
and its hypothesis and rejection rules are preregistered.

## Completed: audit the surprising CTA v1 result

CTA Trend v1 remains rejected under its locked rules, but rejection assumes the
experiment implementation is correct. Before designing CTA v2, independently
audit the complete path from stored bars to the final decision:

- reproduce at least one candidate and fold outside the experiment runner;
- verify training, validation, test, warm-up, and contaminated-tail boundaries;
- prove that validation selection cannot read test or later bars;
- reconcile strategy and constant-exposure benchmark daily returns by date;
- verify commission, spread, slippage, cash yield, and open-trade treatment;
- check bootstrap centering, block construction, one-sided p-value direction,
  Holm correction, candidate-family completeness, and deterministic seeds;
- inspect raw effect sizes, trade counts, exposure, and symbol-level dispersion,
  not only adjusted p-values;
- distinguish “no measurable effect” from “too little statistical power”; and
- record any defect as a corrected v1 result without silently rewriting history.

**Status:** completed with no material defect found. The original rejection
remains valid under its locked rules. See the
[implementation audit](research-results/cta-trend-wf-v1-audit.md). Passive
ETF-12 v1 is now implemented; CTA v2 remains parked.

An audit that finds no defect increases confidence in the rejection but does not
prove the strategy has zero value. An audit that finds a material defect
invalidates the reported result and requires a versioned rerun under the original
rules.

## Possible CTA v2 research directions — parked

These are structural questions, not instructions to search until a backtest
wins:

- long/short trend exposure so persistent declines can be captured;
- volatility-scaled positions rather than equal nominal exposure;
- a broader set of genuinely different futures or forward markets, subject to
  reliable point-in-time data and contract-roll modeling;
- a small combination of predeclared fast, medium, and slow trend horizons;
- simpler signals or removal of filters that only reduce sample size;
- portfolio correlation and risk-budget allocation rather than overlapping ETF
  signals; and
- explicit comparison of absolute return, crisis behavior, and diversification
  objectives instead of changing the objective after results are seen.

Machine learning is parked further back. Daily data across 12 correlated ETFs
does not provide a large independent sample, while features, labels, model
classes, hyperparameters, and thresholds multiply researcher choices. ML should
not be introduced unless a later hypothesis explains why it is necessary, uses
appropriate point-in-time data, and budgets for the additional overfitting risk.

## Restart instructions

A future agent should not tune or implement CTA v2 immediately. Read the CTA v1
protocol and result, complete the independent v1 audit, implement the accepted
Passive ETF-12 benchmark, and then ask whether one of the parked structural
questions deserves a new preregistered experiment. CTA v1 remains a recorded
failed attempt; it must never be relabeled as successful by changing its gates.
