# 2026-08-19 — pending candidate checklist, cheap to orthogonal

> Brainstorm · non-evidential · loaded only on explicit request · no acceptance weight.
> A personal recall list, not a plan. Nothing here is scored, prioritized, or
> authorized. An item only becomes real via hypothesis engineering → Stage 9A
> scorecard → preregistration, same as every candidate so far.

Ordering principle, stated so future-me doesn't skip it out of impatience:
**work top to bottom.** Each tier costs more — in engineering, in new data, in
real money — than the one above it. Jumping to a lower tier because the
cheap tiers disappointed is the FOMO trap, not a shortcut: two simple tests
failing is cheap information; a purchased dataset failing is not. Don't
"deweight" a tier by skipping it; deweight it by actually clearing it first.

Already resolved, not pending — listed only so they don't get re-proposed:
CTA v1 (`rejected`), consolidation support-recovery (`not_evaluable`), SMA
Cross v1 exposure-reduction (`not_material_or_not_consistent`).

## Tier 0 — already scored in Cycle 2, sitting idle

No new data, no new infrastructure. Just needs someone to pick one and start
hypothesis engineering again.

- [ ] **TA Breakout v1** — resistance-zone breakout, distinct from
  consolidation's mean-reversion-at-support. Scored (10/16) but not
  prioritized; lowest of the batch, explicit `0` on diversification.

## Tier 1 — cheap, single-asset, zero new infrastructure, data already in hand

Same shape as SMA Cross v1: one asset, existing daily bars, no engine to
build. This is where "next cheap test" should come from.

- [x] **RSI mean-reversion** — picked up in [Cycle
  3](../research-candidates/2026-08-19-cycle-3.md), scored `15/16`, highest
  of any candidate so far. Executed and closed
  [`not_material_or_not_consistent`](../research-results/rsi-oversold-reversal-v1.md):
  0/12 assets reached raw significance even before correction — a power
  limitation at 36-56 events per asset, not a confound like SMA Cross v1. A
  future attempt to fix the power problem (more events, pooled estimator)
  would be new, independently justified work, not a repair of this one.
- [x] **S/R Bounce formalization** — scored in [Cycle
  3](../research-candidates/2026-08-19-cycle-3.md): `0` on distinct
  information, too close to Cycle 1's already-closed consolidation work with
  a cruder detector. Not prioritised; would need a materially different
  construction to earn a re-look, same rule as any future consolidation
  matcher. `Fib Retrace` remains poor exploratory result, low priority; `Wave
  Pull` remains blocked by a known `IndexError` bug at `impulse_bars >= 59`
  (2026-08-19 audit's L4 finding) — fix before scoring, not after.

## Tier 2 — needs new engineering, not new data

The 12-ETF data already supports these; what's missing is code. Building
either engine is a real, separately-justified project decision — not
something to start by default just because it would unblock a candidate.

- [ ] **CTA v2** — pooled, volatility-scaled cross-asset trend overlay.
  Needs a genuine multi-instrument weighted-portfolio engine (nothing in
  this codebase does simultaneous cross-instrument position weighting
  today — every backtest path is single-instrument or median-of-single-
  instrument). Scored 13/16, eligible.
- [ ] **ETF-12 cross-sectional rotation** — relative-strength ranking across
  the 12 ETFs. Needs panel/permutation statistics tooling (no `scipy`/
  `statsmodels` dependency, no panel regression or cluster-shuffle null
  anywhere in `research.py`). Scored 13/16, eligible. Overlaps with CTA v2's
  trend family — building one engine doesn't reduce the case for the other;
  they'd need to be checked against each other before both are treated as
  independent evidence.

## Tier 3 — needs new but still free/accessible data

FRED's live series are already fetched (`0.44.0`) but are display-only,
final-revised values — not usable as a signal input under
[ADR 0006](../adr/0006-macro-data-contract.md) until point-in-time vintage
data exists. FRED's own ALFRED archive provides that vintage history for
free; nobody has wired it up yet.

- [ ] **Any macro-conditioned strategy** — e.g. the parked [long-end yield
  shock](2026-08-19-long-end-yield-shock.md) idea. Blocked on: ALFRED
  vintage ingestion, release-datetime alignment, a preregistered hypothesis
  — all before scoring, per ADR 0006 clauses 2–9. This is "new data" but
  free new data; the cost is engineering + governance discipline, not money.

## Tier 4 — orthogonal, multidimensional, real cost

Nothing here is free. These are the ideas that would need an actual
vendor relationship or paid feed before they could even be operationalized,
per the existing [strategy taxonomy brainstorm](2026-08-19-strategy-taxonomy-benchmark-research-tracks.md)'s Class B framing and the
[governance/data-policy brainstorm](2026-08-18-governance-beta-data.md)'s
"escalate to survivorship-free PIT data (Norgate-class)" rule: only pay for
data after a cheap, same-shape test on available data has already survived,
not before.

- [ ] **Point-in-time equity membership/delisting data** — unlocks
  cross-sectional equity momentum, value, quality, and any broad-universe
  factor work. The current ~500-symbol list is today's Wikipedia snapshot
  only (`universe.py`'s own docstring warns of this) — structurally
  survivorship-biased, not fixable by more fetching.
- [ ] **Futures continuous-contract and roll data** — unlocks a genuine
  diversified futures-trend candidate in the original Moskowitz/Ooi/Pedersen
  shape. Nothing in `fetch.py` constructs continuous contracts or rolls
  today; this is a data-engineering project on its own, before any research
  question.
- [ ] **Point-in-time fundamentals (statements, revisions)** — unlocks
  value/quality-style factors. This is Class B2 in the taxonomy brainstorm:
  discrete, event-stamped, the harder PIT-vintage class.
- [ ] **Options-implied volatility** — would let the volatility-managed
  candidate use a genuine forward-looking risk measure instead of trailing
  realized vol, and would give macro/rate strategies a real market-implied
  expectation instead of a price-based proxy.

## Promotion status

None promoted. This memo is non-evidential; if any item matures into a
candidate, it still goes through exploration-protocol → 9A → preregistration
→ 9B like everything else. Revisit and re-check off items here as they get
picked up, dropped, or superseded — this file is meant to be edited, not
archived.
