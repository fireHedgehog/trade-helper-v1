# Changelog

Concise version ledger. Research decisions and exact contracts belong in `docs/`; Git preserves file-level implementation history.

## 0.47.0

Locked, executed, and closed TA Breakout v1 (Cycle 2's unpicked Candidate E); assessed and declined MACD and full Elliott Wave counting. No strategy implemented, no trade, no cost/execution modelling.

- Picked up TA Breakout v1 (scored `10/16` in Cycle 2, never disqualified) from the pending checklist. Locked [docs/research-protocols/ta-breakout-v1.md](docs/research-protocols/ta-breakout-v1.md): a deliberately simplified, close-price-only rejected-resistance breakout, tested against the exact placebo Cycle 2's own verification named — a raw new-high breakout with no rejection requirement — reusing RSI's proven event-recomputing bootstrap rather than Cycle 1's caliper-matching design.
- Implemented `ta_breakout_bootstrap` and supporting functions in `backend/app/research.py`, reusing `_apply_cooldown`/`_mean_forward_return` from the RSI implementation. Added 6 unit tests, including a deterministic no-lookahead check for the resistance calculation and a direct check that the event/placebo distinction behaves as designed.
- Result: `1,477` total qualifying events across 12 assets (far more than RSI's `508`), yet `0/12` reached raw significance (smallest raw p `0.099`). Disclosed a genuine design weakness rather than filing this as an equivalent negative to the prior two results: the `≥2`-rejection filter barely separated event from placebo on any asset (e.g. `SPY`: `190` events vs. `195` placebo occurrences), so the `7/12` placebo-beating count reflects weak separation, not a clean comparison. Recorded in [docs/research-results/ta-breakout-v1.md](docs/research-results/ta-breakout-v1.md).
- Assessed MACD and full Elliott Wave (5-3/ABCDE) counting against the pending checklist and declined both, with reasons recorded rather than silently skipped: MACD is mechanically the same shape as SMA Cross v1 and would very likely reproduce its exact confound; Elliott Wave counting cannot be made objective without discretionary judgment, in tension with this project's falsifiability requirement. The existing `WavePull` prototype remains the honest, already-scoped stand-in, currently blocked by a known bug.

## 0.46.0

Selected, locked, executed, and closed Stage 9A Cycle 3; no strategy implemented, no trade, no cost/execution modelling.

- Scored two candidates from the pending checklist: RSI(14) oversold-crossing short-horizon reversal (`15/16`, highest of any candidate so far — a genuinely different mechanism from every trend-family candidate tested) and S/R Bounce formalization (`0/16` on distinct information — too close to Cycle 1's already-closed consolidation work). Prioritised RSI only. Recorded in [docs/research-candidates/2026-08-19-cycle-3.md](docs/research-candidates/2026-08-19-cycle-3.md).
- Locked [docs/research-protocols/rsi-oversold-reversal-v1.md](docs/research-protocols/rsi-oversold-reversal-v1.md): an event study reusing the block-resample-and-recompute method proven by SMA Cross v1, extended from continuous state-gating to sparse event/forward-return recomputation — deliberately avoids Cycle 1's caliper-matching failure mode by never constructing a separate matched control set.
- Implemented the extension in `backend/app/research.py` (`rsi_bootstrap` and supporting functions), reusing the existing `RsiReversion` prototype's exact RSI formula. Added 8 unit tests, including a direct cross-check against that prototype's own formula on real closes — caught and fixed a real bug where the reconstructed-price RSI diverged from the reference by up to 0.3% due to a warm-up initialization mismatch (padding the first price delta with `0.0` instead of letting pandas' EWM skip a leading `NaN`).
- Result: all 12 assets cleared the 15-event minimum (508 events total), but 0/12 reached raw significance even before Holm correction (smallest raw p 0.138); the placebo comparison was genuinely mixed (6/12 each way), unlike SMA Cross v1's clean sweep. Recorded as `not_material_or_not_consistent` in [docs/research-results/rsi-oversold-reversal-v1.md](docs/research-results/rsi-oversold-reversal-v1.md), explicitly distinguished from Cycle 2's confound-driven result as a power limitation instead.

## 0.45.0

Executed the locked Stage 9A Cycle 2 protocol and closed it `not_material_or_not_consistent`; no strategy implemented, no trade, no cost/execution modelling.

- Implemented the protocol's one named statistics extension in `backend/app/research.py`: a state-recomputing generalization of `circular_block_bootstrap_p_value` (each resample reconstructs a synthetic price path and recomputes both trailing states on it) plus `delta_sigma`/`delta_mdd` computation, reusing `holm_adjust` unchanged. Added 7 unit tests proving no future bar affects an earlier state value and pinning the favourable-direction sign convention.
- Added `backend/app/run_sma_cross_exposure_reduction.py`, executed against the real 12-ETF dataset fetched this session (data SHA-256 `0c5a81332f9ba941ddce9bd6a69cb9fe90c3f7570b163c1a4ec3bd4c609fc5bc`).
- Result: 4/12 assets cleared raw materiality and significance on both statistics; 0/12 survived Holm correction across the 12-asset × 2-statistic family on both statistics at once. The volatility-state placebo matched or beat the SMA state's variance reduction on 12/12 assets and drawdown reduction on 5/12 — the protocol's own falsifier triggering directly. Recorded in [docs/research-results/sma-cross-v1-exposure-reduction.md](docs/research-results/sma-cross-v1-exposure-reduction.md).
- Pre-execution amendment: corrected the concentration gate from a paraphrased "2 of 4 asset-class clusters" to the actual "3 of 6" distinct `cluster` values in `portfolio_universe.py`, verified by reading the field directly rather than from memory, before any data access.
- Fetched the full S&P 500 ∪ NASDAQ-100 ∪ XL sector ETF universe and all ten managed FRED macro series onto this machine using existing CLI tools; no new code required for the fetch itself.

## 0.44.0

Fixed a real bar-validation defect found while fetching FRED macro data; no research conclusion changed.

- `backend/app/store.py::upsert_bars` enforced `require_positive` on every symbol not in `MARKET_CONTEXT_SYMBOLS` (`GC=F`, `CL=F`, `^TNX`) — but FRED series were never added to that relaxation, so a legitimately negative value (`A191RL1Q225SBEA`, real GDP growth, negative in every contraction) was rejected as if it were a stock price.
- Added `FRED_MANAGED_SERIES` to `backend/app/assets.py` (moved from `backend/app/fred.py`, which now imports it) and extended `upsert_bars`'s relaxed-validation check to include it, alongside the existing Yahoo market-context symbols.
- Added a regression test confirming a negative FRED value is stored while an equity symbol with the same negative value is still rejected — the existing strict-equity guarantee is unchanged.
- Found and fixed while fetching real macro data for the first time on this machine; all ten `FRED_MANAGED_SERIES` are now stored.

## 0.43.0

Locked the Stage 9A Cycle 2 protocol; no data fetched, no code executed, no result computed.

- Locked [SMA Cross v1 exposure-reduction and volatility-state placebo v1](docs/research-protocols/sma-cross-v1-exposure-reduction.md): recast Candidate B's volatility-managed-exposure mechanism into a second self-referential trailing state (below/above its own expanding-median realized volatility) instead of a continuous, target-vol-anchored weight, so the joint experiment needs no new portfolio-weighting engine.
- Specified a bounded extension of the existing `circular_block_bootstrap_p_value` (state-recomputing resample, not a new panel/permutation library) as the only new statistics code required, reusing the existing `holm_adjust` unchanged.
- Locked warm-up (252 sessions, keeping 2008 in-sample for every asset including DBC), materiality thresholds (Δσ ≤ −3pp, ΔMDD ≤ −5pp), an 8/12-asset breadth gate, and an explicit placebo rule so the SMA state must beat the volatility state, not merely beat continuous exposure — resolving every open item Cycle 2's verification flagged against the raw Candidate A/B records.
- Created `research/experiments/sma-cross-v1-exposure-reduction.json` with every constant above, canonical-hashed (spec SHA-256 `5bee965b775645681149049e3ecf43a618b4e71b225bc97b53b88b62b6ebf4ae`); its data-fingerprint fields are honestly `null`, pending a data fetch on the executing machine.
- Appended one `preregistered_no_results` attempts-ledger entry before any execution, per the exploration protocol.

## 0.42.0

Closed Stage 9A Cycle 2 candidate selection; no strategy implemented, no result computed, no code changed.

- Operationalized, independently scored, and adversarially verified five candidates against the actual codebase (not narrative docs): CTA v2, ETF-12 cross-sectional rotation, volatility-managed exposure, TA Breakout v1, and a formalized SMA Cross.
- Prioritised SMA Cross v1's exposure-reduction claim, jointly designed against volatility-managed exposure's control after verification found the two share one research question and would double-count as independent evidence if scored separately.
- Found that CTA v2 and cross-sectional rotation are data-ready but require infrastructure this codebase does not have — a pooled multi-instrument portfolio-weighting engine and panel/permutation statistical tooling respectively — and parked both on that basis, not on data readiness.
- Recorded that data readiness scored `2` for all five candidates precisely because the batch stayed on the one data shape already confirmed clean (12-ETF adjusted daily OHLCV); this was not read as a general "data is solved" conclusion.
- TA Breakout v1 was not prioritised: lowest score of the batch, an explicit zero on diversification, and its own record concedes its distinguishing mechanic degenerates to a CTA v1 retest once stripped out.
- During this cycle's workflow run, a subagent wrote an unauthorized file into `docs/research-hypotheses/` and edited `docs/research-backlog.md` without instruction; both were caught, reverted, and are not part of this release. Recorded here as a governance note on this session's tooling, not a project research finding.

## 0.41.0

Documentation-only agent-memory and environment-portability hardening; no runtime behaviour or research conclusion changed.

- Added identical `AGENTS.md` and `CLAUDE.md` root pointers routing any agent tool to `docs/README.md` as the single authoritative checkpoint; neither file duplicates checkpoint content.
- Added an "Environment and data portability" section to `docs/README.md`: `data/` and `.venv/` are git-ignored and non-portable; a checkout missing either supports documentation and specification work only, never execution.
- Recorded the data-fingerprint reproducibility rule for locked specifications: a fresh Yahoo fetch is not fingerprint-stable under `auto_adjust=True`; moving locked-data execution to another machine requires copying `data/market.db` itself, not re-fetching.
- Verified by direct run that a data-less checkout produces `220 passed, 2 failed`, both failures attributable to the empty database, not a code defect; recorded the two expected failing test names so a future agent does not mistake them for a regression.
- Surfaced the untriaged 2026-08-19 methodology/implementation audit (2 critical, 2 high, 5 medium, 4 low) as a "Pending triage" checkpoint fact; findings remain non-evidential and unactioned per `docs/audits/README.md`.

## 0.40.0

Closed Stage 9A Cycle 1 as `not_evaluable`, without accessing actual-event outcomes.

- Completed detector-prevalence and locked pre-event matching feasibility for 274 deduplicated consolidation support-recovery events.
- Retained six of eight detector variants; two were transparently excluded as sparse under the preregistered prevalence gate.
- Recorded a zero-control matching result: 66,161 same-year candidates, 16,489 after event exclusion, and zero inside every locked feature caliper.
- Correctly short-circuited before prospective power; no return, drawdown, P&L, or post-event price was joined to an actual event.
- Added deterministic matching leakage/exclusion tests, a final decision artifact, immutable result documentation, and an attempts-ledger closure.
- Preserved the distinction between `not_evaluable` and hypothesis rejection; any alternative comparison design must enter a new research cycle.
- Verification: `222 passed`, locked input reproduction, and byte-identical structural rerun.

## 0.39.0

First Stage 9A execution checkpoint; structural feasibility only, with no forward-outcome or P&L access.

- Added indexed candidate-selection and preregistration folders while keeping canonical authority documents at `docs/` root.
- Selected consolidation support recovery through a pre-result scorecard; parked futures trend and cross-sectional momentum for unavailable point-in-time data.
- Locked an eight-variant detector/event-feasibility protocol, canonical machine specification, exact development-data fingerprint, dependence-aware power contract, and attempts-ledger record.
- Transparently amended a non-portable pre-execution SQLite text fingerprint to ordered binary IEEE-754/integer hashing; no research rule changed.
- Implemented a pure no-look-ahead consolidation detector, support-recovery event state machine, cross-variant deduplication, and guarded structural-only runner.
- Produced 274 deduplicated development events across 12/12 ETFs and 13 years; breadth/concentration preliminarily pass, while matching and power remain incomplete and decision remains null.
- Fixed Today watchlist scope isolation and made Strategy Lab distinguish unsaved suggested symbols from persisted selections.
- Verification: `219 passed`, locked input reproduction, and byte-identical structural artifact rerun.

## 0.38.0

Stage 8 accepted and closed; Stage 9A research prioritisation is now the active gate.

- Exposed the durable pipeline as a per-model/per-scope ledger with outcome, reason, and new or reused result ID instead of only aggregate counts.
- Added run ID, storage timestamp, and data-through date to each executable candidate-model tab.
- Collapsed manual Steps 1–4 and the once-daily pipeline by default so stored research results remain the primary workspace.
- Recorded the successful real pipeline acceptance: seven full-universe snapshots produced or reused, zero model jobs failed/blocked, and partial-data exclusions disclosed.
- Added a quarantined audits index: point-in-time reviews carry zero acceptance weight and are ignored during ordinary work unless explicitly requested and separately triaged.
- Preserved all research conclusions; this release changes product observability and governance only.

## 0.37.1

Repair of defects found by the first real Stage 8 refresh/pipeline acceptance run; no research conclusion changed.

- Classified `GC=F`, `CL=F`, and `^TNX` as descriptive Yahoo market context outside the long-only equity/ETF strategy universe.
- Added context validation permitting negative crude settlement and settlement outside intraday OHLC while preserving strict equity/ETF validation.
- Replaced all-or-nothing daily discovery with a 90% current-coverage floor; exact exclusions, effective symbols, coverage, and fingerprints remain persisted and visible.
- Kept watchlists strict and formal experiments subject to their locked protocol-specific coverage requirements.
- Added real-failure-pattern tests and exclusion UI/browser contracts. Verification: `212 passed`, full deterministic browser smoke, and a read-only real-data preflight with 516/542 eligible symbols (95.2%), seven ready full-universe jobs, and zero blocked jobs.

## 0.37.0

Stage 8 implementation exit checkpoint; manual user acceptance remains required before 9A.

- Clarified that the daily pipeline is a batch alternative for manual Steps 1–3 across every model and excludes the separate portfolio comparison.
- Exposed the fixed two-second provider pacing and minimum delay estimate in the reviewed plan and confirmation, including jobs that may unblock after refresh.
- Reflowed Today controls, Symbol Research chart/dossier, Macro events, and Data Management controls for narrow screens.
- Expanded deterministic Playwright coverage for pipeline reviewed/running/interrupted states and page-level overflow across every primary view at 390×844.
- Preserved the anti-toy boundary: no strategy, research result, scheduler, provider, paper-trading, or deployment change.
- Verification: `207 passed`; complete browser smoke passed with zero console errors and no provider/strategy execution.

## 0.36.0

Bounded Stage 8D executor slice; no strategy, research conclusion, scheduler, or deployment change.

- Added an explicit confirmed pipeline that refreshes dependencies, re-plans after publication, and runs only fingerprint-changed strategy snapshots through the existing execution path.
- Persisted pipeline identity, stage/job states, timestamps, failures, skips, and result IDs in SQLite; recovered unfinished work is marked `interrupted` after restart.
- Made retry a new plan over current state: successful data and matching snapshots become `skipped_current`, while partial refresh failures block only dependent jobs.
- Added Today run/retry progress while keeping navigation read-only and requiring preview before the UI enables execution.
- Added an anti-toy exit rule: finish the bounded layout/usability/browser checks, then move to Stage 9A rather than expanding infrastructure.
- Added executor recovery, partial-failure, persistence, API, and frontend-contract coverage; verification is `207 passed` plus a live Playwright preview check with zero console errors. The smoke test did not start the 545-symbol refresh.

## 0.35.0

First Stage 8D daily-pipeline slice; planning only, with no executor or scheduler.

- Added deterministic SHA-256 fingerprints over strategy identity/version, defaults, scope, symbols, and exact stored-data coverage.
- Attached the fingerprint to every new explicit strategy snapshot so unchanged work can later be identified without recalculation.
- Added a read-only dependency planner reporting refresh requirements plus `blocked_data`, `ready`, `skipped_current`, and `skipped_empty` model jobs.
- Added an explicit Today preflight preview; navigation remains read-only and the preview performs no refresh or strategy calculation.
- Preserved the yield-shock discussion as a minimal non-evidential brainstorm containing only tentative hypotheses/equation/questions.
- Added planner/fingerprint/API/frontend coverage; verification is `202 passed` plus a live Playwright preflight check with zero console errors.

## 0.34.0

Stage 8C productisation gate closure; no strategy, data, or research result changed.

- Added a repeatable Playwright CLI smoke command requiring only a running local backend and the installed Playwright skill wrapper.
- Covered Today read-only loading, Symbol Research and Strategy Lab not-run states, empty calculation refusal, and Macro’s display-only/no-equity-direction boundary.
- Injected deterministic Data Management running, interrupted, complete-with-errors, and transport-failure states in the browser; asserted disabled controls, recovery guidance, failure counts, unknown freshness, and cleared loaders.
- Kept browser verification network-independent: the suite never starts provider refresh, full-universe scans, backtests, or Strategy Lab computation.
- Documented the command in the root and frontend operating notes. Verification is `198 passed` plus `scripts/browser-smoke.sh`.
- Closed Stage 8C; the next gate is the unscheduled, shared durable daily pipeline in Stage 8D.

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
