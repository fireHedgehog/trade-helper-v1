# Research program — chaptered index

Status: organizing index, not a contract. Chapter numbers and titles are
namings of convenience, not locked identifiers — renumber freely if a
better grouping emerges. What must not change casually is the underlying
principle: **chapters are living and extensible.** Picking up Chapter 1
again at its next section is a normal continuation of an open research
thread, not a reflexive retry of a closed result — provided the new
section states plainly which prior section it sits next to and what
specifically makes it a new mechanism, not a repair. That naming
discipline, not a cooldown period, is what keeps reopening honest.

Every chapter below except Chapters 4, 5, and 6 answers the same question —
*is this pattern distinguishable from random noise, at high confidence?* —
held to the full standard in [ADR 0003](adr/0003-research-statistics.md),
[hypothesis-engineering.md](hypothesis-engineering.md), and
[model-acceptance-standard.md](model-acceptance-standard.md). Chapter 4
answers a different question — see [ADR
0007](adr/0007-risk-budgeted-ensemble-acceptance.md). Chapter 5 answers a
different question again — not "is this real," but "what has to be true
operationally before anything real gets acted on" — see [ADR
0008](adr/0008-bounded-paper-trading.md). Chapter 6 is not evidentiary at
all — a discussion chapter, no decision vocabulary applies.

## Chapter 1 — Falsifying single-asset, own-history technical and calendar patterns

$E[R_i(t+h) \mid X_i(t)]$: does a condition computed from an asset's own
trailing history predict that same asset's own forward return or risk
shape? Parked as a line (not closed) after ten sections found nine
different reasons to fail and one partial pass — see the [closure
record](stage-closures/2026-08-20-single-asset-time-series-line.md) for
the full inventory and the eight lessons that must not be re-litigated
before reopening a new section here.

| § | Result |
|---|---|
| 1 | [CTA v1 walk-forward](research-results/cta-trend-wf-v1.md) — `reject`; [audit](research-results/cta-trend-wf-v1-audit.md) reclassifies to insufficient evidence |
| 2 | [Consolidation support-recovery](research-results/consolidation-support-feasibility-v1.md) — `not_evaluable` |
| 3 | [SMA Cross v1](research-results/sma-cross-v1-exposure-reduction.md) — `not_material_or_not_consistent`, confound |
| 4 | [RSI oversold reversal](research-results/rsi-oversold-reversal-v1.md) — `not_material_or_not_consistent`, power limitation |
| 5 | [TA Breakout v1](research-results/ta-breakout-v1.md) — `not_material_or_not_consistent`, weak separation |
| 6 | [Wave Pull v1](research-results/wave-pull-v1.md) — `not_material_or_not_consistent`, clean null |
| 7 | [Calendar Turn-of-Month v1](research-results/calendar-turn-of-month-v1.md) — `not_material_or_not_consistent`, well-powered null |
| 8 | [Calendar Day-of-Week v1](research-results/calendar-day-of-week-v1.md) — `not_material_or_not_consistent`, directionally consistent, uncorrected |
| 9 | [Overnight Gap Continuation v1](research-results/overnight-gap-continuation-v1.md) — `not_material_or_not_consistent`, decisive, opposite-signed |
| 10 | [CTA v2 pooled trend overlay](research-results/cta-v2-pooled-trend-overlay.md) — `not_material_or_not_consistent`, materiality cleared, significance/placebo did not |

**Open, not yet sections:** Dow theory higher-highs/higher-lows swing
structure; Fibonacci retracement reaction rates; golden/death cross
(50/200); volume-confirms-breakout as a conditioning variable; 52-week-high
anchoring momentum (George & Hwang — distinct mechanism, cheap, data in
hand) — see the [trading-folklore
list](brainstorm/2026-08-20-trading-folklore-falsification-list.md).

## Chapter 2 — Falsifying cross-sectional and relative-strength claims

$E[R_i(t+h) - R_j(t+h) \mid X_i(t) > X_j(t)]$: asset selection, not asset
timing. Distinct estimand from Chapter 1, per the [stage-closure
record](stage-closures/2026-08-20-single-asset-time-series-line.md)'s own
framing of what comes next.

| § | Result |
|---|---|
| 1 | [ETF-12 cross-sectional rotation v1](research-results/etf12-cross-sectional-rotation-v1.md) — `not_material_or_not_consistent`, cleanest null of the session, `N=12` |
| 2 | [Cross-sectional equity momentum feasibility v1](research-results/cross-sectional-equity-momentum-feasibility-v1.md) — `engine_feasible` only, `N=495`; explicitly not evidence for or against the claim (survivorship bias, pre-lock parameter peek both disclosed and disqualifying) |
| 3 | [Cross-sectional momentum v1 (CS-01)](research-results/cross-sectional-momentum-v1.md) — `not_material_or_not_consistent`, `N=501`, first confirmatory attempt with real point-in-time S&P 500 membership (clears materiality `0.146≥0.10` but fails significance decisively, `p=0.999` — the null is dominated by common-factor co-movement, a known limitation of raw non-market-neutral rank correlation); residual survivorship bias remains (`705`/`1206` ever-members have no stored price history) |

**Open, not yet sections:** CS-02/03/04/05/09 (momentum×fragility, quiet-vs-loud winner,
residual momentum, breadth-before-price, drawdown recovery speed) — the
same point-in-time universe (`universe_pit.py`, `0.81.0`) now unblocks each
individually; none scored or preregistered yet. A market-neutral or
beta-adjusted re-design of CS-01 itself is also open — named in its own
result as a new, independently justified estimand, not a retry. See the
[cross-sectional idea
library](brainstorm/2026-08-20-cross-sectional-experiment-ideas.md) for the
full list.

## Chapter 3 — Falsifying macro and event-driven claims

$MacroState_t \rightarrow R_{i,t:t+h}$ or $Event_{i,t} \rightarrow
R_{i,t:t+h}$: a state or discrete event, not an own-asset technical
condition. First chapter to use point-in-time vintage data
([macro_pit](../backend/app/macro_pit.py)) and the [Thesis
Track](thesis-track-small-n.md) small-*n* method instead of block
bootstrap.

| § | Result |
|---|---|
| 1 | [Fed put: yield-stress precursor v1](research-results/fed-put-yield-stress-precursor-v1.md) — `not_evaluable`, n=4, `p=0.989` |
| 2 | [v2, n=6 (adds "not QE" actions)](research-results/fed-put-yield-stress-precursor-v2.md) — `not_evaluable`, `p=0.981` |
| 3 | [v3, 20yr lookback](research-results/fed-put-yield-stress-precursor-v3.md) — `not_evaluable`, `p=0.885`; one real, unresolved thread: the current episode (2025 RMP) is the only one of six that flips positive under this lookback — not something a 6-episode pooled test can confirm alone |
| 4 | [Labor-market claims lead-lag](research-hypotheses/labor-market-claims-lead-lag-v1.md) — operationalization record + bounded exploration only, not yet a scored candidate; real lead found (median 34 weeks) but a disclosed ~43% false-positive rate on a naive trigger |

**Open, not yet sections:** the [macro reaction-function
library](brainstorm/2026-08-20-macro-reaction-function-narrative-library.md)'s
seven state variables (real yield, curve slope, credit stress, gold, oil,
DXY, Taylor-rule gap); PEAD/earnings-gap continuation (needs an earnings-date
ingestion module — `yfinance.get_earnings_dates()` confirmed to work, free,
1987–2026 depth, not yet built); the [policy-exposure
factor](brainstorm/2026-08-20-policy-exposure-industrial-factor.md).

## Chapter 4 — Risk-budgeted ensemble construction (parallel track)

Not a falsification chapter. Governed by [ADR
0007](adr/0007-risk-budgeted-ensemble-acceptance.md): signals with a
disclosed, modest, *uncertain* expected value — not proven, not rejected —
sized small via Loss-based Quantity Determination and combined into a
diversified, risk-controlled ensemble instead of being asked to prove
themselves alone at high confidence. Chapters 1–3's falsification standard
is unchanged and unweakened by this chapter's existence. Confidence-
multiplier sizing (`block_bootstrap_confidence_interval`,
`chapter4_confidence_multiplier` in `backend/app/research.py`) is built
and tested.

| § | Candidate | Result |
|---|---|---|
| 1 | [CTA v2, primary variant](research-results/cta-v2-chapter4-eligibility.md) | `not eligible`, `68%` CI spans zero |
| 2 | [Wave Pull, `TLT` solo → all 12 assets](research-results/wave-pull-chapter4-eligibility.md) | eligible on paper, walked back — `2/11` not distinguishable from chance |
| 3 | [Calendar Day-of-Week, all 12 assets](research-results/calendar-dow-chapter4-eligibility.md) | naive `6/12`; correlation-aware joint-null test settles it — `p≈0.13–0.14`, not distinguishable from chance |
| 4 | [Eligibility-rule calibration v1](research-results/chapter4-eligibility-calibration-v1.md) | false-eligible rates measured directly; a pasted critique's `32%` figure did not survive, but its winner's-curse concern (`84.67%`) was confirmed and was worse than estimated |
| — | [Orthogonality screen v1](research-results/chapter4-orthogonality-v1.md) | `3`/`28` nominally-eligible pairs redundant, all within Day-of-Week's winners |
| 5 | [Factor zoo v1 — 27-formula screen](research-results/factor-zoo-v1.md) | `atr_normalized` independent, Sharpe `0.84`; the top-cluster reversal shape (`10` factors) flagged as one shared bid-ask-bounce hypothesis, not ten |
| 5b | [Factor zoo cost sensitivity v1](research-results/factor-zoo-cost-sensitivity-v1.md) | §5's reversal cluster (`6` factors) not material at this project's own standard cost — every Sharpe flips deeply negative; `atr_normalized` survives the same check, degrading mildly, a second independent confirmation by a different mechanism |
| 5c | [Factor zoo regime concentration v1](research-results/factor-zoo-regime-concentration-v1.md) | `atr_normalized`'s ADR 0007 clause 5 check: unlike CTA v2, no single year's exclusion flips the sign — the effect spreads across all `8` sample years, clause 5 closed |
| 5d | [Factor zoo academic anomalies v1](research-results/factor-zoo-academic-anomalies-v1.md) | 5 named anomalies, a different family from the reversal cluster: `2` (`low_volatility`, `max_effect`) turned out redundant with `atr_normalized` (`r=0.81`–`0.98`); `amihud_illiquidity` is genuinely independent and survives standard cost (`0.70→0.29` Sharpe) — a second live candidate; the other `2` are clean nulls |

None of §1–3's hand-picked candidates has a settled, adversarially-checked
positive read — a governance framework that correctly catches its own
candidates failing a properly rigorous test, rather than waving them
through on an approximation, is doing exactly what ADR 0007 and the
calibration discipline (§4) exist to do. The ensemble-construction engine
and minimum-breadth floor remain named, unbuilt (ADR 0007 Consequences) —
premature ahead of a settled positive candidate, not merely undersupported.

**Not yet done, next concrete step**: two live candidates now, `atr_normalized`
(§5/§5b/§5c all cleared) and `amihud_illiquidity` (§5d, independent of
everything, cost-checked, regime-concentration not yet run). Both still
need clause 1 (a written economic mechanism) and clause 2 (a
cross-validated point estimate with an explicit uncertainty band — the
confidence-multiplier scoring already built and used for CTA v2/Wave
Pull/Calendar-DOW) before a formal Chapter 4 proposal.
`alpha028`/`alpha004`/`alpha026`/`low_volatility`/`max_effect` are all
answered (redundant or not material after cost) and not carried forward.

**Also done, ahead of clauses 1/2**: `atr_normalized`'s own-history,
single-asset execution now exists as a real Tier A strategy — "ATR Vol
Premium" in `backend/app/strategies.py` — selectable everywhere alongside
the other 7, running a real backtest with real entry/exit markers. This
is a new, independently-designed protocol (a per-symbol rule never
existed for the cross-sectional finding), not a shortcut around clauses
1/2 for the ensemble-sizing question ADR 0007 governs — it answers a
different, product-facing question ("does a runnable version of this
exist"), evidence status `exploratory`, not yet a validated claim.

## Chapter 5 — Operational bridge: from research verdict to bounded paper trading

Not a falsification chapter, and not Chapter 4's risk-budgeting question
either — a third, operational question: once a candidate *does* reach a
terminal state on one of the three approval paths (the strict ladder,
Chapter 4's ladder, or Track B below), what concretely has to be true
before anything real gets tracked, sized, and reconciled. Governed by [ADR
0008](adr/0008-bounded-paper-trading.md), status `accepted` `2026-08-21`.
Acceptance settled the design; none of its required infrastructure
(`live_price_snapshots`, `paper_ledger_events`, the Alpaca integration
module, the reconciliation action) is built yet, and the actual real-data
connectivity test is blocked on the user creating an Alpaca paper account
and API keys — not something this project can do on its own.

The gap this chapter names is a real, verified one, not a hypothetical:
`positions` in `data/market.db` has zero rows; `backend/app/signals.py`'s
`advance_positions` recomputes the entire paper ledger by replaying full
history from `bars` on each call rather than advancing a persisted,
append-only transaction log; and none of the seven registered strategies
carries an accurate, current research-status label in
`backend/app/research_catalog.py` — only `CTA Trend` is marked with its
real verdict (`rejected`); the other six all read `not evaluable`
regardless of their actual closed Chapter 1–3 results. There is, in short,
no working bridge yet between a research verdict and anything the running
product does — a disconnect an outside review independently named this
same evening ("it has already built the order-placer, but has not yet
established a system under which it truly dares to approve orders").

ADR 0008 answers this with five named pieces, each mapped to something
that already exists rather than invented fresh: an **approval gate**
(`research_catalog.py`, corrected and kept honest, gating only which
strategies may expose a "start paper trading" action — never which are
shown, per [workspace-redesign.md](workspace-redesign.md)'s established
show-everything-label-honestly pattern); **Track B**, a third, explicitly
lighter approval path for disclosed discretionary/common-sense patterns —
relaxes the statistical-proof requirement, never the risk budget or the
locked-in-advance kill rule — designed as a reusable template so this
project can cover many different pattern *types* cheaply going forward
rather than continuing to deeply re-scrutinize a narrow family (the
same over-narrowing concern Chapter 1's own ten close-variant sections
already illustrate); a **point-in-time data contract** (a new append-only
`live_price_snapshots` table, decoupled from `bars`, which stays
retroactively adjustable and backtest-only); **operational risk** reusing
[ADR 0004](adr/0004-portfolio-risk-contract.md)'s sizing and drawdown
formulas unchanged, with [ADR 0007](adr/0007-risk-budgeted-ensemble-acceptance.md)'s
`chapter4_confidence_multiplier` wired in as an inert-until-needed scaling
input; and a **reconciliation** check comparing this project's own ledger
against a broker's paper-account state. Build-vs-buy was checked directly,
not assumed: Alpaca Markets' free paper trading API covers this project's
exact asset class (US equities/ETFs), so the broker owns market-data
capture and fill simulation; this project owns only the approval gate,
sizing, and reconciliation logic that are specific to its own governance.

**This chapter documents the bridge; it does not create eligible traffic
across it.** As of this draft, zero strategies or candidates hold
`eligible for operational validation` under any of the three paths —
[identity.md](identity.md)'s strict ladder, ADR 0007's parallel one, or
Track B (nothing has yet been proposed under it). Chapter 4's own three
scored candidates all closed §1–§4 above without a settled positive read.
Building or activating any part of this chapter's design ahead of a real,
qualifying candidate would be exactly the sizing-infrastructure-before-
earning-it mistake Chapter 4 named and avoided; ADR 0008 is deliberately
sequenced the same way ADR 0007 was — drafted and reviewed before anything
is built.

## Chapter 6 — Discussion: what the ten closed nulls might still be worth

Not a protocol, not a claim, no decision vocabulary applies. A discussion
chapter, explicitly preliminary — fifteen experiments is not a large enough
sample to conclude anything about the discussion itself, only to state it
clearly enough to test later. Written because a Chapter 1–3
`not_material_or_not_consistent` answers one specific question — *is this
distinguishable from noise, alone, at high confidence* — and it is a real
error to silently read that as *this has no expected value and would
contribute nothing to a diversified, sized ensemble*. Those are different
claims. A null on the first does not resolve the second either way.

### Two ways to build a strategy out of the same underlying facts

$0.995^4 \approx 98.0\%$: four independent legs, each individually
near-certain, compounded. This is what Chapters 1–3 are built to find —
and finding four *independent*, structurally near-arbitrage effects,
simultaneously, is supposed to be almost never possible in a liquid market.
That every closed result so far has failed to clear this bar on cheap,
famous, likely-already-arbitraged signals is the textbook-predicted
outcome, not a broken test.

$0.685^4 \approx 22.0\%$: four legs, each individually modest and
uncertain, compounded the same naive way, looks much worse — but that
arithmetic is the wrong model for how a real multi-factor book actually
works. Diversified strategies do not need every leg to be simultaneously
right; they need many weakly-correlated legs whose *individual* edge is
real but small, combined so no one leg's failure is costly and the
*portfolio's* risk-adjusted return, not the joint probability of every leg
being correct, is what compounds favourably. This is Grinold and Kahn's
Fundamental Law again (`IR ≈ IC × √breadth`), stated in probability
language instead of information-coefficient language. Different survivability,
different risk premium: a true near-arbitrage effect, if one existed, would
carry a *small* risk premium (efficient markets price out genuinely riskless
edges quickly) but would be robust once found; a risk-premium strategy
carries a *larger* expected return specifically because it requires genuine
risk-bearing through periods where the premium does not pay off — its
survivability depends on sizing and diversification discipline, not on
statistical proof.

### An honest triage of the ten closed results, not a blanket rescue

Chapter 4 is not a magic re-reading that turns every null into a hidden
win — most of the closed set genuinely has nothing to carry forward even
under a loosened lens, and saying so plainly matters more here than
anywhere else in this document, because the temptation to retroactively
rescue a disappointing result is exactly the failure mode this project's
whole discipline exists to resist.

**Showed a real, disclosed, modestly-sized point estimate that looked worth
a Chapter 4 eligibility score** — not proven, but not merely "failed,"
either. All three named below have since actually been scored in Chapter 4
(§1–§4); this triage is the reasoning that motivated scoring them, kept as
the historical record of why, not a live prediction of the outcome — none
of the three held up under Chapter 4's own calibration and correlation-aware
testing:

- [CTA v2](research-results/cta-v2-pooled-trend-overlay.md) — materiality
  cleared (`+2.18pp` annualized), consistently signed across all three
  locked lookbacks, beat the placebo point estimate. The clearest candidate
  in the closed set. Its own disclosed 2008-dependency is exactly the kind
  of regime-concentration risk a real ensemble/diversification framing
  would have to confront directly. Scored: not eligible (Chapter 4 §1).
- [Wave Pull](research-results/wave-pull-v1.md) — `TLT`'s raw `p=0.032` on
  a thin `20`-event sample. A genuine near-miss, but the sample is small
  enough that "real but unconfirmed" and "noise" remain nearly
  indistinguishable either way. Scored: walked back to candidate status,
  not distinguishable from chance (Chapter 4 §2b/§4).
- [Calendar Day-of-Week](research-results/calendar-day-of-week-v1.md) —
  `9/12` assets negative, matching the literature's predicted sign; no
  single asset clears correction, but the breadth of the directional tilt
  is real and disclosed, not cherry-picked. Scored: not distinguishable
  from chance once real correlation is accounted for (Chapter 4 §4).

**Weaker version of the same shape, worth naming but not overselling:**

- [Calendar Turn-of-Month](research-results/calendar-turn-of-month-v1.md) —
  `EEM` raw `p=0.013` (the strongest single-asset raw signal of the
  session) but only `7/12` assets positive, barely a majority. A real
  near-miss on one asset inside a much less consistent whole.

**Genuinely nothing to carry forward, said plainly rather than
soft-pedaled:**

- [Overnight Gap Continuation](research-results/overnight-gap-continuation-v1.md) —
  `12/12` assets opposite-signed. Not "unconfirmed positive" — a clean
  signal in the wrong direction. Fails Chapter 4's own positive-EV
  eligibility clause outright, at any confidence level. (Its own disclosed
  reversal diagnostic is a *different* hypothesis, a possible future
  Chapter 1 section, not a rescue of this one.)
- [ETF-12 rotation](research-results/etf12-cross-sectional-rotation-v1.md) —
  a genuinely small point estimate (`0.045` vs. a `0.10` floor) on an ample,
  well-separated sample. Not a near-miss, just small.
- [Fed put v1/v2/v3](research-results/fed-put-yield-stress-precursor-v3.md) —
  `p=0.885`–`0.989`, most episodes flatly opposite-signed on the pooled
  claim tested. (The single 2025 episode's own reading remains a distinct,
  unresolved thread — but `n=1` is not something a sizing decision can
  safely act on regardless of framework.)
- [TA Breakout](research-results/ta-breakout-v1.md) — a disclosed
  weak-separation *design* flaw, not just an unconfirmed effect; closer to
  an invalid test than a modest one.
- [RSI oversold reversal](research-results/rsi-oversold-reversal-v1.md) — a
  genuine power limitation (`36`–`56` events/asset); the design could not
  have told either way, which is different from "told us it's small."
- [SMA Cross v1](research-results/sma-cross-v1-exposure-reduction.md) —
  `QQQ`'s near-miss (Holm `p=0.0506`) sits inside a *fully explained*
  confound (a volatility-only placebo matched/beat it on `12/12` assets).
  A near-miss with a clean alternative explanation is not the same shape as
  CTA v2's near-miss with no alternative explanation offered.
- [Consolidation support-recovery](research-results/consolidation-support-feasibility-v1.md) —
  `not_evaluable`; no point estimate exists to discuss either way.

### Risk preference as a spectrum, not a rule

Where any future researcher sets the Chapter 4 confidence bar is a personal
risk-tolerance choice, not something the statistics alone resolve — the
same point [ADR 0007](adr/0007-risk-budgeted-ensemble-acceptance.md) makes
about there being no third party to protect here. Sketched as a spectrum,
not a locked scale:

1. Chapters 1–3 only. Never touches Chapter 4. Accepts a near-zero hit
   rate on cheap signals as the honest price of requiring proof.
2. Chapter 4 eligible only for a *disclosed near-miss with no clean
   alternative explanation* (CTA v2's shape) — the narrowest possible
   opening.
3. Chapter 4 eligible for any signal with a positive, cross-validated point
   estimate and a stated mechanism, regardless of how wide its uncertainty
   band is — sized down accordingly, never sized up.
4. Actively seeks breadth — deliberately operationalizes more Chapter-4-shaped
   candidates (weak mechanism, modest expected value) specifically to
   increase ensemble breadth, on the Grinold-Kahn logic that breadth itself
   is where the edge lives.
5. Treats the diversification and sizing discipline as *the* risk control,
   and is willing to run a genuinely wide zoo of individually-unconfirmed,
   weakly-correlated signals, provided the live-attrition rule and drawdown
   halt are real and enforced.

No position is stated here on which level is correct — that is exactly the
kind of conclusion this chapter is not yet entitled to reach.

## How a chapter's "why, not just whether" reads

Every section within a chapter should be checkable against the two
questions the [stage-closure
record](stage-closures/2026-08-20-single-asset-time-series-line.md)
established: is this the *same estimand* as a nearby closed section (if so,
it needs a new, independently-argued mechanism, not a parameter tweak), and
does it inherit any of the eight named lessons by default (placebo
requirement, power precommitment, discriminability, paired significance,
regime diagnostics, Thesis Track for small-*n*) rather than rediscovering
them. This index exists so that check is always one link away, not
something a future session has to reconstruct from memory.
