# Cross-sectional experiment idea library

> Brainstorm · non-evidential · loaded only on explicit request · no acceptance weight.
> Distilled from an external note ("Cross-Sectional Quant Experiment Ideas",
> reviewed 2026-08-20). The source note is not preserved verbatim here on
> purpose — this file is the personal reference; the note itself said it is
> not rigorous and is free to be cut, reworded, or dropped without ceremony.

## The reframing worth keeping verbatim

> Do not merely change an indicator. Change the structure of the scientific
> question.

Concretely: every idea below varies the **estimand** ($E[R_i \mid X_i]$ vs.
$E[R_i - R_j \mid X_i > X_j]$ vs. a conditional/interaction form), not just
the trigger. That is exactly the axis the
[stage-closure record](../stage-closures/2026-08-20-single-asset-time-series-line.md)
used to separate the parked line from what comes next.

## The ten ideas, compact

| # | Name | One-line question | Shape |
|---|---|---|---|
| CS-01 | Raw cross-sectional momentum | Rank by return, does rank predict forward rank? | positive control |
| CS-02 | Momentum × activity (fragility) | Does extreme volume/participation turn continuation into reversal? | interaction |
| CS-03 | Quiet vs. loud winner | Among equal winners, does low realized-vol/volume beat high? | interaction |
| CS-04 | Residual momentum | Is strength stock-specific after removing market (and later sector) beta? | decomposition |
| CS-05 | Breadth before price | Does narrowing participation predict weaker forward index return? | aggregate diagnostic |
| CS-06 | Cross-sectional dispersion regime | Does factor IC depend on the dispersion/correlation regime? | regime-conditioning |
| CS-07 | Correlation crowding | Does rising within-group correlation predict fragility, independent of activity? | interaction |
| CS-08 | Leadership diffusion | Do sector leaders move before laggards (lead-lag), controlling for the sector index itself? | lead-lag |
| CS-09 | Drawdown recovery speed | Does fast recovery from a drawdown carry information beyond distance-to-high? | own-asset, ranked cross-sectionally |
| CS-10 | Macro sensitivity rotation | Rank by estimated rate/DXY beta, does realized sensitivity match a realized shock? | conditional macro cross-section |
| CS-11 | Factor conflict | Does one factor change another's conditional IC (e.g. momentum \| quality)? | multi-factor, later-stage only |

## Read before treating CS-01 as untested ground

CS-01 is not a blank slate. [ETF-12 cross-sectional
rotation](../research-results/etf12-cross-sectional-rotation-v1.md) already
ran this exact estimand shape — rank by relative strength, test forward-rank
correlation — and closed clean and decisive: pooled `ρ=0.045` against a
`0.10` floor, `p=0.266`, no confound. What it did **not** test is breadth:
`N=12` vs. a real equity universe is roughly the whole point of
Grinold–Kahn (`IR ≈ IC × √breadth`) — a null at 12 names does not predict
the answer at 500. If this line resumes, CS-01 should be explicitly
re-run at the new breadth as the required re-baseline, not skipped over as
"already answered" or silently treated as untested.

## Where the real blocker actually sits

The instinct is to ask for finer tiering than the existing informal
`T0`-`T4` cost ladder in the
[pending checklist](2026-08-19-pending-candidate-checklist.md). Checked
against these eleven ideas, more granularity is not actually the gap — what's
useful instead is seeing that **most of this library collapses onto one
existing blocker**, not eleven separate ones:

- **Cleared, `0.81.0`.** CS-01, 02, 03, 04, 05, 09 all needed genuine
  cross-sectional breadth to mean anything (the ETF-12 lesson above), which
  meant clearing the Tier 4 "point-in-time equity membership/delisting data"
  item. That turned out not to need the assumed vendor purchase — a free,
  MIT-licensed, hand-maintained history exists
  ([fja05680/sp500](https://github.com/fja05680/sp500)), now ingested via
  [`universe_pit.py`](../../backend/app/universe_pit.py) and live-verified.
  Volume, realized vol, and market beta were already computable from stored
  bars; membership was the one missing piece, for the S&P 500 subset. Six
  ideas unlocked at once, for the cost of one ingestion module, not one
  vendor invoice. None of the six is yet a scored candidate — this cleared
  the data blocker, not the hypothesis-engineering/Stage-9A/preregistration
  steps every one of them still needs individually.
- **CS-08 and CS-07** (leadership diffusion, correlation crowding via named
  peer groups) — **cleared, `0.83.0`.** GICS Sector/Sub-Industry labels
  ingested via [`universe_sectors.py`](../../backend/app/universe_sectors.py),
  free, from the same Wikipedia table `universe.py` already scrapes
  (`503` symbols, `11` sectors, current-classification snapshot only — no
  history of sector reassignment is tracked). Correlation crowding could
  have sidestepped this via rolling correlation clustering instead; real
  labels are used regardless since they're now free.

  **A sharper, separate bias this does not fix**, user-identified
  `2026-08-21`: index membership is itself endogenous to size/performance —
  committees add companies that grow big/successful enough and remove ones
  that shrink or underperform enough. A real example: a company can fall
  out of Nasdaq-100 (removed by reconstitution) while remaining listed and
  traded — invisible to any universe built from "ever an index member,"
  point-in-time or not. This means CS-01's universe (and any sector test
  built the same way) can only compare groups *among names that stayed
  prominent enough to remain index members* — it cannot capture the true
  spread between winners and names that shrank enough to be removed. This is
  the same reason serious academic momentum studies use CRSP's full
  listed-universe, not an index-membership list. No free source at that
  depth (full US-listed history including non-index delistings) is known to
  exist — this is very plausibly a real, justified Tier 4 vendor-data case
  (CRSP academic access, or a vendor like Sharadar with broader delisted
  coverage) if the sharp version of a leader-vs-abandoned-laggard claim is
  ever pursued, distinct from the sector-rotation-among-survivors claim
  CS-07/CS-08 can test today.
- **CS-10** (macro sensitivity rotation) is not a new blocker at all — it is
  Fed put's own ADR 0006 point-in-time-vintage gate, already Tier 3, already
  scoped in the [Fed put memo](2026-08-19-fed-put-long-end-reversal.md).
- **CS-06 and CS-11** (dispersion regime, factor conflict) are second-order:
  both condition on a factor that has to exist and be established first.
  Not starting candidates on their own.

So the honest answer to "do we need finer granularity": no — the existing
ladder is fine-grained enough. What changes is the *reading* of Tier 4: it
is not "one expensive item behind one candidate," it is the single gate
behind most of an entire idea library, which is a materially different
cost/benefit case than any one factor test made alone.

## Not scored, not authorized

Nothing here has been through hypothesis engineering, the Stage 9A
scorecard, or preregistration. Per the [stage-closure
record](../stage-closures/2026-08-20-single-asset-time-series-line.md)'s
own §6, the next line is still an explicit, scored choice — this note only
makes that choice more informed, it does not make it.
