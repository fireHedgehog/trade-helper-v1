# Documentation and resume checkpoint

This file is the authoritative entry point for a new agent or work session. Do not infer current work from the changelog.

## Checkpoint

| Field | Value |
|---|---|
| Version | `0.68.0` |
| Parent release | `0.37.0` (first Stage 8 acceptance candidate) |
| Current state | Research reorganized into a chaptered, living program — see [research-program.md](research-program.md). Chapters 1-3 (single-asset/TA+calendar, cross-sectional, macro/event-driven) hold the existing strict falsification standard unchanged; a new, parallel Chapter 4 (risk-budgeted ensemble construction, [ADR 0007](adr/0007-risk-budgeted-ensemble-acceptance.md), draft/proposed) answers a different question — not "is this proven," but "is this worth a small, sized, loss-controlled bet" — reusing ADR 0004's existing loss-based sizing formula and drawdown halt rather than inventing new risk machinery |
| Verification | `332 passed` at `0.67.0`; not re-run for this doc-only 0.68.0 change — re-run before touching code |
| Completed | Stage 8; Stage 9A Cycles 1–6; CTA v1/v2; TA Breakout, Wave Pull, ETF-12 rotation, both calendar candidates, Overnight Gap, Fed put yield-stress precursor v1+v2+v3 — all closed and indexed in [research-protocols/README.md](research-protocols/README.md); labor-market claims lead-lag operationalized and bounded-explored (not yet scored) |
| Next product work | No queued Stage 9A candidate. ADR 0007 is a draft awaiting review, not yet accepted — the ensemble-construction engine, confidence-multiplier sizing function, and minimum-breadth floor it names are required decisions, not yet built. Chapter 1-3 open threads (not yet sections): Dow theory swing structure, Fibonacci, golden/death cross, 52-week-high anchoring (Ch.1); the six Tier-4-blocked cross-sectional ideas (Ch.2); the 7-variable macro library, PEAD/earnings-gap (needs an earnings-date ingestion module — `yfinance.get_earnings_dates()` confirmed working, free, 1987-2026 depth), policy-exposure factor (Ch.3) — see [research-program.md](research-program.md) for the full inventory |
| Active research | None active. Next step is a deliberate choice: accept/revise ADR 0007 and start building Chapter 4's engine, or pick a Chapter 1-3 open thread via [next-priority-evaluation.md](next-priority-evaluation.md). Stage 9B remains gated |
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
| What's the whole research program's shape, and how does a closed line get reopened honestly? | [Research program index](research-program.md) |
| Can a signal that hasn't cleared the strict falsification bar ever be sized and traded? | [ADR 0007 (draft)](adr/0007-risk-budgeted-ensemble-acceptance.md) |
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
