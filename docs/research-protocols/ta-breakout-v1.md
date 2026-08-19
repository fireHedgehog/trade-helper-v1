# TA Breakout v1 — rejected-resistance breakout vs. raw new-high placebo

Status: executed and closed as `not_material_or_not_consistent`. See the
[result](../research-results/ta-breakout-v1.md) — includes a disclosed
design weakness (weak event/placebo separation), not just a bare negative.

Selection authority: [Stage 9A Cycle 2, Candidate
E](../research-candidates/2026-08-19-cycle-2.md), scored `10/16`, not
prioritised at the time but never disqualified — picked up here from the
[pending candidate checklist](../brainstorm/2026-08-19-pending-candidate-checklist.md)'s
Tier 0. Cycle 2's own verification named the exact discriminating placebo this
protocol locks: "strip out the touch-count and pivot-confirmation mechanics
and the claim degenerates into re-testing the already-rejected CTA v1
hypothesis... via the existing `DonchianTrend` prototype." That placebo — a
raw rolling-high breakout with no rejection requirement — is the required
control below, not a separate candidate.

## Scope decision, stated plainly

Cycle 2's operationalization described a full multi-touch zone with a
tolerance band, pivot-confirmation lag, and four stop families — Cycle
1-level complexity. Locking that construction now would risk repeating Cycle
1's exact caliper-matching failure mode. This protocol instead reuses the
design that already worked twice this cycle (SMA Cross v1, RSI oversold
reversal): a **close-price-only**, self-referential event/placebo pair,
tested via block-resample-and-recompute, no separate matched control set.
This is a deliberate simplification, not an oversight — it does not use
intraday high/low touch precision or ATR-scaled tolerances; it is close-only,
matching the same data shape every other locked protocol this cycle already
uses.

## Decision this protocol may make

No-trade event study and significance test only:

- `material_and_consistent`: the rejected-resistance breakout event shows a
  material forward-return effect, beats the raw-breakout placebo, and is
  consistent across at least `8/12` assets;
- `not_material_or_not_consistent`: gates fail on event count, materiality,
  significance, the placebo comparison, or consistency;
- `invalid`: implementation, leakage, warm-up, or reproducibility checks fail.

May not output `reject`, `revise`, `continue research`, an entry signal, a
stop, a position size, or a portfolio return/Sharpe claim.

## Claim and definitions

**Resistance.** $R_i(t)$ = the rolling `60`-session maximum close, computed
through close $t-1$ only (excludes today, matching `DonchianTrend`'s own
`shift(1)` convention).

**Rejection.** A session $s$ is a rejection when
$R_i(s) \times 0.99 \le \text{close}_i(s) < R_i(s)$ — the close approached
within `1%` of the rolling high without exceeding it. `RejectionCount}_i(t)`
is the count of rejections in the trailing `60` sessions through $t$.

**Event (the claim).** $\text{Event}_i(t) = \mathbb{1}\{\text{close}_i(t) >
R_i(t) \times 1.005 \wedge \text{RejectionCount}_i(t) \ge 2\}$ — a completed
close beyond the rolling high by a `0.5%` buffer, only counted where at least
`2` prior rejections at that same rolling level occurred.

**Placebo (the required control).** $\text{Placebo}_i(t) = \mathbb{1}\{
\text{close}_i(t) > R_i(t) \times 1.005\}$ — the same breakout condition with
no rejection-count requirement at all, i.e. `DonchianTrend`'s own raw
breakout rule.

Both use a `10`-session cooldown after each qualifying occurrence, and both
are excluded during the first `100` sessions of warm-up.

## Estimand

Mean forward `10`-session log return following each event/placebo
occurrence, $\bar{R}^{10}_i$, tested against a block-resampled,
event-recomputed null — identical method and code path (`research.py`'s
event-recomputing bootstrap, generalised from RSI's implementation) to RSI
oversold reversal, applied to this event definition instead. One-sided
p-value: fraction of `5,000` resamples with
$\bar{R}^{10}_{\text{resampled}} \ge \bar{R}^{10}_i$ (favourable is positive),
plus add-one correction. `holm_adjust` across the `12`-asset family for the
event statistic; the placebo is a direct per-asset comparison, not a second
Holm-corrected family — identical structure to both prior protocols this
cycle.

## Universe, data, and warm-up

- The 12 locked ETFs, adjusted daily OHLCV (close only), full available
  history.
- Warm-up: `100` sessions, matching RSI's convention and long enough for the
  `60`-session rolling resistance to be well-populated.
- Minimum event count: `15` qualifying events per asset, below which that
  asset is excluded from the qualifying-asset count and disclosed as such,
  not silently dropped.

## Gates

| Gate | Requirement |
|---|---|
| Minimum event count | `≥15` qualifying breakout events after warm-up |
| Materiality | $\bar{R}^{10}_i \ge +0.5\%$ **and** Holm-adjusted $p \le 0.05$ |
| Breadth | Materiality holds in at least `8` of the eligible assets |
| Placebo | Event $\bar{R}^{10}_i$ `>` placebo $\bar{R}^{10}_i$ on the same asset — the rejection-count requirement must add something beyond a raw new-high breakout |
| Concentration | At least `3` of the `6` distinct `cluster` values in `portfolio_universe.py:PORTFOLIO_CLASSIFICATIONS` represented among qualifying assets |
| Reproducibility | Byte-identical artifact on an independent rerun |

`+0.5%` materiality and the `15`-event floor match RSI's own thresholds,
locked here for the same reason: comparability across this cycle's
event-study experiments, not a threshold chosen per-candidate after seeing
anything.

## Multiplicity, dependence, and trial ledger

- One family: the `12`-asset event-statistic Holm correction. No parameter
  grid — one locked resistance window (`60`), tolerance (`1%`), buffer
  (`0.5%`), rejection minimum (`2`), and forward horizon (`10`).
- Append one `preregistered_no_results` attempt to `research/attempts.jsonl`
  with `variant_count=1` and dependence group `ta-breakout-v1` before
  execution.

## Implementation and artifact contract

1. Implement the breakout/placebo event functions and reuse the existing
   event-recomputing bootstrap scaffold in `backend/app/research.py`; add
   unit fixtures proving no future bar affects an earlier resistance,
   rejection, event, or placebo value.
2. `research/experiments/ta-breakout-v1.json` locks every constant above;
   `data` fingerprint fields are `null` until computed at execution time.
   Locked specification SHA-256:

   `40929c9de93633d15284ded96b6dde84998932044ef502ef75954dbb375bda6a`
3. No new data fetch required — the 12-ETF universe already exists on this
   machine.

Outputs live under `output/research/ta-breakout-v1/<spec-fingerprint>/`:
`manifest.json`, `per-asset-results.json`, `decision.json`. No cost,
execution, position, or portfolio field is authorised in any artifact.

## Lock checklist

- Close-price-only design stated explicitly as a scope decision, not a
  silent simplification of Cycle 2's fuller construction.
- Placebo is the exact comparison Cycle 2's own verification named as the
  discriminating test — not invented fresh here.
- No parameter grid; one locked construction.
- Reuses the proven event-recomputing bootstrap rather than Cycle 1's
  caliper-matching design, by deliberate choice.
