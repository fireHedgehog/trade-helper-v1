# Fed put: yield-stress precursor v3

Decision: **`not_evaluable`**. `p=0.885`.

Specification SHA-256:
`fb1aa71f36715f66c2bb854d1614aa2b5108e25b44cd10d81b6c16a1bf0a0616`.
Data SHA-256:
`64d4b8883905c47869dc73dbe9508937e1a48dd2011ae8a0be3809d0b509fe49`
(same aligned series as v1/v2).

## Result

| Episode | Start | Max score (20yr lookback) | Max score (v2, 3yr lookback) |
|---|---|---:|---:|
| QE1 | 2008-11-25 | -2.79 | -2.72 |
| QE2 | 2010-11-03 | -3.81 | -2.43 |
| QE3 | 2012-09-13 | -3.87 | -2.31 |
| COVID QE | 2020-03-23 | -1.53 | -1.95 |
| 2019 bill purchases | 2019-10-15 | -1.35 | -0.97 |
| **2025 RMP** | 2025-12-12 | **+0.13** | -1.31 |

Observed mean: **-2.20**, `p=0.885` — still `not_evaluable` on the
pooled test.

## The one episode that flipped, exactly as the disclosed structural note predicted

**2025 RMP is the only positive score of the six**, and it flipped from
`-1.31` (3yr lookback) to `+0.13` (20yr lookback). This is the specific,
concrete confirmation of the user's own reading of the current situation:
measured against two decades, not three years, today's long-end level
*is* a genuine outlier with the short end relatively contained — the
"2Y ok, 10Y too high" pattern is real for *this* episode, on this
measure.

It just isn't enough to move the pooled 6-episode statistic, because —
exactly as the protocol disclosed *before* this ran — the four older
crisis episodes got *more* negative under the longer lookback, not less.
QE2 and QE3 in particular deepened sharply (`-2.43→-3.81`,
`-2.31→-3.87`): their 20-year trailing windows are dominated by the much
higher yields of the 1990s-2000s, so 2010-2012's already-low yields read
as even more extreme-low by comparison. This is the secular-decline
asymmetry named in the protocol before execution, not a post-hoc excuse.

## Honest reading

Two things are simultaneously true and not in conflict:

1. **Pooled across 6 real historical episodes, elevated long-end yield
   (by any of the three lookbacks tried) does not predict Fed action.**
   Three independent designs (v1, v2, v3) all land on `not_evaluable`.
2. **The current episode specifically does show the pattern**, on the
   one measure (20yr lookback) that matches what "rocket high" plausibly
   means. One data point cannot be evidence on its own — that is
   precisely why Thesis Track's whole apparatus (episodes, placebo
   nulls, pooling) exists rather than reading today's number in
   isolation.

This closes the yield-stress-precursor line as a *pooled, cross-episode*
claim. It does not resolve whether today specifically is different from
history — that is not a statistical question this design, or arguably
any small-*n* backtest, can answer with confidence either way.

## Reproducibility

- Artifacts: `output/research/fed-put-yield-stress-precursor-v3/fb1aa71f36715f66c2bb854d1614aa2b5108e25b44cd10d81b6c16a1bf0a0616/`.
- Byte-identical on independent rerun. No trade, no cost, no position.

[Protocol](../research-protocols/fed-put-yield-stress-precursor-v3.md)
· [v2](fed-put-yield-stress-precursor-v2.md) · [v1](fed-put-yield-stress-precursor-v1.md)
· [Machine specification](../../research/experiments/fed-put-yield-stress-precursor-v3.json)
