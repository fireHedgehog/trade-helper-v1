# Single-asset / time-series research line — closure record

Status: **parked**, not rejected. Not a Stage transition — Stage 9A remains
open; this closes one mechanism family being searched inside it. Called
"Stage A" in an external research memo reviewed 2026-08-20
(distinct from, and not to be confused with, this project's own Stage
8/9/10/11 numbering — that memo's "Stage A/B" language is never reused
elsewhere in this project's docs).

## 1. The question this line asked

For a single asset $i$, does a condition computed from asset $i$'s own
trailing history predict asset $i$'s own forward return or risk shape?
Formally: $E[R_i(t+h) \mid X_i(t)]$ — absolute, own-asset prediction. Every
candidate in this line varied the trigger ($X$), not the estimand: a
threshold crossing, a breakout, an impulse, a calendar position, an
overnight gap. None of them compared one asset's state to another's at the
same date — that is a different estimand, addressed separately below.

## 2. Complete evidence inventory

Ten closed results in this line, locked-protocol status and one-line
reading each:

| Result | Decision | Why, in one line |
|---|---|---|
| [CTA v1 walk-forward](../research-results/cta-trend-wf-v1.md) | `reject` (protocol); [audit](../research-results/cta-trend-wf-v1-audit.md): `insufficient evidence`, not evidence of absence | 54-candidate-per-fold design underpowered (MDE ≈ IR 4.1); best candidate's joint-bootstrap p ≈ 0.63, indistinguishable from noise |
| [Consolidation support-recovery feasibility v1](../research-results/consolidation-support-feasibility-v1.md) | `not_evaluable` | Detector structurally viable; locked matcher admitted 0/274 controls — feasibility failed, not the claim |
| [SMA Cross v1 exposure-reduction](../research-results/sma-cross-v1-exposure-reduction.md) | `not_material_or_not_consistent` | Confound: a pure volatility-only placebo matched or beat it on 12/12 assets |
| [RSI oversold reversal](../research-results/rsi-oversold-reversal-v1.md) | `not_material_or_not_consistent` | Power limitation: 0/12 raw-significant even before correction, 36–56 events/asset |
| [TA Breakout v1](../research-results/ta-breakout-v1.md) | `not_material_or_not_consistent` | Weak-by-construction: event and placebo populations nearly identical in count |
| [Wave Pull v1](../research-results/wave-pull-v1.md) | `not_material_or_not_consistent` | Clean separation, still null; `TLT` near-miss failed on 20 events |
| [Calendar Turn-of-Month v1](../research-results/calendar-turn-of-month-v1.md) | `not_material_or_not_consistent` | Well-powered null (987–1,612 events/asset); confound explicitly ruled out |
| [Calendar Day-of-Week v1](../research-results/calendar-day-of-week-v1.md) | `not_material_or_not_consistent` | Well-powered, directionally consistent (9/12) but uncorrected null |
| [Overnight Gap Continuation v1](../research-results/overnight-gap-continuation-v1.md) | `not_material_or_not_consistent` | Decisive: 12/12 assets opposite-signed from the hypothesis |
| [CTA v2 pooled trend overlay](../research-results/cta-v2-pooled-trend-overlay.md) | `not_material_or_not_consistent` | Properly-powered (5,165 pooled days); materiality cleared, significance did not; result depends materially on 2008 |

**Not part of this line, included for context because it directly informs
what "Stage B" would face:**
[ETF-12 cross-sectional rotation v1](../research-results/etf12-cross-sectional-rotation-v1.md)
already tested a genuinely *cross-sectional* estimand (asset $i$'s rank vs.
asset $j$'s rank at the same date) — the one candidate this session shaped
like the next line, not this one. Its result: the cleanest, most decisive
null of the entire session — pooled correlation `0.045` against a `0.10`
floor, `p = 0.266`, no confound, no power limitation, no design caveat.
Cross-sectional research on this project's own 12-asset universe is
therefore not untested territory with an unknown prior; one clean test
already ran there and found nothing. That does not predict the outcome of
a differently-scaled, differently-signaled cross-sectional study (see §6),
but it is real prior evidence, not a blank slate, and should be weighed as
such rather than forgotten.

Methodology validation, not a market result, also produced by this line:
[event-recomputing bootstrap Type-I calibration v1](../research-results/event-bootstrap-calibration-v1.md) —
no anti-conservative bias found in the shared testing machinery; if
anything several variants are measurably conservative. This means the ten
nulls above are not artifacts of a machinery that manufactures false
positives; the honest open question it raises (possible reduced power from
that same conservatism) is carried forward in §3, not resolved.

## 3. Lessons that must not be re-litigated

- **A raw risk-reduction claim from any trailing-state filter must be
  tested against a volatility-only placebo before being trusted.**
  SMA Cross v1's entire result was this confound; any future single-asset
  candidate with a similar shape inherits this requirement by default, not
  by rediscovery.
- **A null at a low event count (RSI's 36–56/asset) is a power-limitation
  finding, not evidence the mechanism is absent.** Do not cite RSI as "RSI
  doesn't work" — cite it as "this design could not tell."
- **An event/placebo comparison is only as good as its separation.** TA
  Breakout's populations nearly overlapped in count; a p-value from a
  poorly-separated comparison is not equivalent evidence to a cleanly
  separated one (Wave Pull's), even when both report `0/12`.
- **Sparse-trigger mechanisms can silently drop assets entirely** (Wave
  Pull's `IEF`, zero qualifying events) — always disclose exclusions as a
  named fact, never let a "0" asset count vanish into an averaged figure.
- **Abundant data does not guarantee a finding.** Both calendar candidates
  had 900+ events per asset and still returned clean nulls — this is
  informative about the world, not evidence of a broken design.
- **A bare point-estimate placebo comparison is weak evidence between two
  correlated statistics.** Overnight-Gap's pre-lock review proved this
  before data access; any future placebo comparison needs a paired
  significance test, not a point-estimate inequality, by default.
- **A properly-powered, pooled retest can still be regime-concentrated.**
  CTA v2 cleared materiality but the entire positive point estimate
  depended on 2008 — always run and disclose a regime-exclusion diagnostic
  before trusting a pooled point estimate, even a materially-sized one.
- **The shared bootstrap machinery itself is not the reason for these
  nulls.** The Type-I calibration found no inflated false-positive risk;
  several variants are conservative. The risk profile of this line, to the
  extent one exists, tilts toward false negatives (missed real effects),
  not false positives — which is the opposite failure mode a first
  instinct might suspect after ten consecutive nulls.

## 4. Closed vs. merely parked

**Parked, not closed.** Nothing here is rejected in the CTA v1 sense (a
locked, executed, audited protocol with a decision). This line is paused
because the reachable mechanism space on the current data shape (12-asset
adjusted daily OHLCV) is thinning — five-plus distinct mechanism families
tested (trend/momentum, contrarian reversal, breakout, calendar timing,
microstructure gap), each falsified or nulled for a real, disclosed,
*different* reason, not a shared design flaw. New data (unadjusted prices
unlocking round-number S/R Bounce; point-in-time macro data unlocking Fed
put) or a genuinely new mechanism family not yet considered could reopen a
specific candidate within this line at any time, through the same
hypothesis-engineering → 9A scoring → preregistration path as anything
else — never by default, never by simply resuming.

## 5. The explicit gate condition

Mechanism-space exhaustion on the current data shape, evidenced directly
by the inventory in §2 and §3 above, not token cost or fatigue — though
those are real, honestly-acknowledged secondary factors, and are named
here rather than left to masquerade as the primary reason. The calibration
study in §2 additionally rules out the specific alternative explanation
that these nulls reflect a systematically broken shared testing machinery
rather than the underlying signals — strengthening, not weakening, the
case that mechanism space, not tooling, is the binding constraint.

## 6. The next line's opening statement

**Not yet chosen — explicitly.** Closing this line does not crown a
successor; the next line is gated by the same scored, adversarially-
checked evaluation that picked CTA v2, not by whichever proposal is
newest. Two candidate directions are on the table as of this record:

- **Cross-sectional / relative-performance estimands**
  ($E[R_i(t+h) - R_j(t+h) \mid X_i(t) > X_j(t)]$, asset selection rather
  than asset timing) — of which this project has already run one clean
  instance (§2's ETF-12 rotation note). A larger extension — cross-sectional
  momentum plus abnormal trading activity across the ~500-symbol universe —
  has been proposed and is well-constructed on paper, but is blocked on a
  real, already-identified data-governance gap (`research-backlog.md`
  Tier 4: point-in-time equity membership/delisting data; the current
  ~500-symbol list is a today's-snapshot survivorship-biased panel) and
  needs a new large-scale cross-sectional computational engine that does
  not exist yet. Not automatically next.
- **Fed put** (rates/Fed-support macro estimand) — real, credible
  literature-backed mechanism, blocked on ADR 0006 point-in-time macro
  data and an unbuilt small-*n* Thesis Track statistical design this
  codebase's bootstrap machinery cannot express. Not automatically next
  either.

The next research session's first action on this thread should be to score
these (and any other live options) against the model-acceptance scorecard,
the same discipline that surfaced CTA v2 over reflexive alternatives —
not to start building either one on the strength of this closure record
alone.
