# Changelog

Concise version ledger. Research decisions and exact contracts belong in `docs/`; Git preserves file-level implementation history.

## 0.33.0

ADR 0006 Macro presentation slice; no macro signal or new ingestion capability was added.

- Added an API-level display-only contract declaring point-in-time vintages, canonical release datetimes, and historical forecast series unavailable and macro signals prohibited.
- Distinguished Yahoo adjusted market-context cards from final-revised FRED observations with per-card provider, dataset, revision, date, and eligibility metadata.
- Added observation/release/revision availability fields to calendar events and marked current schedules and forecasts as non-historical display data.
- Removed the backend equity-direction heuristic, the `good/bad for equities` UI, and the unused threshold-based macro regime payload/banner.
- Added neutral Macro hierarchy and explicit ALFRED/preregistration upgrade requirements.
- Added API, calendar, and frontend contract coverage; verification is `198 passed` plus fresh-server browser checks confirming display-only copy, no equity-direction claim, and zero console errors.

## 0.32.0

Durable manual-refresh state slice; scheduling remains parked and no data-provider policy changed.

- Added a SQLite singleton for the latest refresh job, including identity, timestamps, counters, current item, and per-symbol outcomes.
- Persisted state at job creation and each atomic item transition; bar publication remains independently transactional.
- On server startup, recovered formerly running work as `interrupted`, preserving completed/failed outcomes and marking unfinished items honestly instead of implying a worker still exists.
- Updated Data Management to display durable job identity and recovery guidance; Resume still recalculates freshness and skips current symbols.
- Corrected the workspace and market-data contracts that previously described refresh progress as volatile.
- Added manager-recovery, SQLite round-trip, and frontend contract coverage; verification is `195 passed` plus a fresh-server headless browser check.

## 0.31.0

Stage 8C Strategy Lab evidence-hierarchy slice; no strategy mechanics or research conclusions changed.

- Separated selected strategy definition, default configuration, execution/data contract, evidence boundary, documented decision, and artifact path from the interactive result table.
- Preserved CTA v1 as `rejected` with its immutable research artifact; all unvalidated prototypes are explicitly `not evaluable`.
- Labelled the scoreboard as an exploratory in-memory calculation using same-symbol buy-and-hold medians, not a durable fingerprinted experiment or the formal Passive ETF-12 protocol result.
- Added visible not-run, running, complete, partial-failure, and failed states.
- Prevented an empty symbol selection from silently calculating the default basket.
- Added metadata and frontend contract coverage; verification is `193 passed` plus headless browser checks of the evidence hierarchy and empty-selection refusal.

## 0.30.0

Bounded Stage 8C research-metadata product slice; no strategy mechanics or historical conclusions changed.

- Added a code-owned registry for the three data products the application actually consumes, including provenance, information class, schema/cadence, point-in-time and revision limitations, licence caveats, permitted research use, quality state, and freshness policy.
- Linked each stored symbol to its dataset contract and rendered the registry in Data Management, including explicit final-revised/display-only treatment for FRED data.
- Added stable strategy IDs, versions, families, information profiles, required datasets, and evidence status for every executable strategy.
- Exposed typed parameter schemas through `/api/strategies` and rendered contract metadata in Symbol Research and Strategy Lab instead of duplicating frontend evidence claims.
- Preserved the practical boundary: new catalog entries require a real ingestion path or executable strategy; no general ontology, new provider, or untested model was invented.
- Added registry/API/frontend contract coverage; verification is `192 passed` plus a headless browser smoke check.

## 0.29.1

Independent audit of `0.29.0`; no strategy, data, or calculation behaviour change. Runtime version metadata is aligned to the checkpoint.

- Corrected the CTA universe erratum: Git proves the executed machine spec was locked before evaluation; the conflicting list was introduced later by documentation consolidation, not by a pre-result universe substitution.
- Added the hypothesis-engineering bridge from narrative thesis to measurable claim, point-in-time proxies, falsifier, and separately evaluated trade expression.
- Defined Passive ETF-12 as a project-specific default with material limitations and a mandatory candidate-specific benchmark/universe suitability audit before Stage 9B.
- Replaced universal statistical-method mandates and an invalid ledger-row trial count with hypothesis-specific diagnostics and a conservative variant/dependence inventory.
- Specified extensible dataset-registry and typed strategy-parameter metadata for pending Stage 8C product work; orthogonality is a measured relationship, not a strategy/data-cost category.
- Recorded the remaining Macro UI mismatch with ADR 0006 and aligned the API application version with the repository checkpoint.

## 0.29.0

Documentation-only hardening of research governance; no runtime behaviour change. CTA v1 rejection unchanged.

- Added [ADR 0006](docs/adr/0006-macro-data-contract.md): macro series are non-tradable context; point-in-time vintage (FRED ALFRED), release-datetime alignment, revision policy, surprise-vs-level estimand declaration, episode-count discipline, and an explicit upgrade path to signal status.
- Added Macro to the product contract and clarified Research Record as a documentation surface ([docs/product.md](docs/product.md)); macro-derived signals are out of scope until ADR 0006 is satisfied.
- Added institutional verification layers to the [model acceptance standard](docs/model-acceptance-standard.md): trial-count deflation, backtest-overfitting diagnostics (CSCV), power pre-commitment, break-even cost, alpha decomposition, regime/sub-sample stability, and an exploratory non-evidential tier.
- Added a mandatory preregistration template to [research-protocol.md](docs/research-protocol.md) for any hypothesis after CTA v1.
- Added the [exploration protocol](docs/exploration-protocol.md): the non-evidential search layer, attempts-ledger contract, search discipline, and the promotion path into Stage 9A.
- Added the [product identity](docs/identity.md): distilled v1 statement of what the project runs, mandated as the first read of every work session.
- Documented an erratum in [research-protocol.md](docs/research-protocol.md): the locked universe line was superseded before execution; the executed-of-record universe is `research/experiments/cta-trend-v1.json` / `locked-etf-12-v1` (SPY, QQQ, IWM, EFA, EEM, TLT, IEF, GLD, DBC, XLK, XLF, XLE).
- Centralised modern estimation refinements and references (data-driven HAC bandwidth, fixed-b critical values, automatic bootstrap block length, FDR/stepwise multiplicity) in ADR 0006; one-line pointer in the acceptance standard.

## 0.28.1

- Inserted Stage 9A before new model research: candidates must be scored before results are observed, and model-specific acceptance thresholds must be preregistered; the consolidation-zone draft is no longer presented as the default priority.

## 0.28.0

- Clarified interrupted data refresh: successful per-symbol publications survive server restart; the primary resume action skips current symbols, while core/all refreshes are explicitly labelled as forced operations.
- Prevented silent empty-watchlist replacement and added explicit recovery from the latest immutable strategy-run snapshot.
- Populated every Symbol Research model accordion after an explicit run while keeping chart overlays and markers exclusive to the selected model.
- Identified the existing S/R Bounce model as the classical-TA prototype and parked a separately specified local-resistance breakout hypothesis rather than inventing untested next-open markers or stops.
- Rebalanced the Symbol Research layout: a wider dossier rail and readable typography remain, while the selected-model guide uses a compact 96px scroll area so the chart retains focus.
- Moved the selected model’s green `Now` observation directly below the guide heading; rules and chart legend remain secondary scroll references.

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
