# Documentation and resume checkpoint

This file is the authoritative entry point for a new agent or work session. Do not infer current work from the changelog.

## Checkpoint

| Field | Value |
|---|---|
| Version | `0.63.2` |
| Parent release | `0.37.0` (first Stage 8 acceptance candidate) |
| Current state | Single-asset/time-series line **parked** — [stage-closures record](stage-closures/2026-08-20-single-asset-time-series-line.md). Both new engines proven (`app.macro_pit`; cross-sectional bootstrap `N=12→495`, `engine_feasible`); neither authorizes a candidate. Cycle 6: Fed put 14/16, sole eligible candidate, reframed (`0.63.1`) as yield-stress-precedes-QE, not QE-precedes-reversal — the well-known direction isn't a real edge. `TREAST`/`TREAS10Y` live-ingested; [Thesis Track](thesis-track-small-n.md) small-*n* method designed. Treasury buybacks dropped from this candidate entirely (different institution/mandate than the Fed) — `app.treasury_buybacks` remains built and live-verified infrastructure, unused by any candidate for now. Not yet preregistered |
| Verification | `324 passed` at `0.63.0` |
| Completed | Stage 8; Stage 9A Cycles 1–6; CTA v1/v2; TA Breakout, Wave Pull, ETF-12 rotation, both calendar candidates, Overnight Gap — all closed and indexed in [research-protocols/README.md](research-protocols/README.md) |
| Next product work | Preregister Fed put: lock hypothesis/episode definitions (dated by policy record, not outcome data — [Thesis Track](thesis-track-small-n.md)), estimand, placebo-window null construction, fingerprint. `S/R Bounce`, a reversal-framed overnight-gap candidate, MACD, Elliott Wave remain separately parked — see [pending checklist](brainstorm/2026-08-19-pending-candidate-checklist.md) |
| Active research | Fed put (Cycle 6), pending preregistration. 6-variable [macro library](brainstorm/2026-08-20-macro-reaction-function-narrative-library.md): idea-stage. [Cross-sectional](brainstorm/2026-08-20-cross-sectional-experiment-ideas.md): disqualified this cycle (Tier 4 unpurchased). Stage 9B remains gated |
| Parked operations | Stage 10 cron; Stage 11 deployment |
| Pending triage | 2026-08-19 methodology/implementation audit — H2 (non-atomic bar publication) fixed in `0.54.0`; 2 critical, 1 high (H1, the orphaned mutating `GET /api/today`), 5 medium, 4 low remain untriaged; see [audits/README.md](audits/README.md) |

`0.37.1` fixed two full-universe-scan contract defects (settlement-vs-equity candle confusion; a small invalid subset blocking every scan) — see CHANGELOG if debugging scan coverage.

Local-optimum guard: Stage 8 is closed, do not add infrastructure/UX polish absent a concrete defect. The single-asset/time-series line is parked — read [stage-closures](stage-closures/2026-08-20-single-asset-time-series-line.md) before proposing anything back into it. No closed result licenses a reflexive follow-up (wider window, pooled version, same claim retried) — that is always a new, independently justified candidate.

Research is active (Cycle 6, Fed put). Do not tune CTA v1 after its rejection. Do not skip [next-priority-evaluation.md](next-priority-evaluation.md) when >1 candidate is live.

## Non-negotiable state

- Product purpose: decide `reject`, `revise`, or `continue research`; never imply validated profit.
- Default project benchmark: Passive ETF-12 v1; every new protocol audits suitability; SPY and cash remain references.
- CTA v1: rejected under its locked protocol; this does not reject trend following generally.
- Execution: signal on completed close `N`, fill at next available open `N+1`.
- Watchlists: user-selected symbols persist per strategy and show lifecycle state.
- Candidate tabs: full-universe new-entry candidates per model, plus intersections; they are not watchlists.
- Data refresh and strategy runs are explicit actions, not navigation side effects.
- Macro series are non-tradable context under [ADR 0006](adr/0006-macro-data-contract.md); they never generate candidates until point-in-time data and a preregistered hypothesis exist.
- Cron, paper/live trading, brokers, and AWS remain out of scope.

## Environment and data portability

`data/` and `.venv/` are git-ignored ([data/README.md](../data/README.md)); Git carries specifications, code, and immutable evidence, never the local database or interpreter. A checkout without both populated can read, edit, and plan documentation and specifications, and can run any test that does not require `data/market.db` rows; it cannot run the server or any detector/matching/experiment runner against real data.

A locked specification's data fingerprint (for example `consolidation-support-feasibility-v1`'s `development_sha256`) is computed over the exact rows in `data/market.db` at lock time. Re-fetching is not a substitute: Yahoo `auto_adjust=True` rebases full price history on every dividend, so a fresh `python -m app.fetch` run is not guaranteed to reproduce a prior fingerprint, and `run_consolidation_feasibility.py` raises `RuntimeError` on any mismatch rather than proceeding on unverified data. To move locked-data execution to another machine, copy the `data/market.db` file itself; do not re-fetch and expect an identical hash.

Consequence for new locked work (Stage 9A Cycle 2 or later): candidate selection, scorecard, and protocol drafting need no data. Locking a specification's data fingerprint and running its detector must happen on the machine holding the intended `data/market.db`; that machine then becomes the only one able to execute that specification until the database file is copied across.

On a checkout with no `data/market.db` rows, `pytest -q` fails exactly two tests, not zero: `test_consolidation_feasibility.py::test_real_locked_spec_and_development_data_reproduce` (fingerprint mismatch against an empty database) and `test_api.py::test_signal_rejects_unknown_parameter` (`/api/signal/SPY` returns `404` before parameter validation because `SPY` is not stored). Both are the expected empty-database state, confirmed by direct run at `0.41.0`, not a regression to fix.

## Document authority

| Question | Authoritative document |
|---|---|
| What is the product? | [Product contract](product.md) |
| What are we actually running? (distilled, load first) | [Product identity](identity.md) |
| How should the interface work? | [Workspace redesign](workspace-redesign.md) |
| What happens next? | [Roadmap](roadmap.md) |
| How was CTA v1 tested? | [Research protocol](research-protocol.md) |
| What did CTA v1 show? | [Result](research-results/cta-trend-wf-v1.md) and [audit](research-results/cta-trend-wf-v1-audit.md) |
| What research may follow? | [Research backlog](research-backlog.md) |
| How does a narrative become a measurable hypothesis? | [Hypothesis engineering](hypothesis-engineering.md) |
| How is a candidate selected and allowed to advance? | [Model acceptance standard](model-acceptance-standard.md) |
| How is candidate search governed? | [Exploration protocol](exploration-protocol.md) |
| How to rank across multiple live candidates? | [Next-priority evaluation](next-priority-evaluation.md) |
| How to test a claim with only a handful of regime episodes? | [Thesis Track](thesis-track-small-n.md) |
| Which Stage 9A candidate was prioritised, and why? | [Candidate-selection index](research-candidates/README.md) and [Cycle 1 record](research-candidates/2026-08-19-cycle-1.md) |
| Which new preregistrations exist? | [Research-protocol index](research-protocols/README.md) |
| What did consolidation feasibility v1 establish? | [Result](research-results/consolidation-support-feasibility-v1.md) |
| What did the properly-powered CTA v2 retest show? | [Result](research-results/cta-v2-pooled-trend-overlay.md) |
| Is the event-recomputing bootstrap machinery itself trustworthy? | [Type-I calibration](research-results/event-bootstrap-calibration-v1.md) |
| Where do non-contract brainstorm notes live? | [Brainstorm index](brainstorm/README.md) |
| Where do point-in-time codebase/methodology audits live? | [Audits index](audits/README.md) |
| Where are research-line/paradigm boundaries recorded, and why did a line pause? | [Stage closures index](stage-closures/README.md) |
| How is macro data governed? | [Macro data contract](adr/0006-macro-data-contract.md) |
| What is the drafted consolidation study? | [Daily Consolidation Zone v1](research-hypotheses/daily-consolidation-zone-v1.md) |
| Why are contracts fixed this way? | [ADRs](adr/) |
| What changed by version? | [Changelog](../CHANGELOG.md) |

Component notes: [backend](../backend/README.md), [frontend](../frontend/README.md), [data](../data/README.md), and [generated outputs](../output/research/README.md).

## Resume sequence

1. Confirm `git status`, current version, and tests.
2. Read this checkpoint, then [product identity](identity.md), then the document for the active stage.
3. Preserve locked contracts unless creating a versioned ADR/protocol amendment.
4. Implement one bounded stage slice; update tests, roadmap, checkpoint, and changelog together.
5. Record research evidence as immutable results, not rewritten narrative.
