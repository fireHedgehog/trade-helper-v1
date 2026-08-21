# Research program — chaptered index

Status: organizing index. Chapter numbers are labels, not fixed IDs — renumber freely. Chapters stay open and extensible: reopening Chapter 1 at a new section is a normal continuation, provided the section states which prior section it sits next to and what new mechanism — not a parameter tweak — justifies it.

| Chapter | Question | Standard |
|---|---|---|
| 1–3 | Is this pattern distinguishable from noise, at high confidence? | [ADR 0003](adr/0003-research-statistics.md), [hypothesis-engineering.md](hypothesis-engineering.md), [model-acceptance-standard.md](model-acceptance-standard.md) |
| 4 | Given a modest, uncertain edge, how should it be sized? | [ADR 0007](adr/0007-risk-budgeted-ensemble-acceptance.md) |
| 5 | What must be true operationally before a candidate is acted on? | [ADR 0008](adr/0008-bounded-paper-trading.md) |
| 6 | Discussion — no decision vocabulary applies | — |

## Chapter 1 — Single-asset, own-history technical and calendar patterns

$E[R_i(t+h) \mid X_i(t)]$: does a condition computed from an asset's own trailing history predict that same asset's own forward return or risk shape? Paused, not closed, after ten sections found nine failure modes and one partial pass — see the [closure record](stage-closures/2026-08-20-single-asset-time-series-line.md) for the full inventory and the eight lessons a reopening must address.

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

**Open sections:** Dow theory higher-highs/higher-lows swing structure; Fibonacci retracement reaction rates; golden/death cross (50/200); volume-confirms-breakout as a conditioning variable; 52-week-high anchoring momentum (George & Hwang — distinct mechanism, cheap, data in hand). See the [trading-folklore list](brainstorm/2026-08-20-trading-folklore-falsification-list.md).

## Chapter 2 — Cross-sectional and relative-strength claims

$E[R_i(t+h) - R_j(t+h) \mid X_i(t) > X_j(t)]$: asset selection, not asset timing. A distinct estimand from Chapter 1 — see the [stage-closure record](stage-closures/2026-08-20-single-asset-time-series-line.md).

| § | Result |
|---|---|
| 1 | [ETF-12 cross-sectional rotation v1](research-results/etf12-cross-sectional-rotation-v1.md) — `not_material_or_not_consistent`, cleanest null of the session, `N=12` |
| 2 | [Cross-sectional equity momentum feasibility v1](research-results/cross-sectional-equity-momentum-feasibility-v1.md) — `engine_feasible` only, `N=495`; survivorship bias and a pre-lock parameter peek both disqualify it as evidence |
| 3 | [Cross-sectional momentum v1 (CS-01)](research-results/cross-sectional-momentum-v1.md) — `not_material_or_not_consistent`, `N=501`, first confirmatory attempt with real point-in-time S&P 500 membership. Correlation clears materiality (`0.146 ≥ 0.10`) but significance fails decisively (`p=0.999`) — the null is dominated by common-factor co-movement, a known limitation of raw non-market-neutral rank correlation. Residual survivorship bias remains: `705`/`1206` ever-members have no stored price history |
| 4 | [Sector rotation v1](research-results/sector-rotation-v1.md) — `not_material_or_not_consistent`, `N=11` GICS sectors, 12-month formation / 1-month holding. Correlation is slightly negative (`-0.019`, `p=0.895`) — a clean null on both gates, unlike §3. Tests sector-level relative strength directly, the aggregation CS-01 could not reach. Today's-GICS-classification is not point-in-time; disclosed in the result |

**Open sections:** CS-02/03/04/05/09 (momentum × fragility, quiet-vs-loud winner, residual momentum, breadth-before-price, drawdown recovery speed) — unblocked individually by the same point-in-time universe (`universe_pit.py`, `0.81.0`); none scored or preregistered yet. A market-neutral or beta-adjusted re-design of CS-01 is a new, independently justified estimand. A finer GICS Sub-Industry rotation test ("Semiconductors" specifically, not "Information Technology") or a different horizon/estimand for sector rotation are likewise new candidates, not retries of §4. Full list: [cross-sectional idea library](brainstorm/2026-08-20-cross-sectional-experiment-ideas.md).

## Chapter 3 — Macro and event-driven claims

$MacroState_t \rightarrow R_{i,t:t+h}$ or $Event_{i,t} \rightarrow R_{i,t:t+h}$: a state or discrete event, not an own-asset technical condition. First chapter to use point-in-time vintage data ([macro_pit](../backend/app/macro_pit.py)) and the [Thesis Track](thesis-track-small-n.md) small-*n* method instead of block bootstrap.

| § | Result |
|---|---|
| 1 | [Fed put: yield-stress precursor v1](research-results/fed-put-yield-stress-precursor-v1.md) — `not_evaluable`, `n=4`, `p=0.989` |
| 2 | [v2, n=6 (adds "not QE" actions)](research-results/fed-put-yield-stress-precursor-v2.md) — `not_evaluable`, `p=0.981` |
| 3 | [v3, 20yr lookback](research-results/fed-put-yield-stress-precursor-v3.md) — `not_evaluable`, `p=0.885`. One unresolved thread: the current episode (2025 RMP) is the only one of six that flips positive under this lookback — a 6-episode pooled test cannot confirm that alone |
| 4 | [Labor-market claims lead-lag](research-hypotheses/labor-market-claims-lead-lag-v1.md) — operationalization record and bounded exploration, not yet scored. Real lead found (median 34 weeks), with a disclosed ~43% false-positive rate on a naive trigger |

**Open sections:** the [macro reaction-function library](brainstorm/2026-08-20-macro-reaction-function-narrative-library.md)'s seven state variables (real yield, curve slope, credit stress, gold, oil, DXY, Taylor-rule gap); PEAD/earnings-gap continuation (needs an earnings-date ingestion module — `yfinance.get_earnings_dates()` confirmed working, free, 1987–2026 depth, not yet built); the [policy-exposure factor](brainstorm/2026-08-20-policy-exposure-industrial-factor.md).

## Chapter 4 — Risk-budgeted ensemble construction (parallel track)

A different question from Chapters 1–3, governed by [ADR 0007](adr/0007-risk-budgeted-ensemble-acceptance.md): a signal with a disclosed, modest, uncertain expected value — neither proven nor rejected — is sized small via Loss-based Quantity Determination and combined into a diversified, risk-controlled ensemble, rather than required to prove itself alone at high confidence. Chapters 1–3's standard is unchanged. Confidence-multiplier sizing (`block_bootstrap_confidence_interval`, `chapter4_confidence_multiplier` in `backend/app/research.py`) is built and tested.

| § | Candidate | Result |
|---|---|---|
| 1 | [CTA v2, primary variant](research-results/cta-v2-chapter4-eligibility.md) | `not eligible`, `68%` CI spans zero |
| 2 | [Wave Pull, `TLT` solo → all 12 assets](research-results/wave-pull-chapter4-eligibility.md) | eligible on paper, walked back — `2/11` not distinguishable from chance |
| 3 | [Calendar Day-of-Week, all 12 assets](research-results/calendar-dow-chapter4-eligibility.md) | naive `6/12`; correlation-aware joint-null test settles it — `p≈0.13–0.14`, not distinguishable from chance |
| 4 | [Eligibility-rule calibration v1](research-results/chapter4-eligibility-calibration-v1.md) | false-eligible rates measured directly; a pasted critique's `32%` figure did not survive, but its winner's-curse concern (`84.67%`) was confirmed and was worse than estimated |
| — | [Orthogonality screen v1](research-results/chapter4-orthogonality-v1.md) | `3`/`28` nominally-eligible pairs redundant, all within Day-of-Week's winners |
| 5 | [Factor zoo v1 — 27-formula screen](research-results/factor-zoo-v1.md) | `atr_normalized` independent, Sharpe `0.84`; the top-cluster reversal shape (`10` factors) is one shared bid-ask-bounce hypothesis, not ten |
| 5b | [Factor zoo cost sensitivity v1](research-results/factor-zoo-cost-sensitivity-v1.md) | §5's reversal cluster (`6` factors) fails materiality at this project's own standard cost — every Sharpe flips deeply negative. `atr_normalized` survives, degrading mildly — a second independent confirmation by a different mechanism |
| 5c | [Factor zoo regime concentration v1](research-results/factor-zoo-regime-concentration-v1.md) | `atr_normalized`'s ADR 0007 clause 5 check: unlike CTA v2, no single year's exclusion flips the sign — the effect spreads across all `8` sample years, clause 5 closed |
| 5d | [Factor zoo academic anomalies v1](research-results/factor-zoo-academic-anomalies-v1.md) | 5 named anomalies, a different family from the reversal cluster. `2` (`low_volatility`, `max_effect`) are redundant with `atr_normalized` (`r=0.81`–`0.98`); `amihud_illiquidity` is independent and survives standard cost (`0.70 → 0.29` Sharpe) — a second live candidate; the other `2` are clean nulls |
| 6 | [Ensemble-construction engine v1](ensemble-construction-engine-v1.md), [ADR 0010](adr/0010-long-short-ensemble-construction.md) | Accepted design (not yet implemented) for the alpha model, risk model, and optimizer this chapter's ensemble needs — exact formulas, function signatures, a worked numeric example, and a test/acceptance checklist. Amends ADR 0004 to permit long-short positions inside a Chapter 4 ensemble only |
| 7 | [Sector rotation — Chapter 4 evaluation](research-results/sector-rotation-chapter4-v1.md) | Exploratory, real entry/exit rule (top-3/bottom-3 GICS sectors by 252-session return, hold until rank-set changes), real Sharpe/CAGR/drawdown, no p-value. Result: Sharpe `-0.17`, CAGR `-1.87%`, max drawdown `-51.9%`, confidence multiplier `0.0` — converges with Chapter 2 §4's correlation-based null via a different statistic; `1,879` rebalances over `24.6` years flags real rank-boundary whipsaw as a concrete diagnostic |
| 8 | [ATR Vol Premium — real backtest survey](research-results/atr-vol-premium-survey-v1.md) | Exploratory, per-symbol CAGR/Calmar/drawdown/win-rate/profit-factor/Sharpe across the `501`-symbol point-in-time universe (common `2015`-present window), via the app's own backtest engine (real commission/spread/slippage) — the strategy has run live since §5's Tier A translation but had never been surveyed at real breadth. Median CAGR `3.74%`, median max drawdown `-46.6%`, median win rate `62.9%`, median profit factor `1.61`, `93%` of symbols Sharpe-positive but only `11%` beat their own buy-and-hold over this bull-heavy window |
| 9 | [amihud_illiquidity — Chapter 4 evaluation, point-in-time universe](research-results/amihud-illiquidity-chapter4-v1.md) | §5d's screen re-run masked to real point-in-time S&P 500 membership (the same fix CS-01 applied) plus this project's standard `32`bps cost, via `factor_zoo.evaluate_factor` unmodified. Sharpe `0.29`, CAGR `2.67%`, max drawdown `-41.7%`, Calmar `0.064`, block-bootstrap EV interval `[+4.32e-5, +2.22e-4]` — entirely positive, confidence multiplier `0.33`. First genuinely positive confidence multiplier of this research program |
| 10 | [Ensemble-construction engine — smoke test](research-results/ensemble-smoke-test-v1.md) | `backend/app/ensemble.py` implemented and unit-tested against §6's own checklist, then run end to end on real data combining `atr_normalized` + `amihud_illiquidity`. All ADR 0010 §1 constraints held exactly (`100.00%` gross, `~0%` net, symmetric `98`/`98` groups). Caught and fixed a real bug during the run (a recently-added S&P 500 member's incomplete return history silently poisoned the covariance diagonal, zeroing the whole long side) — exactly what a smoke test exists to surface. Byproduct finding: `atr_normalized`'s *cross-sectional* form does not survive point-in-time correction (Sharpe `-0.012`, confidence multiplier `0.0`) — same pattern as CS-01, on a different signal; the own-history "ATR Vol Premium" Tier A strategy is a different claim, unaffected |
| 11 | [Academic anomalies — Chapter 4 re-evaluation](research-results/academic-anomalies-chapter4-v1.md) | `low_volatility`/`max_effect` were closed as "redundant with `atr_normalized`" — moot once §10 found `atr_normalized`'s cross-sectional form invalid. Re-scored all `4` remaining academic anomalies masked to point-in-time membership. Two new, real, independent candidates: `max_effect` (confidence multiplier `0.56`) and `expected_skewness_proxy` (`0.81`, strongest yet) — both below this project's own `|r|≥0.5` redundancy threshold against `amihud_illiquidity` and each other. `low_volatility` confirmed still not a candidate (CI straddles zero). `corwin_schultz_spread`: investigated, not assumed — a real (not a bug), decisive, catastrophic negative (Sharpe `-11.07`) from persistent crisis-period losses, not one corrupted data point |
| 12 | [Ensemble-construction engine — 3-signal breadth test](research-results/ensemble-smoke-test-v2.md) | The real breadth test §10 could not run: `amihud_illiquidity` + `max_effect` + `expected_skewness_proxy` combined for real. All three contributed genuine weight this time (no signal zeroed out); every ADR 0010 §1 constraint still held exactly (`100.00%` gross, `~0%` net, symmetric `98`/`98` groups) |

Every §1–3 candidate has been adversarially checked and has failed to hold up — the calibration discipline (§4) is catching its own candidates under a properly rigorous test, exactly its intended function. §6/§10 is the ensemble-construction engine ADR 0007 named and deferred: designed, then implemented and smoke-tested the same day, then re-tested at real 3-signal breadth (§12) once §11 found the breadth to test it with. §7-9/§11 are the Sharpe/CAGR/drawdown-based evaluation this chapter always intended for a modest, uncertain edge — not a falsification p-value — applied directly per user feedback (`2026-08-21`) that Chapter 2's bar had been misapplied to Chapter 4-shaped claims, and that "keep enumerating, we will eventually seek alpha" (the user's own words) is exactly what this chapter's method is for.

**Next step**: three live candidates — `amihud_illiquidity` (§9, confidence multiplier `0.33`), `max_effect` (§11, `0.56`), `expected_skewness_proxy` (§11, `0.81`, strongest yet) — genuinely independent of each other (`|r|<0.5` all pairs), combined and proven in §12. `atr_normalized`'s own-history Tier A execution (§5/§5b/§5c/§8) remains live and documented; its cross-sectional form is a disclosed non-candidate (§10). Sector rotation (§4/§7) and `corwin_schultz_spread` (§11, decisive negative) are closed, not pursued further at this design. All three live candidates still need clause 1 (a written economic mechanism — the Amihud 2002, Bali-Cakici-Whitelaw 2011, and Boyer-Mitton-Vorkink 2010 literature already supplies one each, needs stating for this project's own record) and clause 2 (§9/§11's numbers are the raw material) before a formal Chapter 4 proposal. `alpha028`/`alpha004`/`alpha026`/`low_volatility`/`corwin_schultz_spread` are answered — redundant, immaterial after cost, or decisively wrong-signed — and closed.

**Ahead of clauses 1/2**: `atr_normalized`'s own-history, single-asset execution exists as a real Tier A strategy — "ATR Vol Premium" in `backend/app/strategies.py`, selectable alongside the other 7, running a real backtest with real entry/exit markers. This is an independently-designed protocol answering a different, product-facing question ("does a runnable version exist"), evidence status `exploratory` — separate from clauses 1/2's ensemble-sizing question.

## Chapter 5 — Operational bridge: research verdict to bounded paper trading

A third, operational question, distinct from Chapters 1–4: once a candidate reaches a terminal state on one of the three approval paths (the strict ladder, Chapter 4's ladder, or Track B below), what must be true before anything real gets tracked, sized, and reconciled. Governed by [ADR 0008](adr/0008-bounded-paper-trading.md), status `accepted`, `2026-08-21`. Acceptance settled the design; its infrastructure (`live_price_snapshots`, `paper_ledger_events`, the Alpaca integration module, the reconciliation action) is not built, and the real-data connectivity test is blocked on the user creating an Alpaca paper account and API keys.

The gap is verified directly: `positions` in `data/market.db` holds zero rows; `backend/app/signals.py`'s `advance_positions` recomputes the entire paper ledger by replaying full history from `bars` on each call, rather than advancing a persisted, append-only transaction log; and of the seven registered strategies, only `CTA Trend` carries its real verdict (`rejected`) in `backend/app/research_catalog.py` — the other six read `not evaluable` regardless of their actual closed Chapter 1–3 results. An independent review named this same gap the same evening: "it has already built the order-placer, but has not yet established a system under which it truly dares to approve orders."

ADR 0008 answers with five pieces, each mapped to existing infrastructure:

| Piece | Design |
|---|---|
| Approval gate | `research_catalog.py`, corrected and kept honest — gates which strategies may expose a "start paper trading" action, never which are shown, per [workspace-redesign.md](workspace-redesign.md)'s show-everything-label-honestly pattern |
| Track B | A third, lighter approval path for disclosed discretionary/common-sense patterns. Relaxes the statistical-proof requirement, never the risk budget or the locked-in-advance kill rule — a reusable template covering many pattern types, rather than re-scrutinizing one narrow family (the same over-narrowing Chapter 1's ten close-variant sections already illustrate) |
| Point-in-time data contract | A new append-only `live_price_snapshots` table, decoupled from `bars`, which stays retroactively adjustable and backtest-only |
| Operational risk | Reuses [ADR 0004](adr/0004-portfolio-risk-contract.md)'s sizing and drawdown formulas unchanged, with [ADR 0007](adr/0007-risk-budgeted-ensemble-acceptance.md)'s `chapter4_confidence_multiplier` wired in as an inert-until-needed scaling input |
| Reconciliation | Compares this project's own ledger against a broker's paper-account state |

Build-vs-buy was checked directly: Alpaca Markets' free paper trading API covers this project's exact asset class (US equities/ETFs), so the broker owns market-data capture and fill simulation; this project owns only the approval gate, sizing, and reconciliation logic specific to its own governance.

**Status**: this chapter documents the bridge design; no candidate yet qualifies to use it. Zero strategies or candidates hold `eligible for operational validation` under any of the three paths — [identity.md](identity.md)'s strict ladder, ADR 0007's parallel one, or Track B (nothing proposed under it yet). Chapter 4's three scored candidates all closed §1–§4 above without a settled positive read. ADR 0008 is sequenced the same way ADR 0007 was: drafted and reviewed before anything is built, ahead of a qualifying candidate rather than in response to one.

## Chapter 6 — Discussion: what the closed nulls might still be worth

A discussion chapter: no protocol, no claim, no decision vocabulary. Fifteen experiments is too small a sample to conclude anything about the discussion itself — only to state it clearly enough to test later. A Chapter 1–3 `not_material_or_not_consistent` answers one specific question — is this distinguishable from noise, alone, at high confidence — and reading that as "this has no expected value and contributes nothing to a diversified, sized ensemble" is a distinct claim the same null does not resolve.

### Two ways to build a strategy from the same facts

$0.995^4 \approx 98.0\%$: four independent legs, each individually near-certain, compounded. This is what Chapters 1–3 are built to find, and finding four independent, structurally near-arbitrage effects simultaneously is supposed to be almost never possible in a liquid market. Every closed result failing this bar on cheap, famous, likely-already-arbitraged signals is the textbook-predicted outcome.

$0.685^4 \approx 22.0\%$: four legs, each individually modest and uncertain, compounded the same naive way, looks far worse — but that arithmetic is the wrong model for a real multi-factor book. Diversified strategies do not need every leg simultaneously right; they need many weakly-correlated legs whose individual edge is real but small, combined so no single leg's failure is costly, where the portfolio's risk-adjusted return — not the joint probability of every leg being correct — is what compounds favourably. This restates Grinold and Kahn's Fundamental Law (`IR ≈ IC × √breadth`) in probability language.

Survivability differs by mechanism: a true near-arbitrage effect, if one existed, would carry a small risk premium (efficient markets price out genuinely riskless edges quickly) but would be robust once found. A risk-premium strategy carries a larger expected return specifically because it requires bearing real risk through periods where the premium does not pay off — its survivability rests on sizing and diversification discipline, not statistical proof.

### Triage of the closed results

Most of the closed set has nothing to carry forward even under a loosened lens — stated plainly, since retroactively rescuing a disappointing result is the failure mode this project's discipline exists to resist.

**Showed a real, disclosed, modestly-sized point estimate** — not proven, and worth a Chapter 4 eligibility score. All three have since been scored (§1–§4); this is the reasoning that motivated scoring them, kept as historical record — none held up under Chapter 4's calibration and correlation-aware testing:

| Result | Reasoning | Chapter 4 outcome |
|---|---|---|
| [CTA v2](research-results/cta-v2-pooled-trend-overlay.md) | Materiality cleared (`+2.18pp` annualized), consistently signed across all three locked lookbacks, beat the placebo point estimate — the clearest candidate in the closed set. Its disclosed 2008-dependency is a regime-concentration risk a real diversification framing must confront directly | Not eligible (§1) |
| [Wave Pull](research-results/wave-pull-v1.md) | `TLT`'s raw `p=0.032` on a thin 20-event sample — a genuine near-miss, but the sample is small enough that "real but unconfirmed" and "noise" remain nearly indistinguishable | Walked back — not distinguishable from chance (§2b/§4) |
| [Calendar Day-of-Week](research-results/calendar-day-of-week-v1.md) | `9/12` assets negative, matching the literature's predicted sign; no single asset clears correction, but the breadth of the tilt is real and disclosed | Not distinguishable from chance once correlation is accounted for (§4) |

**Weaker version of the same shape:**

- [Calendar Turn-of-Month](research-results/calendar-turn-of-month-v1.md) — `EEM` raw `p=0.013`, the strongest single-asset raw signal of the session, but only `7/12` assets positive — barely a majority, a near-miss on one asset inside a much less consistent whole.

**Nothing to carry forward:**

| Result | Reasoning |
|---|---|
| [Overnight Gap Continuation](research-results/overnight-gap-continuation-v1.md) | `12/12` assets opposite-signed — a clean signal in the wrong direction, failing Chapter 4's positive-EV clause outright at any confidence level. Its disclosed reversal diagnostic is a different hypothesis, a possible future Chapter 1 section, not a rescue of this one |
| [ETF-12 rotation](research-results/etf12-cross-sectional-rotation-v1.md) | A genuinely small point estimate (`0.045` vs. a `0.10` floor) on an ample, well-separated sample — small, not a near-miss |
| [Fed put v1/v2/v3](research-results/fed-put-yield-stress-precursor-v3.md) | `p=0.885`–`0.989`, most episodes opposite-signed on the pooled claim. The single 2025 episode's own reading is a distinct, unresolved thread, but `n=1` cannot support a sizing decision regardless of framework |
| [TA Breakout](research-results/ta-breakout-v1.md) | A disclosed weak-separation design flaw, closer to an invalid test than a modest effect |
| [RSI oversold reversal](research-results/rsi-oversold-reversal-v1.md) | A genuine power limitation (`36`–`56` events/asset) — the design could not distinguish either way, different from "told us it's small" |
| [SMA Cross v1](research-results/sma-cross-v1-exposure-reduction.md) | `QQQ`'s near-miss (Holm `p=0.0506`) sits inside a fully explained confound — a volatility-only placebo matched or beat it on `12/12` assets. A near-miss with a clean alternative explanation, unlike CTA v2's near-miss with none |
| [Consolidation support-recovery](research-results/consolidation-support-feasibility-v1.md) | `not_evaluable` — no point estimate exists to discuss |

### Risk preference as a spectrum

Where a future researcher sets the Chapter 4 confidence bar is a personal risk-tolerance choice, not something statistics alone resolve — the same point [ADR 0007](adr/0007-risk-budgeted-ensemble-acceptance.md) makes about there being no third party to protect here.

1. Chapters 1–3 only. Never touches Chapter 4. Accepts a near-zero hit rate on cheap signals as the price of requiring proof.
2. Chapter 4 eligible only for a disclosed near-miss with no clean alternative explanation (CTA v2's shape) — the narrowest opening.
3. Chapter 4 eligible for any signal with a positive, cross-validated point estimate and a stated mechanism, regardless of uncertainty-band width — sized down accordingly, never up.
4. Actively seeks breadth: operationalizes more Chapter-4-shaped candidates specifically to increase ensemble breadth, on Grinold-Kahn's logic that breadth itself is where the edge lives.
5. Treats diversification and sizing discipline as the risk control, running a genuinely wide zoo of individually-unconfirmed, weakly-correlated signals, provided the live-attrition rule and drawdown halt are real and enforced.

This chapter does not state which level is correct.

## Reopening discipline

Every new section should answer two questions from the [stage-closure record](stage-closures/2026-08-20-single-asset-time-series-line.md): is this the same estimand as a nearby closed section (if so, it needs a new, independently-argued mechanism, not a parameter tweak), and does it inherit any of the eight named lessons by default (placebo requirement, power precommitment, discriminability, paired significance, regime diagnostics, Thesis Track for small-*n*) rather than rediscovering them.
