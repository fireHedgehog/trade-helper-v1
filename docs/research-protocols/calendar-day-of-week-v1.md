# Calendar Day-of-Week v1 — Monday daily-return differential vs. block-resampled null

Status: executed and closed as `not_material_or_not_consistent`. See the
[result](../research-results/calendar-day-of-week-v1.md) — no power
limitation and a directionally consistent tilt (`9/12` assets negative,
`DBC` raw `p=0.048`), but nothing survived Holm correction or cleared
materiality and significance together.

Selection authority: [Stage 9A Cycle 5, Candidate
B](../research-candidates/2026-08-20-cycle-5.md), scored `12/16`, eligible,
picked up directly from that record without a new selection cycle — the
same precedent as TA Breakout v1 (scored in Cycle 2, locked and executed
later without minting a new cycle). Not a repair of Calendar Turn-of-Month
v1 (Candidate A, closed `not_material_or_not_consistent`): this is a
different calendar-position definition, deliberately not bundled into the
same cycle to avoid non-independent evidence from one underlying
"calendar effects in this universe" answer, per Cycle 5's own selection
record.

## Scope decision, stated plainly

This reuses `tom_daily_differential` and `tom_volatility_diagnostic` from
`backend/app/research.py` unchanged — both are generic, mask-based
statistics functions with no turn-of-month-specific logic; only the event
mask changes. A new `dow_event_mask` and `dow_bootstrap` are added,
structurally identical to `tom_event_mask`/`tom_bootstrap` (calendar-fixed
event positions, computed once and held fixed across every resample; no
mean-centering; no warm-up; contemporaneous zero-horizon estimand) with the
month-position rule replaced by a weekday rule.

Only **Monday** is tested against all other weekdays — not a five-way scan
across every weekday. French (1980)'s original and most widely cited
finding is specifically about Monday; testing all five weekdays as separate
families would introduce a genuine new multiple-comparisons dimension (`5`
day-types `× 12` assets `= 60` tests) that this protocol deliberately avoids
by locking onto the literature's single most robust historical claim, the
same restraint principle used by every candidate this session.

A small, disclosed overlap exists with Calendar Turn-of-Month v1: a Monday
can also fall within the turn-of-month window (the last trading day of a
month or the first `3` of the next). The two event masks are not mutually
exclusive. This is disclosed as a minor design note, not corrected for,
since it affects only a small fraction of days and both candidates were
scored and locked independently before either was executed.

## Decision this protocol may make

No-trade event study and significance test only:

- `material_and_consistent`: the Monday daily-return differential is
  material, statistically distinguishable from the block-resampled null,
  and consistent across at least `8` of the `12` assets;
- `not_material_or_not_consistent`: gates fail on event count, materiality,
  significance, breadth, or concentration;
- `invalid`: implementation, leakage, warm-up, or reproducibility checks fail.

May not output `reject`, `revise`, `continue research`, an entry signal, a
stop, a position size, or a portfolio return/Sharpe claim.

## Claim and definitions

**Monday event.** $\text{DOW}_i(t) = 1$ if session $t$'s calendar weekday is
Monday, else `0`. Computed purely from the trading-day calendar; carries no
price information and no look-ahead risk, identical in kind to Calendar
Turn-of-Month v1's event definition.

**Daily differential (the claim).**
$\Delta_i = \overline{r_i(t) \mid \text{DOW}_i(t)=1} - \overline{r_i(t) \mid
\text{DOW}_i(t)=0}$, where $r_i(t)$ is the daily log return. The first
session in each asset's history (synthetic zero-return padding entry) is
excluded from both groups.

No cooldown and no warm-up are applied, matching Calendar Turn-of-Month v1's
scope decision — every trading day is classified into exactly one group.

## Estimand

One-sided p-value (favourable is positive, matching the historically
documented Monday-underperformance framing tested as "does Monday
under-perform," i.e. materiality is checked in the *negative* direction —
see Gates below): fraction of `5,000` block-resampled iterations with
$\Delta_i^{\text{resampled}} \le \Delta_i^{\text{observed}}$, plus add-one
correction. Block length `20` sessions. `holm_adjust` across the `12`-asset
family.

Unlike Calendar Turn-of-Month v1 (favourable is positive — a claimed
outperformance), this candidate's literature claim is a historical
*underperformance* on Mondays, so the one-sided test direction is flipped
to match the actual claim being tested, stated explicitly here rather than
silently reusing the wrong sign.

## Universe, data, and warm-up

- The 12 locked ETFs, adjusted daily close, full available history.
- No warm-up period.
- Minimum event count: `200` qualifying Mondays per asset. Mondays are
  structurally ~`20`% of trading days, so even the shortest-history asset
  (`DBC`) is expected to clear this comfortably; stated for consistency with
  every other protocol, not because binding is expected.

## Gates

| Gate | Requirement |
|---|---|
| Minimum event count | `≥200` qualifying Mondays after exclusion of the padding entry |
| Materiality | $\Delta_i \le -0.05\%$ **and** Holm-adjusted $p \le 0.05$ |
| Breadth | Materiality holds in at least `8` of the `12` assets |
| Concentration | At least `3` of the `6` distinct `cluster` values in `portfolio_universe.py:PORTFOLIO_CLASSIFICATIONS` represented among qualifying assets |
| Reproducibility | Byte-identical artifact on an independent rerun |

`-0.05%` mirrors Calendar Turn-of-Month v1's `+0.05%` materiality floor in
magnitude, sign-flipped to match this candidate's underperformance
direction — not a fresh, independently chosen number.

## Diagnostics (disclosed, non-gating)

Per-asset realized volatility on Monday vs. all other days, via
`tom_volatility_diagnostic`, identical in purpose to Calendar Turn-of-Month
v1's diagnostic.

## Multiplicity, dependence, and trial ledger

- One family: the `12`-asset event-statistic Holm correction. No parameter
  grid — one locked day (Monday), sourced from French (1980), not fit to
  this data.
- Append one `preregistered_no_results` attempt to `research/attempts.jsonl`
  with `variant_count=1` and dependence group `calendar-day-of-week-v1`
  before execution.

## Implementation and artifact contract

1. Implement `dow_event_mask` and `dow_bootstrap` in
   `backend/app/research.py`, reusing `tom_daily_differential` and
   `tom_volatility_diagnostic` unchanged; add unit fixtures proving the mask
   matches a hand-computed calendar and that a planted differential is
   detected.
2. `research/experiments/calendar-day-of-week-v1.json` locks every constant
   above; `data` fingerprint fields are `null` until computed at execution
   time. Locked specification SHA-256:

   `8283d00b5a10a7778fd5826a6931226013c3435b4f5f14fbe07c40a868d7ff19`
3. No new data fetch required.

Outputs live under
`output/research/calendar-day-of-week-v1/<spec-fingerprint>/`:
`manifest.json`, `per-asset-results.json`, `decision.json`. No cost,
execution, position, or portfolio field is authorised in any artifact.

## Lock checklist

- Reuses Calendar Turn-of-Month v1's generic statistics functions unchanged;
  only the event mask and test direction differ, both stated explicitly.
- Test direction (negative/underperformance) explicitly stated and justified
  against the literature claim, not silently copied from Turn-of-Month's
  positive-direction convention.
- Small overlap with Calendar Turn-of-Month v1's event definition disclosed,
  not hidden.
- Single locked day (Monday); no five-way weekday scan, avoiding a new
  multiple-comparisons dimension.
- Not a repair of Calendar Turn-of-Month v1's closed result — a distinct,
  independently justified claim already scored in Cycle 5.
