# CTA trend walk-forward v1 preregistration

Status: locked, executed, and rejected. This document describes the experiment as specified before evaluation; results are in [cta-trend-wf-v1.md](research-results/cta-trend-wf-v1.md).

> **Documentation erratum (2026-08-19).** Git history shows that `research/experiments/cta-trend-v1.json` was created on 2026-08-17 with the executed universe `SPY, QQQ, IWM, EFA, EEM, TLT, IEF, GLD, DBC, XLK, XLF, XLE`, before the evaluation runner and result. The conflicting list below was introduced after execution by documentation consolidation commit `1a77309`; it was never the machine preregistration and did not govern the experiment. The fingerprint `40a79707811b6d13f92fa88a87a9e5251a72d0d5ffa58a2709e027f7bbc0bafd`, cache, output, result, and audit all reproduce from the original machine spec. The incorrect line remains visible only to preserve the provenance of the documentation defect.

## Hypothesis and estimand

Test whether a long-only CTA parameter family produces positive out-of-sample value over constant exposure across a broad, long-lived ETF universe after costs.

Primary fold statistic: median across eligible symbols of OOS strategy return minus same-symbol constant-exposure return, net of identical costs.

## Data and universe

- Adjusted Yahoo daily OHLCV under [ADR 0002](adr/0002-market-data-contract.md).
- Incorrect post-result documentation list (never executed; see erratum): `SPY, QQQ, IWM, EFA, EEM, VNQ, GLD, TLT, LQD, HYG, DBC, USO`.
- Common calendar begins `2006-02-06`.
- A candidate is eligible only when at least `8/12` symbols have valid common observations.
- Data/specification SHA-256 identifies each cache artifact; writes are atomic.

The latest 504-bar tail available during development was contaminated by inspection and is not a valid final holdout. Confirmation requires genuinely future or independently point-in-time data.

## Walk-forward design

| Segment | Bars |
|---|---:|
| Training | 756 |
| Validation | 252 |
| Test | 252 |
| Fold step | 252 |

Fourteen folds were available. Parameter selection uses validation only; test data is accessed after selection. No validation survivor implies a cash test fold.

## Candidate family

The locked Cartesian grid contains `54` combinations of entry lookback, exit lookback, trend filter, ATR stop, and optional take-profit parameters. Exact candidate serialization is part of the experiment fingerprint; changing the grid defines another experiment.

## Selection and multiplicity

For every validation candidate, form the daily excess-return series over constant exposure. Compute a one-sided circular moving-block bootstrap with block length `20`, `5,000` deterministic resamples, then apply Holm family-wise correction at `α = 0.05` across all 54 candidates.

A survivor must have adjusted `p < 0.05`. Rank survivors by:

1. higher median symbol-level net excess return;
2. higher median Calmar ratio;
3. less severe median maximum drawdown;
4. lexicographic parameter serialization.

If none survives, allocate that test fold to cash.

## Final decision gate

Continue only if all conditions hold:

- median OOS fold excess return `> 0`;
- positive excess in at least `60%` of folds;
- median OOS Calmar `> 0`;
- pooled OOS maximum drawdown `≥ −25%`;
- at least `30` closed OOS trades.

Any failure rejects CTA v1. Costs are commission `10 bp/side`, quoted spread `2 bp`, slippage `5 bp/fill`, and zero cash yield. Execution follows [ADR 0001](adr/0001-execution-timing.md).

## Interpretation boundary

The protocol tests this universe, parameter family, selection rule, costs, and period. It neither validates nor rejects trend following in general. Post-result factor addition, deletion, or tuning is a new hypothesis and requires a new preregistration.

---

## Preregistration template — mandatory fields for any new hypothesis

This template is normative for every hypothesis protocol written after CTA v1. It enumerates the fields fixed before comparative results are observed, consistent with [model-acceptance-standard.md](model-acceptance-standard.md) and [ADR 0006](adr/0006-macro-data-contract.md). A protocol that omits a mandatory field is `not evaluable`.

The candidate must first satisfy the [hypothesis-engineering contract](hypothesis-engineering.md). This prospective template does not retroactively change CTA v1's locked decision rule.

| Field | Requirement |
|---|---|
| Hypothesis and mechanism | State the economic/behavioural/structural persistence mechanism and the expected failure mode. |
| Estimand | Define the estimand in symbols (e.g. median OOS excess return over constant exposure). For macro, declare surprise vs level per ADR 0006 clause 5. |
| Universe and provenance | Point-in-time universe; survivorship policy; cite the governing data contract (ADR 0002 and/or ADR 0006). |
| Benchmark | Primary: Passive ETF-12 v1. Secondary references: SPY, cash. |
| Parameter/search budget | Locked grid or family; candidate serialization is part of the fingerprint. |
| Trial-count budget | $N_{\text{trials}}$ registered in `research/attempts.jsonl`; deflation applied per the acceptance standard. |
| Power | Minimum detectable effect $\delta$ and target power $1-\beta$; outcome is `not evaluable` if unattainable. |
| Costs and stress | Locked cost model (ADR 0003); break-even cost $c^*$ reported. |
| Validation topology | Walk-forward and/or CSCV; multiplicity policy; dependence treatment. |
| Alpha decomposition | Active return, tracking error, information ratio, residual alpha. |
| Regime stability | Sub-sample and structural-break plan (Chow; Bai–Perron). |
| Acceptance thresholds | Model-specific, justified by objective, payoff distribution, power, and implementation burden. |
| Confirmation data | Untouched holdout or future point-in-time data, protected from inspection. |
| Fingerprint | SHA-256 of the immutable specification; atomic artifact writes. |
