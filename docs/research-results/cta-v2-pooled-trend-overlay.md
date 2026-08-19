# CTA v2 — pooled vol-scaled trend overlay v1

Decision: **not material or not consistent**. The primary variant clears
materiality with room, and all three lookback variants point the same
direction, beating both the benchmark and the required placebo on point
estimate — but none of it survives the bootstrap's significance test, and
the positive result depends materially on 2008. This is a properly-powered
retest of CTA v1's own founding thesis (own-asset trend continuation,
pooled across 12 instruments and the full sample instead of 54 independent
per-fold candidates) — closing a loop this project has carried since CTA
v1's audit, not opening a new one.

Specification SHA-256:
`958a3c838778f32cfb562090309b21f42826394517f0f5f68020ac0067f2382e`.
Data SHA-256: `d07c0d744186575ae7ba5d67a0758b3a06367997e6de9944b62a586853898aea`.
Pooled calendar: `2006-02-06` through `2026-08-18`, `5,165` trading days.

## Result

| Gate | Observation | State |
|---|---:|---|
| Locked specification identity | Verified before execution | Pass |
| Materiality (primary, `≥ +1.0pp` annualized) | `+2.18pp` | **Pass** |
| Significance (primary, Holm `p ≤ 0.05`) | raw `p = 0.231`, Holm `p = 0.692` | **Fail** |
| Placebo (point estimate **and** paired `p ≤ 0.05`) | beats point estimate; paired `p = 0.116` | **Fail** |
| Actual costs, execution, or sleeve accessed | `false` | Pass (no-trade study) |

| Variant | SMA lookback | Annualized excess | Raw `p` | Holm `p` |
|---|---:|---:|---:|---:|
| A (secondary) | 150 | `+0.69pp` | `0.402` | `0.692` |
| **B (primary)** | **252** | **`+2.18pp`** | **`0.231`** | **`0.692`** |
| C (secondary) | 350 | `+1.14pp` | `0.332` | `0.692` |

All three Holm-adjusted p-values land at the same `0.692` — a correct
consequence of Holm's step-down procedure with a 3-member family: the
smallest raw p (`B`'s `0.231`) produces the largest step-down multiplier
(`3 × 0.231 = 0.693`), and every later comparison in the ranked sequence is
capped by that running maximum, not a computation artifact.

The direction-blind placebo's own mean daily excess return over the
benchmark was **negative** (`-0.587pp` annualized) — pure inverse-volatility
weighting, with no trend information at all, underperformed the benchmark
on average, consistent with it structurally overweighting the lowest-
volatility instruments regardless of whether they are trending. The primary
variant's point estimate beats both the benchmark and this placebo, but the
paired significance test on the primary-minus-placebo difference series
(`p = 0.116`) does not clear the locked `0.05` bar.

**Disclosed, non-gating regime diagnostic:** excluding 2008 from the primary
variant's sample flips its mean daily excess return from `+8.64e-5` to
`-1.24e-5` — negative. Excluding 2020 (`+8.73e-5`) or 2022 (`+6.80e-5`)
leaves it essentially unchanged. The positive point estimate is materially
dependent on the 2008 episode, not a pattern spread evenly across the
sample.

**Disclosed, non-gating asset-weight diagnostic:** the primary variant's
mean weight share is heavily concentrated in three names — `SPY` (`25.3%`),
`IEF` (`20.6%`), and `QQQ` (`13.6%`) together account for `~59%` of average
portfolio weight, while `EEM` (`1.4%`), `XLF` (`1.4%`), and `DBC` (`2.5%`)
receive very little. This is a direct consequence of vol-scaling: the two
lowest-realized-volatility instruments in the universe (`IEF`, a
duration bond fund, and `SPY`) are structurally favoured regardless of
whether they are the instruments actually trending, which is itself a
partial explanation for why the direction-blind placebo alone already
produces a large fraction of the primary variant's weight pattern.

## Reading this result

This candidate exists specifically to fix CTA v1's own diagnosed weakness:
the 2026-08-19 methodology audit found CTA v1's 54-candidate-per-fold
design had a minimum detectable effect near IR 4.1 and ~2.5% power at a
realistic IR 1.0 — genuinely unable to tell a modest true trend-following
edge from noise. This protocol pools all 12 instruments and the full
2006–2026 sample into one test instead of 54 independent per-fold
candidates, precisely to remove that power limitation. It succeeds at that:
`5,165` pooled trading days is not a power-limited sample the way CTA v1's
54-way-split, per-fold candidates were, and the result here is a genuine,
informative null on the specific claim tested — not another instance of
"the test couldn't have told either way."

That said, an informative null is still a null, and it is not a clean one
the way ETF-12 cross-sectional rotation's was. Three honest, distinct
things are true simultaneously and should not be blurred into one another:
(1) the raw point estimate is real and consistently signed across every
lookback in the preregistered neighbourhood, not a single lucky variant;
(2) none of it is statistically distinguishable from the null this
project's own bootstrap already trusts for every other candidate this
session; (3) a material fraction of the positive point estimate traces to
one crisis episode. Read together, this is closer to "a plausible but
unconfirmed and regime-concentrated pattern" than to either "trend
following works" or "trend following doesn't work" — the same
insufficient-evidence-not-evidence-of-absence reading the audit already
established for CTA v1, now produced by a test that actually had the power
to say otherwise if the effect had been larger or more consistently spread
across time.

The required placebo comparison is also informative on its own terms: a
pure volatility-timing rule with zero directional information actually lost
to the benchmark on average, so whatever the primary variant's point
estimate reflects is not simply "vol-scaling mechanically raises Sharpe" —
SMA Cross v1's confound does not repeat itself here. But the placebo's own
weight-concentration pattern shows vol-scaling still does a lot of the
portfolio-construction work regardless of trend content, which the
asset-weight diagnostic above makes concrete rather than leaving as an
abstract concern.

This tests one specific, locked design: three SMA lookbacks (`150`, `252`,
`350`) normalized by a shared `20`-session close-to-close volatility
estimator, long-only, unlevered, no costs, against a daily-rebalanced
equal-weight benchmark and a required vol-only placebo. It says nothing
about a leveraged or vol-targeted expression, a different vol-scaling
estimator, a different rebalance cadence, or a costed executable version —
any of those would be a new, independently justified protocol, not a retry
of this one. Per this protocol's own decision vocabulary, only
`material_and_consistent`, `not_material_or_not_consistent`, or `invalid`
may be output here.

## Reproducibility and blinding

- Variant and placebo artifact:
  [`output/research/cta-v2-pooled-trend-overlay/958a3c83.../variant-results.json`](../../output/research/cta-v2-pooled-trend-overlay/958a3c838778f32cfb562090309b21f42826394517f0f5f68020ac0067f2382e/variant-results.json).
- Regime-diagnostic artifact:
  [`diagnostics.json`](../../output/research/cta-v2-pooled-trend-overlay/958a3c838778f32cfb562090309b21f42826394517f0f5f68020ac0067f2382e/diagnostics.json).
- Decision artifact:
  [`decision.json`](../../output/research/cta-v2-pooled-trend-overlay/958a3c838778f32cfb562090309b21f42826394517f0f5f68020ac0067f2382e/decision.json).
- No cost, execution, position, or portfolio field is present in any
  artifact — this was a no-trade, no-cost characterization study throughout.
- Data fingerprinted fresh at execution time from this machine's own stored
  bars (protected by `store.py::upsert_bars`'s atomic per-symbol publication,
  fixed in `0.54.0`); not guaranteed to reproduce bit-for-bit on a different
  machine's fetch under `auto_adjust=True` rebasing.

[Protocol](../research-protocols/cta-v2-pooled-trend-overlay.md) ·
[Selection record (Cycle 2, Candidate C, picked up 2026-08-20)](../research-candidates/2026-08-19-cycle-2.md) ·
[Machine specification](../../research/experiments/cta-v2-pooled-trend-overlay.json)
