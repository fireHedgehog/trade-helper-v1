# Overnight Gap Continuation v1 — gap-conditioned signed forward return vs. joint-paired-resampled null

Status: executed and closed as `not_material_or_not_consistent`. See the
[result](../research-results/overnight-gap-continuation-v1.md) — the most
decisive negative of the session: `12`/`12` assets showed a *negative*
signed forward return, the opposite sign from the hypothesis, and the
pre-lock review's strengthened placebo gate correctly rejected three assets
that would have trivially passed the old bare point-estimate comparison.
Independent adversarial pre-lock review completed `2026-08-20` (three
lenses, three agents, zero shared context between them) found six real,
well-verified issues — three statistical/design gaps and three concrete
robustness gaps — none catastrophic, all fixed before the lock. See
[Pre-lock verification](#pre-lock-verification-record) below for the full
disposition.

Selection authority: [Stage 9A Cycle 5, Candidate
C](../research-candidates/2026-08-20-cycle-5.md), scored `13/16`. Flagged at
selection time as **not implementable** without a new joint/paired
resampling design — the existing event-recomputing bootstrap scaffold
reconstructs a single synthetic close-price path per resample; this
candidate needs two paired return components (overnight and intraday)
resampled *together* to preserve their real day-to-day relationship. This
protocol is that design step, picked up directly from Cycle 5 without
minting a new selection cycle, same precedent as Calendar Day-of-Week v1.

## Scope decision, stated plainly

This is a genuinely new statistical construction for this session, not a
parameter swap on an existing one — the first candidate whose event
definition depends on **two** return components of the same asset rather
than one. Three design choices carry real weight and are stated explicitly
here so a future reader does not have to reverse-engineer them from code:

**1. Self-calibrating, expanding-quantile thresholds, not a fixed size.** A
fixed absolute gap threshold (e.g. "`|gap| ≥ 1%`") would produce wildly
different event rates across a `12`-asset universe spanning `IEF`'s typical
sub-`0.2`% daily moves and `EEM`'s multi-percent ones — starving the
low-volatility assets of events (RSI's own power-limitation failure mode)
or flooding the high-volatility ones. Instead, the event is defined
relative to each asset's own trailing distribution: the largest `10`% of
that asset's own overnight gaps *seen so far*, using the existing
`_expanding_quantile` (already proven in the RSI placebo design) — leakage-
safe by construction, since it only uses data through session `t-1`. This
keeps the qualifying rate comparable across assets without introducing a
new confound tied to which asset happens to be more volatile in absolute
terms.

**2. Joint-paired block resampling, not independent resampling of the two
components.** Overnight return $g(t)$ and intraday return $d(t)$ are not
independent in real markets — a real day's specific $(g,d)$ pairing carries
information (e.g. gap-then-fade vs. gap-then-extend patterns) that an
*independent* resample of each component separately would destroy,
manufacturing spurious effects or spurious nulls that say nothing about the
real joint relationship. Every resample instead draws the **same** block-
index sequence and applies it to both components at once — exactly the
principle ETF-12 rotation used to preserve real cross-*asset* correlation
(same resampled dates applied to all `12` assets simultaneously), applied
here to preserve real cross-*component* correlation within one asset
instead. This is the one piece of this protocol most in need of independent
verification, since a bug here would not crash — it would silently produce
a plausible-looking but statistically meaningless result.

**3. Signed continuation, not raw direction.** The claim is that a large
gap predicts continuation *in the direction of the gap*, not that gaps
predict positive returns generically. The outcome statistic multiplies each
qualifying occurrence's forward return by the *sign of that occurrence's
own gap*, so a real continuation effect shows up as a positive mean
regardless of whether individual gaps were up or down — the same idiom Wave
Pull already used for its impulse-continuation claim, applied here to a
session-structure event instead of a multi-day one.

The placebo strips only the overnight precondition, keeping everything else
identical: `Placebo(t)` uses the same `90`th-percentile-of-trailing-history
rule applied to the **intraday** component $d(t)$ instead of the overnight
component $g(t)$, signed by $d(t)$'s own sign. This isolates whether it is
specifically the *overnight* (order-flow / gap) component that carries
continuation information, or whether any equally large one-day move —
regardless of which part of the session it occurred in — would do just as
well (the generic-volatility confound named at selection time, the same
shape of confound that closed SMA Cross v1). `Gap` and `Placebo` are not
constructed to be mutually exclusive (a day can rarely qualify for both);
this is disclosed, not corrected for, the same treatment given to Day-of-
Week v1's small overlap with Turn-of-Month v1.

**Placebo comparison has genuine statistical backing, not just a point
estimate.** Every prior candidate this session compared its event and
placebo means as a bare real-data inequality (Wave Pull's, TA Breakout's
convention) with no significance test on the *difference* — defensible
there mainly to avoid a second Holm-corrected family. A pre-lock review
argued this leaves little real discriminating power here specifically: a
generic, non-overnight-specific momentum/volatility-clustering effect would
produce comparably-sized signed continuation in *both* tracks, making which
one's point estimate happens to be larger on a given asset close to a coin
flip. Because $g$ and $d$ are already jointly resampled every iteration for
the `Gap` bootstrap, recomputing the `Placebo` statistic on the *same*
resampled path each time was a near-zero marginal cost, so this protocol
does it: `p_gap_vs_placebo` is a genuine paired-null p-value for whether
`Gap`'s advantage over `Placebo` on the same asset is itself distinguishable
from chance, not a second independent Holm-corrected family (still one
family — the `Gap` event statistic — for multiplicity purposes; the
paired-difference test rides on the same resamples already being drawn).

Unlike Calendar Turn-of-Month/Day-of-Week v1 (event definition is
calendar-fixed, needs no per-resample recomputation), this candidate's event
depends on price, so — like RSI, TA Breakout, and Wave Pull — its event and
threshold must be recomputed fresh on every resampled synthetic path, not
held fixed.

## Decision this protocol may make

No-trade event study and significance test only:

- `material_and_consistent`: the gap-conditioned signed forward return is
  material, statistically distinguishable from the joint-paired-resampled
  null, beats the intraday-range placebo on the same asset, and is
  consistent across at least `8` of the `12` assets;
- `not_material_or_not_consistent`: gates fail on event count, materiality,
  significance, the placebo comparison, breadth, or concentration;
- `invalid`: implementation, leakage, warm-up, reproducibility, or
  pre-lock verification checks fail.

May not output `reject`, `revise`, `continue research`, an entry signal, a
stop, a position size, or a portfolio return/Sharpe claim.

## Claim and definitions

**Overnight and intraday log returns.**
$g_i(t) = \ln O_i(t) - \ln C_i(t-1)$ (overnight), $d_i(t) = \ln C_i(t) -
\ln O_i(t)$ (intraday), for $t \ge 1$. Note $g_i(t) + d_i(t) = \ln C_i(t) -
\ln C_i(t-1)$, the ordinary daily log return, so the two components sum
exactly to the existing `log_returns_from_closes` series — reconstructing a
synthetic close path from resampled $(g,d)$ pairs is a direct sum, no new
price-reconstruction logic.

**Thresholds (expanding, `90`th percentile, self-referential, strictly
positive).** $\theta^g_i(t) = \text{ExpandingQuantile}_{0.90}(|g_i(1..t)|)$,
$\theta^d_i(t) = \text{ExpandingQuantile}_{0.90}(|d_i(1..t)|)$ — reusing
`_expanding_quantile` unchanged, which includes session $t$'s own value in
its own threshold (the same "self-referential, no full-sample calibration"
convention already established and disclosed by RSI's placebo design, not a
new leakage risk: only data through session $t$'s own close is ever used,
never a future session, and the identical rule is applied to real and
resampled data alike, which is what the bootstrap's validity actually
depends on). A threshold of exactly `0` never qualifies any day (see the
degenerate-history guard below).

$g_i(0)$ is undefined (no prior close) and is excluded from $\theta^g_i$'s
own trailing history entirely, not zero-padded into it: a pre-lock review
found that zero-padding $g_i(0)$ (this session's usual convention for a
missing first observation) would silently enter the threshold calibration
as a spurious real observation, diluting it in a way $d_i(0)$ — genuinely
observed — never was. `_expanding_quantile` already skips non-finite
entries, so $g_i(0)$ is represented as `NaN` for this purpose specifically,
not `0.0`.

**Event (the claim).** $\text{Gap}_i(t) = 1\{|g_i(t)| \ge \theta^g_i(t) >
0\}$.

**Placebo (the required control).** $\text{Placebo}_i(t) = 1\{|d_i(t)| \ge
\theta^d_i(t) > 0\}$.

**Degenerate-history guard.** A near-degenerate trailing history (e.g. a
long tied-at-zero stretch from stale or forward-filled prices) collapses an
expanding quantile to that tied value; a bare `≥` comparison would then flag
almost every session as an "event" instead of the intended top decile — a
pre-lock review constructed this failure mode concretely and confirmed it
would otherwise occur. The `> 0` requirement above closes it: a qualifying
occurrence must clear a *strictly positive* calibrated threshold, which a
degenerate all-tied (typically all-zero) history can never produce. Not
observed anywhere in the current 12-ETF universe (checked directly against
`data/market.db`), but guarded against regardless of today's data.

Both use a `10`-session cooldown after each qualifying occurrence (matching
every event-based candidate this session) and are excluded during the first
`20` sessions (enough for the expanding quantile to be non-degenerate; not
the full `100`-session warm-up used by rolling-window indicators, since
none is used here).

**Signed forward return.** For a qualifying `Gap` occurrence at $t$:
$SFR_i(t) = \text{sign}(g_i(t)) \times \sum_{k=1}^{10} r_i(t+k)$, where
$r_i$ is the ordinary daily log return. For `Placebo`, sign by
$\text{sign}(d_i(t))$ instead.

## Estimand

Mean signed forward return over the qualifying `Gap` occurrences, tested
one-sided (favourable is positive — continuation) against a joint-paired
block-resampled null: each resample draws one shared block-index sequence,
applies it to *both* $g$ and $d$ simultaneously (preserving their real
day-to-day pairing), reconstructs the synthetic daily-return path as their
sum ($g$'s `NaN` padding replaced with `0.0` only for this summation, never
for threshold calibration), recomputes the expanding-quantile threshold and
event mask fresh on that resampled $g$, and recomputes the signed forward
return. `5,000` resamples, block length `20` sessions (matching every prior
candidate), add-one correction, yielding `p_event`. `holm_adjust` across the
`12`-asset family. On the *same* resampled path, `Placebo`'s statistic is
also recomputed, yielding a second, paired-null p-value `p_gap_vs_placebo`
for the `Gap`-minus-`Placebo` difference — see "Placebo comparison has
genuine statistical backing" above. This is still one Holm-corrected family
(the `Gap` event statistic); `p_gap_vs_placebo` gates each asset
individually and is not itself Holm-corrected across assets, the same
non-family treatment TA Breakout's and Wave Pull's bare placebo comparison
already had — the difference here is that comparison now has a real p-value
behind it instead of a bare point estimate.

## Diagnostics (disclosed, non-gating)

Per-asset, the `Gap` occurrences are split by their own sign into an
up-gap subset and a down-gap subset, each reporting its own mean *unsigned*
forward return and count. A pooled signed-continuation statistic can mask a
real, directionally asymmetric effect (e.g. up-gaps continuing while
down-gaps revert) — a pre-lock review's concern. This does not affect the
estimand or any gate, only what a closed result discloses, the same
treatment `tom_volatility_diagnostic` already gave Calendar Turn-of-Month
v1.

## Universe, data, and warm-up

- The 12 locked ETFs, adjusted daily open and close — the first candidate
  this session to use the open price. Full available history.
- Warm-up: `20` sessions (see Scope decision above).
- Minimum event count: `30` qualifying `Gap` occurrences per asset after
  cooldown. The `90`th-percentile construction targets a comparable
  qualifying rate across assets regardless of each asset's own volatility
  scale, so a shortfall here would be a genuine, disclosed anomaly, not an
  expected outcome.

## Gates

| Gate | Requirement |
|---|---|
| Minimum event count | `≥30` qualifying `Gap` occurrences after cooldown |
| Materiality | $\overline{SFR}_i \ge +0.5\%$ **and** Holm-adjusted $p \le 0.05$ |
| Breadth | Materiality holds in at least `8` of the `12` assets |
| Placebo | `Gap` mean signed forward return must exceed `Placebo` mean signed forward return on the same asset **and** the paired-null `p_gap_vs_placebo \le 0.05` |
| Concentration | At least `3` of the `6` distinct `cluster` values in `portfolio_universe.py:PORTFOLIO_CLASSIFICATIONS` represented among qualifying assets |
| Reproducibility | Byte-identical artifact on an independent rerun |

`+0.5%`/`10`-session materiality matches RSI's, TA Breakout's, and Wave
Pull's own thresholds exactly, locked here for comparability, not chosen
fresh.

## Multiplicity, dependence, and trial ledger

- One family: the `12`-asset event-statistic Holm correction. No parameter
  grid — one locked quantile (`0.90`), cooldown, warm-up, and forward
  horizon.
- Append one `preregistered_no_results` attempt to `research/attempts.jsonl`
  with `variant_count=1` and dependence group
  `overnight-gap-continuation-v1` before execution.

## Implementation and artifact contract

1. Implemented in `backend/app/research.py`: `gap_and_intraday_returns`,
   `overnight_gap_event_mask` (shared by both `Gap` and `Placebo`),
   `_circular_block_resample_indexes`, `_signed_mean_forward_return`,
   `_gap_track_events_and_signs`, `_gap_track_forward_return`,
   `_split_by_gap_direction_forward_return` (the diagnostic), and
   `overnight_gap_bootstrap` (the joint-paired-resampling loop, now
   recomputing both `Gap` and `Placebo` on every resample). `10` unit tests
   in `backend/tests/test_overnight_gap_continuation_v1.py` prove: the
   $(g,d)$ decomposition sums to the ordinary daily return; the
   expanding-quantile mask matches a hand-computed fixture; the joint
   resample preserves $(g,d)$ pairing exactly (a resampled row's two
   components always come from the same original day); a planted
   continuation effect is detected; a correctly-paired bootstrap does
   **not** falsely reject on strong same-day anti-correlated (gap-then-
   fade) data with no genuine forward effect planted — the key correctness
   property of this design, required by this checklist and specifically
   absent before the pre-lock review flagged the gap; a degenerate
   tied-at-zero history does not flag almost every day as an event; p-value
   validity, mismatched-length rejection, non-positive-price rejection, and
   insufficient-event flagging.
2. `research/experiments/overnight-gap-continuation-v1.json` locks every
   constant above; `data` fingerprint fields are `null` until computed at
   execution time. Locked specification SHA-256:

   `8cf8881c155fc7006b76055c443a3e830e214ca9d2f65d2d05cc350a68df17e5`
3. No new data fetch required — `open` is already in `data/market.db`.

Outputs live under
`output/research/overnight-gap-continuation-v1/<spec-fingerprint>/`:
`manifest.json`, `per-asset-results.json`, `decision.json`. No cost,
execution, position, or portfolio field is authorised in any artifact.

## Pre-lock verification record

Conducted `2026-08-20`, before the specification hash was computed and
before any market data was touched: three independent agents, zero shared
context between them, each assigned a distinct lens (statistical/
methodological soundness; line-by-line implementation correctness; adversarial
test-coverage — actively trying to construct a concrete scenario where the
implementation would silently misbehave). All three had full read access to
the protocol, the implementation, and the self-authored test suite, and were
told explicitly not to re-flag design choices already considered and
disclosed in this document. Six findings survived, all disposed of before
this lock:

| # | Lens | Finding | Confidence | Disposition |
|---|---|---|---|---|
| 1 | Statistical | $g_i(0)$'s zero-padding silently entered $\theta^g_i$'s trailing-history calibration as a spurious observation; $d_i(0)$ (genuinely observed) never had the equivalent problem | Medium | **Fixed** — $g_i(0)$ now padded `NaN` for threshold purposes specifically, excluded by `_expanding_quantile`'s own NaN-skipping; still `0.0`-filled for the daily-return-path sum only |
| 2 | Statistical | The `Placebo` gate was a bare point-estimate inequality with no significance test on the difference, giving little real power to rule out a generic (non-overnight-specific) confound | Medium | **Fixed** — `p_gap_vs_placebo`, a genuine paired-null p-value, added at near-zero marginal cost since $g$/$d$ are already jointly resampled; the `Placebo` gate now requires both the point inequality and this p-value |
| 3 | Statistical | Signing by each event's own gap direction before pooling can mask a real, directionally asymmetric effect (e.g. up-gaps continue, down-gaps revert), with no way to detect this after the fact | Medium | **Fixed** — added a non-gating up-gap/down-gap diagnostic breakdown, same treatment as `tom_volatility_diagnostic`; does not change the estimand or any gate |
| 4 | Implementation | This protocol's own lock checklist promised a test proving a planted *decorrelated* effect is **not** falsely detected by the correctly-paired bootstrap; that test was missing, and the existing pairing test only checked the low-level index helper in isolation, not the full `overnight_gap_bootstrap` pipeline | High (gap confirmed; no live bug — the implementation itself was already correct on this point) | **Fixed** — added `test_correctly_paired_bootstrap_does_not_falsely_reject_on_anti_correlated_noise`, exercising the full pipeline on strong same-day gap-then-fade data with zero genuine forward effect |
| 5 | Adversarial coverage | A near-degenerate (tied, typically all-zero) trailing history collapses the expanding-quantile threshold, and a bare `≥` comparison would then flag almost every day as an event — empirically verified (98% flagged vs. an intended ~10%) on a constructed fixture; not triggered by the current 12-ETF universe (checked directly against `data/market.db`, max tied-fraction ~3.8%) | High | **Fixed** — event mask now additionally requires a strictly positive threshold; added a regression test with a synthetic tied-at-zero series |
| 6 | Adversarial coverage | No finiteness/positivity validation on `opens`/`closes`; a single non-positive price would propagate `NaN`/`inf` and could manufacture a spuriously tiny p-value for that asset while distorting the other 11 assets' Holm-adjusted p-values in the same family — empirically verified end-to-end; not triggered by real data today (checked directly against `data/market.db`, zero non-positive prices) | High | **Fixed** — `gap_and_intraday_returns` now raises `ValueError` on any non-finite or non-positive input price, failing loud before any computation rather than propagating a corrupted result; regression test added |

Two findings were explicitly considered and **not** changed: the reviewers'
own re-derivation of the hand-computed quantile test and the pairing test's
expected values both confirmed the author's original values were correct
(not a finding, a confirmation); and a possible "does the joint-pairing
property matter empirically, or is it mostly theoretical" question was
answered affirmatively by the adversarial-coverage reviewer's own
constructed experiments (roughly `0.03`–`0.15` absolute p-value differences
between correctly-paired and deliberately-mispaired resampling on
gap-then-fade synthetic data) — the design's core innovation is load-bearing
for realistic effect sizes, not a theoretical nicety.

Full test suite after all fixes: `10/10` new tests pass; `279/280` across
the whole backend suite (the one failure is the pre-existing, documented,
environment-specific fingerprint mismatch unrelated to this work).

## Lock checklist

- Joint-paired resampling design justified explicitly against the
  alternative (independent per-component resampling) and why that
  alternative would be wrong.
- Self-calibrating expanding-quantile threshold justified against a fixed
  threshold and the specific power-imbalance failure mode it avoids; guarded
  against degenerate (tied/zero) collapse.
- $g_i(0)$'s placeholder excluded from threshold calibration specifically,
  not just self-referentially included like every other session's index-0
  padding.
- Signed-continuation statistic justified and tied to Wave Pull's existing
  precedent for the same idiom; a non-gating up/down diagnostic discloses
  what pooling could mask.
- Placebo isolates the overnight-vs-intraday distinction specifically, the
  load-bearing mechanic named at selection time, and now carries a genuine
  paired-null significance test rather than a bare point estimate.
- Non-finite/non-positive price inputs rejected explicitly rather than
  silently propagating.
- Independent adversarial code review completed and disposed of before the
  specification hash is computed — see Pre-lock verification record above.
- No parameter grid; one locked quantile, cooldown, warm-up, and horizon.
