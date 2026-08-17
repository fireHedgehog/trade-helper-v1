[Home](../README.md) · [Docs index](README.md) · [Roadmap](roadmap.md) · [Product](product.md) · [Research protocol](research-protocol.md) · [Changelog](../CHANGELOG.md)

# Out-of-sample research protocol

Status: Stage 4 foundation; **no valid historical final holdout currently exists**.

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

1. Hide the latest 504 available trading bars (about two years) as a candidate
   holdout solely to rehearse the workflow. It is contaminated: earlier versions
   tuned and displayed full-history SPY results, and therefore already exposed
   this period. It cannot support a confirmatory claim.
2. Use the earlier history for expanding walk-forward folds: 756 training bars,
   252 validation bars, and 252 test bars, stepping 252 bars at a time.
3. Parameter candidates may use only a fold's training and validation history.
   A fold's test results cannot change that fold's chosen parameters.
4. A valid final confirmation requires observations not previously inspected:
   prospectively collected bars after the model commit is locked, or a genuinely
   unexamined point-in-time universe. The contaminated tail remains useful only
   for engineering tests and clearly labeled exploratory estimates.

## Universe and bias controls

The first experiment will use broad, long-lived ETFs with adequate stored
history, chosen before results are calculated. Current index constituents and
individual winners are excluded from the primary claim because point-in-time
membership is unavailable. This reduces but does not eliminate survivorship and
selection bias. Symbols missing required history are reported, never replaced
after seeing results.

## Parameter search and multiple testing

The locked experiment record contains 54 candidates and 12 long-lived ETFs.
Every candidate and every later revision increments the attempt ledger, including
failed and abandoned ideas; the earlier 14-configuration tuning run is recorded
as contaminated exploratory work. Parameter-stability tables must be shown; an
isolated optimum is rejected.

Each candidate's validation excess daily returns will use a one-sided circular
moving-block bootstrap (20-bar blocks, 5,000 deterministic resamples). The 54
raw p-values will receive a Holm family-wise-error correction at alpha 0.05.
This controls the declared family but not the unrecorded human choices that led
to it, which is why prospective confirmation remains necessary.

The statistical primitives are implemented and deterministic. They center each
candidate's excess-return series under a zero-mean null, resample contiguous
blocks with circular wrapping, use an add-one p-value correction, and apply Holm
across the complete candidate family. They have not yet been run on candidate
performance; fold-local return construction and selection remain the next gate.

## Current boundary

The checked-in notebook creates a candidate-tail partition and walk-forward
manifest only. It intentionally does not evaluate returns or select a winner.
The finite grid, attempt ledger, and multiple-testing treatment are now locked.
The next implementation slice must implement and test the block bootstrap,
fold-local selection, stability report, and immutable result record. Even after
that work, the historical SPY tail remains exploratory because prior inspection
cannot be undone.
