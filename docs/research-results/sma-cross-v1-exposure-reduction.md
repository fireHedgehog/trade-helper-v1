# SMA Cross v1 exposure-reduction and volatility-state placebo

Decision: **not material or not consistent**. This is a properly-powered,
completed significance test, not a blocked feasibility gate like Cycle 1's
consolidation result — it ran to completion on real data and produced an
interpretable negative finding, not an "unable to tell."

Specification SHA-256:
`3c7e8be2a5fb636a8234bf982e42862412143213f9f42f592a93babcc9956238`.
Data SHA-256: `0c5a81332f9ba941ddce9bd6a69cb9fe90c3f7570b163c1a4ec3bd4c609fc5bc`.

## Result

| Gate | Observation | State |
|---|---:|---|
| Locked specification identity | Verified before execution | Pass |
| Materiality + significance, both statistics, same asset, after Holm | `0/12` assets | **Fail** |
| Breadth (`≥8/12` required) | `0/12` | **Fail** |
| Placebo comparison (SMA state must beat the volatility-state placebo on both statistics) | `0/12` assets | **Fail** |
| Concentration (`≥3/6` clusters, contingent on breadth) | Not reached | Not reached |
| Actual costs or execution accessed | `false` | Pass (no-trade experiment) |

Before multiplicity correction, the raw SMA-state effect looked real on several
assets: `8/12` had `p_delta_sigma < 0.05` and `7/12` had `p_delta_mdd < 0.05`,
with `4/12` (`EEM`, `EFA`, `QQQ`, `XLF`) clearing both raw materiality
thresholds (`Δσ ≤ −3pp`, `ΔMDD ≤ −5pp`) and both raw significance tests at
once. After the locked Holm correction across the `12`-asset × `2`-statistic
family, none survived on both statistics simultaneously: `QQQ`'s
Holm-adjusted `p_delta_sigma` came closest at `0.0506` (its `p_delta_mdd` was
`0.48`), and `XLF`'s Holm-adjusted `p_delta_mdd` cleared at `0.043` (its
`p_delta_sigma` was `0.22`) — no asset cleared both at once.

The placebo comparison is the more decisive finding. The volatility-only
placebo (a binary state with no trend information at all, gated purely on
whether trailing volatility is below its own expanding median) matched or
beat the SMA-state rule's variance reduction on **12 of 12** assets, and
matched or beat its drawdown reduction on `5/12`. Zero assets showed the
SMA-state rule strictly outperforming the volatility-only placebo on both
statistics. This is the falsifier named in the locked protocol directly
triggering: "an unconditional trailing-volatility-scaling control achieves
equal or greater volatility/drawdown reduction than the SMA-state rule,
showing the trend-state variable adds nothing beyond generic vol-timing." The
data supports exactly that reading — the raw risk-reduction visible in the
trend rule looks like it is substantially generic risk-avoidance, not
information specific to the moving-average crossover.

## Reading this result

This is evidence against the *specific* claim locked in this protocol:
that a `20/50`-day SMA trailing-state gate reduces volatility and drawdown
*and* does so distinctly from a simpler volatility-only rule, consistently
across the 12-ETF universe. It is not evidence about SMA-based trend
following in general, about a different window pair, about a pooled or
panel version of this same test, or about any executable expression —
none of those were run. It also does not test whether the rule adds
*return*; that estimand was explicitly secondary and unscored by design.

Per this protocol's own decision vocabulary
([docs/research-protocols/sma-cross-v1-exposure-reduction.md](../research-protocols/sma-cross-v1-exposure-reduction.md)),
only `material_and_consistent`, `not_material_or_not_consistent`, or
`invalid` may be output here; `reject`/`revise`/`continue research` require a
Stage 9B protocol this feasibility-and-significance gate does not constitute.
A closely related design (a different window pair, a pooled/panel estimator,
or a genuinely distinct control) would be a new attempt, not an amendment to
this one.

## Reproducibility and blinding

- Per-asset artifact:
  [`output/research/sma-cross-v1-exposure-reduction/3c7e8be2.../per-asset-results.json`](../../output/research/sma-cross-v1-exposure-reduction/3c7e8be2a5fb636a8234bf982e42862412143213f9f42f592a93babcc9956238/per-asset-results.json).
- Decision artifact:
  [`decision.json`](../../output/research/sma-cross-v1-exposure-reduction/3c7e8be2a5fb636a8234bf982e42862412143213f9f42f592a93babcc9956238/decision.json).
- No cost, execution, position, or portfolio-level field is present in any
  artifact — this was a no-trade characterization run throughout.
- Data fingerprinted at execution time from this machine's own fetch; a
  different machine's fetch of the same 12 symbols is not guaranteed to
  reproduce this exact data hash under `auto_adjust=True` rebasing (see
  [docs/README.md](../README.md)'s environment-portability section), though
  row/symbol counts and the statistical conclusion are expected to be stable.

[Protocol](../research-protocols/sma-cross-v1-exposure-reduction.md) ·
[Selection record](../research-candidates/2026-08-19-cycle-2.md) ·
[Machine specification](../../research/experiments/sma-cross-v1-exposure-reduction.json)
