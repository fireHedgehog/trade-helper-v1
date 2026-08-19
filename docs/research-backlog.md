# Research backlog

Status: active Stage 9A. Cycle 1 consolidation feasibility closed `not_evaluable`
because the locked matcher admitted no controls; see the [selection
record](research-candidates/2026-08-19-cycle-1.md) and [result](research-results/consolidation-support-feasibility-v1.md). Cycle 2 selected SMA Cross v1's
exposure-reduction claim, jointly designed against a volatility-state placebo;
see the [selection record](research-candidates/2026-08-19-cycle-2.md). Its
[locked protocol](research-protocols/sma-cross-v1-exposure-reduction.md) executed
and [closed](research-results/sma-cross-v1-exposure-reduction.md)
`not_material_or_not_consistent` on a confound — a volatility-only placebo
matched or beat the SMA state's variance reduction on every asset. Cycle 3
selected RSI(14) oversold-crossing short-horizon reversal; its
[locked protocol](research-protocols/rsi-oversold-reversal-v1.md) executed and
[closed](research-results/rsi-oversold-reversal-v1.md)
`not_material_or_not_consistent` on a *power limitation* instead — 0/12 assets
reached raw significance even before correction, at 36–56 events per asset;
the placebo comparison was genuinely mixed rather than a clean explanation.
TA Breakout v1 (Cycle 2's unpicked Candidate E) was then picked up directly
from the [pending checklist](brainstorm/2026-08-19-pending-candidate-checklist.md);
its [locked protocol](research-protocols/ta-breakout-v1.md) executed and
[closed](research-results/ta-breakout-v1.md) `not_material_or_not_consistent`
on a *disclosed design weakness* — 0/12 reached raw significance despite
1,477 events, and the event/placebo separation was weak by construction.
Cycle 4 selected Wave Pull impulse-pullback continuation, unblocked after its
`IndexError` bug fix; its [locked protocol](research-protocols/wave-pull-v1.md)
executed and [closed](research-results/wave-pull-v1.md)
`not_material_or_not_consistent` on a *clean-separation-but-null* result — the
event/placebo split was sharp this time (unlike TA Breakout), one asset
(`TLT`) reached raw significance before correction for the first time this
session, but failed Holm correction on a thin 20-event sample. ETF-12
cross-sectional rotation (Cycle 2's Candidate D) was picked up next by
resolving its infrastructure gap through redesign, not a new dependency; its
[locked protocol](research-protocols/etf12-cross-sectional-rotation-v1.md)
executed and [closed](research-results/etf12-cross-sectional-rotation-v1.md)
`not_material_or_not_consistent` on a *clean, decisive null* — pooled rank
correlation `0.045` against a `0.10` floor, `p=0.266`, no confound or design
caveat attached, the cleanest of the five. Five negative results, five
different reasons — see each result's own reading before treating them as
interchangeable. Every Tier 0/1 item and one Tier 2 item on the [pending
checklist](brainstorm/2026-08-19-pending-candidate-checklist.md) was then
scored or executed. An independent, adversarially verified next-priority
evaluation (2026-08-20) scored five options for what to do next and
surfaced [Cycle 5](research-candidates/2026-08-20-cycle-5.md): a
turn-of-month calendar effect, the first time-based (not price-derived)
mechanism family this session, scored `15/16` — tied with RSI for the
highest of any candidate. Its [locked
protocol](research-protocols/calendar-turn-of-month-v1.md) executed and
[closed](research-results/calendar-turn-of-month-v1.md)
`not_material_or_not_consistent` — a *well-powered null* — `987`-`1,612`
events per asset ruled out a power limitation, and a locked volatility
diagnostic ruled out a confound story, but the daily differential was small
and inconsistent; `EEM`'s raw `p=0.013` was the strongest single-asset raw
signal this session but did not survive Holm correction. Day-of-week
(Cycle 5, Candidate B) was picked up directly afterward without a new
selection cycle; its [locked
protocol](research-protocols/calendar-day-of-week-v1.md) executed and
[closed](research-results/calendar-day-of-week-v1.md)
`not_material_or_not_consistent` too — `9`/`12` assets negative, a more
directionally consistent tilt than turn-of-month, and `DBC` reached raw
`p=0.048`, but its Holm-adjusted `p=0.578` did not survive correction.
Overnight-gap conditioning (Cycle 5, Candidate C) was picked up last: its
joint-paired resampling design step (same block-index sequence applied to
both the overnight and intraday return components, preserving their real
day-to-day pairing) was completed, then put through independent
adversarial pre-lock code review — three lenses, three agents, zero shared
context — before any data was touched, finding and fixing six real issues
(see the
[protocol](research-protocols/overnight-gap-continuation-v1.md)'s Pre-lock
verification record). Its locked protocol executed and
[closed](research-results/overnight-gap-continuation-v1.md)
`not_material_or_not_consistent` — the most decisive negative of the
session: `12`/`12` assets showed a *negative* signed forward return, the
opposite sign from the continuation hypothesis, not merely small or mixed.
The strengthened placebo significance gate added during review correctly
rejected `3` assets that would have trivially passed the bare
point-estimate comparison every prior candidate used, directly validating
the review's own concern. Eight negative results, eight different reasons
this session. No follow-up research task is queued, and the next step
(CTA v2's engine, macro data investment, or a fresh cycle) is a deliberate
choice, not a default.

## Resume gate

Before proposing another model, read [hypothesis engineering](hypothesis-engineering.md), [the model acceptance standard](model-acceptance-standard.md), [CTA v1 protocol](research-protocol.md), [result](research-results/cta-trend-wf-v1.md), [audit](research-results/cta-trend-wf-v1-audit.md), and [benchmark ADR](adr/0005-product-objective-and-portfolio-benchmark.md). Audit benchmark/universe suitability before scoring. CTA v1 is closed; do not optimize it retrospectively.

## Candidate research programmes

[Daily Consolidation Zone v1](research-hypotheses/daily-consolidation-zone-v1.md)
competed in the Cycle 1 Stage 9A scorecard. Support recovery—not breakout or failed
breakout—was prioritised for detector/event feasibility only. The detector was
structurally viable, but matching feasibility failed. This does not authorise a
strategy implementation or outcome calculation, and it does not reject the claim.

### CTA v2

Operationalized and scored in Cycle 2 as a pooled, volatility-scaled trend overlay
across the 12-ETF universe — see [Candidate C](research-candidates/2026-08-19-cycle-2.md). Eligible (score 13) but parked: its estimand needs a
multi-instrument pooled-portfolio weighting engine. Its overlap concern with cross-sectional rotation is now moot —
rotation ran and [closed `not_material_or_not_consistent`](research-results/etf12-cross-sectional-rotation-v1.md) — so building this engine no longer risks
double-counting a shared trend-family effect against a still-open sibling; the
overlap with volatility-managed exposure remains live. Park is an infrastructure
gate, not a data or rationale gate; do not choose parameters until that engine
is scoped. **Cost correction (2026-08-20):** the true engineering cost is
lower than "exists nowhere in this codebase" previously implied —
`portfolio_execution.py` and `portfolio.py` (committed 2026-08-18) already
implement a real shared-cash, multi-symbol, sector/cluster-capped daily
replay engine, though built for the live "Today" view (discrete-share,
stop-sized) rather than CTA v2's continuous vol-scaled target-weight
estimand, and not wired into `research.py`'s bootstrap pipeline — a new
weight-vector return-construction function is still needed, not a
from-scratch engine. Separately, both of CTA v2's own rationale channels are
now pre-undermined by this session's closed results (CTA v1's audit for
channel 1, SMA Cross v1's confound for channel 2) — see the [pending
checklist](brainstorm/2026-08-19-pending-candidate-checklist.md) for the
full evaluation; not recommended to start next.

### SMA cross, breakout, and momentum horizons

SMA cross was operationalized, scored, and prioritised in Cycle 2 as an
exposure-reduction claim, jointly designed against a volatility-state placebo —
see [Candidate A](research-candidates/2026-08-19-cycle-2.md). Its
[locked protocol](research-protocols/sma-cross-v1-exposure-reduction.md) is
closed `not_material_or_not_consistent`: the volatility-only placebo matched or
beat it on every asset, and no asset survived Holm correction on both statistics
at once — see the [result](research-results/sma-cross-v1-exposure-reduction.md).
A different window pair or a pooled/panel version would be a new, independently
justified attempt, not a repair of this one. Momentum
horizons was operationalized as ETF-12 cross-sectional relative-strength rotation
— see [Candidate D](research-candidates/2026-08-19-cycle-2.md), score `13/16`.
Its infrastructure gap (no `scipy`/`statsmodels`, no panel-regression or
permutation-null machinery) was resolved by redesign, not a new dependency:
Spearman rank correlation plus a joint-panel block-resampling null. Its
[locked protocol](research-protocols/etf12-cross-sectional-rotation-v1.md)
executed and [closed](research-results/etf12-cross-sectional-rotation-v1.md)
`not_material_or_not_consistent` — pooled correlation `0.045` against a `0.10`
floor, `p=0.266`, the cleanest negative of the session. A different formation
window, holding horizon, or rebalance cadence would be a new, independently
justified attempt. Generic breakout is covered under Classical TA series
below. UI availability must never imply statistical approval.

### RSI mean reversion

Operationalized, scored (`15/16`, highest of any candidate so far), and
prioritised in Cycle 3 as a short-horizon contrarian reversal claim, distinct
in mechanism from every trend-family candidate above — see [Candidate
A](research-candidates/2026-08-19-cycle-3.md). Its [locked
protocol](research-protocols/rsi-oversold-reversal-v1.md) is closed
`not_material_or_not_consistent`: 0/12 assets reached raw significance even
before Holm correction, at `36`–`56` qualifying events per asset — see the
[result](research-results/rsi-oversold-reversal-v1.md). This reads as a power
limitation, not a confound; a future attempt aimed at more events (longer
horizon, shorter cooldown, pooled estimator) would be a new, independently
justified protocol, not a repair of this one.

### Classical TA series

`S/R Bounce` is the existing quantified classical-TA prototype: prior rolling support/resistance, support-test recovery entry, resistance target, and ATR-buffered stop. It may be charted and backtested but has no accepted edge claim. Scored in Cycle 3 ([Candidate B](research-candidates/2026-08-19-cycle-3.md)): `0` on distinct information — its mechanism is close enough to Cycle 1's already-closed consolidation support-recovery detector, with a cruder unconfirmed construction, that it would substantially re-ask a question already answered. Not prioritised; eligible only behind a materially different construction. A genuinely different construction is now known — round-number/psychological price levels (Donaldson and Kim 1993; Osler 2003), an exogenous order-clustering mechanism rather than Cycle 1's endogenous own-history level — but it is blocked (2026-08-20): every fetched price series is dividend/split-adjusted under [ADR 0002](adr/0002-market-data-contract.md), and adjusted prices diverge substantially from real nominal historical prices for 10 of the 12 locked assets (e.g. `SPY`'s adjusted 2007 high is ~30% below its real nominal price; `TLT`/`IEF` are off by roughly `2×`). A round-number detector on this data would silently test price levels that were never on any trader's screen. Blocked until an ADR 0002 amendment or a new unadjusted-price data path exists — see the [pending checklist](brainstorm/2026-08-19-pending-candidate-checklist.md).

`TA Breakout v1` was operationalized and scored in Cycle 2 ([Candidate
E](research-candidates/2026-08-19-cycle-2.md), `10/16`, not prioritised at the
time), then picked up from the [pending
checklist](brainstorm/2026-08-19-pending-candidate-checklist.md) and locked as
a deliberately simplified, close-price-only [event-study
protocol](research-protocols/ta-breakout-v1.md) — rolling-high resistance,
rejection-count requirement, and a raw-breakout placebo, no zone tolerance
band, pivot-confirmation lag, or stop family. Executed and
[closed](research-results/ta-breakout-v1.md) `not_material_or_not_consistent`,
with a disclosed design weakness: the rejection filter barely separated event
from placebo. A future attempt at a tighter separation (stricter tolerance,
more required touches) or the fuller original construction (zone tolerance,
pivot lag, stop families) would be new, independently justified work — no
`NDO entry` marker is permitted until an executable rule is separately locked
and evidenced. Descriptive support/resistance lines may be shown as chart
context but must be labelled non-signal.

### Calendar effects

Turn-of-month was operationalized and scored `15/16` in Cycle 5 ([Candidate
A](research-candidates/2026-08-20-cycle-5.md)) — the first time-based, not
price-derived, mechanism family this session. Its [locked
protocol](research-protocols/calendar-turn-of-month-v1.md) is closed
`not_material_or_not_consistent`: `0`/`12` assets cleared materiality and
Holm-corrected significance simultaneously, despite `987`-`1,612` qualifying
events per asset ruling out any power-limitation explanation — see the
[result](research-results/calendar-turn-of-month-v1.md). A locked, non-gating
volatility diagnostic found no evidence of SMA Cross v1's confound (event-day
and non-event-day realized volatility were nearly identical for every
asset). Day-of-week (Candidate B, `12/16`) was picked up directly afterward
(2026-08-20), not bundled into the same cycle as turn-of-month to avoid
non-independent evidence from one underlying "calendar effects" answer. Its
[locked protocol](research-protocols/calendar-day-of-week-v1.md) is closed
`not_material_or_not_consistent`: `0`/`12` cleared materiality and
Holm-corrected significance together, but the direction was notably more
consistent than turn-of-month's (`9`/`12` assets negative, matching French
1980's predicted sign) and `DBC` reached raw `p=0.048` — the only
raw-significant single-asset result at the conventional `0.05` threshold
across both calendar experiments — before Holm correction (`p=0.578`)
erased it. A locked, non-gating diagnostic also found `8`/`12` assets have
modestly higher realized volatility on Mondays than other days, disclosed
but not further interpreted. Overnight-gap conditioning (Candidate C,
`13/16`) is a
distinct market-microstructure mechanism, not a calendar effect. It needed
a new joint/paired resampling design (the existing scaffold only
reconstructs a single synthetic close-price path per resample, not two
paired series) — completed, put through independent adversarial pre-lock
code review, then locked and closed
[`not_material_or_not_consistent`](research-results/overnight-gap-continuation-v1.md):
`12`/`12` assets showed a negative signed forward return, opposite the
continuation hypothesis — the most decisive negative of the session. A
disclosed, non-gating diagnostic suggests a reversal-shaped pattern instead
(down-gaps tend to bounce back), which this protocol was not designed to
test and cannot claim; a reversal-framed candidate would be new,
independently justified work.

### Model selection and machine learning

ML is justified only if the sample, target, leakage controls, turnover/cost model, nested validation, feature stability, and interpretability constraints are specified first. It is not a substitute for an economic hypothesis, and unrestricted feature search increases false discovery risk.

## Required outputs for any new hypothesis

- pre-result candidate scorecard and selection record;
- immutable specification and fingerprint;
- point-in-time universe and data provenance;
- executable timing and portfolio contract;
- passive benchmark and decision threshold;
- train/validation/test separation with multiplicity control;
- sensitivity, regime, and cost stress tests;
- explicit `reject`, `revise`, or `continue` decision;
- durable artifact sufficient for independent reproduction.
