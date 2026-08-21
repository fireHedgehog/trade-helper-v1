# 2026-08-19 — pending candidate checklist, cheap to orthogonal

> Brainstorm · non-evidential · loaded only on explicit request · no acceptance weight.
> A personal recall list, not a plan. Nothing here is scored, prioritized, or
> authorized. An item only becomes real via hypothesis engineering → Stage 9A
> scorecard → preregistration, same as every candidate so far.

Ordering principle: **work top to bottom.** Each tier costs more — engineering,
new data, real money — than the one above. Don't skip a tier because the
cheap ones disappointed; that's cheap information, a purchased dataset
failing is not.

**Status (2026-08-20): Tiers 0-2 fully cleared.** Every item in them is
closed, all `not_material_or_not_consistent`/`not_evaluable`, different
reasons each — see [research-protocols/README.md](../research-protocols/README.md)
for the one-line-per-result index rather than re-reading this file's own
history. This is why the single-asset/time-series line is now formally
[parked](../stage-closures/2026-08-20-single-asset-time-series-line.md).

## Tier 0 — closed

- [x] TA Breakout v1 — `not_material_or_not_consistent`, weak event/placebo separation. [Result](../research-results/ta-breakout-v1.md).
- [x] Wave Pull — `not_material_or_not_consistent`, clean separation, still null. [Result](../research-results/wave-pull-v1.md).

## Tier 1 — closed

- [x] RSI mean-reversion — `not_material_or_not_consistent`, power limitation not a confound. [Result](../research-results/rsi-oversold-reversal-v1.md).
- [x] S/R Bounce — not prioritized, `0` on distinct information vs. Cycle 1. A distinct round-number-levels construction exists but is blocked: fetched prices are adjusted (ADR 0002), and adjusted vs. real nominal history diverges substantially for most locked assets — a real governance/data decision, not a redesign task.
- [x] Turn-of-month — `not_material_or_not_consistent`, well-powered null. [Result](../research-results/calendar-turn-of-month-v1.md).
- [x] Day-of-week — `not_material_or_not_consistent`, directionally consistent but not significant. [Result](../research-results/calendar-day-of-week-v1.md).
- [x] Overnight-gap — `not_material_or_not_consistent`, decisively opposite-signed (12/12). [Result](../research-results/overnight-gap-continuation-v1.md).

## Tier 2 — closed

- [x] CTA v2 — picked up directly (2026-08-20), `not_material_or_not_consistent`: materiality cleared, significance and paired placebo test did not, depends on 2008. [Result](../research-results/cta-v2-pooled-trend-overlay.md).
- [x] ETF-12 rotation — `not_material_or_not_consistent`, cleanest negative of the session (ρ=0.045, p=0.266). [Result](../research-results/etf12-cross-sectional-rotation-v1.md).

## Tier 3 — needs new but still free/accessible data

Engineering gap closed (`0.60.0`/`0.61.0`): `app.macro_pit` implements ADR
0006 clauses 2-4, live-verified against the real FRED API. Ingestion
existing authorizes nothing — every item below still needs its own
preregistered hypothesis and Stage 9A score.

- [ ] Any macro-conditioned strategy (e.g. [long-end yield shock](2026-08-19-long-end-yield-shock.md)) — engineering unblocked, still needs its own hypothesis.
- [x] Fed put: yield-stress precursor — see [memo](2026-08-19-fed-put-long-end-reversal.md). Three independent designs (v1 n=4, v2 n=6 adding real "not QE" actions, v3 20yr lookback), all `not_evaluable`. One live finding: the current episode (2025 RMP) is the only one that matches the hypothesized pattern under a 20yr lookback — real, but not confirmable by a 6-episode pooled test. [Results: v1](../research-results/fed-put-yield-stress-precursor-v1.md) · [v2](../research-results/fed-put-yield-stress-precursor-v2.md) · [v3](../research-results/fed-put-yield-stress-precursor-v3.md). Closes this line — a follow-up needs a new mechanism, not a retry.

## Tier 4 — orthogonal, multidimensional, real cost

Nothing here is free — needs a vendor relationship or paid feed before
operationalizing, per the [taxonomy brainstorm](2026-08-19-strategy-taxonomy-benchmark-research-tracks.md)'s
Class B framing: pay for data only after a cheap, same-shape test survives.

- [x] Point-in-time equity membership/delisting data — turned out not to need a vendor purchase at all: [`universe_pit.py`](../../backend/app/universe_pit.py) (`0.81.0`) ingests a free, MIT-licensed, hand-maintained S&P 500 membership history ([fja05680/sp500](https://github.com/fja05680/sp500)), live-verified (`1,259` intervals, `1,206` symbols, `503` currently active). Shared blocker behind 6 [cross-sectional idea library](2026-08-20-cross-sectional-experiment-ideas.md) candidates, now cleared for the S&P 500 subset. CS-01 itself is done — operationalized, scored ([cycle 7](../research-candidates/2026-08-21-cycle-7.md)), preregistered, executed, and closed `not_material_or_not_consistent` ([result](../research-results/cross-sectional-momentum-v1.md)) same day. CS-02/03/04/05/09 remain open — each still needs its own hypothesis-engineering note, Stage 9A score, and preregistration.
- [ ] Futures continuous-contract and roll data — unlocks a genuine Moskowitz/Ooi/Pedersen-shape diversified futures-trend candidate; `fetch.py` builds neither today.
- [ ] Point-in-time fundamentals (statements, revisions) — unlocks value/quality factors; Class B2 in the taxonomy brainstorm.
- [ ] Options-implied volatility, Greeks, and open interest (by strike, daily) — forward-looking risk measure, market-implied macro expectation, and the raw ingredient for a "call wall/put wall" (largest OI strike above/below spot -- a derived metric, not a separate purchase). Cheapest real option researched `2026-08-21`: [EODHD US options API](https://eodhd.com/lp/us-stock-options-api), `$99.99/mo`, 6,000+ US stocks, all 5 Greeks, IV, OI with day-over-day change, 42+ fields/contract -- but only `Q4 2023`-present (<3yr history). Deeper history means OptionMetrics IvyDB or CBOE DataShop, neither with public pricing (real cost, four-figures/year territory). Not purchased -- no queued hypothesis needs it yet, per this file's own Class B framing.
- **Level 2 / order-book depth: considered and excluded, not a checklist item.** Researched `2026-08-21` (Databento, metered/pay-per-byte, cheapest available access model). Not queued because it is already out of scope by design ([data-layers.md](../data-layers.md)'s "Intraday/tick" row): this project only ever reaches bounded paper trading (ADR 0008), never live/HFT execution, so microstructure-priced data buys nothing it would use.

## Promotion status

None promoted. Revisit and re-check items as they get picked up, dropped,
or superseded — this file is meant to be edited, not archived.
