# Fed put: purchase-conditioned long-end yield reversal

> Brainstorm · non-evidential · loaded only on explicit request · no acceptance weight.
> Distinct from [long-end-yield-shock.md](2026-08-19-long-end-yield-shock.md) —
> that memo is about yield shocks breaking equity trend entries; this one is
> about the yield's own reversal, conditioned on Fed support. Grounded, not
> folk: Gagnon et al. (2011), Krishnamurthy and Vissing-Jorgensen (2011), and
> D'Amico and King (2013) establish the term-premium-compression mechanism.
> One narrow instance of a wider family — see the [macro reaction-function
> narrative library](2026-08-20-macro-reaction-function-narrative-library.md)
> for the broader set (real yields, credit stress, gold, oil, DXY,
> Taylor-rule gap) this one sits inside.

$$FP_t(w) = f\big(\Delta\text{SOMA holdings}_t^{(w)},\ \text{buyback}_t^{(w)}\big)\;?$$

- $H_0$: after a long-end yield extreme (e.g. 30Y at a multi-year high), Fed
  support activity ($\Delta$SOMA holdings, Treasury buyback operations) adds
  no information beyond a price-only mean-reversion signal?
- $H_1$: elevated $FP_t$ following a yield extreme predicts subsequent
  yield decline/flattening?

Explicitly out: any claim about a specific Fed chair's/governor's intentions
(e.g. leadership psychology, SEP-vote optics) — that is discretionary
narrative, not a quantifiable input, and does not enter this thesis in any
form. Only realized purchase/buyback behavior is in scope.

**Correction (2026-08-20, user-caught):** buybacks are not a co-equal
episode source with SOMA holdings. Live data confirms the modern buyback
program only restarted 2024-04-03 after a long pause (a dissimilar
2000-2002 debt-paydown program before that) — on their own, buybacks give
~1 usable episode, far short of Thesis Track's already-thin $n\approx3$–$5$.
Episodes must be defined primarily from **SOMA/balance-sheet expansion**
(`TREAST`, full QE history since 2008 — QE1/2/3, COVID QE, each a real,
publicly-dated regime), not from buyback operations. Buybacks are a
recent, secondary corroborating signal only, informative from 2024
onward, not a primary episode source. $FP_t(w)$'s buyback term is
near-zero information before 2024 by construction, not by choice.

Open: 30Y or belly-of-curve? Event definition for "yield extreme" ($h,L$,
percentile vs. rolling z-score)? Episode boundaries: officially-dated QE
program starts/ends (FOMC/Desk record), never a changepoint detected in
`TREAST` or the outcome series itself — see
[Thesis Track](../thesis-track-small-n.md)'s own rule against this.
Data: `TREAST`/`TREAS10Y` (Fed SOMA holdings) live via `app.macro_pit`;
Treasury buybacks live via `app.treasury_buybacks` (`0.63.0`), settled
operations only, long-end defined as maturity-bucket upper bound
$\ge 20$Y — both ingested 2026-08-20. Preregistered hypothesis still
required before any signal use, same as every macro candidate.

## Promotion status

None promoted. If this matures into a hypothesis: exploration-protocol → 9A
→ preregistration → 9B, same as every candidate.
