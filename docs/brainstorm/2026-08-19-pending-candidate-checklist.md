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

- [x] **TA Breakout v1** — resistance-zone breakout, distinct from
  consolidation's mean-reversion-at-support. Scored (10/16) in Cycle 2.
  Locked, executed, and closed
  [`not_material_or_not_consistent`](../research-results/ta-breakout-v1.md):
  0/12 assets reached raw significance despite 1,477 events (far more than
  RSI's 508) — and the event/placebo separation was weak by construction
  (the ≥2-rejection filter barely screened anything out), a disclosed design
  limitation, not just a bare negative. A tighter rejection definition would
  be new, independently justified work.
- [x] **Wave Pull** — impulse-pullback continuation. Unblocked by the
  `0.48.0` bug fix, scored (13/16) in [Cycle
  4](../research-candidates/2026-08-19-cycle-4.md). Locked, executed, and
  closed
  [`not_material_or_not_consistent`](../research-results/wave-pull-v1.md):
  0/11 eligible assets (`IEF` had zero qualifying events, disclosed) survived
  Holm correction. Event/placebo separation was clean this time, unlike TA
  Breakout — `TLT` reached raw p=0.032, the closest single-asset near-miss
  this session, but failed correction on only 20 events.

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
  matcher. `Fib Retrace` remains poor exploratory result, low priority. `Wave
  Pull`'s known `IndexError` (2026-08-19 audit's L4 finding) is
  [fixed](../../CHANGELOG.md) as of `0.48.0`; it is now unblocked and could be
  operationalized and scored in a future cycle, but has not been yet — a bug
  fix is not a score. **New blocker found (2026-08-20, from a Cycle 5
  next-priority evaluation):** a genuinely distinct construction exists —
  round-number/psychological price levels (Donaldson & Kim 1993; Osler
  2003), an *exogenous* order-clustering mechanism rather than Cycle 1's and
  the original prototype's *endogenous* own-history technical level. But it
  cannot be soundly executed on this project's current data: every fetched
  price series is dividend/split-**adjusted** (`auto_adjust=True`, locked by
  [ADR 0002](../adr/0002-market-data-contract.md), which also forbids mixing
  adjusted and unadjusted prices in one run). A direct query of
  `data/market.db` confirms the resulting distortion from real nominal
  history is large for 10 of the 12 locked assets — e.g. `SPY`'s stored
  adjusted close on 2007-10-01 is `$109.32` against its real nominal
  ~`$156` all-time high that week (~30% off); `TLT`/`IEF` are off by
  roughly `2x` by the early 2000s from two decades of compounded bond-
  distribution adjustment. A round-number detector built on this pipeline
  would silently flag "round-number touches" at prices that were never on
  any trader's screen. Blocked until either an ADR 0002 amendment or a new
  unadjusted-price data path exists — a real governance/data decision, not
  a redesign task, and not something to start by default.

- [x] **Turn-of-month calendar effect** (new, 2026-08-20) — mean daily
  return on the last trading day of the month plus the first 3 trading days
  of the following month (Lakonishok & Smidt 1988's window), vs. all other
  days. First mechanism family this session that is time-based rather than
  price-based; "calendar coincidence" was named as an untested alternative
  explanation in two prior candidate docs (SMA Cross v1, ETF-12 rotation)
  without ever being tested directly. Scored `15/16` in [Cycle
  5](../research-candidates/2026-08-20-cycle-5.md) — highest of any
  candidate this session, tied with RSI. Locked, executed, and closed
  [`not_material_or_not_consistent`](../research-results/calendar-turn-of-month-v1.md):
  987-1,612 events per asset ruled out a power limitation, and a locked
  volatility diagnostic ruled out SMA Cross v1's confound story, but the
  differential was small and inconsistent (`7`/`12` positive, `4`/`12`
  negative). `EEM` reached raw `p=0.013` — the strongest single-asset raw
  significance this session — but its Holm-adjusted `p=0.156` did not
  survive correction.
- [x] **Day-of-week calendar effect** — Monday-only underperformance claim
  (French 1980), scored `12/16` in [Cycle
  5](../research-candidates/2026-08-20-cycle-5.md). Picked up directly
  (2026-08-20) without a new selection cycle, same precedent as TA Breakout
  v1. Locked, executed, and closed
  [`not_material_or_not_consistent`](../research-results/calendar-day-of-week-v1.md):
  `969`-`1,588` Mondays per asset, no power limitation; `0/12` cleared
  materiality and Holm-corrected significance simultaneously. Notably more
  directionally consistent than turn-of-month (`9/12` assets negative,
  matching the literature's predicted sign), and `DBC` reached raw
  `p=0.048` — the only raw-significant single-asset result at the
  conventional `0.05` threshold across both calendar experiments — but its
  Holm-adjusted `p=0.578` did not survive correction.
- [x] **Overnight-gap conditioned forward return** (new, 2026-08-20) —
  session-structure decomposition: a large overnight gap (open vs. prior
  close) conditioning a forward K-session return, distinct from every prior
  candidate in that it is the first to touch the open price at all (order-
  flow/liquidity-provision literature, e.g. Berkman et al. 2012). Scored
  `13/16` in [Cycle 5](../research-candidates/2026-08-20-cycle-5.md).
  Needed a genuinely new joint-paired resampling design (same block-index
  sequence applied to both the overnight and intraday components at once,
  preserving their real day-to-day pairing) — designed, then put through
  independent adversarial pre-lock code review (three lenses, three agents,
  six real issues found and fixed) before any data was touched. Locked,
  executed, and closed
  [`not_material_or_not_consistent`](../research-results/overnight-gap-continuation-v1.md):
  the most decisive negative of the session — `12/12` assets showed a
  *negative* signed forward return, the opposite sign from the continuation
  hypothesis. The strengthened placebo significance gate (added during
  review) correctly rejected 3 assets that would have trivially passed the
  bare point-estimate comparison every prior candidate used, directly
  validating the review's concern. A disclosed, non-gating diagnostic
  suggests a reversal-shaped pattern instead (down-gaps tend to bounce),
  which this protocol was not designed to test and cannot claim.

## Tier 2 — needs new engineering, not new data

The 12-ETF data already supports these; what's missing is code. Building
either engine is a real, separately-justified project decision — not
something to start by default just because it would unblock a candidate.

- [ ] **CTA v2** — pooled, volatility-scaled cross-asset trend overlay.
  Scored 13/16, eligible. Its overlap concern with cross-sectional rotation
  is now moot: rotation ran and found nothing, so building CTA v2 no longer
  risks double-counting a shared trend-family effect against a still-open
  sibling. **Cost correction (2026-08-20, from a Cycle 5 next-priority
  evaluation):** the "nothing in this codebase does simultaneous
  cross-instrument position weighting" framing above is stale.
  `backend/app/portfolio_execution.py` and `portfolio.py` (committed
  2026-08-18, one day before this line was first written) already implement
  a real shared-cash, multi-symbol, sector/cluster-capped daily replay
  engine with cross-instrument capital allocation. It was built for the live
  "Today" view — discrete whole-share sizing, stop-distance risk, a
  drawdown kill switch — not the continuous vol-scaled target-weight return
  series CTA v2's estimand needs, and it is not wired into `research.py`'s
  bootstrap pipeline at all. So this is not a from-scratch engine build
  (the true remaining cost is lower than this item implies), but it is also
  not a small wiring task: a new weight-vector return-construction function
  is still needed, plus a shared placebo design against Candidate B's
  variance-timing mechanism (the same overlap this item already names).
  Separately, both of CTA v2's own disclosed rationale channels are now
  pre-undermined by this session's own closed results — channel 1 (own-asset
  trend continuation) by CTA v1's audit (2.5% power at a realistic IR=1.0),
  channel 2 (vol-scaled de-risking) by SMA Cross v1's proven volatility-only
  placebo confound — so a third trend-family test behind this build is a
  weak bet regardless of its true engineering cost. Not recommended to start
  next; cheaper Tier 1 items remain unexhausted.
- [x] **ETF-12 cross-sectional rotation** — relative-strength ranking across
  the 12 ETFs. Scored 13/16 in Cycle 2, parked pending panel/permutation
  tooling. Unblocked without adding `scipy`/`statsmodels`: redesigned around
  Spearman rank correlation (computable in plain `numpy`/`pandas`) and a
  joint-panel block-resampling null (same resampled dates applied to all 12
  assets at once, preserving real cluster correlation) instead of a formal
  panel regression. Locked, executed, and closed
  [`not_material_or_not_consistent`](../research-results/etf12-cross-sectional-rotation-v1.md):
  pooled correlation `0.045` against a `0.10` floor, `p=0.266` — the cleanest
  negative of the session, no confound or design caveat attached. CTA v2's
  overlap concern is now moot in the other direction: this candidate ran and
  found nothing, so CTA v2 no longer risks double-counting a shared
  trend-family effect with it.

## Tier 3 — needs new but still free/accessible data

FRED's live series are already fetched (`0.44.0`) but are display-only,
final-revised values — not usable as a signal input under
[ADR 0006](../adr/0006-macro-data-contract.md) until point-in-time vintage
data exists. FRED's own ALFRED archive provides that vintage history for
free. **Ingestion now exists and is live-verified (`0.60.0`/`0.61.0`):**
`app.macro_pit` implements ADR 0006 clauses 2-4 (vintage storage,
timestamp discipline, revision immutability) and a `value_asof`
point-in-time query function, verified against the real FRED API with
real `PAYEMS`/`DFII10` ingestion — see the ADR's updated Consequences
section. This unblocks the engineering gap, not the governance one: every
item below still needs its own preregistered hypothesis and Stage 9A score
before any signal use — ingestion existing and working authorizes nothing
by itself.

- [ ] **Any macro-conditioned strategy** — e.g. the parked [long-end yield
  shock](2026-08-19-long-end-yield-shock.md) idea. Blocked on: ALFRED
  vintage ingestion, release-datetime alignment, a preregistered hypothesis
  — all before scoring, per ADR 0006 clauses 2–9. This is "new data" but
  free new data; the cost is engineering + governance discipline, not money.
- [ ] **Fed put: yield-stress precursor to Fed balance-sheet expansion** —
  see [memo](2026-08-19-fed-put-long-end-reversal.md). Reframed
  (`0.63.1`, user-directed): tests whether long-end yield stress
  *precedes* QE, not whether QE causes yield reversal (the latter is
  common knowledge, not a real edge). Treasury buybacks dropped entirely
  — different institution/mandate than the Fed. **Cycle 6 (`0.62.0`),
  sole eligible candidate, 14/16 — not yet preregistered.** `TREAST`/
  `TREAS10Y` live via `macro_pit`. [Thesis Track](../thesis-track-small-n.md)
  (small-*n* regime-episode design, reversed direction: precursor →
  event) now exists, not the block-bootstrap method used for every
  candidate scored so far. Explicitly excludes any claim about a specific
  Fed official's intentions — narrative, not quantifiable.

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
  survivorship-biased, not fixable by more fetching. **Leverage note
  (2026-08-20):** checked against the [cross-sectional idea
  library](2026-08-20-cross-sectional-experiment-ideas.md), this single item
  is the shared blocker behind six distinct candidate ideas, not one — the
  cost/benefit case for this line item is materially different read that
  way than as a gate on any single factor test. **Engine feasibility
  checked (0.61.0):** the panel-bootstrap machinery itself scales to real
  equity breadth (`N=495`) with zero code change — see [cross-sectional
  equity momentum feasibility
  v1](../research-results/cross-sectional-equity-momentum-feasibility-v1.md).
  This Tier 4 data item remains exactly as unpurchased and unblocking as
  before; only the "would the engine even work" uncertainty is resolved.
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
