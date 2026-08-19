# Wave Pull v1 — impulse-pullback continuation vs. plain-breakout placebo

Status: executed and closed as `not_material_or_not_consistent`. See the
[result](../research-results/wave-pull-v1.md) — a clean event/placebo
separation this time, with one small-sample single-asset near-miss (`TLT`)
that did not survive correction.

Selection authority: [Stage 9A Cycle 4, Candidate
A](../research-candidates/2026-08-19-cycle-4.md), scored `13/16`.
Parent design: the existing unvalidated `WavePull` prototype in
`backend/app/strategies.py` (`impulse_bars 8`, `impulse_pct 6.0`,
`pullback_bars 3`), unblocked by the `0.48.0` `IndexError` fix.

## Scope decision, stated plainly

The existing prototype's pullback range uses intraday high/low. This
protocol substitutes a close-only rolling extreme — the same scope decision
already made for TA Breakout v1 — to stay compatible with the proven
event-recomputing bootstrap, which only reconstructs a synthetic close-price
path from resampled returns. Risk/stop mechanics from the prototype (ATR-free
target at `2×` entry risk) are not used here at all: this is a no-trade event
study, not the executable expression.

## Decision this protocol may make

No-trade event study and significance test only:

- `material_and_consistent`: the impulse-pullback event shows a material
  forward-return effect, beats the plain-breakout placebo, and is consistent
  across at least `8` of the eligible assets;
- `not_material_or_not_consistent`: gates fail on event count, materiality,
  significance, the placebo comparison, or consistency;
- `invalid`: implementation, leakage, warm-up, or reproducibility checks fail.

May not output `reject`, `revise`, `continue research`, an entry signal, a
stop, a position size, or a portfolio return/Sharpe claim.

## Claim and definitions

**Impulse.** $\text{Impulse}_i(t) = \mathbb{1}\{\text{close}_i(t) /
\text{close}_i(t-8) - 1 \ge 0.06\}$.

**Pullback high (close-only).** $PH_i(t)$ = rolling `3`-session maximum
close, computed through close $t-1$ only (`shift(1)` before the rolling
window, matching the existing prototype's own no-lookahead convention).

**Event (the claim).** $\text{Event}_i(t) = \mathbb{1}\{\text{Impulse}_i(t)
\wedge \text{close}_i(t) > PH_i(t)\}$ — an impulse followed by a completed
close breaking the immediate pullback high.

**Placebo (the required control).** $\text{Placebo}_i(t) =
\mathbb{1}\{\text{close}_i(t) > PH_i(t)\}$ — the same breakout condition with
no impulse precondition at all, isolating whether the prior impulse adds
anything beyond a generic `3`-session breakout.

Both use a `10`-session cooldown after each qualifying occurrence
(identical convention to RSI/TA Breakout), and both are excluded during the
first `100` sessions of warm-up.

## Estimand

Mean forward `10`-session log return following each event/placebo
occurrence, tested against a block-resampled, event-recomputed null —
identical method and code path (`research.py`'s event-recomputing bootstrap)
to RSI oversold reversal and TA Breakout v1, applied to this event
definition. One-sided p-value: fraction of `5,000` resamples with
$\bar{R}^{10}_{\text{resampled}} \ge \bar{R}^{10}_i$ (favourable is
positive), plus add-one correction. `holm_adjust` across the eligible-asset
family for the event statistic; the placebo is a direct per-asset
comparison, not a second Holm-corrected family.

## Universe, data, and warm-up

- The 12 locked ETFs, adjusted daily close, full available history.
- Warm-up: `100` sessions, matching every other protocol this cycle.
- Minimum event count: `15` qualifying events per asset. The compound
  impulse-AND-breakout precondition is expected to be rarer than either
  RSI's or TA Breakout's single-condition triggers; an asset falling short is
  excluded from the qualifying-asset count and disclosed as such, not
  silently dropped or compensated for by loosening the threshold.

## Gates

| Gate | Requirement |
|---|---|
| Minimum event count | `≥15` qualifying events after warm-up |
| Materiality | $\bar{R}^{10}_i \ge +0.5\%$ **and** Holm-adjusted $p \le 0.05$ |
| Breadth | Materiality holds in at least `8` of the eligible assets |
| Placebo | Event $\bar{R}^{10}_i$ `>` placebo $\bar{R}^{10}_i$ on the same asset |
| Concentration | At least `3` of the `6` distinct `cluster` values in `portfolio_universe.py:PORTFOLIO_CLASSIFICATIONS` represented among qualifying assets |
| Reproducibility | Byte-identical artifact on an independent rerun |

`+0.5%` materiality and the `15`-event floor match RSI's and TA Breakout's
own thresholds, locked here for comparability across this session's
event-study experiments, not chosen after seeing anything.

## Multiplicity, dependence, and trial ledger

- One family: the eligible-asset event-statistic Holm correction. No
  parameter grid — one locked impulse threshold, pullback window, and
  forward horizon, matching the existing prototype's own defaults.
- Append one `preregistered_no_results` attempt to `research/attempts.jsonl`
  with `variant_count=1` and dependence group `wave-pull-v1` before
  execution.

## Implementation and artifact contract

1. Implement the impulse/breakout/placebo event functions, reusing the
   existing event-recomputing bootstrap scaffold in `backend/app/research.py`
   (`_apply_cooldown`, `_mean_forward_return`); add unit fixtures proving no
   future bar affects an earlier impulse, pullback-high, event, or placebo
   value.
2. `research/experiments/wave-pull-v1.json` locks every constant above;
   `data` fingerprint fields are `null` until computed at execution time.
   Locked specification SHA-256:

   `618a482ae4866887d13b38d84679a98b7343fe2e4e983e29ead6a249f49050c1`
3. No new data fetch required.

Outputs live under `output/research/wave-pull-v1/<spec-fingerprint>/`:
`manifest.json`, `per-asset-results.json`, `decision.json`. No cost,
execution, position, or portfolio field is authorised in any artifact.

## Lock checklist

- Close-price-only scope decision stated explicitly, matching TA Breakout
  v1's precedent, not silently diverging from the prototype's own high/low
  construction.
- Placebo isolates the impulse precondition specifically — the load-bearing
  mechanic named in Cycle 4's own scorecard.
- No parameter grid; one locked construction matching the existing
  prototype's defaults.
- Overlap with TA Breakout's breakout-trigger family is disclosed in the
  selection record, not assumed away by this protocol.
