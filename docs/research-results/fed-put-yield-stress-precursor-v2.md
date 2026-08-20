# Fed put: yield-stress precursor v2

Decision: **`not_evaluable`** (same reading rule as v1). `p=0.981`.

Specification SHA-256:
`59ef27791a68e7750848b772c070196d403c739d9539efd12f8f4d9e0d7e6e5f`.
Data SHA-256:
`64d4b8883905c47869dc73dbe9508937e1a48dd2011ae8a0be3809d0b509fe49`
(same aligned `DGS2`/`DGS10` series as v1 — unchanged).

## Result

| Episode | Start | Max score | Fed's own framing |
|---|---|---:|---|
| QE1 | 2008-11-25 | -2.72 | "QE" |
| QE2 | 2010-11-03 | -2.43 | "QE" |
| QE3 | 2012-09-13 | -2.31 | "QE" |
| COVID QE | 2020-03-23 | -1.95 | "QE" |
| 2019 bill purchases | 2019-10-15 | -0.97 | **"not QE"** (Powell) |
| 2025 RMP | 2025-12-12 | -1.31 | **"not QE"** (Fed) |

Observed mean: **-1.95**. `6`/`6` negative — adding the two real "not
QE" actions the Fed itself branded differently did not change the
picture: no episode, including the two closest to today's actual
situation, was preceded by the hypothesized "10Y high, 2Y contained"
pattern.

## What actually preceded each kind of episode (disclosed diagnostic)

Not one uniform story — two distinct shapes:

- **The 4 crisis episodes** (QE1/2/3, COVID): both `2Y` and `10Y`
  collapsed together, sharply (flight-to-safety) — see
  [v1's result](fed-put-yield-stress-precursor-v1.md).
- **2019**: `z(10Y)` window mean `-1.91`, `z(2Y)` window mean `-0.41` —
  long end fell more than the short end (growth-scare, not full
  recession).
- **2025 RMP — the actual current episode**: `z(10Y)` window mean
  `-0.10` (roughly *neutral* vs. its own trailing 3-year history, not
  elevated), `z(2Y)` window mean `-1.73` (short end *falling*, consistent
  with rate-cut pricing during 2025). The precursor here was "short end
  easing, long end unremarkable relative to recent history" — the
  reverse emphasis from the hypothesis, not a match to it either.

## The real limitation this surfaces: lookback-window sensitivity

`10Y` at `~4%` in late 2025 reads as "extremely high" against a longer
memory (the nine years, 2009-2021, when rates sat near zero) but is
close to *average* against this study's pre-committed 756-session
(~3yr) trailing window, because that window is itself mostly populated
by the already-elevated 2023-2025 period. This is disclosed, not
resolved: the "10Y too high" narrative and this study's z-score can both
be correct simultaneously, because they're implicitly measuring against
different reference periods. A longer lookback (e.g. 10yr) is a
genuinely different, separately-locked design, not a parameter tweak to
this one — reusing this same locked result under a new lookback would be
exactly the kind of post-hoc adjustment this project's discipline
forbids.

## What this means for the motivating narrative

Two closed studies now (v1, v2), same conclusion from different angles:
no historical precedent — crisis-driven or "not QE" — was preceded by
the specific curve shape the user was watching for. The current episode
itself (2025 RMP) doesn't fit it either, once measured on a
pre-committed, undodgeable definition. This closes the yield-stress
precursor line as framed; a materially different design (longer
lookback, different reference period, or a different variable entirely)
would be new, independently-justified work, not a retry.

## Reproducibility

- Artifacts: `output/research/fed-put-yield-stress-precursor-v2/59ef27791a68e7750848b772c070196d403c739d9539efd12f8f4d9e0d7e6e5f/`.
- Byte-identical on independent rerun.
- No trade, no cost, no position, no sleeve.

[Protocol](../research-protocols/fed-put-yield-stress-precursor-v2.md)
· [v1 (amended)](fed-put-yield-stress-precursor-v1.md)
· [Machine specification](../../research/experiments/fed-put-yield-stress-precursor-v2.json)
