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

Open: 30Y or belly-of-curve? PIT source for SOMA holdings (Fed H.4.1) and
Treasury buyback operations — neither exists in this codebase yet, both are
free. Event definition for "yield extreme" ($h,L$, percentile vs. rolling
z-score)? Sample size — likely $n \approx 5$–$10$ regime episodes across
decades, not hundreds of daily crossings; this needs a Thesis Track design
(immutable preregistered thesis, no bootstrap significance claimed), not the
block-bootstrap method used for SMA Cross/RSI/TA Breakout. Blocked on
[ADR 0006](../adr/0006-macro-data-contract.md) point-in-time data and a
preregistered hypothesis before any signal use, same as every macro
candidate.

## Promotion status

None promoted. If this matures into a hypothesis: exploration-protocol → 9A
→ preregistration → 9B, same as every candidate.
