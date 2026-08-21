# Sector-level cross-sectional momentum v1 — GICS sector rotation

Status: executed and closed as `not_material_or_not_consistent`. See the
[result](../research-results/sector-rotation-v1.md). Confirmatory attempt, same estimand shape
as [ETF-12 rotation](etf12-cross-sectional-rotation-v1.md) and
[CS-01](cross-sectional-momentum-v1.md), applied at the GICS-sector
aggregate level (`11` sectors) instead of individual ETFs (`12`) or
individual stocks (`501`).

Selection authority: [Stage 9A Cycle 8](../research-candidates/2026-08-21-cycle-8.md),
scored `15/16`. Operationalization record:
[sector-rotation-v1.md](../research-hypotheses/sector-rotation-v1.md).

## 1. What's reused, and what's new

Reused, unmodified: `backend/app/research.py:etf12_rotation_bootstrap` —
the exact same pooled-Spearman-rank-correlation-vs-joint-panel-block-null
engine ETF-12 rotation and CS-01 both used. No new statistical machinery.
New: a **sector-aggregation step** (§4) that turns `501` individual stock
price series plus point-in-time membership plus GICS labels into `11`
synthetic sector-index price series, which is what actually gets fed to the
unmodified engine.

## 2. Disclosed limitation — today's GICS classification, not point-in-time

`universe_sectors.py` (`0.83.0`) captures **today's** GICS Sector
classification only. A stock reclassified between sectors at some point in
its real history (a real, documented occurrence — GICS periodically
reassigns companies) is attributed to its *current* sector for its *entire*
price history in this design. This is a real, disclosed limitation,
distinct from and in addition to CS-01's own residual survivorship-bias
disclosure — it does not make the estimand unmeasurable (Stage 9A's
`Data readiness` score is `2`, not `0`), but any positive result here must
be reported alongside this caveat, not silently.

## 3. Universe

The same `501`-symbol universe as CS-01 (real point-in-time S&P 500 members
with stored bars), further restricted to symbols with a real GICS
classification in `equity_sectors` (all `501` have one — `universe_sectors.py`
and `universe_pit.py` both source from S&P 500 membership, so coverage is
complete by construction). Grouped into GICS Sector (`11` distinct values).

## 4. Sector-aggregation methodology (the new step)

For each session `t` and each GICS sector `s`:

1. Eligible members: stocks that are simultaneously (a) real point-in-time
   S&P 500 members on date `t` (`members_asof`), (b) classified into sector
   `s` (today's GICS label), and (c) have a real, non-`NaN` close on both
   session `t` and session `t-1` (needed to compute a daily return).
2. Sector daily return: the **equal-weighted average** of eligible members'
   session-over-session simple returns. Equal-weighted, not cap-weighted,
   because cap-weighting a sector aggregate would let one or two megacap
   names dominate the "sector" signal — exactly alternative (b) named in
   the operationalization record, avoided by construction rather than left
   to confound the result.
3. A sector-date with fewer than `2` eligible members produces no return
   for that sector on that date (carried forward as `0%` for that session
   only, so the compounding index stays defined — disclosed, not hidden;
   in practice every GICS sector has well over `2` eligible S&P 500 members
   on every session in the analysis window).
4. Synthetic sector-index level: compound each sector's daily return series
   into a price-like level series starting at `100` (`level_t = level_{t-1}
   × (1 + return_t)`), producing an `11`-column matrix in the exact shape
   `etf12_rotation_bootstrap` already expects.

## 5. Formation, holding, and rebalance — independently chosen, not copied

- Formation: `252` sessions (~12 months) — chosen to match the natural
  cadence of a sector/thematic rotation claim (capex, rate, and demand
  cycles play out over quarters to years, not weeks), and to match the
  horizon in the user's own real-world observation ("long chips... over
  roughly the past year"). Deliberately different from CS-01's `126`
  (6-month, Jegadeesh-Titman individual-stock convention) — a different
  estimand justifies a different, independently-reasoned horizon, not a
  copy.
- Holding: `21` sessions (~1 month) — same monthly-rebalance convention as
  every other protocol this session, for direct comparability of the
  *rebalance cadence*, while the *formation* window is what actually
  differs and is justified above.
- Rebalance grid: warm-up `252` sessions, spacing `21` sessions.
- Rank: average-rank tie-breaking, `11` sectors per rebalance date (no
  masking needed — a GICS sector as a category exists on every session by
  construction, unlike an individual stock's point-in-time membership).

## 6. Estimand and bootstrap

Pooled Spearman rank correlation between sector formation rank and sector
forward rank across all (sector, rebalance date) pairs, via
`etf12_rotation_bootstrap`, unmodified: `block_bars=21`, `resamples=2,000`,
`seed=17291` — same joint-panel block-resampling null as every prior
protocol this session, applied to the `11`-column synthetic sector-index
panel instead of the `12`-column ETF panel or the `501`-column (masked)
equity panel.

## 7. Decision vocabulary

`permitted_decisions`: `material_and_consistent`, `not_material_or_not_consistent`,
`invalid`.

- `material_and_consistent` requires: pooled Spearman correlation `≥ 0.10`
  **and** one-sided `p ≤ 0.05` against the joint-panel null, **and** must be
  reported with §2's today's-classification caveat attached.
- `not_material_or_not_consistent`: correlation or significance gate fails.
  Unaffected by §2's caveat.
- `invalid`: implementation, leakage, reproducibility, or aggregation-
  methodology checks fail.

`forbidden_outputs`: `reject`, `revise`, `continue_research`, `alpha`,
`entry_signal`, `exit_signal`, `stop`, `position_size`, `sleeve`, `sharpe`.

## 8. Multiplicity, dependence, and trial ledger

One family: one pooled estimand, one aggregation methodology, one locked
formation/holding/spacing grid — no parameter sweep. Append one
`preregistered_no_results` attempt to `research/attempts.jsonl` with
`variant_count=1` and dependence group `sector-rotation-v1` before
execution.

## 9. Lock checklist

- Sector-aggregation methodology (§4) specified precisely before any data
  is touched, including the equal-weight-not-cap-weight decision and its
  reason.
- Formation/holding independently justified (§5), not copied from CS-01.
- Today's-classification limitation (§2) stated precisely up front.
- No parameter grid.
- `research/experiments/sector-rotation-v1.json` locks every constant
  above; `data` fingerprint fields are `null` until computed at execution
  time.
