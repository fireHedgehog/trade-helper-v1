# Calendar Day-of-Week — Chapter 4 eligibility score

Decision: **not distinguishable from chance**. Governed by
[ADR 0007](../adr/0007-risk-budgeted-ensemble-acceptance.md). Scripts:
[`score_calendar_dow_chapter4.py`](../../backend/app/score_calendar_dow_chapter4.py)
(naive per-asset score),
[`score_calendar_dow_full_correlation.py`](../../backend/app/score_calendar_dow_full_correlation.py)
(full `66`-pair correlation matrix),
[`run_calendar_dow_breadth_significance.py`](../../backend/app/run_calendar_dow_breadth_significance.py)
(rigorous joint-null test).

## Result

Naive per-asset score: `6/12` eligible (`DBC`, `EFA`, `GLD`, `IEF`, `TLT`,
`XLF`) on each asset's own full history — a two-sample block bootstrap on
Monday vs. non-Monday returns per asset. Under a naive independent-trials
reading this looked like `p≈0.7%` against the `16.25%` calibrated
per-asset base rate ([calibration v1](chapter4-eligibility-calibration-v1.md)).

**Correlation-aware joint-null test, final answer: `p≈0.13`–`0.14`**,
stable across three independent block-size checks (`19`, `17`, `23` bars).
Not distinguishable from chance.

## Reading this result

The naive reading ignores that the `6` winners are not independent —
[orthogonality v1](chapter4-orthogonality-v1.md) found `3` of the `6`
winner-vs-winner pairs materially correlated (`dow_IEF`/`dow_TLT` `r=0.92`,
`dow_EFA`/`dow_XLF` `r=0.81`, `dow_DBC`/`dow_EFA` `r=0.51`), and the full
`66`-pair matrix across all `12` assets found `31` redundant pairs overall
— the broader universe is saturated with ordinary equity-beta correlation
(`EEM`/`EFA` `r=0.89`, `IWM`/`SPY` `r=0.90`, `QQQ`/`XLK` `r=0.94`).
Positive correlation among winners *inflates* the variance of an extreme
count under the null — it makes `6` more likely by chance, not less, the
opposite of the direction needed to defend `p≈0.7%`. A partial correction
using only the `3` known pairs left a real, unresolved range (`p≈1.5%` to
as high as `~17%–21%` depending on unmeasured correlation among the `9`
non-winning assets) — not precise enough to trust, which is what motivated
building the rigorous version directly rather than continuing to argue
from a hand-adjusted partial matrix.

[`dow_breadth_correlation_aware_null`](../../backend/app/research.py) is a
joint circular-block-resampling null — one shared block-shift applied to
all `12` assets' real return series simultaneously per replication, the
same principle `etf12_rotation_bootstrap` and `overnight_gap_bootstrap`
already use, preserving the *entire* real joint correlation structure
automatically rather than approximating it from a handful of pairwise
numbers. Pre-lock adversarially reviewed before touching real data (two of
three lenses completed; the third hit a session limit mid-run and was
completed directly) — the review caught one real, non-obvious bug: the
original shared `block_bars=20` is an exact multiple of the `5`-day
trading week, so resampled blocks could quietly reproduce genuine
historical Monday-to-return pairings instead of scrambling them, biasing
the test conservative. Fixed by giving the outer cross-asset shift its own
block size, deliberately not a multiple of `5`, decoupled from the inner
per-asset CI's block size (left matching production).

Full record:
[breadth-significance.json](../../output/research/chapter4-eligibility/calendar-day-of-week/breadth-significance.json).
Not a rejection of the underlying French-1980 Monday-effect literature,
but this specific `6/12` breadth reading does not clear even Chapter 4's
loosened bar once real cross-asset correlation is properly accounted for
— nowhere near conventional significance either.

One more disclosed wrinkle: on the common-date window all three block-size
checks require (bounded by `DBC`'s shorter history, `2006`–`2026`), the
observed count itself comes out `5/12` with a *different* eligible set
(`DBC`, `EEM`, `EFA`, `GLD`, `XLF` — `IEF` and `TLT` drop out, `EEM`
enters) than the `6/12` reported against each asset's own full history —
a real, disclosed sensitivity to the evaluation window, not a discrepancy
that changes the significance conclusion either way.

[Chapter 4 index](../research-program.md)
