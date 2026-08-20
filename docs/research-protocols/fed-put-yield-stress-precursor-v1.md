# Fed put: yield-stress precursor v1

Status: locked before execution. [Thesis Track](../thesis-track-small-n.md)
candidate — 4 real episodes, not the block-bootstrap family. Implements
the reframed claim in the [Fed put
memo](../brainstorm/2026-08-19-fed-put-long-end-reversal.md): does
long-end yield stress, with the short end contained, precede Fed
balance-sheet expansion? Not "does QE cause yield reversal" (common
knowledge, not a real edge).

## 1. Hypothesis and falsifier

- $H_0$: the yield-stress score (§3) in the 60 sessions before a real QE
  launch is no higher than in a random placebo window of the same length.
- $H_1$: it is higher, at a rate a placebo-window null would not produce
  by chance.
- Falsifier: the precursor score is not elevated before real launches
  relative to the placebo distribution, or is elevated but no more than
  chance given the empirical null.

Explicitly out: any claim about a specific Fed official's intentions —
narrative, not quantifiable, never enters this thesis (same exclusion as
the memo).

## 2. Universe and provenance

`DGS2`, `DGS10` (nominal constant-maturity Treasury yields), `fred.py`'s
`bars` table, common date range `1976-06-01`–`2026-08-18` (`12,550`
sessions; DGS2 is the binding start).

**Point-in-time justification (not ADR 0006's ALFRED mechanism):**
verified live (2026-08-20) that `DFII10`'s ALFRED vintage history shows
the *value* never changes across "revisions" (e.g. `2003-05-28`'s `1.83`
repeats across 4 stamps) — these are ALFRED re-publication timestamps,
not real revisions. But early `release_datetime`s reflect when FRED
*backfilled* old data into ALFRED (`2005-10-12` for a `2003-05-28`
observation), not when the market actually knew the yield — using that
timestamp would *understate* real availability. Treasury yields are
published same-day via the Treasury's own H.15 release, a genuinely
public, real-time record. Correct, disclosed convention here: use
`fred.py`'s final-revised series (correct, since the value never
actually revises) with the trading date itself as the availability
date — better-justified than ALFRED's backfill-contaminated timestamp
for this specific series shape, not a shortcut.

## 3. Yield-stress score

$$z_s(t) = \frac{y_s(t) - \overline{y_s}(t-756:t)}{\sigma(y_s(t-756:t))}, \quad s \in \{2Y, 10Y\}$$

756-session (~3yr) strictly-trailing lookback (excludes $t$ itself, no
look-ahead), chosen for "multi-year high/low" framing, not mined from
this data.

$$score(t) = z_{10Y}(t) - |z_{2Y}(t)|$$

High when the long end is stressed relative to its own history *and* the
short end stays near its own mean — directly operationalizes "2Y ok, 10Y
too high," and structurally excludes recession-driven curve *inversion*
(which typically shows the short end also at an extreme, pricing cuts or
continued hikes) without needing a separate inversion filter.

## 4. Episodes (dated by official FOMC/Desk record, not by this series)

| Episode | Start (announcement) | End (approx. completion) |
|---|---|---|
| QE1 | 2008-11-25 | 2010-03-31 |
| QE2 | 2010-11-03 | 2011-06-30 |
| QE3 | 2012-09-13 | 2014-10-29 |
| COVID QE | 2020-03-23 | 2022-03-16 |

Verified against the Federal Reserve's own balance-sheet-policy timeline
and contemporaneous reporting (2026-08-20), not from memory. Start dates
are precise (single-day announcements); end dates are approximate
wind-down completions, disclosed as less precise than starts for all 4,
not selectively. **No episode boundary is derived from `DGS2`/`DGS10`
themselves** — deriving boundaries from the outcome series would be
circular, per Thesis Track's own rule.

## 5. Estimand and statistic

Per-episode statistic: $\max(score(t))$ over the 60 sessions immediately
before the episode's start date. One number per episode (4 total) — no
within-episode daily statistic enters inference, per Thesis Track rule 2.

## 6. Inference — `app.thesis_track`

Placebo-in-time randomization (`thesis_track_p_value`): observed = mean
of the 4 real per-episode statistics. Null = 5,000 resamples, each
drawing 4 random 60-session windows from the full `1976`–`2026` history,
excluding any window overlapping `[episode_start - 60, episode_end + 60]`
for any real episode (keeps the null from being contaminated by
real-signal-adjacent periods). One-sided p-value: fraction of resamples
with synthetic mean $\ge$ observed mean, plus add-one correction.
`resamples=5000`, `seed=17291` (project convention, not tuned here).

## 7. Power pre-commitment (mandatory, before results)

At $n=4$, this is expected to be underpowered by construction — see
[Thesis Track](../thesis-track-small-n.md#power-pre-commitment)'s general
warning. A null or inconclusive result here is `not evaluable`/
`insufficient evidence`, never silently reframed as a real rejection of
the underlying mechanism.

## 8. Materiality / decision

No trade, no cost model, no position. `permitted_decisions`:
`not_evaluable`, `weak_evidence`, `evidence_present` — deliberately not
`reject`/`revise`/`continue_research` (this is Thesis Track's exploratory
evidence layer, not a Stage 9B trade-eligibility decision). Reading rule,
fixed before results: $p \le 0.10$ (looser than the usual `0.05`, an
explicit, disclosed concession to $n=4$'s power ceiling — the tightest
possible sign-test bound at $n=4$ is itself `0.0625` two-sided) →
`evidence_present`; $0.10 < p \le 0.30$ → `weak_evidence`; otherwise
`not_evaluable`.

## 9. Scope exclusions

No trade, no cost, no signal, no sleeve. Does not authorize any Stage 9B
work — a real trading expression, if this clears evidence review, is a
separate, later, separately-locked protocol.
