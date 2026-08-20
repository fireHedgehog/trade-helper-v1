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

Every chapter below except Chapter 4 answers the same question — *is this
pattern distinguishable from random noise, at high confidence?* — held to
the full standard in [ADR 0003](adr/0003-research-statistics.md),
[hypothesis-engineering.md](hypothesis-engineering.md), and
[model-acceptance-standard.md](model-acceptance-standard.md). Chapter 4
answers a different question — see [ADR
0007](adr/0007-risk-budgeted-ensemble-acceptance.md).

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

**Open, not yet sections:** the [cross-sectional idea
library](brainstorm/2026-08-20-cross-sectional-experiment-ideas.md)'s
eleven ideas, six of which (CS-01/02/03/04/05/09) collapse onto one
blocker — point-in-time equity membership data (Tier 4) — clearing that
one item unlocks six sections at once, not one.

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
is unchanged and unweakened by this chapter's existence — a candidate that
clears Chapter 1–3's full bar graduates there, not here.

No sections yet. ADR 0007 is a draft awaiting review; the ensemble engine,
confidence-multiplier sizing function, and minimum-breadth floor are named
as required decisions, not yet built.

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
