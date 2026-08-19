# Calendar Turn-of-Month v1 — daily-return differential vs. block-resampled null

Status: executed and closed as `not_material_or_not_consistent`. See the
[result](../research-results/calendar-turn-of-month-v1.md) — no power
limitation (987-1,612 events/asset) and no volatility confound (checked via
the locked diagnostic), just a small, inconsistent differential with one
single-asset near-miss (`EEM`, raw `p=0.013`) that did not survive
correction.

Selection authority: [Stage 9A Cycle 5, Candidate
A](../research-candidates/2026-08-20-cycle-5.md), scored `15/16`, the highest
of any candidate this session tied with RSI oversold reversal. Picked up
directly from the [pending
checklist](../brainstorm/2026-08-19-pending-candidate-checklist.md)'s Tier 1
after an independent, adversarially verified next-priority evaluation
surfaced it as a genuinely new, cheap, mechanistically-distinct candidate.

## Scope decision, stated plainly

Every candidate scored so far this session (SMA Cross, RSI, TA Breakout, Wave
Pull, ETF-12 rotation) defines its event from a price-derived condition,
which means the event must be *recomputed* from the resampled synthetic
price path on every bootstrap iteration — that recomputation is the whole
point of the event-recomputing bootstrap scaffold used everywhere else in
`research.py`. Turn-of-month membership is different in kind: it depends only
on the trading-day calendar, which is known in advance and does not change
under any resampling of return *values*. So this protocol uses a genuinely
simpler bootstrap variant: the event mask (which day-positions are
turn-of-month) is computed once from the real dates and held fixed; each
resample only reshuffles the return *values* occupying those fixed
positions, then recomputes the group-mean differential directly, with no
event-detection logic re-run at all. This is not a new dependency and not a
new external technique — it is a simplification of the same block-bootstrap
machinery already proven five times this session, justified by the fact that
the event definition here carries zero look-ahead risk and zero price
dependence by construction, unlike every prior candidate.

No mean-centering is applied to the resampled values before computing the
differential (unlike `circular_block_bootstrap_p_value`'s single-group
test against a zero-mean null). The statistic here is a *difference between
two groups*, and block placement is calendar-position-blind: any overall
drift in the underlying series affects both groups symmetrically under the
null and cancels in the difference. Centering would only be necessary for a
single-group test against a fixed reference level, which this is not.

This is also the first candidate this session with a contemporaneous
(zero-horizon) estimand rather than an event-then-forward-K-session-return
design: the claim is about the return realized *on* the classified day
itself, matching the standard construction in the turn-of-month literature
(Lakonishok and Smidt 1988), not a forecast from a trigger to a future
window.

## Decision this protocol may make

No-trade event study and significance test only:

- `material_and_consistent`: the turn-of-month daily-return differential is
  material, statistically distinguishable from the block-resampled null, and
  consistent across at least `8` of the `12` assets;
- `not_material_or_not_consistent`: gates fail on event count, materiality,
  significance, breadth, or concentration;
- `invalid`: implementation, leakage, warm-up, or reproducibility checks fail.

May not output `reject`, `revise`, `continue research`, an entry signal, a
stop, a position size, or a portfolio return/Sharpe claim.

## Claim and definitions

**Turn-of-month event.** For each symbol, group its trading-day sequence by
calendar month. $\text{TOM}_i(t) = 1$ if session $t$ is either (a) the last
trading day of its month, or (b) one of the first `3` trading days of a
month — the Lakonishok and Smidt (1988) `4`-trading-day window. Membership is
computed once from the real trading-day calendar; it does not depend on any
price value and is never recomputed on a resampled path.

**Daily differential (the claim).**
$\Delta_i = \overline{r_i(t) \mid \text{TOM}_i(t)=1} - \overline{r_i(t) \mid
\text{TOM}_i(t)=0}$, where $r_i(t)$ is the daily log return. The first
session in each asset's history (a synthetic zero-return padding entry, no
real prior close to difference against) is excluded from both groups.

No cooldown and no warm-up are applied: every trading day is classified into
exactly one group (this is a partition, not a sparse-event trigger), and
calendar position is known from the first real trading day of the sample,
carrying no look-ahead risk to exclude.

## Estimand

One-sided p-value (favourable is positive): fraction of `5,000`
block-resampled iterations with $\Delta_i^{\text{resampled}} \ge
\Delta_i^{\text{observed}}$, plus add-one correction. Block length `20`
sessions, matching every prior candidate's convention. `holm_adjust` across
the `12`-asset family.

## Universe, data, and warm-up

- The 12 locked ETFs, adjusted daily close, full available history.
- No warm-up period (see Scope decision above — this is a genuine first for
  this session).
- Minimum event count: `200` qualifying turn-of-month days per asset.
  Turn-of-month days are structurally ~19% of all trading days, so even the
  shortest-history asset (`DBC`, 2006-02-06 onward) is expected to clear this
  by roughly `4x` — this floor is stated for consistency with every other
  protocol this session and as a genuine data-integrity check, not because
  binding is expected. If it does bind, that is disclosed as a data anomaly,
  not silently worked around.

## Gates

| Gate | Requirement |
|---|---|
| Minimum event count | `≥200` qualifying turn-of-month days after exclusion of the padding entry |
| Materiality | $\Delta_i \ge +0.05\%$ **and** Holm-adjusted $p \le 0.05$ |
| Breadth | Materiality holds in at least `8` of the `12` assets |
| Concentration | At least `3` of the `6` distinct `cluster` values in `portfolio_universe.py:PORTFOLIO_CLASSIFICATIONS` represented among qualifying assets |
| Reproducibility | Byte-identical artifact on an independent rerun |

`+0.05%` scales the `+0.5%`-per-`10`-session materiality floor used by RSI,
TA Breakout, and Wave Pull down to a single-day statistic
($0.5\% \div 10 = 0.05\%$) — the same proportional scaling already implicit
in this session's other thresholds, not a new number chosen after seeing
data. `8`-of-`12` breadth and `3`-of-`6` concentration match Wave Pull's own
thresholds, locked here for comparability, not re-derived.

## Diagnostics (disclosed, non-gating)

Per-asset realized volatility (standard deviation of daily log returns) on
turn-of-month days vs. all other days is computed and reported alongside the
primary result, but does not affect the decision. This directly checks the
alternative explanation named in the selection record — that any apparent
effect is a volatility-timing artifact rather than a return-level one, the
same lesson SMA Cross v1's confound already taught this session — without
waiting to discover it after the fact.

## Multiplicity, dependence, and trial ledger

- One family: the `12`-asset event-statistic Holm correction. No parameter
  grid — one locked window definition (last trading day of month plus first
  `3` of the next), sourced from Lakonishok and Smidt (1988), not fit to this
  data.
- Append one `preregistered_no_results` attempt to `research/attempts.jsonl`
  with `variant_count=1` and dependence group `calendar-turn-of-month-v1`
  before execution.

## Implementation and artifact contract

1. Implement `tom_event_mask`, `tom_daily_differential`, and `tom_bootstrap`
   in `backend/app/research.py`, reusing the existing block-resampling loop
   structure (no new dependency); add unit fixtures proving (a) the event
   mask matches a hand-computed calendar for a small fixture, (b) a planted
   differential is detected, (c) no future bar affects an earlier
   classification.
2. `research/experiments/calendar-turn-of-month-v1.json` locks every
   constant above; `data` fingerprint fields are `null` until computed at
   execution time. Locked specification SHA-256:

   `e961ffd26eb65b77b51ef397a603507aead215a4c9748a3073d4cc2e4bd01e92`
3. No new data fetch required.

Outputs live under
`output/research/calendar-turn-of-month-v1/<spec-fingerprint>/`:
`manifest.json`, `per-asset-results.json`, `decision.json`. No cost,
execution, position, or portfolio field is authorised in any artifact.

## Lock checklist

- Scope decision (calendar-fixed event positions, no per-resample
  recomputation, no centering, zero-horizon estimand) stated explicitly and
  justified against every prior candidate's design, not silently diverging.
- Materiality threshold's proportional derivation from prior thresholds
  stated explicitly, not picked freshly.
- Volatility-confound diagnostic locked in advance as non-gating disclosure,
  addressing SMA Cross v1's own already-learned lesson pre-emptively rather
  than discovering it post hoc.
- No parameter grid; one locked construction sourced from literature.
- Overlap with the day-of-week calendar-effect candidate (Cycle 5, Candidate
  B) is disclosed in the selection record, not assumed away by this
  protocol.
