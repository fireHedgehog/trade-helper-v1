# Ensemble/factor vocabulary and open questions

> Brainstorm · non-evidential · loaded only on explicit request · no acceptance weight.
> Distilled from an external research memo ("Are Daily Bars Obsolete?",
> 2026-08-20), reviewed and partly corrected against this session's actual
> results. A personal glossary and question list for evaluating future
> hypotheses — not a candidate, not a protocol, not scored.

## The one question worth keeping verbatim

When evaluating any future primitive feature, ask this instead of "does it
work":

> Does this feature contain incremental information, at what horizon, with
> what decay, and does it improve the existing signal ensemble?

Not: "is this a standalone strategy that beats a materiality/significance/
breadth gate on its own." Both questions are legitimate, but they are
different questions, and this project's tooling to date only asks the
second one.

## Vocabulary worth having on hand

- **IC (information coefficient)** — correlation between a signal and
  subsequent return. A realistic "good" single-market IC is often cited
  around `0.02`–`0.05`; this is small by design, not a red flag.
- **Fundamental Law of Active Management** (Grinold–Kahn): `IR ≈ IC ×
  √breadth`. The formal backing for "a weak signal survives through
  breadth" — this project's own docs gesture at the idea (diversification
  scoring, cross-candidate dependence) but don't name the law.
- **IC decay** — how an information coefficient fades across forward
  horizons; distinct from whether the raw effect is significant at one
  fixed horizon, which is all this project's event studies test today.
- **Incremental IC** — a feature's added value *conditional on* signals
  already in the ensemble, not its IC alone. The relevant question once
  more than one primitive feature exists; not yet relevant here (one
  feature at a time so far).
- **Effective dimensionality / redundancy** — whether N measured features
  are really N independent signals or collapse to a handful of latent
  factors (e.g. several vol/credit/correlation measures may all just be
  "risk aversion"). Same spirit as the effective-independent-tests finding
  in the 2026-08-19 audit's C2, applied to a factor panel instead of a
  candidate-parameter grid.

## Already covered here under different names — don't re-derive

The memo's "Layer A–E" (price / macro-rates-credit / fundamentals /
narrative-text / derivatives-microstructure) is the same taxonomy as
[hypothesis-engineering.md](../hypothesis-engineering.md)'s existing
information classification (own-asset market data; cross-asset market
data; fundamentals; macro and policy; events and text; derived portfolio
state) — same six buckets, new label names. No new governance concept here.

## Two things worth tracking

1. **Bootstrap Type-I calibration — checked 2026-08-20, see
   [result](../research-results/event-bootstrap-calibration-v1.md).** No
   candidate showed an inflated (anti-conservative) rejection rate under a
   true null across 300 replications; several (SMA Cross v1, Wave Pull v1)
   were measurably conservative. This answers the memo's specific concern.
   It does not answer a related, still-open question the result itself
   raises: conservative calibration is often associated with reduced
   power, and no power calibration (planted-effect detection rate at
   realistic effect sizes) has been run for these five candidates — a
   natural companion study, not yet scheduled.
2. **A Factor Lab, if ever adopted, is a product surface, not only a
   script.** [product.md](../product.md)'s surface table (Today, Symbol
   Research, Strategy Lab, Data Management, Macro, Research Record) has no
   row for a factor/IC panel. Deferring UI/production work now is correct
   while there is no factor ensemble to show — but the day a Factor Lab
   research layer is adopted, it needs its own product-surface decision,
   not silent inclusion under an existing page. Not proposed for action;
   recorded so it isn't reinvented as a surprise later.
