# Cross-sectional equity momentum — operationalization record

Status: operationalization record per [hypothesis-engineering.md](../hypothesis-engineering.md). This is CS-01 from the [cross-sectional idea library](../brainstorm/2026-08-20-cross-sectional-experiment-ideas.md), re-baselined now that [`universe_pit.py`](../../backend/app/universe_pit.py) (`0.81.0`) clears the point-in-time membership blocker that made every prior attempt at this estimand non-confirmatory. **Executed and closed**, same day: [result](../research-results/cross-sectional-momentum-v1.md), `not_material_or_not_consistent`.

## Why re-open a "closed" idea

[ETF-12 cross-sectional rotation v1](../research-results/etf12-cross-sectional-rotation-v1.md) already tested this exact estimand shape and closed clean: pooled ρ=0.045 against a 0.10 floor, p=0.266, no confound, N=12. [Cross-sectional equity momentum feasibility v1](../research-results/cross-sectional-equity-momentum-feasibility-v1.md) proved the engine scales to N=495 but was explicitly non-confirmatory (today's-membership survivorship bias + a disclosed pre-lock parameter peek). Per [research-program.md](../research-program.md)'s own reopening rule, this is a normal continuation, not a reflexive retry: what's new is genuine breadth (N≈495 vs. 12) via real point-in-time membership, which is exactly the axis Grinold-Kahn (IR ≈ IC × √breadth) says a null at 12 names cannot speak to.

## Operationalization record

| Field | Answer |
|---|---|
| Claim | Among S&P 500 members at each rebalance date, prior 6-month formation-period return rank predicts subsequent 1-month forward return rank (positive cross-sectional correlation). |
| Scope | S&P 500 constituents only (not Nasdaq-100 or XL ETFs — `universe_pit.py` covers S&P 500 alone), 2001-01-01 onward (the point-in-time source's own maintainer flags 1996-2000 as lower-confidence), monthly rebalance, no regime restriction. |
| Mechanism | Behavioral underreaction to news (Jegadeesh & Titman 1993) or slow information diffusion across investor attention — the classic momentum rationale; not assumed true, this run tests whether it is measurable in this universe/period at all before asking why. |
| Market-belief proxy | Current price relative to its own 126-session-ago price (formation-period return) — a public, already-known quantity. |
| Reality proxy | Same quantity; this is a pure price-momentum claim, not a value/quality gap between price and a fundamental estimate. |
| Information set | At each rebalance date `t`, the eligible universe is `members_asof(t)` (genuinely knowable at `t` — no name enters the ranking before its real S&P 500 addition date, none stays after its real removal date) and each member's trailing 126-session close history, both fully available at `t`. |
| Estimand | Pooled Spearman rank correlation between formation-period rank and forward-period rank, across all (asset, rebalance date) pairs — identical statistic to ETF-12 rotation and the feasibility check, for direct comparability. |
| Alternatives | (a) Size/liquidity confound — momentum concentrated in illiquid small-caps within the index; (b) sector concentration — momentum is really a sector-rotation effect in disguise (no sector labels exist in this codebase, a named, disclosed gap, not silently ignored); (c) survivorship-bias residue — even with point-in-time membership, `bars` itself may still be missing some delisted names' price history entirely (see Data feasibility). |
| Falsifier | Observed pooled correlation at or below what a block-permuted null produces at the preregistered one-sided threshold (mirroring ETF-12 rotation's own falsifier design) — a null result here, at real breadth, is a complete, valid answer, not a defect. |
| Data feasibility | Point-in-time membership: available (`universe_pit.py`, free, hand-maintained, disclosed bimonthly lag and pre-2001 lower confidence). Price history: available for members still active or delisted after `bars`' own coverage start, but **not** for a name that was both added and removed from the S&P 500 entirely before Yahoo/`fetch.py` ever captured it — this residual gap must be measured and disclosed as its own exclusion list (same discipline the feasibility protocol's §3 used), not silently dropped. |
| Expression candidates | Long-short top-minus-bottom quintile portfolio (the standard momentum expression); long-only top-quintile overlay against Passive ETF-12 v1; `no trade` if the correlation does not clear its preregistered floor. |
| Path and risk | Monthly turnover from full quintile reconstitution (real cost, must be charged — see `factor-zoo`'s own `round_trip_cost_bps` precedent); concentration risk if momentum clusters in a handful of sectors/megacaps; liquidity assumed adequate (S&P 500 members only, no small-cap/micro-cap tail). |

## What must change in the engine before this can run

`etf12_rotation_bootstrap` (`backend/app/research.py`) assumes a **fixed** asset set for the whole sample (`closes_matrix` is one static matrix, ranked cross-sectionally at every rebalance date over the same columns). Real point-in-time membership means the eligible column set changes *by rebalance date* — a name ranked on one date may not exist yet or may have already left the index on another. This is not the "zero code change" the feasibility check needed; it requires a genuinely new, masked-ranking variant of `rotation_pooled_correlation` that: (a) restricts each rebalance date's cross-sectional rank to `members_asof(date)` only, (b) still applies one shared block-permuted date sequence across all assets in the bootstrap null (preserving the real contemporaneous-correlation discipline), and (c) handles a resampled date sequence pointing at a session where a given asset was not yet a member (exclude that asset from that resampled date's ranking, the same as the real-date case, not a lookup error). This is new engine work, scoped here so it isn't discovered mid-preregistration.

## Promotion gate

Per [hypothesis-engineering.md](../hypothesis-engineering.md)'s promotion gate: claim, information set, estimand, falsifier, and feasible data path are all explicit above. Next step is Stage 9A scoring (separate note), then preregistration — this record does not itself authorize a run.
