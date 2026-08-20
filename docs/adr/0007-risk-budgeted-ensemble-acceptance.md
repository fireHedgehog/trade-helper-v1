# ADR 0007: Risk-budgeted ensemble acceptance and Loss-based Quantity Determination

Status: **accepted**, `2026-08-20`. Confidence-multiplier sizing is built
and has scored three real candidates, none with a settled positive read as
of `0.71.0`: CTA v2 not eligible; Wave Pull `TLT` initially scored eligible,
since walked back — a symmetric 12-asset rescore (`2/11`) proved not
distinguishable from the calibrated chance rate once selection bias
(winner's curse) was corrected for; Calendar Day-of-Week's `6/12` initially
looked eligible, since directly tested with a correlation-aware joint null
and found not distinguishable from chance (`p≈0.13`–`0.14`) — see [the
research program](../research-program.md) Chapter 4 §2b/§4 for the full
corrected record. Acceptance does not mean
finished: the ensemble-construction engine, the minimum-breadth floor, and
the live attrition rule remain named, required, unimplemented decisions
(see Consequences). Acceptance means the *design* — a second, parallel
track alongside the existing epistemic ladder in
[identity.md](../identity.md), not a replacement for it — is settled
enough to keep building on without revisiting its shape from scratch.

## Why a second track exists

Every acceptance path this project has built so far ([ADR
0003](0003-research-statistics.md), [model-acceptance-standard.md](../model-acceptance-standard.md),
[identity.md](../identity.md)'s epistemic ladder) answers one question:
**is this pattern distinguishable from random noise, on its own, at
high confidence?** That is the right question for confirming a genuinely
new claim exists — and it is why nine of the ten mechanism families tested
to date have honestly closed `not_material_or_not_consistent` or
`not_evaluable`: most of what was tested was cheap, famous, and likely
already arbitraged, and the standard correctly detected that.

But that standard implicitly assumes the evidentiary situation of a
regulator certifying a treatment for people who cannot personally evaluate
the trial data themselves — an informed-consent problem. This project has
no such third party. The researcher, the capital, and the only party who
bears any consequence are the same person. A standard built to protect
strangers from asymmetric information is not the only legitimate standard
available when there are no strangers to protect.

Real systematic trading books resolve this differently: they do not
require certainty before acting on a signal. They require **position size
to shrink as certainty shrinks**, genuine diversification so no single
wrong signal is costly, and live monitoring that removes a signal quickly
once it stops earning its keep. The edge many real strategies capture is
not "proven arbitrage" — it is a **risk premium**, earned reliably only
through discipline across many bets, not through any one bet being
statistically bulletproof. Grinold and Kahn's Fundamental Law of Active
Management (`IR ≈ IC × √breadth`) is the formal version of this: a real
edge with a weak, individually-unconfirmable information coefficient still
becomes a detectable, usable edge once combined with enough
weakly-correlated others.

## Scope: what this replaces, and what it does not

This ADR does **not** lower the bar for Chapters 1/2-style falsification
work (classical TA, event-driven/macro claims of a structural,
near-riskless effect) — see [the research program
index](../research-program.md). A claim that something is a genuine,
structural statistical arbitrage is an extraordinary claim; it keeps
needing extraordinary (Holm-corrected, placebo-controlled,
adversarially-reviewed) evidence, exactly as built. Nothing here weakens
that.

This ADR opens a **second, parallel track** — call it Chapter 4 of the
research program — for signals that have real, disclosed, but *modest and
uncertain* expected value: not proven, not rejected, genuinely ambiguous.
Its job is not to resolve that ambiguity through more statistics. Its job
is to make acting on that ambiguity **safe** through sizing and
diversification instead.

## Eligibility (the Chapter 4 inclusion bar)

A candidate is Chapter-4-eligible if, and only if, all of the following
are true and disclosed in its own operationalization record (same fields
as [hypothesis-engineering.md](../hypothesis-engineering.md) — claim,
mechanism, falsifier, information set — this is not a lighter-weight
documentation standard, only a lighter-weight *statistical* one):

1. **A stated economic or structural mechanism**, not a bare pattern —
   the same "why might this exist and persist" test every candidate this
   session has already had to answer.
2. **A cross-validated, positive expected-value point estimate**, with an
   explicitly reported uncertainty band (at minimum, a one-sigma /
   ~68%-coverage interval on the EV estimate — deliberately not the 95%
   bar Stage 9A requires). The *lower* bound of that interval need not be
   positive. The point estimate and its dispersion must both be reported;
   neither may be reported alone.
3. **Measured, not assumed, orthogonality** — a return-correlation check
   against every other signal already accepted into the same ensemble.
   Redundant signals do not expand effective breadth and must be disclosed
   as redundant, not silently included as if independent.
4. **No claim of statistical significance.** A Chapter-4 candidate that
   *does* clear Stage 9A's full bar is not a Chapter-4 candidate — it
   graduates to Chapter 1/2's stronger claim instead. This track is only
   for signals that explicitly do not, and are not claimed to, clear that
   bar.
5. **A disclosed regime-concentration check, not just a diagnostic.**
   Clause 2's positive point estimate must be reported alongside what
   fraction of it traces to any single year or episode (the same
   calculation CTA v2's own closed result already discloses). A point
   estimate concentrated in one regime is not automatically disqualified —
   but sizing it as if it were a diversified edge, without first deciding
   explicitly whether "this regime recurs" is itself part of the bet being
   taken, is exactly the kind of undocumented decision this ADR exists to
   prevent. That decision must be written down in the candidate's own
   eligibility record, not left implicit.

## Loss-based Quantity Determination (sizing)

Reuses [ADR 0004](0004-portfolio-risk-contract.md)'s existing entry-capacity
formula as the base, unchanged: `q_base = floor(min(0.005E / d, 0.10E / P))`
— risk `0.5%` of equity against the stop distance `d`, capped at `10%` of
equity notional. That formula is already loss-based sizing; Chapter 4 does
not replace it.

What Chapter 4 adds: every position sized through this track is scaled by
an explicit, disclosed **confidence multiplier** derived from the
signal's own reported uncertainty band (eligibility clause 2 above) —
smaller for a wider/weaker band, capped at `1.0` (a Chapter-4 signal may
never be sized as large as a fully-validated one, by construction, since it
has not cleared that bar). The exact scaling function (e.g., a
fractional-Kelly-style ratio of the interval's lower bound to the point
estimate, floored at zero) is a required decision before any
implementation — named here as the shape of the solution, not locked as a
specific number yet.

## Ensemble-level risk controls (reused, not reinvented)

- Portfolio drawdown halt at `−15%` close-to-close — [ADR 0004](0004-portfolio-risk-contract.md)'s
  existing policy, applied at the whole-ensemble level, unchanged.
- Sector/cluster exposure caps (`25%`/`30%` of equity) — same source,
  unchanged.
- **New**: a minimum-breadth floor — a Chapter-4 ensemble may not deploy
  with fewer than some minimum number of measurably-orthogonal signals
  (exact number a required decision before implementation), since the
  entire safety argument for accepting individually-unconfirmed signals
  depends on genuine diversification existing, not just being intended.

## Live attrition rule

Backtests cannot fully resolve the ambiguity Chapter 4 signals are
explicitly allowed to carry. What resolves it instead is live tracking: a
Chapter-4 signal's realized paper-trading performance must be monitored on
a fixed, preregistered cadence against its own backtested expectation, and
removed from the ensemble if it underperforms a preregistered threshold for
a preregistered duration. Both the threshold and duration must be fixed
before the signal is ever deployed, not chosen after observing live
results. This rule is what makes "accept the ambiguity and size it small"
different from "accept the ambiguity and hope" — the mechanism does not
end at the acceptance decision.

## Out of scope, unchanged

This ADR does not authorize live or broker-connected trading. Chapter 4's
terminal state is the same one [identity.md](../identity.md)'s existing
epistemic ladder already names for a fully-validated candidate: bounded
paper trading. `identity.md`'s statement that "passing grants observation,
never profit" applies to Chapter 4 exactly as it applies to Chapter 1/2 —
the difference this ADR introduces is *what bar a signal must clear to
reach paper-traded observation*, not what happens after it gets there.

## Consequences

- A signal may now enter live-tracked, sized, risk-controlled observation
  without clearing Stage 9A's full compound bar — but only inside a
  diversified ensemble, only at a size that shrinks with its own reported
  uncertainty, and only with a preregistered live-attrition rule already
  in place before deployment.
- Chapter 1/2 falsification work is unchanged in every respect. This ADR
  adds a second door; it does not widen the first one.
- The ensemble-construction engine, the confidence-multiplier sizing
  function, and the minimum-breadth floor are all named here as required
  future decisions, not yet implemented. This ADR authorizes their design,
  not their deployment.
