# Fed put: yield-stress precursor v3

Status: locked before execution. Amends [v2](fed-put-yield-stress-precursor-v2.md)
(closed `not_evaluable`) — same score formula, same 6 episodes, same
Thesis Track machinery. **One change only: the trailing lookback for the
z-scores, 756 sessions (~3yr) → 5,040 sessions (~20yr).**

## Why this is a real, separate design, not a parameter tweak

v2's own result disclosed the gap this closes: `10Y` at `~4%` in late
2025 reads as extreme against a ~20-year memory (a fresh high since June
2007, confirmed live) but as unremarkable against a 3-year trailing
window, because that window is itself mostly the already-elevated
2023-2025 period. User-directed (2026-08-20): test the multi-decade-extreme
reading directly, since that is what "rocket high" actually means in
the motivating narrative — not a 3-year deviation. This was named as a
follow-up requiring its own lock in v2's own result doc, not something
to silently substitute into a closed spec.

**A structural asymmetry to expect, disclosed before results:** Treasury
yields were in a secular decline for most of 1981-2020. A 20-year
trailing window for the older episodes (2008, 2010, 2012) mostly covers
a period of *higher*, not lower, yields than the episode itself — so
those episodes are structurally unlikely to register as a "20-year high"
regardless of the true mechanism, while 2025-2026 sits at the end of
that decline breaking into fresh multi-decade highs. A low score for the
older episodes here would not be surprising or contradictory; it is a
property of the long lookback crossing a genuine regime change in the
level of rates, not a design flaw.

## 1-2. Hypothesis, episodes

Unchanged from [v2](fed-put-yield-stress-precursor-v2.md) §1, §2 — same
6 episodes (QE1/2/3, COVID QE, 2019 bill purchases, 2025 RMP), same
dates, same sourcing discipline (operational record, never derived from
`DGS2`/`DGS10`).

## 3. Score — lookback changed, formula unchanged

$$z_s(t) = \frac{y_s(t) - \overline{y_s}(t-5040:t)}{\sigma(y_s(t-5040:t))}, \quad s \in \{2Y, 10Y\}$$

$$score(t) = z_{10Y}(t) - |z_{2Y}(t)|$$

5,040-session (~20yr) strictly-trailing lookback (excludes $t$). Verified
sufficient trailing history exists before the earliest episode (QE1,
2008-11-25: `8,116` sessions available, `5,100` needed including the
60-session precursor window).

## 4-7. Window, inference, power pre-commitment, decision

Unchanged from v2 §3 (window), §4-6 (inference, buffer, decision
vocabulary and reading rule). `resamples=5000`, `seed=17291`.

## 8. Scope exclusions

Unchanged — no trade, no cost, no signal, no Stage 9B authorization.
