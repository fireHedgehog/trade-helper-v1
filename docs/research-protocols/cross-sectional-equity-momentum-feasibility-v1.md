# Cross-sectional equity momentum feasibility v1

Status: locked before execution. This is an **engine-feasibility check**,
not a Stage 9A candidate and not a confirmatory test. It answers one
question only: does the cross-sectional panel-bootstrap engine already
built for [ETF-12 rotation](etf12-cross-sectional-rotation-v1.md) run
correctly at real equity-universe scale (~500 assets instead of 12)? It
does not, and cannot, answer whether cross-sectional equity momentum is
real. See §1 and §2 for why, both disclosed before any data was touched.

## 1. Why this cannot be a confirmatory result — disclosed up front

Two independent reasons, neither fixable by this protocol's own design:

1. **Survivorship bias.** The universe (§3) is today's S&P 500 ∪ Nasdaq-100
   ∪ XL sector ETF membership, applied to the whole 2019–2026 history. Any
   company that was removed from either index in that window (bankruptcy,
   acquisition, delisting) is silently absent from the panel. This biases
   toward whatever a positive finding would look like — survivorship bias
   inflates apparent momentum/quality effects in exactly this design shape
   — so a positive result here is not trustworthy evidence either way, per
   [Tier 4 of the pending candidate
   checklist](../brainstorm/2026-08-19-pending-candidate-checklist.md) and
   the [cross-sectional idea
   library](../brainstorm/2026-08-20-cross-sectional-experiment-ideas.md).
2. **A disclosed pre-lock parameter peek.** While timing this engine's
   runtime at ~500 assets (an engineering question: is 2,000 resamples
   computationally feasible before committing to a locked resample count),
   the author computed the real pooled Spearman correlation on this exact
   panel using the module's bare default parameters (`formation=60`,
   `holding=20`, matching ETF-12 rotation's own defaults) before any
   specification was locked — a genuine violation of this project's own
   no-touch discipline, caught and disclosed rather than hidden. To keep
   this run honest rather than pretend the peek didn't happen, the locked
   parameters below (`formation=126`, `holding=21`) are deliberately
   different from what was peeked at — chosen for real, independent
   reasons (§4, the classic Jegadeesh & Titman 1993 6-month/1-month
   momentum horizon, appropriate for individual equities and not merely a
   copy of ETF-12's rotation-cadence-tuned 60/20), not picked to launder
   the peek. The correlation value observed during timing was not written
   down anywhere and did not influence any threshold or gate below, but a
   reader should not treat this run's number as clean regardless of which
   parameters were used, given reason 1 above already rules out
   confirmatory status on its own.

Because of both, this run's decision vocabulary (§6) never uses
`material_and_consistent`, `reject`, or any word implying a real verdict.

## 2. What this run is for

The [cross-sectional idea library](../brainstorm/2026-08-20-cross-sectional-experiment-ideas.md)
identified six ideas (CS-01/02/03/04/05/09) that all need real
cross-sectional breadth to mean anything — ETF-12's `N=12` is far too thin
(Grinold–Kahn). Before any of them can become a real Stage 9A candidate,
two separate things are needed: (a) survivorship-bias-free point-in-time
universe data (Tier 4, real cost, not yet purchased) and (b) proof that the
existing panel-bootstrap engine (`etf12_rotation_bootstrap`) mechanically
scales to hundreds of assets without a redesign. This protocol tests (b)
only, using the free, already-fetched, currently-survivorship-biased
~500-symbol universe as a stand-in — exactly the same free-data-first
sequencing this project used for the macro line (`app.macro_pit`, `0.60.0`,
built before any hypothesis is scored against it).

## 3. Universe

`build_universe()` (S&P 500 ∪ Nasdaq-100 ∪ 11 XL sector ETFs, `529`
symbols) intersected with what `data/market.db` actually holds, further
restricted to symbols with a first stored date on or before `2019-01-01` —
chosen because it is the latest cutoff that keeps ≥90% of the intersected
universe (`495`/`527`, ~94%) while giving a ~7.5-year common window with
ample formation/holding room. Every exclusion is named, not averaged away:

- Missing from `data/market.db` entirely (`2`): `RDDT`, `VMRK`.
- Present but first-traded after the cutoff (`32`, mostly 2020s IPOs and
  spin-offs): `ABNB`, `ALAB`, `APP`, `ARM`, `CARR`, `CEG`, `COIN`, `CRWD`,
  `CRWV`, `CTVA`, `DASH`, `DDOG`, `DOW`, `EXE`, `FDXF`, `FOX`, `FOXA`,
  `GEHC`, `GEV`, `HONA`, `HOOD`, `KVUE`, `NBIS`, `OTIS`, `PLTR`, `Q`,
  `RKLB`, `SNDK`, `SOLV`, `SPCX`, `UBER`, `VLTO`.
- Final universe: `495` symbols, common date range `2019-01-01` to
  `2026-08-14` (the tightest shared window across all 495, computed as a
  true set-intersection of trading dates per symbol, not a min/max range —
  two symbols each had one idiosyncratic single-day gap inside that range
  that a naive range filter would have missed).

No sector/industry classification exists for this universe (a gap the
cross-sectional idea library already named for `CS-07`/`CS-08`) — unlike
ETF-12 rotation, this protocol has **no cluster/sector breadth gate**. That
gate is dropped, not silently omitted: ETF-12's version depended on
`portfolio_universe.py`'s locked 12-ETF classification, which does not
extend to individual equities.

## 4. Formation, holding, and rebalance

- Formation: $F_i(t) = close_i(t)/close_i(t-126) - 1$ — 6-month momentum,
  the classic Jegadeesh & Titman (1993) horizon for individual equities.
- Holding: $G_i(t) = close_i(t+21)/close_i(t) - 1$ — 1-month forward
  return, the classic monthly-rebalance pairing.
- Rebalance grid: warm-up `126` sessions, spacing `21` sessions (equals the
  holding horizon, avoiding overlapping-window rebalances, same principle
  ETF-12 rotation used with `spacing == holding == 20`).
- Rank: average-rank tie-breaking, cross-sectional `n = 495` per rebalance
  date (vs. ETF-12's `n = 12`).

## 5. Estimand and bootstrap

Identical statistic and machinery to ETF-12 rotation, unmodified: pooled
Spearman rank correlation between formation rank and forward rank across
all (asset, rebalance date) pairs, tested via
`etf12_rotation_bootstrap` — the same joint-panel block-resampling null
(one shared resampled date-block sequence applied to all 495 assets per
resample, preserving real contemporaneous correlation). `block_bars=21`,
`resamples=2,000`, `seed=17291` (same seed as every other locked
protocol this session, for consistency, not because it is meaningful
here). A pre-lock timing probe (§1, reason 2) measured `2,000` resamples
at ~`1.7` minutes on this panel — computationally trivial, confirming (b)
from §2 is answerable either way.

## 6. Decision vocabulary — deliberately not the standard set

`permitted_decisions`: `engine_feasible`, `engine_not_feasible`. Nothing
else. `engine_feasible` requires: the bootstrap executes without error,
`rebalance_date_count > 0`, the observed correlation and `p_value` are
finite and well-formed, and the joint-resampling loop completes all 2,000
iterations. `engine_not_feasible` is any crash, degenerate output (NaN,
undefined correlation from zero-variance ranks), or a resample loop that
does not complete. The raw observed correlation and `p_value` are recorded
and reported for transparency, but are explicitly non-evidential per §1 —
neither this protocol nor any downstream reader may cite them as evidence
for or against real cross-sectional equity momentum.

`forbidden_outputs`: `material_and_consistent`, `not_material_or_not_consistent`,
`reject`, `revise`, `continue_research`, `alpha`, `entry_signal`,
`exit_signal`, `stop`, `position_size`, `sleeve`, `sharpe`.

## 7. Scope exclusions

No trade, no cost model, no sector/cluster breadth gate (§3), no claim
about real-world predictive power. This protocol authorizes nothing beyond
its own `engine_feasible`/`engine_not_feasible` verdict; any future
cross-sectional equity candidate still needs its own hypothesis-engineering
note, Stage 9A score, and preregistration, and — separately — either the
Tier 4 data purchase or an accepted, disclosed survivorship-bias caveat
strong enough to survive that scoring.
