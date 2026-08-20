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

The confidence-multiplier sizing function is now built and tested
(`block_bootstrap_confidence_interval`, `chapter4_confidence_multiplier` in
`backend/app/research.py`) — a genuine second bootstrap procedure, distinct
from every null-hypothesis test this session: it characterizes the
plausible *range* of the true effect size (no centering), which a p-value
does not provide.

| § | Candidate | Result |
|---|---|---|
| 1 | [CTA v2, primary variant](../backend/app/score_cta_v2_chapter4.py) | **Not eligible.** `68%` confidence interval on the daily excess return: `[-0.0035%, +0.0204%]`, annualized lower bound `-0.88%`. Even at Chapter 4's deliberately loosened one-sigma bar, the interval still spans zero — confidence multiplier `0.0`, no position sized. Consistent with CTA v2's own raw `p=0.231` under the null test (not a contradiction, a cross-check: a raw p that far from significant implies a wide-enough interval to plausibly include zero at 68% coverage too). This is Chapter 4 working as designed, not failing — being the strongest candidate in Chapter 6's triage does not guarantee clearing even a lower bar, and checking that honestly was the entire point of building this before opening a new falsification thread. |
| 2 | [Wave Pull, `TLT`](../backend/app/score_wave_pull_tlt_chapter4.py) | **Eligible on paper, since walked back — see §2b/§4.** `68%` confidence interval on the 10-session forward return, case-resampled across the `20` qualifying events: `[+1.22%, +2.40%]`, multiplier `0.674`. `TLT` was pre-selected as the single best raw-`p` asset of `12` from Wave Pull v1's own Chapters 1–3 test *before* this score was run — a winner's-curse selection this report did not originally disclose or correct for. §2b and §4 below show that correction changes the read materially. |
| 2b | [Wave Pull, all 12 assets](../backend/app/score_wave_pull_chapter4.py) | **`2`/`11` eligible** (`GLD`, `TLT`; `IEF` had zero qualifying events, not scoreable). Symmetric rescoring of the full universe genuinely fixes the selection-bias objection an external critique (2026-08-20) correctly raised about §2's `TLT`-only report — no more cherry-picking which asset to show. But §4's calibration settles what this count is actually worth: `2/11` against a calibrated `19.08%` per-asset chance rate is **not distinguishable from noise** — `2` is in fact the single most probable outcome the null model predicts (`P(X≥2)≈65%`, mode `=2`). An earlier same-session read of this result ("a second independent hit is harder to explain by chance") was checked against the calibration and does not survive it; corrected here rather than left standing. `GLD`/`TLT`'s near-zero cross-correlation (`r=0.02`, see orthogonality below) is real but narrower evidence than that: it rules out `GLD` and `TLT` being a disguised double-count of one redundant artifact (the failure mode seen in Day-of-Week's correlated pairs below), not that either reflects a genuine effect — both "two real independent signals" and "two independent noise false-positives" predict low correlation equally well. Net: `GLD`/`TLT` remain clean, bias-free, decorrelated *candidates* appropriately queued for Chapters 1–3's strict bar or out-of-sample testing — the loosened `68%` screen doing its intended job of admitting candidates for further scrutiny, not a verdict that nothing is there. |
| 3 | [Calendar Day-of-Week, all 12 assets](../backend/app/score_calendar_dow_chapter4.py) | **`6`/`12` eligible** (`DBC`, `EFA`, `GLD`, `IEF`, `TLT`, `XLF`) on each asset's own full history — **tested directly and found not distinguishable from chance; see §4.** A third confidence-interval shape: a two-sample block bootstrap on Monday vs. non-Monday returns per asset. Under a naive independent-trials reading `6/12` looked like a striking anomaly (`p≈0.7%` against the `16.25%` calibrated per-asset base rate) — but a correlation-aware joint null built specifically to test this (§4) settles it directly rather than by approximation: `p≈0.13`–`0.14`, stable across three independent resampling grids. Not a rejection of the underlying French-1980 Monday-effect literature, but this specific `6/12` breadth reading does not clear even Chapter 4's loosened bar once real cross-asset correlation is properly accounted for. |

Three sections scored so far (§1–§3), each initially looking more
promising than it turned out to be under further scrutiny — full detail,
the calibration that settled it, and the final conclusion are below (§4
and the closing summary at the end of this chapter).

**Orthogonality (ADR 0007 clause 3) is measured, not assumed, but this
measures redundancy among nominally-eligible signals — it does not by
itself establish that any of them are real** —
[`score_chapter4_orthogonality.py`](../backend/app/score_chapter4_orthogonality.py),
pairwise Pearson correlation of each signal's own daily return
contribution, aligned per pair to its overlapping date range. Of the `28`
pairs across the `8` nominally-eligible signal-slots, `3` are flagged
materially redundant (`|correlation| ≥ 0.5`, a disclosed, locked
rule-of-thumb, not derived from this project's own data), and all `3` sit
entirely among Calendar Day-of-Week's `6` winners: `dow_IEF`/`dow_TLT`
(`r=0.92`, two treasury-duration bets moving almost identically on Mondays
— the exact suspicion named when Calendar Day-of-Week was first scored),
`dow_EFA`/`dow_XLF` (`r=0.81`), and `dow_DBC`/`dow_EFA` (`r=0.51`, just over
the line) — forming two thematic clusters (bond-duration; commodities/
international-equity/financials) plus `dow_GLD` standing alone. This
redundancy concentration was the reason §4's Day-of-Week significance
question needed a direct correlation-aware test rather than an
approximation from this partial view — the `6` winners' apparent breadth
could represent as few as `3`–`5` genuinely independent underlying effects,
not `6`. §4 below reports that direct test's result: not distinguishable
from chance. Both Wave Pull signals
are, by contrast, cleanly independent of everything: `wave_pull_TLT` tops
out at `r=-0.12` against all six `dow_` signals (including `dow_TLT`, the
same underlying asset under a different mechanism), and `wave_pull_GLD`
tops out at `r=-0.22`, including `r=0.02` against `wave_pull_TLT` itself —
real, useful information about redundancy, but (per §2b) not itself
evidence that either signal reflects a genuine effect.

**§4 — Calibrating the eligibility rule itself, and what an adversarial
verification pass changed.** A pasted external critique (2026-08-20) argued
Calendar Day-of-Week's `6/12` is close to what pure chance would produce at
a `68%` band, and separately that `TLT`'s solo report suffers "winner's
curse." Rather than argue the arithmetic analytically,
[`calibrate_chapter4_eligibility.py`](../backend/app/calibrate_chapter4_eligibility.py)
measures it directly — same Monte Carlo discipline as
[event-bootstrap-calibration-v1](research-results/event-bootstrap-calibration-v1.md):
`300` replications of zero-mean GARCH(1,1) synthetic null data, each
eligibility construction run unmodified, empirical false-eligible rate
reported with a Wilson `95%` CI. Full result:
[chapter4-eligibility-calibration-v1](../output/research/chapter4-eligibility-calibration-v1/calibration-report.json).

- Two-sample (Day-of-Week-shape), single independent null asset: `16.25%`
  false-eligible (`95%` CI `[15.08%, 17.49%]`, `n=3,600`) — matches a
  one-sided-normal-tail approximation almost exactly, **not** the critique's
  `32%` figure; the critique's own number does not survive this check.
- Case-resample (Wave-Pull-shape), single independent null asset: `19.08%`
  (`95%` CI `[17.70%, 20.54%]`, `n=2,945`).
- Case-resample, *selected winner of 12* (the single best of `12`
  independent null assets by observed mean — mirroring exactly how `TLT`
  was chosen): `84.67%` false-eligible (`95%` CI `[80.15%, 88.30%]`,
  `n=300`). This is the critique's winner's-curse concern, measured
  directly, and it is worse than the critique itself estimated: a
  best-of-`12` selection clears Chapter 4's bar under pure noise more often
  than not.

A first pass at interpreting these numbers against the real `6/12` and
`2/11` results was itself run through independent adversarial verification
(four reviewers, two per claim, working from the raw numbers rather than
from each other's framing) before being written here, matching this
project's standing practice of checking pasted critiques empirically rather
than arguing about them — applied for once to a first-pass reading of its
own results, not just to an outside critique. Two corrections resulted:

1. **Wave Pull's `2/11` (§2b)** — already corrected there against the
   `19.08%` calibrated null (`P(X≥2 of 11)≈65%`, modal outcome); see that
   cell for the full numbers, not restated here.
2. **Day-of-Week's `6/12` (§3) is not the settled "real, elevated" result
   it initially looked like, either.** Positive correlation among the `6`
   winners (the `3` flagged pairs above) inflates the variance of an
   extreme count under the null — it makes `6` *more* likely by chance, not
   less, the opposite of the direction needed to defend the naive
   `p≈0.7%` reading. Correcting for only the `3` known winner-vs-winner
   pairs (treating the other `51` of `66` possible pairs as uncorrelated,
   an assumption not actually verified) still leaves the result notable
   (`p≈1.5%–2.5%`), but that assumption is unverified and optimistic —
   financial assets often cluster by category even below the `0.5`
   flagging threshold, and if unmeasured correlation among the `9` non-
   winning assets is non-trivial, a defensible correction pushes the
   tail probability as high as `~17%–21%`, coin-flip range. **The honest
   state is a real, unresolved range, not a settled answer either way.**

**The concrete next step named above has now been run, and it settles the
question.** [`score_calendar_dow_full_correlation.py`](../backend/app/score_calendar_dow_full_correlation.py)
measured all `66` pairs across the full `12`-asset universe (not just the
`6` winners): `31` pairs flagged redundant overall, `28` of them touching a
non-winning asset — the broader universe is saturated with ordinary
equity-beta correlation (`EEM`/`EFA` `r=0.89`, `IWM`/`SPY` `r=0.90`, `QQQ`/
`XLK` `r=0.94`), confirming correlation is pervasive enough that a
hand-adjusted design-effect estimate from a partial matrix was never going
to be precise enough to trust on its own. So rather than stop at the fuller
matrix,
[`run_calendar_dow_breadth_significance.py`](../backend/app/run_calendar_dow_breadth_significance.py)
built the rigorous version directly:
[`dow_breadth_correlation_aware_null`](../backend/app/research.py) is a
joint circular-block-resampling null — one shared block-shift applied to
all `12` assets' real return series simultaneously per replication (the
same principle `etf12_rotation_bootstrap` and `overnight_gap_bootstrap`
already use), preserving the *entire* real joint correlation structure
automatically rather than approximating it from a handful of pairwise
numbers. Pre-lock adversarially reviewed before touching real data (two of
three lenses completed; the third hit a session limit mid-run and was
completed directly) — the review caught one real, non-obvious bug: the
original shared `block_bars=20` is an exact multiple of the `5`-day trading
week, so resampled blocks could quietly reproduce genuine historical
Monday-to-return pairings instead of scrambling them, biasing the test
conservative. Fixed by giving the outer cross-asset shift its own block
size, deliberately not a multiple of `5`, decoupled from the inner
per-asset CI's block size (left matching production).

**Result: `p≈0.13`–`0.14`, stable across three independent block-size
checks (`19`, `17`, `23` bars — a disclosed robustness check on the fix
itself).** Full record:
[breadth-significance.json](../output/research/chapter4-eligibility/calendar-day-of-week/breadth-significance.json).
Calendar Day-of-Week's breadth result is **not distinguishable from
chance** once the real correlation structure is properly preserved, not
approximated — nowhere near conventional significance. One more disclosed
wrinkle: on the common-date window all three checks require (bounded by
`DBC`'s shorter history, `2006`–`2026`), the observed count itself comes out
`5/12` with a *different* eligible set (`DBC`, `EEM`, `EFA`, `GLD`, `XLF` —
`IEF` and `TLT` drop out, `EEM` enters) than the `6/12` reported against
each asset's own full history — a real, disclosed sensitivity to the
evaluation window, not a discrepancy that changes the significance
conclusion either way.

The remaining gap is the ensemble-construction engine and the
minimum-breadth floor's exact number — both still named, required,
unimplemented decisions, and now clearly premature rather than merely
undersupported: of the three candidates scored so far, **none has a
settled, adversarially-checked positive read** — CTA v2 cleanly rejected,
Wave Pull walked back to candidate status (not distinguishable from
chance), Calendar Day-of-Week now directly tested and also not
distinguishable from chance. Building ensemble machinery ahead of that
would be sizing infrastructure around signals that have not yet earned it.
That is a real, complete answer for this pass of Chapter 4 — not a null
result for the exercise itself, since a governance framework that
correctly catches its own first three candidates failing a properly
rigorous test, rather than waving them through on an approximation, is
doing exactly what ADR 0007 and this chapter's calibration discipline exist
to do.

**§5 — Factor zoo v1: seventeen-formula screen, real Sharpe/IC, not itself
a Chapter 4 candidate.** [`factor_zoo.py`](../backend/app/factor_zoo.py)
ports 17 of the published WorldQuant "101 Formulaic Alphas" (Kakushadze
2015; verified against
[popbo/alphas](https://github.com/popbo/alphas/blob/main/alphas101.py)),
restricted to formulas needing only OHLCV+volume — alpha191 and the
vwap-heavy WQ101 formulas need fields this project's free Yahoo data
doesn't have. Purpose: generate breadth cheaply instead of hand-picking one
Chapter 1–3 candidate at a time into Chapter 4, generalizing the small,
separately-parked idea in
[parallel-multi-agent-research-pipeline.md](brainstorm/2026-08-21-parallel-multi-agent-research-pipeline.md)
from "rank closed candidates" to "generate and rank a whole zoo." A
screening scan, same non-evidential framing as
[cross-sectional-equity-momentum-feasibility-v1](research-results/cross-sectional-equity-momentum-feasibility-v1.md):
same disclosed-survivorship-biased 495-symbol universe, no cost/slippage
modeled, 1-session forward return, IC t-stats informative only (overlapping
draws, no multiple-comparisons correction across the 17). Screening well
here confers nothing by itself — a factor still needs its own stated
mechanism (ADR 0007 clause 1) before formal proposal into Chapter 4.

Run: [`run_factor_zoo_scan.py`](../backend/app/run_factor_zoo_scan.py),
`495`/`495` symbols, `2018-12-07`–`2026-08-14` (`1,929` common sessions).
Full numbers:
[scan-report.json](../output/research/factor-zoo-v1/scan-report.json);
charts:
[IC-IR ranking](../output/research/factor-zoo-v1/ic-ir-ranking.png),
[top-6 equity curves](../output/research/factor-zoo-v1/top-factor-equity-curves.png).

Top by IC-IR: `alpha034` (volatility-ratio/close-delta composite, Sharpe
`0.76`, CAGR `8.8%`, max drawdown `-19.0%`), `alpha004` (low-rank
persistence, Sharpe `0.71`), `alpha028` (volume-price scale composite,
Sharpe `0.66`), `alpha033` (open/close reversal, Sharpe `0.47`),
`alpha026`/`alpha009` (Sharpe `0.42`/`0.40`). Two were decisively negative:
`alpha001` (Sharpe `-0.45`) and `alpha035` (Sharpe `-0.30`, max drawdown
`-52%`) — both among the more cited WQ101 formulas, so a clean negative
here is itself informative, not noise.

Orthogonality (same `|r|≥0.5` rule as the screen above): `alpha034`/
`alpha033`/`alpha009`/`alpha028` form one tightly-correlated cluster
(`r=0.58`–`0.79`), and `alpha004`/`alpha026` touch parts of it too
(`r=0.52`–`0.55`). **Disclosed risk, not yet resolved**: every top
performer is some shape of short-horizon (1–10 session) price reversal —
the classic setting for the bid-ask-bounce artifact (Jegadeesh 1990,
Lehmann 1990), where raw daily closes alternating near the bid and ask can
manufacture an apparent reversal profit with no real edge once realistic
transaction costs are modeled, and this scan models zero cost. By the same
design-effect logic Calendar Day-of-Week's correlated pairs established
above, this cluster's real breadth is closer to `2`–`3` independent effects
than `6` — until cost-adjusted, read the whole top cluster as one shared,
unconfirmed hypothesis, not six.

**Not yet done, named as the next concrete step**: propose the
least-redundant survivors (`alpha028`, `alpha004`, `alpha026` — Sharpe
`0.66`/`0.71`/`0.42`, mutual `|r|≤0.52`) as individual Chapter 4 candidates,
each with its own stated mechanism and a cost-sensitivity check before any
eligibility read is trusted. The reversal cluster (`alpha034`/`033`/`009`)
needs a transaction-cost-aware rerun before it is even scan-worthy of
further attention, given the bid-ask-bounce risk just disclosed.

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
