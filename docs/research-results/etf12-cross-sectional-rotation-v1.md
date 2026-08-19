# ETF-12 cross-sectional rotation v1 — rank continuation vs. joint-panel null

Decision: **not material or not consistent**. The cleanest negative of this
session's five experiments — no design caveat, no confound story, no
near-miss to qualify. The pooled rank correlation was simply small and
statistically unremarkable.

Specification SHA-256:
`ce80d2e15bfdc3a644289e6e762d9c041193fba1366c2e2c0faa1d1b87e5d358`.
Data SHA-256: `e0172560cca89a66d07251347d999872555d5c477358f9a5a910beb5b37edcfa`.

## Result

| Gate | Observation | State |
|---|---:|---|
| Locked specification identity | Verified before execution | Pass |
| Materiality (`≥0.10` correlation) | `0.045` observed | **Fail** |
| Significance (`p ≤ 0.05`) | `p = 0.266` | **Fail** |
| Cluster breadth (`≥3/6`) | `6/6` — every cluster appeared in the top-third group at some point across `253` rebalance dates | Pass (moot — materiality already failed) |
| Actual costs, execution, or sleeve accessed | `false` | Pass (no-trade study) |

The pooled Spearman rank correlation between formation-period rank
(trailing `60`-session return) and forward-period rank (`20`-session
holding return), across all `12` assets and `253` rebalance dates
(`3,036` pooled observations) from `2006-02-06` onward, was `0.045` — an
order of magnitude below the `0.10` materiality floor locked before
execution. The joint-panel block-resampling null (`2,000` resamples,
preserving real cross-asset correlation at every resampled date) placed the
observed correlation at the `73rd` percentile of its own null distribution
(`p = 0.266`) — not remotely distinguishable from what the same cluster
structure produces under scrambled temporal ordering.

## Reading this result

Unlike every other experiment this session, there is no secondary story to
tell here. SMA Cross v1 had a confound; RSI had a power limitation; TA
Breakout had a weak placebo separation; Wave Pull had a near-miss on a thin
sample. This one simply found a small, unremarkable correlation on an ample
sample with a well-separated null. Cluster breadth passing cleanly (all six
`portfolio_universe.py` cluster values appeared in the top-third group at
some point) confirms the design itself was not degenerate or concentrated —
the null result is not an artifact of the test only ever looking at one
corner of the universe.

This tests one specific, locked design: a `60`-session formation window, a
`20`-session holding horizon, a `20`-session rebalance cadence, on these `12`
ETFs. It says nothing about other formation/holding horizons, a different
rebalance cadence, or a broader universe — any of those would be a new,
independently justified protocol, not a retry of this one. Per this
protocol's own decision vocabulary, only `material_and_consistent`,
`not_material_or_not_consistent`, or `invalid` may be output here.

## Reproducibility and blinding

- Rebalance-level artifact:
  [`output/research/etf12-cross-sectional-rotation-v1/ce80d2e1.../rebalance-results.json`](../../output/research/etf12-cross-sectional-rotation-v1/ce80d2e15bfdc3a644289e6e762d9c041193fba1366c2e2c0faa1d1b87e5d358/rebalance-results.json).
- Decision artifact:
  [`decision.json`](../../output/research/etf12-cross-sectional-rotation-v1/ce80d2e15bfdc3a644289e6e762d9c041193fba1366c2e2c0faa1d1b87e5d358/decision.json).
- No cost, execution, position, or sleeve-composition field is present in any
  artifact — this was a no-trade rank-continuation study throughout.
- Data aligned to the shared date range every symbol covers
  (`2006-02-06` onward) and fingerprinted fresh at execution time; not
  guaranteed to reproduce bit-for-bit on a different machine's fetch.

[Protocol](../research-protocols/etf12-cross-sectional-rotation-v1.md) ·
[Selection record (Cycle 2)](../research-candidates/2026-08-19-cycle-2.md) ·
[Machine specification](../../research/experiments/etf12-cross-sectional-rotation-v1.json)
