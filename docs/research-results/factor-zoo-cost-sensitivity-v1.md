# Factor zoo cost sensitivity v1 — reversal cluster vs. transaction cost

Status: screening scan, non-evidential — same standing as
[factor-zoo-v1](factor-zoo-v1.md), which this directly extends. Not a
Chapter 4 eligibility claim for any factor; answers the one question
factor-zoo-v1 left open: does the reversal cluster's apparent edge survive
a realistic transaction cost, or was it a cost-blind artifact all along?
Engine: [`factor_zoo.py`](../../backend/app/factor_zoo.py)'s
`evaluate_factor`, extended with a `round_trip_cost_bps` parameter — not a
bespoke cost model for this one report, reusable by any future factor. Run:
[`run_factor_zoo_cost_sensitivity.py`](../../backend/app/run_factor_zoo_cost_sensitivity.py).

## Method

Cost is charged on quintile turnover, not as a flat daily drag: each day,
the fraction of the top/bottom quintile whose membership changed since
yesterday pays a round-trip rate once. The **standard rate (32bps)** is
this project's own already-decided cost assumption
([`engine.py`](../../backend/app/engine.py): `COMMISSION=0.001`,
`SPREAD=0.0002`, `SLIPPAGE=0.0005`, "deliberate, so results aren't
fantasy") — 2 commission fills + 1 quoted spread + 2 slippage fills — not
invented fresh for this check. Three cost levels: `0bps` (reproduces
factor-zoo-v1's original screen), `32bps` (standard), `64bps` (2x stress).

Tested: the six-factor reversal cluster factor-zoo-v1 flagged as one
shared, unconfirmed hypothesis (`alpha034`/`033`/`009`/`028`/`004`/`026`,
pairwise `r=0.52`–`0.79`) — the classic bid-ask-bounce artifact setting
(Jegadeesh 1990, Lehmann 1990), where raw daily closes alternating near
the bid and ask can manufacture an apparent reversal profit that a
realistic cost erases. Every classic technical indicator restates this
same hypothesis mirrored (factor-zoo-v1's finding), so none is re-tested
here — it would be redundant, not additional evidence. `atr_normalized`
(confirmed orthogonal to the cluster, `|r|≤0.34`) is included as a
control: a real, independent factor should degrade gracefully with cost
like any traded strategy, not collapse the way a reversal artifact should.

Same universe, same window as factor-zoo-v1 (495-symbol S&P 500 ∪
Nasdaq-100 ∪ XL-sector-ETF set), re-run against current `data/market.db`
— a live rescan, same as factor-zoo-v1 always was, not a locked/fingerprinted
replay; the `0bps` row below differs slightly from factor-zoo-v1's
published numbers because roughly a week of additional daily bars had
accumulated locally between the two runs, not because of a code change
(`round_trip_cost_bps=0.0` is unit-tested to reproduce the original
zero-cost path exactly, unchanged).

Full numbers:
[cost-sensitivity-report.json](../../output/research/factor-zoo-cost-sensitivity-v1/cost-sensitivity-report.json).
Chart:
[Sharpe vs. cost](../../output/research/factor-zoo-cost-sensitivity-v1/sharpe-vs-cost.png).

## Result

| Factor | Sharpe @ 0bps | Sharpe @ 32bps (standard) | Sharpe @ 64bps |
|---|---:|---:|---:|
| `alpha034` | `0.78` | `-9.44` | `-19.31` |
| `alpha033` | `0.47` | `-6.61` | `-13.66` |
| `alpha009` | `0.40` | `-8.26` | `-16.79` |
| `alpha028` | `0.68` | `-8.69` | `-17.85` |
| `alpha004` | `0.63` | `-4.73` | `-10.06` |
| `alpha026` | `0.44` | `-4.39` | `-9.13` |
| `atr_normalized` (control) | `0.82` | `0.37` | `-0.09` |

Every reversal-cluster factor flips from a positive Sharpe to a **deeply
negative** one at the standard cost rate — not a shrinking edge, a
collapse and sign flip an order of magnitude larger than the original
signal. `atr_normalized` degrades mildly and monotonically (`0.82 → 0.37 →
-0.09`) — the shape a real, slower-turnover factor eroding under cost is
expected to have, not a collapse.

## Reading this result

**The cluster is not material after realistic costs — this confirms
factor-zoo-v1's disclosed suspicion by measurement, not just by citing the
literature.** A 1-session reversal signal rebalances close to the entire
quintile every single day; charging even a modest realistic round-trip
rate on that much daily turnover overwhelms a raw spread that size. This
is the textbook signature of the bid-ask-bounce artifact factor-zoo-v1
named, not an unlucky cost assumption — the *64bps* stress case makes the
same factors worse still, in the same direction, which is what a real
artifact does and a fragile-but-real edge usually does not.

**`atr_normalized` is further confirmed independent, now by a second,
different mechanism.** factor-zoo-v1 already showed it uncorrelated to
the cluster (`|r|≤0.34`); this shows it does not share the cluster's
turnover-driven fragility either. Two different tests agreeing is
stronger than either alone — still not a Chapter 4 proposal by itself
(clause 5's regime-concentration check was the next gate; now closed too,
see [factor-zoo-regime-concentration-v1](factor-zoo-regime-concentration-v1.md)
— no year's exclusion flips the sign), but the transaction-cost objection
specifically is answered for it here: cleared, not sidestepped.

**Consequence for factor-zoo-v1's own "not yet done" list**: the reversal
cluster is answered — not material after cost, closed, not carried
forward as a live thread. `alpha028`/`alpha004`/`alpha026` were named
there as candidates alongside `atr_normalized`; this result means
proposing any of the three cluster members into Chapter 4 would be
proposing something already shown non-material here, not a new
candidate — `atr_normalized` is the one survivor of this specific check.

[Chapter 4 index](../research-program.md) ·
[Factor zoo v1](factor-zoo-v1.md)
