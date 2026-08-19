# ETF-12 cross-sectional rotation v1 — rank continuation vs. joint-panel null

Status: executed and closed as `not_material_or_not_consistent`. See the
[result](../research-results/etf12-cross-sectional-rotation-v1.md) — the
cleanest negative of this session's five experiments, with no confound or
design caveat attached.

Selection authority: [Stage 9A Cycle 2, Candidate
D](../research-candidates/2026-08-19-cycle-2.md), scored `13/16`, eligible
but parked specifically pending statistical infrastructure — "a
cluster-controlled panel regression plus a cluster-shuffle permutation
null has no implementation anywhere in this codebase... `research.py`
contains only a single-series circular block bootstrap; `backend/requirements.txt`
carries neither `scipy` nor `statsmodels`."

## Scope decision, stated plainly

This protocol resolves that infrastructure gap by redesigning the estimand
around the block-resampling method already proven four times this session,
rather than by adding a new dependency or building a formal panel-regression
library. Two substitutions from Cycle 2's original operationalization:

1. **Spearman rank correlation, not a panel regression.** Rank correlation is
   computable in plain `numpy`/`pandas` (rank the values, then Pearson-
   correlate the ranks) — no `scipy.stats` call needed.
2. **"Net of cluster membership" is achieved by the null construction, not by
   residualizing the data.** Cycle 2 asked for a cluster-shuffle permutation
   null. A literal per-asset residualization (subtract each asset's own
   cluster mean before ranking) is degenerate here: four of the twelve ETFs
   (`TLT`, `IEF`, `GLD`, `DBC`) are the *only* member of their own `cluster`
   value in `portfolio_universe.py:PORTFOLIO_CLASSIFICATIONS` — subtracting a
   singleton's own mean always zeros it, which would silently force those
   four assets to a permanent tie at the origin. Instead, the null is built by
   **block-resampling calendar time jointly across all 12 assets** — the same
   resampled dates are applied to every asset in a given draw, which
   preserves whatever real contemporaneous cluster/regime co-movement exists
   in the data, and only scrambles the specific across-time formation-then-
   forward link being tested. A resampled panel with the same real
   cross-sectional correlation structure but a scrambled temporal order is
   the right null for "is this just generic cluster/regime persistence" —
   achieved without an operation that breaks on singleton clusters.

The overlap with CTA v2 (Cycle 2's Candidate C, absolute time-series trend)
that Cycle 2's verification flagged is currently moot: CTA v2 remains parked
and is not being run alongside this candidate, so no double-counting risk
materializes in practice. It remains disclosed for whenever CTA v2 is
picked up.

## Decision this protocol may make

No-trade rank-continuation study and significance test only:

- `material_and_consistent`: the pooled rank correlation is statistically and
  economically material against the joint-panel null;
- `not_material_or_not_consistent`: the correlation fails materiality,
  significance, or breadth-of-cluster-representation gates;
- `invalid`: implementation, leakage, warm-up, or reproducibility checks fail.

May not output `reject`, `revise`, `continue research`, a position size, a
sleeve composition, or a portfolio return/Sharpe claim.

## Claim and definitions

**Formation.** At each rebalance date $t$ (every `20` sessions, starting once
`100` warm-up sessions have elapsed), for each of the 12 assets $i$: trailing
`60`-session return $F_i(t) = \text{close}_i(t)/\text{close}_i(t-60) - 1$,
computed through close $t$ only.

**Formation rank.** $\text{Rank}^F_i(t)$ = cross-sectional rank of $F_i(t)$
among the 12 assets at date $t$, ties broken by average rank (the standard
symmetric convention — a tie splits the contested rank positions evenly
rather than favouring either asset).

**Forward outcome.** $G_i(t) = \text{close}_i(t+20)/\text{close}_i(t) - 1$ —
realized return over the `20`-session holding period following formation.

**Forward rank.** $\text{Rank}^G_i(t)$ = cross-sectional rank of $G_i(t)$
among the 12 assets at the same date $t$ (all 12 always have complete history
from `2006-02-06` onward, so no missing-asset adjustment is needed).

**Estimand.** The pooled Spearman rank correlation between
$\text{Rank}^F_i(t)$ and $\text{Rank}^G_i(t)$ across all $(i, t)$ pairs —
every asset, every rebalance date, one pooled statistic. Positive and
material means top-formation-ranked assets tend to also be top-forward-ranked
assets — rank continuation.

## Null construction (the required control)

Circularly block-resample **calendar time**, not each asset's return series
independently: draw a set of `20`-session blocks from the shared date index,
apply the *same* resampled date sequence to reconstruct a synthetic price
path for all 12 assets simultaneously (each asset's own returns are
reordered by the same block permutation), then recompute
$\text{Rank}^F$/$\text{Rank}^G$ and the pooled Spearman correlation on that
jointly-resampled panel. This preserves real contemporaneous cross-asset
correlation (including cluster co-movement) at every resampled date, while
breaking the specific sequential link between a date's formation ranks and
its own later forward ranks. One-sided p-value: fraction of `2,000`
resamples with a resampled pooled correlation `≥` the observed one, plus
add-one correction. `2,000`, not `5,000`, because each resample now involves
all 12 assets jointly rather than one — locked lower to keep runtime
reasonable without changing the test's validity.

No Holm correction is applied across assets here — unlike every prior
protocol this session, the estimand is already a single pooled statistic
across the whole panel, not 12 separate per-asset tests.

## Universe, data, and warm-up

- The 12 locked ETFs, adjusted daily close, full available history from
  `2006-02-06` (the common start date already used by every prior locked
  spec touching this universe).
- Warm-up: `100` sessions before the first rebalance date, matching every
  other protocol this session.
- Rebalance grid: every `20` sessions starting at session index `100` —
  fixed and disclosed, not tuned after seeing results.

## Gates

| Gate | Requirement |
|---|---|
| Materiality | Pooled Spearman correlation `≥ 0.10` **and** $p \le 0.05$ against the joint-panel null |
| Cluster breadth | At least `3` of the `6` distinct `cluster` values in `portfolio_universe.py:PORTFOLIO_CLASSIFICATIONS` must each contribute at least one asset to the top-third formation-rank group at least once across all rebalance dates — the same concentration discipline used everywhere else this session, applied to "does the top tier ever diversify across clusters," not just to a qualifying-asset list |
| Reproducibility | Byte-identical correlation/p-value artifact on an independent rerun against the same fingerprinted data |

`0.10` is a modest but non-trivial rank correlation, chosen as an economically
meaningful floor before outcome access — not derived from a pilot run. It is
not relaxed after the correlation is seen.

## Multiplicity, dependence, and trial ledger

- One family: one pooled estimand, one null construction. No parameter grid —
  one locked formation window (`60`), one locked holding horizon (`20`), no
  sweep. A future window/horizon grid is a separate, independently justified
  attempt.
- Append one `preregistered_no_results` attempt to `research/attempts.jsonl`
  with `variant_count=1` and dependence group
  `etf12-cross-sectional-rotation-v1` before execution.

## Implementation and artifact contract

1. Implement rank computation (with disclosed average-rank tie-breaking),
   the pooled Spearman correlation, and the joint-panel block-resampling null
   in `backend/app/research.py`. Add unit fixtures proving: (a) no future bar
   affects an earlier formation or forward rank; (b) the tie-breaking rule
   behaves as documented; (c) a synthetic panel with genuine rank
   continuation produces a materially higher observed correlation than its
   own resampled null, and a synthetic panel built from independent noise
   does not.
2. `research/experiments/etf12-cross-sectional-rotation-v1.json` locks every
   constant above; `data` fingerprint fields are `null` until computed at
   execution time. Locked specification SHA-256:

   `ce80d2e15bfdc3a644289e6e762d9c041193fba1366c2e2c0faa1d1b87e5d358`
3. No new data fetch or new dependency required.

Outputs live under
`output/research/etf12-cross-sectional-rotation-v1/<spec-fingerprint>/`:
`manifest.json`, `rebalance-results.json` (per-rebalance-date ranks, for
audit), `decision.json`. No position, sleeve composition, cost, or execution
field is authorised in any artifact — this is a no-trade rank-continuation
study, not a portfolio construction.

## Lock checklist

- Estimand substitution (Spearman rank correlation for a panel regression)
  and null-construction substitution (joint-panel block resampling for
  per-asset residualization) both stated explicitly as scope decisions, with
  the specific reason (avoiding scipy/statsmodels; avoiding the
  singleton-cluster degeneracy) — not silent simplifications.
- Tie-breaking rule locked and disclosed before any data access.
- No parameter grid; one locked formation window and holding horizon.
- Reuses the block-resampling philosophy proven by every prior protocol this
  session, extended to a joint multi-asset panel rather than inventing an
  unrelated method.
