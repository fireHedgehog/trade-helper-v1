# Changelog

Concise version ledger. Research decisions and exact contracts belong in `docs/`; Git preserves file-level implementation history.

## 0.27.0

- Defined the shared dependency-aware manual/scheduled pipeline contract; scheduling remains parked until the durable pipeline passes Stage 8D.
- Completed Stage 8B: semantic UI tokens, spacious responsive Today command centre, explicit data → watchlist → discovery → portfolio actions, market-oriented lifecycle/candidate presentation, and frontend contract tests.

## Current research-workspace line

| Version | Outcome |
|---|---|
| 0.26.0 | Added persistent per-strategy watchlists, lifecycle fields, full-universe candidate tabs/intersections, explicit action boundaries, product-redesign specification, and Stage 8 checkpoint. |
| 0.25.0 | Implemented Passive ETF-12 v1 and benchmark comparison as the primary business objective. |
| 0.24.0 | Recorded CTA v1 rejection, independent methodology audit, decision language, and parked successor hypotheses. |
| 0.23.0 | Added visible Data Management, freshness, throttled manual refresh, progress, and failure states; parked cron. |
| 0.22.0 | Exposed portfolio research through API/UI with persisted experiment state. |
| 0.21.0 | Implemented multi-asset portfolio simulation, risk/capacity policy, settlement, and drawdown controls. |
| 0.20.0 | Executed locked CTA v1: no validation survivor in 14 folds; all test folds cash; hypothesis rejected. |

## Validation-foundation line

| Version range | Outcome |
|---|---|
| 0.19.0–0.19.11 | Built deterministic walk-forward runner, artifact cache, bootstrap/Holm inference, fingerprints, resume/reproduction, and final-gate reporting. |
| 0.18.0 | Locked the CTA v1 preregistration, universe, parameter family, costs, folds, and decision rule. |
| 0.17.0 | Added dependence-aware post-signal statistics and explicit limitations. |
| 0.16.0 | Enforced market-data validation, adjusted-price policy, API contracts, and regression tests. |
| 0.15.0 | Canonicalised next-open execution and lifecycle state. |
| 0.14.0 | Established reproducible baseline tests and safety boundaries. |
| 0.13.0 | Audited the prototype and paused feature expansion in favour of research validity. |

## Prototype line

| Version range | Outcome |
|---|---|
| 0.10.0–0.12.0 | Added Today workflow, confidence/state presentation, macro context, CTA concepts, and early research UI. These outputs were exploratory, not statistically validated. |
| 0.6.0–0.9.0 | Added strategy definitions, Strategy Lab, technical analysis, support/resistance, and initial Today views. |
| 0.1.0–0.5.0 | Established repository, data ingestion, universe, FastAPI backend, browser frontend, charts, first backtest, and API integration. |

## Interpretation

Versions before `0.14.0` are prototype history and must not be treated as validated strategy evidence. The immutable CTA v1 conclusion is documented in [the result](docs/research-results/cta-trend-wf-v1.md) and [audit](docs/research-results/cta-trend-wf-v1-audit.md).
