# Fed put: yield-stress precursor to Fed balance-sheet expansion

> Brainstorm · non-evidential · loaded only on explicit request · no acceptance weight.
> Distinct from [long-end-yield-shock.md](2026-08-19-long-end-yield-shock.md) —
> that memo is about yield shocks breaking equity trend entries. Reframed
> 2026-08-20 (user-directed): the original claim (Fed support → yield
> reversal) is common knowledge already priced in, not a real edge. The
> reframed claim is the precursor side — does yield stress *predict* Fed
> action — which is forward-looking, not reactive.

**Treasury buybacks dropped from this hypothesis entirely (2026-08-20,
user-directed).** Treasury (debt management, administration-dependent,
swings with fiscal policy) and the Fed (SOMA/QE, monetary policy,
independent-agency) are different institutions with different mandates —
bundling them as one "support" signal was a real conflation in the
original framing, not a simplification. Treasury/fiscal-policy trades
(CHIPS Act-style industrial policy, tariffs, leader announcements) are a
distinct, separately-motivated future line — see the [Policy Exposure /
Industrial-Policy Factor
note](2026-08-20-policy-exposure-industrial-factor.md) — explicitly
idea-stage, not this candidate.

## Claim

Long-end yield stress (10Y/30Y elevated vs. trailing history) *while the
short end stays contained* precedes Fed balance-sheet expansion (QE
launch), above chance.

- **Mechanism**: a steepening driven by the long end alone signals
  term-premium/market-functioning stress the policy rate can't address
  (front end already anchored) — distinct from recession-driven curve
  *inversion*, a different, already-known trigger (cuts, not QE).
- **Estimand**: was the curve-stress state present in the *K* months
  before each real QE launch, vs. placebo windows drawn from the rest of
  history?
- **Episodes**: QE1 (2008), QE2 (2010), QE3 (2012), COVID QE (2020) — 4
  real, publicly-dated launches. [Thesis Track](../thesis-track-small-n.md),
  reversed direction: precursor → event, not event → outcome.
- **Alternative to rule out**: curve *inversion* + recession fear → cuts,
  not QE (2019 shape) — the trigger state must be specified precisely
  enough to exclude this.
- **Data**: simpler than the original framing — Treasury yields aren't
  revision-prone like survey data (final on release), no real
  point-in-time gap. `TREAST`/`TREAS10Y` (live via `app.macro_pit`) covers
  the QE side.
- **Falsifier**: precursor state absent before a real launch, or present
  with no launch following.

Explicitly out: any claim about a specific Fed chair's/governor's
intentions — discretionary narrative, not quantifiable, never enters this
thesis.

Open: 30Y or belly-of-curve? Event definition for "yield extreme" ($h,L$,
percentile vs. rolling z-score)? Precise curve-shape definition separating
this from the inversion/recession case? Episode boundaries: officially-dated
QE program starts (FOMC/Desk record) only, never a changepoint detected in
`TREAST` or the outcome series itself. Preregistered hypothesis still
required before any signal use, same as every macro candidate.

## Promotion status

None promoted. If this matures into a hypothesis: exploration-protocol → 9A
→ preregistration → 9B, same as every candidate.
