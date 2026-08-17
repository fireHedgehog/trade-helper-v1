# Out-of-sample research protocol

Status: Stage 4 foundation; no final holdout result has been inspected.

## Question locked before testing

For the long-only CTA Trend rules already implemented, can parameters chosen
without future data produce a repeatable **net risk-adjusted benefit** versus a
constant-exposure benchmark across broad, long-lived ETFs?

This does not ask whether a tuned chart looks attractive. It asks whether a
predefined process survives later data after commissions, spread, and slippage.

## Primary hypothesis and rejection rule

- Primary metric: median out-of-sample fold return minus the constant-exposure
  benchmark return, net of the default cost assumptions in ADR 0003.
- Stability gate: positive excess return in at least 60% of out-of-sample folds.
- Risk gates: positive median Calmar ratio and no pooled drawdown worse than 25%.
- Evidence gate: at least 30 closed out-of-sample trades across the preregistered
  research universe. Fewer observations means **insufficient evidence**, not a
  pass or a promising near miss.
- Rejection: failure of any gate rejects this version of the hypothesis. The
  result must still be recorded; thresholds cannot be changed after inspection.

These thresholds are research choices, not laws of finance. Any revision creates
a new named experiment and counts as another attempted specification.

## Data boundaries

1. Reserve the latest 504 available trading bars (about two years) as the final
   holdout. Code exposes only its dates and count during development.
2. Use the earlier history for expanding walk-forward folds: 756 training bars,
   252 validation bars, and 252 test bars, stepping 252 bars at a time.
3. Parameter candidates may use only a fold's training and validation history.
   A fold's test results cannot change that fold's chosen parameters.
4. The final holdout remains unopened until the hypothesis, universe, parameter
   grid, costs, metrics, and code commit are locked.

## Universe and bias controls

The first experiment will use broad, long-lived ETFs with adequate stored
history, chosen before results are calculated. Current index constituents and
individual winners are excluded from the primary claim because point-in-time
membership is unavailable. This reduces but does not eliminate survivorship and
selection bias. Symbols missing required history are reported, never replaced
after seeing results.

## Parameter search and multiple testing

The complete finite grid and its size must be written into the experiment record
before evaluation. Every candidate and every later revision increments the
attempt ledger, including failed and abandoned ideas. Parameter-stability tables
must be shown; an isolated optimum is rejected. A multiple-comparison adjustment
will be selected before performance evaluation is implemented. Until that choice
is recorded, the notebook may inspect partitions but must not rank parameters.

## Current boundary

The checked-in notebook creates the holdout reservation and walk-forward
manifest only. It intentionally does not evaluate returns or select a winner.
This is a safety feature: the next implementation slice must define the attempt
ledger, finite grid, selection score, and multiple-testing treatment first.
