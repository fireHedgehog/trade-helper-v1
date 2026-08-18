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
2. Construct the experiment calendar from SPY sessions beginning 2006-02-06,
   the latest inception date in the locked universe (DBC), and end it at the
   earliest latest-date available across all locked ETFs. This coverage-only
   boundary was recorded before candidate returns were calculated.
3. Use the earlier history for expanding walk-forward folds: 756 training bars,
   252 validation bars, and 252 test bars, stepping 252 bars at a time.
4. Parameter candidates may use only a fold's training and validation history.
   A fold's test results cannot change that fold's chosen parameters.
5. A valid final confirmation requires observations not previously inspected:
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

Selection is also locked before evaluation. A symbol is eligible only when its
stored history reaches the fold's training start and covers the validation
window; at least 8 of the 12 preregistered ETFs must be eligible. Each candidate
is measured on the intersection of those symbols' validation dates. The primary
score is the median across symbols of net strategy return minus the constant-
exposure benchmark return. A candidate must also pass the Holm-adjusted 0.05
gate. Ties prefer higher median Calmar, then less-severe median drawdown, then
lexicographic parameter JSON. If no candidate survives, the following test fold
holds cash; it does not promote the least-bad configuration.

The statistical primitives are implemented and deterministic. They center each
candidate's excess-return series under a zero-mean null, resample contiguous
blocks with circular wrapping, use an add-one p-value correction, and apply Holm
across the complete candidate family. They have not yet been run on candidate
performance; fold-local parameter selection remains the next gate.

Fold-local return construction is now implemented separately from selection. A
window receives the complete earlier history needed for indicators and existing
position state, but bars after its declared end are removed before signals are
constructed. Net strategy returns, constant-exposure benchmark returns, and
their daily arithmetic difference use identical dates. Regression tests prove
that modifying later bars cannot change an earlier window. Candidate ranking and
fold-local parameter selection were initially disabled at that checkpoint.

The selection layer is implemented and has run on the locked development data.
It reports every excluded locked symbol, refuses to proceed below the
eight-symbol coverage gate, requires the complete declared candidate family,
aligns eligible symbols on their common dates, applies the bootstrap/Holm gate,
and executes the locked tie breakers. An empty survivor set returns an explicit
cash decision. In the completed run, no candidate survived any validation fold;
the version was rejected and all following test folds held cash.

A pre-run coverage check found that only five locked ETFs were stored locally;
the seven missing preregistered histories were fetched without substitution.
Their inception metadata exposed an invalid 1993 SPY anchor that would have
excluded later ETF launches forever. The common calendar was therefore locked to
2006-02-06 before inspecting candidate returns. This is recorded as a protocol
amendment rather than silently rewritten.

The experiment runner is resumable. Its cache path includes a SHA-256 fingerprint
of the complete specification and every locked OHLCV series, so changed data or
protocol settings cannot silently reuse old candidates. Candidate files and the
evidence record are replaced atomically, and incomplete smoke runs are labeled
incomplete. The runner itself was checkpointed before execution.

## Current boundary

The development experiment and immutable result record are complete; see the
[CTA Trend v1 result](research-results/cta-trend-wf-v1.md). The historical SPY
tail remains contaminated because prior inspection cannot be undone. Because
the all-cash selection was surprising, the next research task is the independent
implementation audit recorded in the [research backlog](research-backlog.md),
not a new parameter search.
