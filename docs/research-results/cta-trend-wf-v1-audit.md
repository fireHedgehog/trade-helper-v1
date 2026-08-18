[Home](../../README.md) · [Docs index](../README.md) · [Protocol](../research-protocol.md) · [Original result](cta-trend-wf-v1.md) · [Evidence](../../output/research/cta-trend-wf-v1.json)

# CTA Trend walk-forward v1: independent implementation audit

- Audit date: 2026-08-18
- Decision: no material implementation defect found
- Original result: remains rejected for insufficient validated evidence
- Evidence fingerprint: `40a79707811b6d13f92fa88a87a9e5251a72d0d5ffa58a2709e027f7bbc0bafd`

## Why this audit was necessary

CTA Trend v1 selected cash in every fold, which was surprising given the use of
simple trend-following ideas by institutional managers. A surprising result is
not itself a defect, but it should not be trusted merely because tests run. This
audit therefore treated the recorded result as untrusted and checked the path
from stored bars to the rejection decision before any CTA v2 work.

## Checks performed

### Evidence and data identity

- Recomputed the specification-and-data SHA-256 fingerprint from the current
  locked JSON specification and all six OHLCV columns for all 12 ETFs.
- The recomputed fingerprint exactly matched the committed evidence.
- Verified 54 candidate cache records for each of 14 folds: 756 complete
  candidate/fold evaluations.
- Ran the complete experiment again from the fingerprinted cache. The generated
  evidence file was byte-for-byte identical to the committed result, including
  SHA-256 `d82a251e6abcab363667b543ab2dabc5e70ae3fe62294ec597896e828c61f2e8`.

### Independent fold reconciliation

Fold 14's strongest raw candidate was independently reconstructed outside the
experiment runner:

```text
n_entry=100, n_exit=40, trend_ma=200,
atr_period=14, atr_mult=3.0, no take-profit
validation: 2022-02-10 through 2023-02-10
```

For each ETF, the audit loaded bars only through the declared validation end,
ran the canonical simulator directly, independently merged account and asset
returns by date, applied the exposure-matched benchmark, and then aggregated the
12 common series. It matched the cache exactly:

- 252 daily observations with identical first and last dates;
- maximum absolute difference across all daily excess returns: `0.0`;
- mean daily excess return: `0.0000662497895997702`;
- median cumulative symbol excess return: `0.0`; and
- eight closed trades across the 12 independent symbol simulations.

The positive mean is approximately 1.67% when arithmetically annualized, but it
was small relative to its block-resampled uncertainty and was not broad across
symbols. Several symbols had no exposure or no completed validation trade.

### Statistical calculation

- Independently reconstructed the one-sided, centered, 20-bar circular block
  bootstrap for the fold-14 candidate using its locked deterministic seed.
- Reproduced raw `p = 0.2513497300539892` exactly.
- The bootstrap null standard deviation of the daily mean was approximately
  `0.00010586`, larger than the observed `0.00006625` mean.
- Independently reconstructed the Holm step-down adjustment for all 54 fold-14
  p-values. Maximum difference from the stored adjusted values was `0.0`; the
  minimum adjusted p-value was `1.0`.
- Confirmed the one-sided direction is correct: only sufficiently positive mean
  excess return can produce a small p-value.

### Cross-fold effect and sample inspection

The lack of survivors was not caused solely by converting a near-significant raw
p-value into a failed Holm result:

- best raw p-value in any fold: approximately `0.251`;
- 10 of 14 folds: every one of the 54 candidate mean excess returns was
  non-positive;
- fold 2: only one candidate had a positive mean;
- folds 4, 12, and 14: 10, 54, and 31 candidates respectively had positive means,
  but the effects were too noisy to pass even the raw 0.05 gate;
- median candidate validation exposure ranged from approximately 6% to 62%; and
- median closed trades per candidate/fold ranged from 8 to 36 across all 12
  symbol simulations.

The full deterministic application suite also passed: 164 tests.

## Finding

No material error was found in the data fingerprint, fold boundaries, future-bar
cutoff, date alignment, cost-bearing strategy returns, exposure-matched
benchmark arithmetic, candidate-family completeness, bootstrap direction, seed,
or Holm correction. The original rejection remains the correct decision under
the preregistered rules.

This does **not** establish that trend following is irrelevant or has zero true
effect. It establishes that this long-only, 12-ETF CTA v1 implementation did not
produce enough repeatable validation evidence under this experiment.

## Important design and power limitations

- Institutional CTA programs commonly trade long and short across many futures
  and currency markets; CTA v1 is a materially narrower long-only ETF model.
- One-year validation windows, sparse trades, correlated ETFs, and a 54-member
  candidate family limit statistical power.
- The 54 parameter candidates are highly related. Holm is conservative but was
  preregistered; changing correction after seeing results would invalidate the
  decision rule.
- The constant-exposure benchmark is an ex-post analytical control, not the new
  investable Passive ETF-12 portfolio benchmark.
- The audit reused the already tested canonical execution engine. It independently
  reconstructed aggregation and statistics, but it was not a second trading
  engine written from scratch.

These limitations support careful wording—“insufficient validated evidence”—not
promotion of the best failed candidate and not a claim that all CTA strategies
underperform.

## Next decision

CTA v2 and machine learning remain parked. The next implementation priority is
Passive ETF-12 v1 so later portfolio research has the accepted investable
benchmark. Any future CTA v2 requires a new economic hypothesis and experiment
record; it cannot retroactively repair CTA v1.
