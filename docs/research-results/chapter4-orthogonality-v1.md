# Chapter 4 orthogonality screen v1

Status: methodology measurement, not a research candidate — measures
redundancy among nominally-eligible signals, does not by itself establish
that any of them are real (ADR 0007 clause 3). Script:
[`score_chapter4_orthogonality.py`](../../backend/app/score_chapter4_orthogonality.py).

## Method

Pairwise Pearson correlation of each signal's own daily return
contribution, aligned per pair to its overlapping date range, across the
`8` nominally-eligible signal-slots from
[Wave Pull](wave-pull-chapter4-eligibility.md) and
[Calendar Day-of-Week](calendar-dow-chapter4-eligibility.md)'s initial
scores. Flagging rule: `|correlation| ≥ 0.5`, a disclosed, locked
rule-of-thumb, not derived from this project's own data.

## Result

Of `28` pairs, `3` are flagged materially redundant, all `3` entirely
among Calendar Day-of-Week's `6` winners:

- `dow_IEF`/`dow_TLT` (`r=0.92`) — two treasury-duration bets moving almost
  identically on Mondays, the exact suspicion named when Day-of-Week was
  first scored.
- `dow_EFA`/`dow_XLF` (`r=0.81`).
- `dow_DBC`/`dow_EFA` (`r=0.51`, just over the line).

These form two thematic clusters (bond-duration; commodities/international-
equity/financials) plus `dow_GLD` standing alone. Both Wave Pull signals
are, by contrast, cleanly independent of everything: `wave_pull_TLT` tops
out at `r=-0.12` against all six `dow_` signals (including `dow_TLT`, the
same underlying asset under a different mechanism), and `wave_pull_GLD`
tops out at `r=-0.22`, including `r=0.02` against `wave_pull_TLT` itself.

## Reading this result

This redundancy concentration is why Calendar Day-of-Week's significance
question needed a direct correlation-aware test rather than an
approximation from this partial `8`-signal view — the `6` winners'
apparent breadth could represent as few as `3`–`5` genuinely independent
underlying effects, not `6`.
[`score_calendar_dow_full_correlation.py`](../../backend/app/score_calendar_dow_full_correlation.py)
later measured all `66` pairs across the full `12`-asset universe (not
just the `6` winners): `31` pairs flagged redundant overall, `28` of them
touching a non-winning asset — the broader universe is saturated with
ordinary equity-beta correlation (`EEM`/`EFA` `r=0.89`, `IWM`/`SPY`
`r=0.90`, `QQQ`/`XLK` `r=0.94`), confirming correlation is pervasive
enough that a hand-adjusted design-effect estimate from a partial matrix
was never going to be precise enough to trust on its own — see
[Calendar Day-of-Week's eligibility record](calendar-dow-chapter4-eligibility.md)
for the rigorous joint-null test this motivated.

`wave_pull_TLT`'s and `wave_pull_GLD`'s near-zero cross-correlation is
real but narrower evidence than "these are genuine effects": it rules out
either being a disguised double-count of one redundant artifact (the
failure mode found among Day-of-Week's winners here), not that either
reflects a true effect — both "two real independent signals" and "two
independent noise false-positives" predict low correlation equally well.

[Chapter 4 index](../research-program.md)
