# Cross-sectional equity momentum v1 — point-in-time re-baseline (CS-01)

Status: executed and closed as `not_material_or_not_consistent`. See the
[result](../research-results/cross-sectional-momentum-v1.md). Confirmatory attempt — unlike
[cross-sectional equity momentum feasibility v1](cross-sectional-equity-momentum-feasibility-v1.md),
which was engine-only and explicitly non-evidential, this protocol is a real
Stage 9B test of the same estimand ETF-12 rotation and the feasibility check
both used, now with real point-in-time S&P 500 membership.

Selection authority: [Stage 9A Cycle 7](../research-candidates/2026-08-21-cycle-7.md),
scored `14/16`, re-scoring [Cycle 1](../research-candidates/2026-08-19-cycle-1.md)/[Cycle 6](../research-candidates/2026-08-20-cycle-6.md)'s
"Data readiness `0`" disqualification now that [`universe_pit.py`](../../backend/app/universe_pit.py)
(`0.81.0`) exists. Operationalization record:
[cross-sectional-momentum-v1.md](../research-hypotheses/cross-sectional-momentum-v1.md).

## 1. What changed, and what didn't

Identical estimand, statistic, and null-construction philosophy to
[ETF-12 rotation](etf12-cross-sectional-rotation-v1.md) and the
[feasibility check](cross-sectional-equity-momentum-feasibility-v1.md):
pooled Spearman rank correlation between formation rank and forward rank,
tested against a joint-panel block-resampled null. What's new is the
universe construction (§3) and the engine itself, which now masks each
rebalance date's cross-sectional rank to real point-in-time members only
(`rotation_pooled_correlation_masked` / `cross_sectional_momentum_bootstrap`,
`backend/app/research.py`, `0.81.0`) instead of ranking every symbol at
every date regardless of whether it was actually in the index yet.

## 2. Why this is not fully survivorship-bias-free — disclosed up front

Real point-in-time *membership* now exists (`universe_pit.py`), but real
point-in-time *price history* for every historical member does not: of
`1,206` distinct symbols ever recorded as an S&P 500 member since 1996, only
`501` have any stored bars at all in this project's database — the other
`705` (mostly names delisted, acquired, or renamed before this project ever
fetched their prices) are unrecoverable from existing data. This is a
**different, narrower** bias than the one being fixed:

- **Fixed**: reverse-survivorship / look-ahead contamination — a symbol
  added to the index in, say, 2023 no longer contaminates a 2019 rebalance
  date's ranking just because it happens to be a member *today*. Verified
  real: `134` genuine point-in-time additions to the S&P 500 since
  `2019-01-01` exist among the `501` bars-covered symbols (e.g. `TSLA`
  joined `2020-12-21`, `META` and its peers on their own real dates) — the
  prior design would have ranked all of them from day one of the window
  regardless.
- **Not fixed**: a name that left the S&P 500 and was never re-fetched
  (or was delisted before Yahoo/`fetch.py` ever captured it) is simply
  absent from the panel for the whole window, not just before/after its
  real membership — the same standing limitation named in the feasibility
  protocol's §1, unresolved by point-in-time membership data alone. Within
  the `501` bars-covered symbols, `33` real historical exits are captured
  (mostly pre-`2019`, e.g. `AMD` `2013-09-23`, `DELL` `2013-10-29`, `DOW`
  `2017-09-01`), plus `2` genuine re-entries in-window (`PCG`: exit
  `2019-01-18`, re-entry `2022-10-03`; `FISV`/`FI`: exit `2023-06-07`,
  re-entry `2025-11-11`) — real churn, but a small, non-random sample of
  all historical exits (survivors of *this project's own fetch history*,
  not of the S&P 500 itself).

Because of this residual bias, this protocol's decision vocabulary (§7)
still cannot claim a clean `material_and_consistent` free of caveat — a
positive result must be reported alongside this section, not silently. A
`not_material_or_not_consistent` result is unaffected by this caveat (a null
is a null regardless of which direction the residual bias could have
pushed).

## 3. Universe

All symbols with **both** (a) at least one point-in-time S&P 500 membership
interval in `universe_membership` (`index_name='SP500'`) and (b) at least
one stored bar in `bars` — `501` symbols. Deliberately narrower than the
feasibility check's `495` (S&P 500 ∪ Nasdaq-100 ∪ 11 XL sector ETFs): this
protocol has no point-in-time membership data for Nasdaq-100 or the XL
ETFs, so including them would silently revert to the "always eligible"
survivorship-biased treatment for that subset — dropped entirely rather
than mixed with the masked subset.

**Date alignment**: SPY's own stored trading-date index (a complete NYSE
session calendar by construction) restricted to `2001-01-01` onward — the
point-in-time source's own maintainer flags `1996`-`2000` as lower-confidence
(§ operationalization record) — through the latest common date. Each of the
`501` symbols' closes are reindexed onto this calendar (introducing `NaN`
outside that symbol's own stored coverage, not forward-filled or
interpolated). Unlike the feasibility check's true set-intersection (which
required every symbol to share the exact same dates), this protocol does
**not** require universal overlap: a symbol contributes to exactly the
rebalance dates where it has real price data *and* real point-in-time
membership, simultaneously. This is the correct alignment for a
time-varying-eligibility design — insisting on full intersection across `501`
symbols with wildly different real histories would either shrink the window
to whatever the shortest-lived symbol allows or silently drop legitimate
churn cases.

## 4. Eligibility mask (the core of this protocol)

For symbol $i$ at session index $t$: eligible iff **all** of:

1. $i \in \text{members\_asof}(\text{date}(t))$ — real point-in-time
   S&P 500 membership (`app.store.members_asof`);
2. $\text{close}_i(t)$, $\text{close}_i(t-126)$, and $\text{close}_i(t+21)$
   are all present (not `NaN`) — real stored price data at formation,
   decision, and forward-outcome dates.

A rebalance date with fewer than `2` eligible symbols is skipped (no rank is
computable), not treated as a zero-correlation observation — see
`rotation_pooled_correlation_masked`'s own documented behavior. Membership
is a fixed, known-in-advance calendar fact; it is never resampled, only the
return panel is (§6) — identical discipline to how `formation`/`holding`/
`spacing` are already treated as fixed grid parameters, not resampled,
throughout every prior protocol in this project.

## 5. Formation, holding, and rebalance

Unchanged from the feasibility check, for direct comparability and because
no new pre-lock peek has occurred:

- Formation: $F_i(t) = \text{close}_i(t)/\text{close}_i(t-126) - 1$ — 6-month
  momentum (Jegadeesh & Titman 1993).
- Holding: $G_i(t) = \text{close}_i(t+21)/\text{close}_i(t) - 1$ — 1-month
  forward return.
- Rebalance grid: warm-up `126` sessions, spacing `21` sessions.
- Rank: average-rank tie-breaking, computed only over each date's eligible
  subset (§4), not the full `501`.

## 6. Estimand and bootstrap

Pooled Spearman rank correlation between formation rank and forward rank
across all (eligible asset, rebalance date) pairs, via
`cross_sectional_momentum_bootstrap` (`backend/app/research.py`, `0.81.0`):
identical joint-panel block-resampling null to ETF-12 rotation and the
feasibility check (`block_bars=21`, `resamples=2,000`, `seed=17291`) —
the same resampled date-block sequence is applied to every symbol's return
series simultaneously, preserving real contemporaneous correlation, while
the eligibility mask itself stays fixed across every resample (§4 — a
calendar fact, not something a return-shuffling null should also
randomize).

## 6b. One more disclosed null-construction caveat

The block-resampling null needs a complete return series per symbol across
the whole aligned calendar to build a synthetic price path (the existing
bootstrap machinery cannot operate on `NaN`); a symbol's real history
shorter than the full calendar (e.g. a recent addition with no real prices
before its IPO) is forward/back-filled with flat, zero-return placeholder
values for that purpose only. The **observed** correlation never touches a
filled value — the eligibility mask (§4) is built from real, unfilled data
and gates every real-position calculation. But a **resampled** iteration can
still draw a block from a symbol's filled placeholder segment even for a
window ending at a real, eligible date, injecting a spurious zero-variance
stretch into that resample's synthetic path for that asset. This narrows
the null's variance slightly (conservative-leaning, not anti-conservative)
rather than invalidating it, and is disclosed here rather than discovered
after seeing a result.

## 7. Decision vocabulary

`permitted_decisions`: `material_and_consistent`, `not_material_or_not_consistent`,
`invalid`.

- `material_and_consistent` requires: pooled Spearman correlation `≥ 0.10`
  **and** one-sided `p ≤ 0.05` against the joint-panel null, **and** must be
  reported with §2's residual-bias caveat attached — never as a clean,
  unqualified confirmation.
- `not_material_or_not_consistent`: correlation or significance gate fails.
  Unaffected by §2's caveat.
- `invalid`: implementation, leakage, reproducibility, or eligibility-mask
  checks fail (see §9 lock checklist).

`forbidden_outputs`: `reject`, `revise`, `continue_research`, `alpha`,
`entry_signal`, `exit_signal`, `stop`, `position_size`, `sleeve`, `sharpe`,
`engine_feasible`, `engine_not_feasible` (that vocabulary belongs to the
separate, already-closed feasibility check, not this protocol).

## 8. Multiplicity, dependence, and trial ledger

One family: one pooled estimand, one eligibility mask design, one locked
formation/holding/spacing grid — no parameter sweep. Append one
`preregistered_no_results` attempt to `research/attempts.jsonl` with
`variant_count=1` and dependence group `cross-sectional-momentum-v1` before
execution.

## 9. Lock checklist

- Eligibility mask (§4) combines real point-in-time membership and real
  data availability, computed once on the real panel, before any resample.
- No parameter grid; formation/holding/spacing identical to the feasibility
  check (no new peek).
- Residual survivorship bias (§2) stated precisely, with real counts, before
  any correlation is computed — not discovered after seeing a favorable
  number.
- Unit fixtures already added (`backend/tests/test_cross_sectional_momentum_v1.py`):
  masked ranking excludes non-members from a date's rank; a date with `<2`
  eligible members is skipped, not zero; no future bar affects an earlier
  eligible date's rank; the masked bootstrap detects genuine persistent rank
  on a synthetic panel.
- `research/experiments/cross-sectional-momentum-v1.json` locks every
  constant above; `data` fingerprint fields are `null` until computed at
  execution time.
